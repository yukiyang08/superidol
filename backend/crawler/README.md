MOS crawler quick start

1) Install deps (if not installed)
- pip install requests beautifulsoup4

2) Crawl and export CSV only
- python backend/crawler/mos_scraper.py --limit-per-category 10

3) Crawl and also upsert into Supabase
- python backend/crawler/mos_scraper.py --to-supabase

4) Import existing CSV into Supabase (no crawling)
- python backend/crawler/mos_scraper.py --from-csv backend/crawler/output/mos_menu.csv --to-supabase

5) Output path
- backend/crawler/output/mos_menu.csv

Notes
- DB connection uses backend/.env (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME).
- For fast smoke test, use --limit-per-category.
- In CSV import mode, empty values are converted to NULL when applicable (e.g., price).

Milksha crawler quick start

1) Crawl Milksha products and export CSV
- python backend/crawler/milksha_scraper.py

2) Crawl and upsert into Supabase
- python backend/crawler/milksha_scraper.py --to-supabase

3) Import existing Milksha CSV into Supabase
- python backend/crawler/milksha_scraper.py --from-csv backend/crawler/output/milksha_menu.csv --to-supabase

McDonald's crawler quick start

1) Crawl McDonald's menu and export CSV
- python backend/crawler/mcdonalds_scraper.py

2) Crawl and upsert into Supabase
- python backend/crawler/mcdonalds_scraper.py --to-supabase

3) Import existing McDonald's CSV into Supabase
- python backend/crawler/mcdonalds_scraper.py --from-csv backend/crawler/output/mcdonalds_menu.csv --to-supabase
