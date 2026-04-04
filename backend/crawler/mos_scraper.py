import argparse
import csv
import os
import json
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin

import psycopg
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


BASE_URL = "https://www.mos.com.tw"
DEFAULT_TIMEOUT = 20
REQUEST_INTERVAL_SECONDS = 0.5

# 先從最有價值的分類開始；之後可再擴充。
CATEGORY_PAGES = {
    "主餐": "/menu/set.aspx",
    "早餐": "/menu/breakfast.aspx",
    "副餐": "/menu/sideDishes.aspx",
    "飲品": "/menu/beverage.aspx",
    "甜品": "/menu/dessert.aspx",
}


@dataclass
class MosItem:
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


def first_int(text: str) -> int | None:
    matches = re.findall(
        r"(?:售價|價格|單點|套餐|單品|優惠價)\s*[:：]?\s*(?:NT\$|\$)?\s*(\d{2,4})\s*元?",
        text,
    )
    for match in matches:
        value = int(match)
        if 10 <= value <= 1200:
            return value
    return None


def extract_price(detail_text: str) -> int | None:
    # Only trust explicit price-like markers to avoid confusing nutrition values with price.
    patterns = [
        r"(?:單點|套餐|售價|優惠價|價格)\s*[:：]?\s*(?:NT\$|\$)?\s*(\d{2,4})\s*元?",
        r"(?:NT\$|\$)\s*(\d{2,4})\b",
        r"\b(\d{2,4})\s*元\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, detail_text)
        if match:
            value = int(match.group(1))
            if 10 <= value <= 1200:
                return value
    return None


def first_calories(text: str) -> float | None:
    patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:kcal|Kcal|KCAL)",
        r"熱量\s*[:：]?\s*(\d+(?:\.\d+)?)\s*(?:大卡|卡|kcal)",
        r"(\d+(?:\.\d+)?)\s*(?:大卡|卡路里)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            value = float(match.group(1))
            if 1 <= value <= 3000:
                return value
    return None


def first_float(text: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(match.group(1)) if match else None


def parse_main_image(detail_soup: BeautifulSoup) -> str | None:
    for img_tag in detail_soup.select("img[src]"):
        src = img_tag.get("src", "")
        if "/upload/product/" in src.lower():
            return urljoin(BASE_URL, src)
    return None


def parse_nutrition_table(detail_soup: BeautifulSoup) -> dict[str, float | None]:
    nutrition = {
        "calories_kcal": None,
        "protein_g": None,
        "fat_g": None,
        "saturated_fat_g": None,
        "trans_fat_g": None,
        "carb_g": None,
        "sodium_mg": None,
    }

    for row in detail_soup.select("tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) < 2:
            continue

        label = normalize_whitespace(cells[0].get_text(" ")).replace(" ", "")
        value_text = normalize_whitespace(cells[1].get_text(" "))
        value = first_float(value_text)
        if value is None:
            continue

        if "熱量" in label:
            nutrition["calories_kcal"] = value
        elif label == "蛋白質":
            nutrition["protein_g"] = value
        elif label == "脂肪":
            nutrition["fat_g"] = value
        elif "飽和脂肪" in label:
            nutrition["saturated_fat_g"] = value
        elif "反式脂肪" in label:
            nutrition["trans_fat_g"] = value
        elif "碳水化合物" in label:
            nutrition["carb_g"] = value
        elif "鈉" in label:
            nutrition["sodium_mg"] = value

    return nutrition


def parse_item_name(listing_text: str, detail_soup: BeautifulSoup) -> str:
    candidates = []

    for selector in ("h1", "h2", "h3", ".title", ".name"):
        heading = detail_soup.select_one(selector)
        if heading:
            candidates.append(normalize_whitespace(heading.get_text()))

    title_tag = detail_soup.find("title")
    if title_tag:
        candidates.append(normalize_whitespace(title_tag.get_text()))

    og_title = detail_soup.find("meta", attrs={"property": "og:title"})
    if og_title and og_title.get("content"):
        candidates.append(normalize_whitespace(og_title.get("content")))

    candidates.append(normalize_whitespace(listing_text))

    for raw in candidates:
        if not raw:
            continue
        name = raw
        name = re.sub(r"\s*[-|｜].*$", "", name)
        name = re.sub(r"\s*\(.*?\)\s*", lambda m: m.group(0) if len(m.group(0)) <= 18 else "", name)
        if "MOS" in name and "首頁" in name:
            continue
        if 2 <= len(name) <= 80:
            return name

    return "未知品項"


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "SuperIdol-MOS-DataBot/1.0 (research; contact: dev@local)",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
        }
    )
    return session


def get_soup(session: requests.Session, url: str) -> BeautifulSoup:
    resp = session.get(url, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    return BeautifulSoup(resp.text, "html.parser")


def iter_detail_links(list_soup: BeautifulSoup, source_url: str) -> Iterable[tuple[str, str]]:
    seen: set[str] = set()
    found = 0

    for a_tag in list_soup.select("a[href]"):
        href = a_tag.get("href", "")
        if "detail.aspx?id=" not in href.lower() and "_detail.aspx?id=" not in href.lower():
            continue
        abs_url = urljoin(source_url, href)
        if abs_url in seen:
            continue
        seen.add(abs_url)
        found += 1
        yield normalize_whitespace(a_tag.get_text()), abs_url

    # MOS 頁面常把 detail 連結寫在腳本或其他屬性中，非 a[href]。
    if found == 0:
        html = str(list_soup)
        pattern = re.compile(r"(/menu/[a-z_]*detail\.aspx\?id=[A-Za-z0-9]+)", re.IGNORECASE)
        for match in pattern.findall(html):
            abs_url = urljoin(source_url, match)
            if abs_url in seen:
                continue
            seen.add(abs_url)
            yield "", abs_url


def crawl_mos(limit_per_category: int | None = None) -> list[MosItem]:
    session = get_session()
    rows: list[MosItem] = []

    for category, path in CATEGORY_PAGES.items():
        source_url = urljoin(BASE_URL, path)
        list_soup = get_soup(session, source_url)
        detail_links = list(iter_detail_links(list_soup, source_url))

        if limit_per_category:
            detail_links = detail_links[:limit_per_category]

        for listing_text, detail_url in detail_links:
            try:
                detail_soup = get_soup(session, detail_url)
                detail_text = normalize_whitespace(detail_soup.get_text(" "))
                item_name = parse_item_name(listing_text, detail_soup)
                image_url = parse_main_image(detail_soup)
                nutrition = parse_nutrition_table(detail_soup)
                rows.append(
                    MosItem(
                        item_name=item_name,
                        category=category,
                        detail_url=detail_url,
                        source_page=source_url,
                        image_url=image_url,
                        price_twd=extract_price(detail_text),
                        calories_kcal=nutrition["calories_kcal"] or first_calories(detail_text),
                        protein_g=nutrition["protein_g"],
                        fat_g=nutrition["fat_g"],
                        saturated_fat_g=nutrition["saturated_fat_g"],
                        trans_fat_g=nutrition["trans_fat_g"],
                        carb_g=nutrition["carb_g"],
                        sodium_mg=nutrition["sodium_mg"],
                        nutrition_json=json.dumps(nutrition, ensure_ascii=False),
                        crawled_at=now_iso(),
                    )
                )
            except requests.RequestException as exc:
                print(f"[WARN] Skip {detail_url}: {exc}")
            time.sleep(REQUEST_INTERVAL_SECONDS)

    return rows


def write_csv(items: list[MosItem], output_csv: Path) -> None:
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
    try:
        return float(text)
    except ValueError:
        return None


def _normalize_nullable_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "" or text.lower() == "null":
        return None
    return text


def read_items_from_csv(csv_path: Path) -> list[MosItem]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    items: list[MosItem] = []
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
                MosItem(
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
    )


def upsert_to_supabase(items: list[MosItem], restaurant_name: str = "摩斯") -> tuple[int, int]:
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
                    ("速食", restaurant_name, 180),
                )
                restaurant_id = cursor.fetchone()[0]

            for item in items:
                cursor.execute(
                    "SELECT foodid, price FROM food WHERE restaurantid = %s AND name = %s LIMIT 1",
                    (restaurant_id, item.item_name),
                )
                existing = cursor.fetchone()

                food_type = "Burger"
                if item.category in ("副餐", "甜品"):
                    food_type = "Snacks"
                elif item.category == "飲品":
                    food_type = "Beverages"

                calories_value = item.calories_kcal if item.calories_kcal is not None else 0
                price_value = item.price_twd
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
                            price_value,
                            food_type,
                            item.category,
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
                            price_value,
                            food_type,
                            item.category,
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
    parser = argparse.ArgumentParser(description="Crawl MOS menu and export CSV / upsert into Supabase")
    parser.add_argument("--limit-per-category", type=int, default=None, help="Limit items per category for quick test")
    parser.add_argument("--output", type=str, default="backend/crawler/output/mos_menu_with_prices.csv", help="CSV output path")
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
        items = crawl_mos(limit_per_category=args.limit_per_category)

        if not items:
            raise SystemExit("No data crawled from MOS.")

        output_csv = Path(args.output)
        write_csv(items, output_csv)
        print(f"[OK] CSV exported: {output_csv} ({len(items)} rows)")

    if args.to_supabase:
        inserted, updated = upsert_to_supabase(items)
        print(f"[OK] Supabase upsert done. inserted={inserted}, updated={updated}")


if __name__ == "__main__":
    main()
