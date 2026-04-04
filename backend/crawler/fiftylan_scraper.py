import argparse
import csv
import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import psycopg
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


BASE_URL = "http://50lan.com/web/"
PRODUCTS_URL = urljoin(BASE_URL, "products.asp")
DEFAULT_TIMEOUT = 20
DEFAULT_OUTPUT_CSV = Path(__file__).resolve().parent / "output" / "fiftylan_menu.csv"

BLOCK_CATEGORIES = {
    1: "找好茶",
    2: "找奶茶",
    3: "找口感",
    4: "找新鮮",
    5: "找拿鐵",
    6: "季節限定",
    7: "推薦",
}


@dataclass
class FiftyLanItem:
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


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "SuperIdol-50Lan-DataBot/1.0 (research; contact: dev@local)",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
        }
    )
    return session


def get_soup(session: requests.Session, url: str) -> BeautifulSoup:
    resp = session.get(url, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    resp.encoding = "big5"
    return BeautifulSoup(resp.text, "html.parser")


def build_nutrition_payload(note: str | None = None) -> str:
    payload = {
        "calories_kcal": None,
        "protein_g": None,
        "fat_g": None,
        "saturated_fat_g": None,
        "trans_fat_g": None,
        "carb_g": None,
        "sodium_mg": None,
    }
    if note:
        payload["availability_note"] = note
    return json.dumps(payload, ensure_ascii=False)


def parse_availability(row) -> str | None:
    dot = row.find("img")
    if not dot:
        return None

    src = (dot.get("src") or "").lower()
    if "iblue" in src:
        return "僅限冷飲"
    if "ired" in src:
        return "僅限熱飲"
    return None


def crawl_fiftylan() -> list[FiftyLanItem]:
    session = get_session()
    soup = get_soup(session, PRODUCTS_URL)

    block_tables = soup.find_all("table", attrs={"width": "210"})
    items: list[FiftyLanItem] = []

    for index, table in enumerate(block_tables, start=1):
        category = BLOCK_CATEGORIES.get(index, f"分類{index}")
        block_image = table.find("img")
        image_url = urljoin(PRODUCTS_URL, block_image.get("src")) if block_image and block_image.get("src") else None

        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 2:
                continue

            name = normalize_whitespace(cells[1].get_text(" "))
            if not name:
                continue
            if name in {"M", "L"}:
                continue

            availability_note = parse_availability(row)
            items.append(
                FiftyLanItem(
                    item_name=name,
                    category=category,
                    detail_url=PRODUCTS_URL,
                    source_page=PRODUCTS_URL,
                    image_url=image_url,
                    price_twd=None,
                    calories_kcal=None,
                    protein_g=None,
                    fat_g=None,
                    saturated_fat_g=None,
                    trans_fat_g=None,
                    carb_g=None,
                    sodium_mg=None,
                    nutrition_json=build_nutrition_payload(availability_note),
                    crawled_at=now_iso(),
                )
            )

    deduped: dict[str, FiftyLanItem] = {}
    for item in items:
        key = f"{item.category}::{item.item_name}"
        if key not in deduped:
            deduped[key] = item

    return list(deduped.values())


def write_csv(items: list[FiftyLanItem], output_csv: Path) -> None:
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


def read_items_from_csv(csv_path: Path) -> list[FiftyLanItem]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    items: list[FiftyLanItem] = []
    with csv_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            item_name = normalize_whitespace(row.get("item_name", ""))
            category = normalize_whitespace(row.get("category", ""))
            detail_url = normalize_whitespace(row.get("detail_url", ""))
            source_page = normalize_whitespace(row.get("source_page", ""))

            if not item_name or not category:
                continue

            nutrition_payload = row.get("nutrition_json") or build_nutrition_payload()
            items.append(
                FiftyLanItem(
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


def upsert_to_supabase(items: list[FiftyLanItem], restaurant_name: str = "50嵐") -> tuple[int, int]:
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
                    ("手搖", restaurant_name, 60),
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
                            "Beverages",
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
                            item.price_twd,
                            "Beverages",
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
    parser = argparse.ArgumentParser(description="Crawl 50lan menu and export CSV / upsert into Supabase")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT_CSV), help="CSV output path")
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
        items = crawl_fiftylan()
        if not items:
            raise SystemExit("No data crawled from 50lan.")

        output_csv = Path(args.output)
        write_csv(items, output_csv)
        print(f"[OK] CSV exported: {output_csv} ({len(items)} rows)")

    if args.to_supabase:
        inserted, updated = upsert_to_supabase(items)
        print(f"[OK] Supabase upsert done. inserted={inserted}, updated={updated}")


if __name__ == "__main__":
    main()