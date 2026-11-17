import os
import uuid
from datetime import datetime, date, time, timedelta

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory, session
from supabase import create_client, Client

load_dotenv()

BASE = os.path.dirname(os.path.abspath(__file__))
ADMIN_PASSWORD = os.environ.get("SMARTVEND_ADMIN_PASSWORD", "1234")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = (
    os.environ.get("SUPABASE_SECRET_KEY")
    or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Missing SUPABASE_URL and SUPABASE_SECRET_KEY. "
        "Set them in .env for local use or in your hosting provider's environment variables."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__, static_folder="frontend")
app.secret_key = os.environ.get("SECRET_KEY", "smartvend-change-this-secret")

INITIAL_ITEMS = [
    {"slot": "A1", "name": "Water", "price": 20, "stock": 10, "category": "beverage", "icon": "💧"},
    {"slot": "A2", "name": "Juice", "price": 30, "stock": 8, "category": "beverage", "icon": "🧃"},
    {"slot": "A3", "name": "Soda", "price": 25, "stock": 6, "category": "beverage", "icon": "🥤"},
    {"slot": "B1", "name": "Chips", "price": 20, "stock": 10, "category": "snack", "icon": "🍟"},
    {"slot": "B2", "name": "Cookies", "price": 15, "stock": 12, "category": "snack", "icon": "🍪"},
    {"slot": "B3", "name": "Chocolate", "price": 25, "stock": 7, "category": "snack", "icon": "🍫"},
]
DENOMINATIONS = [5, 10, 20, 50]
LOW_STOCK_THRESHOLD = 2


def rows_from(response):
    return response.data or []


def inventory_rows():
    return rows_from(
        supabase.table("inventory").select("*").order("slot").execute()
    )


def item(slot):
    data = rows_from(
        supabase.table("inventory").select("*").eq("slot", slot.upper()).limit(1).execute()
    )
    return data[0] if data else None


def machine_counter():
    data = rows_from(
        supabase.table("machine_counter").select("*").eq("id", 1).limit(1).execute()
    )
    return data[0] if data else {"id": 1, "receipt_count": 0, "last_receipt_date": None}


def sets_relations():
    rows = inventory_rows()
    return {
        "sets": {
            "slots": sorted(x["slot"] for x in rows),
            "item_names": sorted(x["name"] for x in rows),
            "prices": sorted(set(x["price"] for x in rows)),
            "stock_values": sorted(set(x["stock"] for x in rows)),
            "categories": sorted(set(x["category"] for x in rows)),
        },
        "relations": {
            "slot_to_item": [[x["slot"], x["name"]] for x in rows],
            "item_to_price": [[x["name"], x["price"]] for x in rows],
            "item_to_stock": [[x["name"], x["stock"]] for x in rows],
            "item_to_category": [[x["name"], x["category"]] for x in rows],
        },
    }


def change_breakdown(amount):
    result = []
    for d in sorted(DENOMINATIONS, reverse=True):
        while amount >= d:
            result.append(d)
            amount -= d
    if amount:
        raise ValueError("Exact change cannot be represented.")
    return result


def fsm(coins, price):
    balance = 0
    rows = []
    moore = "WAITING"
    mealy = "WAITING"
    for coin in coins:
        prev = mealy
        if moore == "WAITING":
            moore = "ACCEPTING"
        balance += coin
        if balance >= price:
            moore = "READY"
        if mealy == "WAITING":
            mealy = "ACCEPTING"
        threshold = balance >= price and prev != "READY"
        mealy = "READY" if balance >= price else "ACCEPTING"
        rows.append({
            "coin": coin,
            "balance": balance,
            "moore_state": moore,
            "moore_output": "DISPENSE" if moore == "READY" else "WAIT",
            "mealy_state": mealy,
            "mealy_output": "DISPENSE" if threshold else "WAIT",
        })
    return rows


def require_unlock(kind):
    key = "inventory_unlocked" if kind == "inventory" else "receipt_unlocked"
    if not session.get(key, False):
        return jsonify({"error": f"{kind.title()} management is locked. Unlock it first."}), 403
    return None


def local_day_bounds():
    now = datetime.now().astimezone()
    start = datetime.combine(now.date(), time.min, tzinfo=now.tzinfo)
    end = start + timedelta(days=1)
    return start, end


@app.get("/")
def index():
    return send_from_directory("frontend", "index.html")


@app.get("/admin")
def admin():
    return send_from_directory("frontend", "admin.html")


@app.get("/api/health")
def health():
    try:
        supabase.table("machine_counter").select("id").eq("id", 1).limit(1).execute()
        return jsonify({"ok": True, "database": "Supabase PostgreSQL"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 503


@app.get("/api/inventory")
def get_inventory():
    return jsonify({
        "items": inventory_rows(),
        "accepted_denominations": DENOMINATIONS,
        "low_stock_threshold": LOW_STOCK_THRESHOLD,
    })


@app.get("/api/sets-relations")
def get_sets_relations():
    return jsonify(sets_relations())


@app.get("/api/access-status")
def access_status():
    counter = machine_counter()
    return jsonify({
        "inventory_unlocked": bool(session.get("inventory_unlocked", False)),
        "receipt_unlocked": bool(session.get("receipt_unlocked", False)),
        "receipt_count": counter["receipt_count"],
        "last_receipt_date": counter["last_receipt_date"],
    })


@app.post("/api/unlock")
def unlock():
    data = request.get_json(silent=True) or {}
    password = str(data.get("password", ""))
    target = str(data.get("target", ""))
    if target not in {"inventory", "receipt", "both"}:
        return jsonify({"error": "Invalid unlock target."}), 400
    if password != ADMIN_PASSWORD:
        return jsonify({"error": "Incorrect password."}), 401
    if target in {"inventory", "both"}:
        session["inventory_unlocked"] = True
    if target in {"receipt", "both"}:
        session["receipt_unlocked"] = True
    return jsonify({
        "success": True,
        "inventory_unlocked": bool(session.get("inventory_unlocked", False)),
        "receipt_unlocked": bool(session.get("receipt_unlocked", False)),
        "message": "Access unlocked successfully.",
    })


@app.post("/api/lock")
def lock():
    session.pop("inventory_unlocked", None)
    session.pop("receipt_unlocked", None)
    return jsonify({"success": True})


@app.get("/api/compare")
def compare():
    try:
        slot = request.args.get("slot", "").upper()
        coins = [int(x) for x in request.args.get("coins", "").split(",") if x]
        it = item(slot)
        if not it:
            return jsonify({"error": "Unknown slot"}), 400
        if any(c not in DENOMINATIONS for c in coins):
            return jsonify({"error": "Invalid denomination"}), 400
        return jsonify({"rows": fsm(coins, it["price"])})
    except ValueError:
        return jsonify({"error": "Invalid coin values."}), 400


@app.post("/api/purchase")
def purchase():
    # Kept for compatibility with the original SmartVend API.
    data = request.get_json(silent=True) or {}
    slot = str(data.get("slot", "")).upper()
    coins = data.get("coins", [])
    try:
        coins = [int(x) for x in coins]
        if not coins or any(c not in DENOMINATIONS for c in coins):
            raise ValueError("Invalid denomination.")
        paid = sum(coins)
        transaction_id = uuid.uuid4().hex
        result = supabase.rpc(
            "process_purchase",
            {"p_slot": slot, "p_paid": paid, "p_transaction_id": transaction_id},
        ).execute()
        payload = result.data
        if not payload or not payload.get("success"):
            raise ValueError((payload or {}).get("error", "Purchase failed."))
        updated = item(slot)
        change = payload["change"]
        notes = change_breakdown(change)
        logic = {
            "P": paid >= payload["price"],
            "Q": payload["stock_after"] >= 0,
            "P_AND_Q": paid >= payload["price"] and payload["stock_after"] >= 0,
            "R_LOW_STOCK": payload["stock_after"] < LOW_STOCK_THRESHOLD,
        }
        receipt = [
            "SMARTVEND",
            f"ITEM  : {slot} - {payload['name']}",
            f"PRICE : ₹{payload['price']}",
            f"PAID  : ₹{paid}",
            f"CHANGE: ₹{change}",
            "THANK YOU",
        ]
        return jsonify({
            "success": True, "item": updated, "paid": paid, "price": payload["price"],
            "change": change, "change_breakdown": notes, "logic": logic,
            "sets_and_relations": sets_relations(), "fsm": fsm(coins, payload["price"]),
            "receipt": receipt, "low_stock": logic["R_LOW_STOCK"],
            "message": f"{payload['name']} dispensed successfully.",
        })
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/cart-purchase")
def cart_purchase():
    data = request.get_json(silent=True) or {}
    cart = data.get("cart", [])
    coins = data.get("coins", [])
    try:
        coins = [int(x) for x in coins]
        if not cart:
            raise ValueError("Cart is empty.")
        if not coins or any(c not in DENOMINATIONS for c in coins):
            raise ValueError("Invalid denomination.")

        requested = {}
        for row in cart:
            slot = str(row.get("slot", "")).upper()
            qty = int(row.get("quantity", 0))
            if not slot or qty <= 0:
                raise ValueError("Invalid cart item.")
            requested[slot] = requested.get(slot, 0) + qty

        paid = sum(coins)
        transaction_id = uuid.uuid4().hex
        result = supabase.rpc(
            "process_cart_purchase",
            {
                "p_cart": [{"slot": slot, "quantity": qty} for slot, qty in requested.items()],
                "p_paid": paid,
                "p_transaction_id": transaction_id,
            },
        ).execute()
        payload = result.data
        if not payload or not payload.get("success"):
            raise ValueError((payload or {}).get("error", "Cart purchase failed."))

        total = payload["total"]
        change = payload["change"]
        notes = change_breakdown(change)
        updated_items = payload["items"]
        receipt = ["SMARTVEND - CART RECEIPT"]
        for row in updated_items:
            receipt.append(f"{row['name']} x{row['quantity_bought']}  ₹{row['line_total']}")
        receipt += [f"TOTAL  : ₹{total}", f"PAID   : ₹{paid}", f"CHANGE : ₹{change}", "THANK YOU"]
        logic = {
            "P": paid >= total,
            "Q": all(x["stock"] >= 0 for x in updated_items),
            "P_AND_Q": paid >= total and all(x["stock"] >= 0 for x in updated_items),
            "R_LOW_STOCK": any(x["stock"] < LOW_STOCK_THRESHOLD for x in updated_items),
        }
        # Refresh stock/category/relations from the database so the theory tiles
        # reflect the same live Supabase data as the vending machine.
        fresh_items = inventory_rows()
        fresh_by_slot = {x["slot"]: x for x in fresh_items}
        display_items = [fresh_by_slot[x["slot"]] for x in updated_items]
        return jsonify({
            "success": True, "items": display_items, "paid": paid, "total": total,
            "change": change, "change_breakdown": notes, "receipt": receipt,
            "logic": logic, "fsm": fsm(coins, total), "low_stock": logic["R_LOW_STOCK"],
            "message": "Cart dispensed successfully.",
        })
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/inventory/restock")
def restock():
    blocked = require_unlock("inventory")
    if blocked:
        return blocked
    data = request.get_json(silent=True) or {}
    try:
        slot = str(data.get("slot", "")).upper()
        amount = int(data.get("amount", 0))
        if amount <= 0:
            raise ValueError("Restock amount must be positive.")
        current = item(slot)
        if not current:
            raise ValueError("Unknown slot.")
        supabase.table("inventory").update({"stock": current["stock"] + amount}).eq("slot", slot).execute()
        return jsonify({"success": True, "item": item(slot)})
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/inventory/set-stock")
def set_stock():
    blocked = require_unlock("inventory")
    if blocked:
        return blocked
    data = request.get_json(silent=True) or {}
    try:
        slot = str(data.get("slot", "")).upper()
        stock = int(data.get("stock", -1))
        if stock < 0:
            raise ValueError("Stock cannot be negative.")
        result = supabase.table("inventory").update({"stock": stock}).eq("slot", slot).execute()
        if not result.data:
            raise ValueError("Unknown slot.")
        return jsonify({"success": True, "item": item(slot)})
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/api/daily-sales")
def daily_sales():
    blocked = require_unlock("receipt")
    if blocked:
        return blocked
    start, end = local_day_bounds()
    try:
        rows = rows_from(
            supabase.table("sales")
            .select("*")
            .gte("sale_time", start.isoformat())
            .lt("sale_time", end.isoformat())
            .order("id")
            .execute()
        )
        return jsonify({"date": start.date().isoformat(), "sales": rows, "count": len(rows)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/end-day")
def end_day():
    blocked = require_unlock("receipt")
    if blocked:
        return blocked
    today = datetime.now().astimezone().date().isoformat()
    try:
        result = supabase.rpc("collect_end_day", {"p_day": today}).execute()
        payload = result.data
        if not payload or not payload.get("success"):
            return jsonify({"error": (payload or {}).get("error", "End-of-day collection failed.")}), 400
        return jsonify(payload)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/reset")
def reset():
    # Kept as a development/demo function so no original functionality is removed.
    try:
        result = supabase.rpc("reset_machine").execute()
        if not result.data or not result.data.get("success"):
            return jsonify({"error": (result.data or {}).get("error", "Reset failed.")}), 400
        return jsonify({"success": True, "items": inventory_rows()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
