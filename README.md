# SmartVend v2 — Supabase Edition

SmartVend is a Flask vending-machine simulator for a Discrete Mathematics and Computational Theory course project.

## Architecture

```text
INTERNET / LAN
      |
      v
+------------------+
| SmartVend Flask  |
| website + logic  |
+--------+---------+
         |
         v
+------------------+
| Supabase         |
| PostgreSQL       |
+------------------+
   |       |       |
   v       v       v
inventory sales counters
```

The browser talks only to Flask. Flask talks to Supabase PostgreSQL. The privileged Supabase secret key is kept on the server and is never sent to the browser.

## Preserved functionality

- Propositional Logic tile
- Sets & Relations tile
- Moore vs Mealy FSM tile
- Product selection
- Coin insertion
- Change calculation
- Shopping cart / multi-item checkout
- Inventory display
- Password-protected inventory management
- Password-protected daily receipt collection
- Daily sales table
- End-of-day receipt
- Delete current day's sales after collection
- Persistent Collection #1, #2, #3... counter
- Development/demo reset endpoint

## 1. Create the Supabase database

1. Create a Supabase project.
2. Open **SQL Editor**.
3. Paste the entire contents of `schema.sql`.
4. Run it.
5. In Supabase Project Settings / API Keys, obtain:
   - Project URL
   - **Secret key** (`sb_secret_...`) for the Flask backend.

Supabase recommends keeping secret/server keys on backend code only. Do not put the secret key in `frontend/index.html`.

## 2. Local setup

```powershell
python -m venv venv
.env\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your real Supabase values.

Then:

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:8000
```

## 3. Online deployment

Set these environment variables in your hosting service:

```text
SUPABASE_URL=...
SUPABASE_SECRET_KEY=...
SMARTVEND_ADMIN_PASSWORD=...
SECRET_KEY=...
PORT=8000
```

Start command:

```text
gunicorn app:app
```

No SQLite database file is needed anymore. Your data lives in Supabase PostgreSQL.

## Default demo password

```text
1234
```

Change it before public deployment.

## Database behavior

- `inventory` persists stock.
- `sales` stores daily transaction rows.
- `machine_counter` stores completed end-of-day collection count.
- Cart checkout uses a PostgreSQL transaction function so stock updates and sales inserts happen together.
- End-of-day collection summarizes and deletes that day's sales in one database transaction, then increments the collection counter.

## Important

Do not commit `.env` or paste your Supabase secret key into GitHub. `.env` is ignored by the included `.gitignore`.
