"""Photo upload and AI estimation helpers for food records."""

from __future__ import annotations

import base64
import json
import mimetypes
import uuid
from dataclasses import dataclass

import requests
from flask import current_app


ALLOWED_IMAGE_MIME_TYPES = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp',
}


@dataclass
class UploadedFoodPhoto:
    path: str
    url: str
    mime_type: str


def _require_config(key: str) -> str:
    value = current_app.config.get(key)
    if not value:
        raise RuntimeError(f'Missing required configuration: {key}')
    return value


def _validate_image_upload(image_file) -> tuple[bytes, str, str]:
    if image_file is None or not image_file.filename:
        raise ValueError('Missing required image file')

    mime_type = image_file.mimetype or 'application/octet-stream'
    if mime_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise ValueError('Unsupported image type. Please upload JPG, PNG, or WebP')

    image_bytes = image_file.read()
    if not image_bytes:
        raise ValueError('Uploaded image is empty')

    max_size = current_app.config.get('MAX_UPLOAD_IMAGE_BYTES', 5 * 1024 * 1024)
    if len(image_bytes) > max_size:
        raise ValueError('Image is too large. Maximum size is 5 MB')

    return image_bytes, mime_type, ALLOWED_IMAGE_MIME_TYPES[mime_type]


def _validate_image_mime(mime_type: str) -> str:
    if mime_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise ValueError('Unsupported image type. Please upload JPG, PNG, or WebP')
    return mime_type


def upload_food_photo(user_id: int | str, image_bytes: bytes, mime_type: str, file_extension: str) -> UploadedFoodPhoto:
    supabase_url = _require_config('SUPABASE_URL').rstrip('/')
    service_role_key = _require_config('SUPABASE_SERVICE_ROLE_KEY')
    bucket = current_app.config.get('SUPABASE_STORAGE_BUCKET', 'food-records')
    object_path = f"food-records/{user_id}/{uuid.uuid4().hex}{file_extension}"

    response = requests.post(
        f"{supabase_url}/storage/v1/object/{bucket}/{object_path}",
        headers={
            'apikey': service_role_key,
            'Authorization': f'Bearer {service_role_key}',
            'Content-Type': mime_type,
            'x-upsert': 'false',
        },
        data=image_bytes,
        timeout=30,
    )
    if response.status_code >= 400:
        raise RuntimeError(f'Supabase upload failed: {response.text}')

    if current_app.config.get('SUPABASE_STORAGE_PUBLIC', True):
        public_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{object_path}"
    else:
        public_url = f"{supabase_url}/storage/v1/object/authenticated/{bucket}/{object_path}"

    return UploadedFoodPhoto(path=object_path, url=public_url, mime_type=mime_type)


def delete_food_photo(object_path: str) -> None:
    if not object_path:
        return

    supabase_url = _require_config('SUPABASE_URL').rstrip('/')
    service_role_key = _require_config('SUPABASE_SERVICE_ROLE_KEY')
    bucket = current_app.config.get('SUPABASE_STORAGE_BUCKET', 'food-records')

    requests.delete(
        f"{supabase_url}/storage/v1/object/{bucket}/{object_path}",
        headers={
            'apikey': service_role_key,
            'Authorization': f'Bearer {service_role_key}',
        },
        timeout=15,
    )


def _extract_json_from_text(content: str) -> dict:
    cleaned = content.strip()
    if cleaned.startswith('```'):
        lines = cleaned.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        cleaned = '\n'.join(lines).strip()
    return json.loads(cleaned)


def _infer_mime_type(photo_url: str, photo_mime_type: str | None = None) -> str:
    if photo_mime_type:
        return _validate_image_mime(photo_mime_type)

    guessed_mime, _ = mimetypes.guess_type(photo_url)
    if guessed_mime:
        return _validate_image_mime(guessed_mime)

    raise ValueError('Unable to determine image type. Please provide photo_mime_type')


def _estimate_food_from_photo_openai(image_bytes: bytes, mime_type: str) -> dict:
    api_key = _require_config('OPENAI_API_KEY')
    base_url = _require_config('OPENAI_BASE_URL').rstrip('/')
    model = current_app.config.get('OPENAI_VISION_MODEL', 'gpt-4.1-mini')
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    data_url = f'data:{mime_type};base64,{image_base64}'

    response = requests.post(
        f"{base_url}/chat/completions",
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        json={
            'model': model,
            'response_format': {'type': 'json_object'},
            'temperature': 0.2,
            'messages': [
                {
                    'role': 'system',
                    'content': (
                        'You estimate nutrition from a single food image. '
                        'Always return JSON with keys: estimated_name, estimated_calories, '
                        'estimated_type, estimated_restaurant, estimated_price, estimated_protein, '
                        'estimated_fat, estimated_carb, estimated_sugar, estimated_sodium, confidence, notes. '
                        'All text values must be Traditional Chinese (Taiwan), unless proper nouns are in English.'
                    ),
                },
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': (
                                '請估算這張餐點照片的一份營養資訊，並只回傳 JSON。'
                                'estimated_calories 為整數。estimated_protein、estimated_fat、estimated_carb、'
                                'estimated_sugar 單位為 g；estimated_sodium 單位為 mg。'
                                'confidence 請回傳 0 到 1。若無法判斷請填 null。'
                                'estimated_name、estimated_type、estimated_restaurant、notes 請使用繁體中文。'
                            ),
                        },
                        {
                            'type': 'image_url',
                            'image_url': {'url': data_url},
                        },
                    ],
                },
            ],
            'max_tokens': 400,
        },
        timeout=60,
    )
    if response.status_code >= 400:
        raise RuntimeError(f'Vision estimation failed: {response.text}')

    content = response.json()['choices'][0]['message']['content']
    parsed = _extract_json_from_text(content)

    return _normalize_estimation_result(parsed, provider='openai_vision')


def _estimate_food_from_photo_gemini(image_bytes: bytes, mime_type: str) -> dict:
    api_key = _require_config('GEMINI_API_KEY')
    base_url = _require_config('GEMINI_BASE_URL').rstrip('/')
    model = current_app.config.get('GEMINI_MODEL', 'gemini-2.5-flash')
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    response = requests.post(
        f"{base_url}/models/{model}:generateContent?key={api_key}",
        headers={'Content-Type': 'application/json'},
        json={
            'contents': [
                {
                    'parts': [
                        {
                            'text': (
                                '請根據這張餐點照片估算營養資訊，只回傳 JSON。'
                                'Keys must be: estimated_name, estimated_calories, estimated_type, '
                                'estimated_restaurant, estimated_price, estimated_protein, estimated_fat, '
                                'estimated_carb, estimated_sugar, estimated_sodium, confidence, notes. '
                                'estimated_calories 為整數。estimated_protein、estimated_fat、estimated_carb、'
                                'estimated_sugar 單位為 g；estimated_sodium 單位為 mg。'
                                'confidence 必須是 0~1。無法判斷請使用 null。'
                                '所有文字欄位請使用繁體中文（台灣），除非是專有名詞。'
                            )
                        },
                        {
                            'inline_data': {
                                'mime_type': mime_type,
                                'data': image_base64,
                            }
                        }
                    ]
                }
            ],
            'generationConfig': {
                'temperature': 0.2,
                'responseMimeType': 'application/json',
            },
        },
        timeout=60,
    )
    if response.status_code >= 400:
        raise RuntimeError(f'Vision estimation failed: {response.text}')

    response_json = response.json()
    candidates = response_json.get('candidates') or []
    if not candidates:
        raise RuntimeError('Vision estimation failed: empty Gemini response')

    parts = candidates[0].get('content', {}).get('parts', [])
    text_content = None
    for part in parts:
        if part.get('text'):
            text_content = part['text']
            break
    if not text_content:
        raise RuntimeError('Vision estimation failed: Gemini did not return text content')

    parsed = _extract_json_from_text(text_content)
    return _normalize_estimation_result(parsed, provider='gemini_2_5_flash')


def _normalize_estimation_result(parsed: dict, provider: str) -> dict:
    def _normalize_optional_float(value):
        try:
            return round(float(value), 2) if value is not None else None
        except (TypeError, ValueError):
            return None

    calories = parsed.get('estimated_calories')
    try:
        normalized_calories = int(float(calories)) if calories is not None else None
    except (TypeError, ValueError):
        normalized_calories = None

    confidence = parsed.get('confidence')
    try:
        normalized_confidence = round(float(confidence), 3) if confidence is not None else None
    except (TypeError, ValueError):
        normalized_confidence = None

    normalized_protein = _normalize_optional_float(parsed.get('estimated_protein'))
    normalized_fat = _normalize_optional_float(parsed.get('estimated_fat'))
    normalized_carb = _normalize_optional_float(parsed.get('estimated_carb'))
    normalized_sugar = _normalize_optional_float(parsed.get('estimated_sugar'))
    normalized_sodium = _normalize_optional_float(parsed.get('estimated_sodium'))

    return {
        'estimated_name': parsed.get('estimated_name') or '未辨識餐點',
        'estimated_calories': normalized_calories,
        'estimated_type': parsed.get('estimated_type'),
        'estimated_restaurant': parsed.get('estimated_restaurant'),
        'estimated_price': parsed.get('estimated_price'),
        'estimated_protein': normalized_protein,
        'estimated_fat': normalized_fat,
        'estimated_carb': normalized_carb,
        'estimated_sugar': normalized_sugar,
        'estimated_sodium': normalized_sodium,
        'confidence': normalized_confidence,
        'notes': parsed.get('notes'),
        'provider': provider,
        'raw': parsed,
    }


def estimate_food_from_photo(image_bytes: bytes, mime_type: str) -> dict:
    provider = str(current_app.config.get('AI_PROVIDER', 'gemini')).strip().lower()
    if provider == 'openai':
        return _estimate_food_from_photo_openai(image_bytes, mime_type)
    if provider in {'gemini', 'gemini2.5', 'gemini-2.5', 'gemini-2.5-flash'}:
        return _estimate_food_from_photo_gemini(image_bytes, mime_type)
    raise RuntimeError(f'Unsupported AI provider: {provider}')


def upload_food_photo_only(user_id: int | str, image_file) -> dict:
    image_bytes, mime_type, _ = _validate_image_upload(image_file)
    upload = upload_food_photo(user_id, image_bytes, mime_type, ALLOWED_IMAGE_MIME_TYPES[mime_type])
    return {
        'photo_url': upload.url,
        'photo_path': upload.path,
        'photo_mime_type': upload.mime_type,
    }


def estimate_existing_food_photo(photo_url: str, photo_path: str | None = None, photo_mime_type: str | None = None) -> dict:
    if not photo_url:
        raise ValueError('Missing required field: photo_url')

    response = requests.get(photo_url, timeout=30)
    if response.status_code >= 400:
        raise RuntimeError(f'Failed to fetch uploaded photo: {response.text}')

    mime_type = _infer_mime_type(photo_url, photo_mime_type)
    estimation = estimate_food_from_photo(response.content, mime_type)
    return {
        'photo_url': photo_url,
        'photo_path': photo_path or '',
        'photo_mime_type': mime_type,
        'estimated_name': estimation['estimated_name'],
        'estimated_calories': estimation['estimated_calories'],
        'estimated_type': estimation['estimated_type'],
        'estimated_restaurant': estimation['estimated_restaurant'],
        'estimated_price': estimation['estimated_price'],
        'estimated_protein': estimation['estimated_protein'],
        'estimated_fat': estimation['estimated_fat'],
        'estimated_carb': estimation['estimated_carb'],
        'estimated_sugar': estimation['estimated_sugar'],
        'estimated_sodium': estimation['estimated_sodium'],
        'estimation_confidence': estimation['confidence'],
        'estimation_provider': estimation['provider'],
        'estimation_notes': estimation['notes'],
        'estimation_raw': estimation['raw'],
    }


def upload_and_estimate_food_photo(user_id: int | str, image_file) -> dict:
    image_bytes, mime_type, _ = _validate_image_upload(image_file)
    upload = upload_food_photo(user_id, image_bytes, mime_type, ALLOWED_IMAGE_MIME_TYPES[mime_type])

    try:
        estimation = estimate_food_from_photo(image_bytes, mime_type)
    except Exception:
        delete_food_photo(upload.path)
        raise

    return {
        'photo_url': upload.url,
        'photo_path': upload.path,
        'photo_mime_type': upload.mime_type,
        'estimated_name': estimation['estimated_name'],
        'estimated_calories': estimation['estimated_calories'],
        'estimated_type': estimation['estimated_type'],
        'estimated_restaurant': estimation['estimated_restaurant'],
        'estimated_price': estimation['estimated_price'],
        'estimated_protein': estimation['estimated_protein'],
        'estimated_fat': estimation['estimated_fat'],
        'estimated_carb': estimation['estimated_carb'],
        'estimated_sugar': estimation['estimated_sugar'],
        'estimated_sodium': estimation['estimated_sodium'],
        'estimation_confidence': estimation['confidence'],
        'estimation_provider': estimation['provider'],
        'estimation_notes': estimation['notes'],
        'estimation_raw': estimation['raw'],
    }