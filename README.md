# SmartVend v2

SmartVend is a Flask vending machine simulator for a Discrete Mathematics and Computational Theory course project. It uses Supabase PostgreSQL for inventory, sales, and daily collection data.

## Pages

- `/` — welcome page with **Enter as a Customer** and a smaller **Admin login** link.
- `/customer` — customer vending interface. Customers can view products and purchase items; admin inventory and daily collection tools are not shown here.
- `/admin` — admin sign-in and protected inventory and daily sales controls.

Admin access uses the password configured by `SMARTVEND_ADMIN_PASSWORD`. It is stored in a Flask session after sign-in. The customer page does not require a customer account.

## Features

- Product selection, coin payment, change, cart, and checkout
- Propositional Logic, Sets & Relations, and Moore vs Mealy FSM demonstrations
- Protected inventory editing
- Daily sales view and end-of-day receipt collection
- Persistent receipt collection counter

## Requirements

- Python 3.10 or newer
- A Supabase project

## Configure Supabase

1. Create a Supabase project and open its **SQL Editor**.
2. Run the contents of [`schema.sql`](schema.sql) to create the required tables and database functions.
3. From your Supabase project settings, copy the project URL and a server-side secret key.

The Supabase secret key must only be configured on the Flask server. Never place it in frontend files or commit it to GitHub.

## Run locally

In PowerShell from the project directory:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Set the required environment variables before starting the app. For local use, create a `.env` file in the project root:

```dotenv
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SECRET_KEY=your-supabase-secret-key
SMARTVEND_ADMIN_PASSWORD=choose-a-strong-admin-password
SECRET_KEY=use-a-long-random-value
```

Then start Flask:

```powershell
python app.py
```

Open `http://127.0.0.1:8000/`. The customer and admin pages are available at `/customer` and `/admin`.

## Deploy to Render

1. Push the project to a GitHub repository. Keep `.env` and `venv/` out of the repository; both are excluded by [`.gitignore`](.gitignore).
2. In Render, create a **New Web Service** and connect the GitHub repository.
3. Select the Python runtime, then set:

   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

4. In the Render service's **Environment** settings, add:

   - `SUPABASE_URL` — Supabase project URL
   - `SUPABASE_SECRET_KEY` — Supabase server-side secret key
   - `SMARTVEND_ADMIN_PASSWORD` — a strong admin password
   - `SECRET_KEY` — a long, random value used to sign Flask sessions

5. Deploy the service. Render provides the public URL. Use `/` for the welcome page, `/customer` for the vending interface, and `/admin` for admin sign-in.

Render can deploy future commits automatically when auto-deploy is enabled. Otherwise, use **Manual Deploy → Deploy latest commit** in the Render dashboard.

The existing `render.yaml` includes a legacy `DATABASE_PATH` setting that this Supabase version does not use. If deploying as a Render Blueprint instead of creating a Web Service in the dashboard, remove that setting and provide the four required environment variables above.

## Data and security notes

- Inventory stock is stored in the `inventory` table.
- Sales are stored in the `sales` table until daily collection.
- The `machine_counter` table tracks completed daily collections.
- Cart checkout and end-of-day collection use PostgreSQL functions to perform related database changes transactionally.
- The admin password defaults to `1234` only when `SMARTVEND_ADMIN_PASSWORD` is not set. Always set a strong value before public deployment.
- Do not commit `.env`, Supabase secrets, or the local virtual environment.
