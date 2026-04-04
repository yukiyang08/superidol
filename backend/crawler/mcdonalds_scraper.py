import argparse
import csv
import html
import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import psycopg
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


BASE_URL = "https://www.mcdonalds.com"
FULL_MENU_URL = f"{BASE_URL}/tw/zh-tw/full-menu.html"
NUTRITION_CALCULATOR_URL = f"{BASE_URL}/tw/zh-tw/sustainability/good-food/nutrition-calculator.html"
DEFAULT_TIMEOUT = 25


@dataclass
class McdonaldsItem:
    item_name: str
    category: str
    detail_url: str
    source_page: str
    image_url: str | None
    price_twd: int | None
    calories_kcal: float | None
    protein_g: float | None
    fat_g: float | None
    saturated_fat_g: float | None
    trans_fat_g: float | None
    carb_g: float | None
    sodium_mg: float | None
    nutrition_json: str
    crawled_at: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def normalize_slug_from_url(url: str) -> str:
    path = urlparse(url).path
    name = Path(path).name
    if name.endswith(".html"):
        name = name[:-5]
    return normalize_whitespace(name).lower()


def to_float(value: str | int | float | None) -> float | None:
    if value is None:
        return None
    text = normalize_whitespace(str(value))
    if not text:
        return None
    text = text.replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "SuperIdol-McDonalds-DataBot/1.0 (research; contact: dev@local)",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
        }
    )
    return session


def get_soup(session: requests.Session, url: str) -> BeautifulSoup:
    resp = session.get(url, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    return BeautifulSoup(resp.text, "html.parser")


def crawl_full_menu_cards(session: requests.Session) -> tuple[dict[str, dict], dict[str, str]]:
    soup = get_soup(session, FULL_MENU_URL)

    cards: dict[str, dict] = {}
    product_id_to_slug: dict[str, str] = {}
    current_category = "Uncategorized"

    for node in soup.find_all(["h2", "li"]):
        if node.name == "h2":
            category_text = normalize_whitespace(node.get_text(" "))
            if category_text:
                current_category = category_text
            continue

        if "cmp-category__item" not in (node.get("class") or []):
            continue

        link_node = node.select_one("a.cmp-category__item-link")
        if not link_node:
            continue

        href = normalize_whitespace(link_node.get("href", ""))
        if not href:
            continue

        detail_url = urljoin(BASE_URL, href)
        slug = normalize_slug_from_url(detail_url)
        if not slug:
            continue

        product_id = normalize_whitespace(node.get("data-product-id", ""))
        if product_id:
            product_id_to_slug[product_id] = slug

        name_node = node.select_one(".cmp-category__item-name")
        item_name = normalize_whitespace(name_node.get_text(" ") if name_node else "")

        image_node = node.select_one("img.categories-item-img")
        image_url = None
        if image_node:
            image_url = normalize_whitespace(image_node.get("src", "")) or None
            if image_url and image_url.startswith("/"):
                image_url = urljoin(BASE_URL, image_url)

        cards[slug] = {
            "item_name": item_name,
            "category": current_category,
            "detail_url": detail_url,
            "image_url": image_url,
            "source_page": FULL_MENU_URL,
            "product_id": product_id,
        }

    return cards, product_id_to_slug


def parse_nutrients(nutrients: list[dict]) -> dict[str, float | None]:
    result = {
        "calories_kcal": None,
        "protein_g": None,
        "fat_g": None,
        "saturated_fat_g": None,
        "trans_fat_g": None,
        "carb_g": None,
        "sodium_mg": None,
    }

    key_map = {
        "energy_kcal": "calories_kcal",
        "protein": "protein_g",
        "fat": "fat_g",
        "saturated_fat": "saturated_fat_g",
        "trans_fat": "trans_fat_g",
        "carbohydrate": "carb_g",
        "sodium": "sodium_mg",
    }

    for nutrient in nutrients:
        nutrient_key = normalize_whitespace(str(nutrient.get("nutrient_name_id", ""))).lower()
        mapped_key = key_map.get(nutrient_key)
        if not mapped_key:
            continue

        parsed_value = to_float(nutrient.get("value"))
        result[mapped_key] = parsed_value

    return result


def crawl_nutrition_items(session: requests.Session) -> dict[str, dict]:
    soup = get_soup(session, NUTRITION_CALCULATOR_URL)
    calc_node = soup.select_one(".cmp-nutrition-calculator")
    if not calc_node:
        raise RuntimeError("Could not locate nutrition calculator dataset on McDonald's page.")

    product_data_raw = html.unescape(calc_node.get("data-product-data", ""))
    if not product_data_raw:
        raise RuntimeError("McDonald's nutrition calculator missing data-product-data payload.")

    product_data = json.loads(product_data_raw)
    category_list = product_data.get("categoryList") or []

    product_collection_api = normalize_whitespace(calc_node.get("data-product-collection-api", ""))
    if not product_collection_api:
        raise RuntimeError("Missing data-product-collection-api in nutrition calculator.")

    site_country = normalize_whitespace(calc_node.get("data-site-country", "TW"))
    site_language = normalize_whitespace(calc_node.get("data-site-language", "zh"))
    show_live_data = normalize_whitespace(calc_node.get("data-show-live-data", "true"))

    result: dict[str, dict] = {}

    for category in category_list:
        category_name = normalize_whitespace(str(category.get("title", ""))) or "Uncategorized"
        product_ids = [normalize_whitespace(str(x)) for x in (category.get("productId") or []) if normalize_whitespace(str(x))]
        if not product_ids:
            continue

        item_param = "".join(f"{product_id}()-" for product_id in product_ids)
        params = {
            "country": site_country,
            "language": site_language,
            "showLiveData": show_live_data,
            "nutrient_req": "Y",
            "item": item_param,
        }

        response = session.get(urljoin(BASE_URL, product_collection_api), params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        payload = response.json()

        raw_items = payload.get("items", {}).get("item")
        if not raw_items:
            continue

        if isinstance(raw_items, dict):
            items = [raw_items]
        else:
            items = [x for x in raw_items if isinstance(x, dict)]

        for product in items:
            short_name = normalize_whitespace(str(product.get("short_name", ""))).lower()
            product_id = normalize_whitespace(str(product.get("id", "")))
            if not short_name:
                short_name = product_id
            if not short_name:
                continue

            name = normalize_whitespace(str(product.get("item_marketing_name") or product.get("item_name") or ""))
            detail_url = f"{BASE_URL}/tw/zh-tw/product/{short_name}.html"

            nutrients = product.get("nutrient_facts", {}).get("nutrient") or []
            if isinstance(nutrients, dict):
                nutrients = [nutrients]
            nutrient_data = parse_nutrients([x for x in nutrients if isinstance(x, dict)])

            result[short_name] = {
                "item_name": name,
                "category": category_name,
                "detail_url": detail_url,
                "product_id": product_id,
                "nutrients": nutrient_data,
                "source_page": NUTRITION_CALCULATOR_URL,
            }

    return result


def build_items(
    menu_cards: dict[str, dict],
    nutrition_items: dict[str, dict],
    product_id_to_slug: dict[str, str],
) -> list[McdonaldsItem]:
    normalized_nutrition_items: dict[str, dict] = {}
    for nutrition_key, nutrition in nutrition_items.items():
        product_id = normalize_whitespace(str(nutrition.get("product_id", "")))
        preferred_key = product_id_to_slug.get(product_id) or nutrition_key
        normalized_nutrition_items[preferred_key] = nutrition

    keys = sorted(set(menu_cards.keys()) | set(normalized_nutrition_items.keys()))
    items: list[McdonaldsItem] = []

    for key in keys:
        menu = menu_cards.get(key, {})
        nutrition = normalized_nutrition_items.get(key, {})
        nutrients = nutrition.get("nutrients", {})

        detail_url = menu.get("detail_url") or nutrition.get("detail_url") or NUTRITION_CALCULATOR_URL
        category = menu.get("category") or nutrition.get("category") or "Uncategorized"
        name = menu.get("item_name") or nutrition.get("item_name") or key

        nutrition_payload = json.dumps(
            {
                "calories_kcal": nutrients.get("calories_kcal"),
                "protein_g": nutrients.get("protein_g"),
                "fat_g": nutrients.get("fat_g"),
                "saturated_fat_g": nutrients.get("saturated_fat_g"),
                "trans_fat_g": nutrients.get("trans_fat_g"),
                "carb_g": nutrients.get("carb_g"),
                "sodium_mg": nutrients.get("sodium_mg"),
                "source": "mcdonalds_nutrition_calculator",
            },
            ensure_ascii=False,
        )

        items.append(
            McdonaldsItem(
                item_name=name,
                category=category,
                detail_url=detail_url,
                source_page=menu.get("source_page") or nutrition.get("source_page") or FULL_MENU_URL,
                image_url=menu.get("image_url"),
                price_twd=None,
                calories_kcal=nutrients.get("calories_kcal"),
                protein_g=nutrients.get("protein_g"),
                fat_g=nutrients.get("fat_g"),
                saturated_fat_g=nutrients.get("saturated_fat_g"),
                trans_fat_g=nutrients.get("trans_fat_g"),
                carb_g=nutrients.get("carb_g"),
                sodium_mg=nutrients.get("sodium_mg"),
                nutrition_json=nutrition_payload,
                crawled_at=now_iso(),
            )
        )

    deduped: dict[str, McdonaldsItem] = {}
    for item in items:
        key = normalize_slug_from_url(item.detail_url)
        if key and key not in deduped:
            deduped[key] = item

    return list(deduped.values())


def crawl_mcdonalds() -> list[McdonaldsItem]:
    session = get_session()
    menu_cards, product_id_to_slug = crawl_full_menu_cards(session)
    nutrition_items = crawl_nutrition_items(session)
    return build_items(menu_cards, nutrition_items, product_id_to_slug)


def write_csv(items: list[McdonaldsItem], output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "item_name",
                "category",
                "image_url",
                "price_twd",
                "calories_kcal",
                "protein_g",
                "fat_g",
                "saturated_fat_g",
                "trans_fat_g",
                "carb_g",
                "sodium_mg",
                "nutrition_json",
                "detail_url",
                "source_page",
                "crawled_at",
            ],
        )
        writer.writeheader()
        for item in items:
            writer.writerow(asdict(item))


def _to_int_or_none(value: str | None) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "" or text.lower() == "null":
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def _to_float_or_none(value: str | None) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "" or text.lower() == "null":
        return None
    text = text.replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _normalize_nullable_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "" or text.lower() == "null":
        return None
    return text


def read_items_from_csv(csv_path: Path) -> list[McdonaldsItem]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    items: list[McdonaldsItem] = []
    with csv_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            item_name = normalize_whitespace(row.get("item_name", ""))
            category = normalize_whitespace(row.get("category", ""))
            detail_url = normalize_whitespace(row.get("detail_url", ""))
            source_page = normalize_whitespace(row.get("source_page", ""))

            if not item_name or not category:
                continue

            nutrition_payload = row.get("nutrition_json")
            if not nutrition_payload:
                nutrition_payload = json.dumps(
                    {
                        "calories_kcal": _to_float_or_none(row.get("calories_kcal")),
                        "protein_g": _to_float_or_none(row.get("protein_g")),
                        "fat_g": _to_float_or_none(row.get("fat_g")),
                        "saturated_fat_g": _to_float_or_none(row.get("saturated_fat_g")),
                        "trans_fat_g": _to_float_or_none(row.get("trans_fat_g")),
                        "carb_g": _to_float_or_none(row.get("carb_g")),
                        "sodium_mg": _to_float_or_none(row.get("sodium_mg")),
                    },
                    ensure_ascii=False,
                )

            items.append(
                McdonaldsItem(
                    item_name=item_name,
                    category=category,
                    detail_url=detail_url,
                    source_page=source_page,
                    image_url=_normalize_nullable_text(row.get("image_url")),
                    price_twd=_to_int_or_none(row.get("price_twd")),
                    calories_kcal=_to_float_or_none(row.get("calories_kcal")),
                    protein_g=_to_float_or_none(row.get("protein_g")),
                    fat_g=_to_float_or_none(row.get("fat_g")),
                    saturated_fat_g=_to_float_or_none(row.get("saturated_fat_g")),
                    trans_fat_g=_to_float_or_none(row.get("trans_fat_g")),
                    carb_g=_to_float_or_none(row.get("carb_g")),
                    sodium_mg=_to_float_or_none(row.get("sodium_mg")),
                    nutrition_json=nutrition_payload,
                    crawled_at=_normalize_nullable_text(row.get("crawled_at")) or now_iso(),
                )
            )

    return items


def get_db_connection() -> psycopg.Connection:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")

    host = os.getenv("DB_HOST")
    port = int(os.getenv("DB_PORT", "5432"))
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    dbname = os.getenv("DB_NAME", "postgres")

    if not all([host, user, password, dbname]):
        raise RuntimeError("Missing DB env vars. Please set DB_HOST, DB_USER, DB_PASSWORD, DB_NAME in backend/.env")

    return psycopg.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=dbname,
        sslmode="require",
        prepare_threshold=None,
    )


def upsert_to_supabase(items: list[McdonaldsItem], restaurant_name: str = "麥當勞") -> tuple[int, int]:
    inserted = 0
    updated = 0

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT restaurantid FROM restaurant WHERE name = %s LIMIT 1", (restaurant_name,))
            row = cursor.fetchone()

            if row:
                restaurant_id = row[0]
            else:
                cursor.execute(
                    "INSERT INTO restaurant (type, name, averageprice) VALUES (%s, %s, %s) RETURNING restaurantid",
                    ("FastFood", restaurant_name, 120),
                )
                restaurant_id = cursor.fetchone()[0]

            for item in items:
                cursor.execute(
                    "SELECT foodid FROM food WHERE restaurantid = %s AND name = %s LIMIT 1",
                    (restaurant_id, item.item_name),
                )
                existing = cursor.fetchone()

                calories_value = float(item.calories_kcal) if item.calories_kcal is not None else 0.0
                protein_value = item.protein_g if item.protein_g is not None else 0
                fat_value = item.fat_g if item.fat_g is not None else 0
                sodium_value = item.sodium_mg if item.sodium_mg is not None else 0
                carb_value = item.carb_g if item.carb_g is not None else 0

                if existing:
                    cursor.execute(
                        """
                        UPDATE food
                        SET calories = %s,
                            price = %s,
                            food_type = %s,
                            set_type = %s,
                            imageurl = %s,
                            protein = %s,
                            fat = %s,
                            sodium = %s,
                            carb = %s
                        WHERE foodid = %s
                        """,
                        (
                            calories_value,
                            item.price_twd,
                            "FastFood",
                            "飲料",
                            item.image_url,
                            protein_value,
                            fat_value,
                            sodium_value,
                            carb_value,
                            existing[0],
                        ),
                    )
                    updated += 1
                else:
                    cursor.execute(
                        """
                        INSERT INTO food (name, calories, price, food_type, set_type, restaurantid, imageurl, protein, fat, sodium, carb)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            item.item_name,
                            calories_value,
                            item.price_twd,
                            "FastFood",
                            "飲料",
                            restaurant_id,
                            item.image_url,
                            protein_value,
                            fat_value,
                            sodium_value,
                            carb_value,
                        ),
                    )
                    inserted += 1

        conn.commit()

    return inserted, updated


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crawl McDonald's menu and export CSV / upsert into Supabase")
    parser.add_argument("--output", type=str, default="backend/crawler/output/mcdonalds_menu.csv", help="CSV output path")
    parser.add_argument("--from-csv", type=str, default=None, help="Load items from CSV instead of crawling")
    parser.add_argument("--to-supabase", action="store_true", help="Upsert crawled data into Supabase")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.from_csv:
        csv_path = Path(args.from_csv)
        items = read_items_from_csv(csv_path)
        if not items:
            raise SystemExit(f"No valid items loaded from CSV: {csv_path}")
        print(f"[OK] CSV loaded: {csv_path} ({len(items)} rows)")
    else:
        items = crawl_mcdonalds()
        if not items:
            raise SystemExit("No data crawled from McDonald's.")

        output_csv = Path(args.output)
        write_csv(items, output_csv)
        print(f"[OK] CSV exported: {output_csv} ({len(items)} rows)")

    if args.to_supabase:
        inserted, updated = upsert_to_supabase(items)
        print(f"[OK] Supabase upsert done. inserted={inserted}, updated={updated}")


if __name__ == "__main__":
    main()
