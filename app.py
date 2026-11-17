"""
SmartVend - Python Flask Backend & Discrete Structures Engine.

Demonstrates 5 core Discrete Mathematics & Computational Theory concepts:
- Unit I: Propositional Logic (dispensing authorization P ∧ Q, low stock R).
- Unit II: Sets & Binary Relations (slot -> item, item -> price, etc.).
- Unit III: Moore vs Mealy Finite Automata (state transitions and edge outputs).
- Unit IV: Greedy Combinatorial Change-Making (canonical denomination breakdown).
- Unit V: Context-Free Grammar (CFG) Pricing Engine & CYK Dynamic Programming.
"""

import os
import json
import copy
import uuid
from datetime import datetime, date, time, timedelta

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory, session
from supabase import create_client, Client
from cfg_engine import (
    DEFAULT_DISCOUNTS,
    DEFAULT_RULES,
    GrammarError,
    MAX_CART_ITEMS,
    evaluate,
    format_grammar,
    normalize,
    parse_rules,
)

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

# Initial catalog items used as fallback if Supabase is temporarily unreachable
INITIAL_ITEMS = [
    {"slot": "A1", "name": "Water", "price": 20, "stock": 10, "category": "beverage", "icon": "💧"},
    {"slot": "A2", "name": "Juice", "price": 30, "stock": 8, "category": "beverage", "icon": "🧃"},
    {"slot": "A3", "name": "Soda", "price": 25, "stock": 6, "category": "beverage", "icon": "🥤"},
    {"slot": "B1", "name": "Chips", "price": 20, "stock": 10, "category": "snack", "icon": "🍟"},
    {"slot": "B2", "name": "Cookies", "price": 15, "stock": 12, "category": "snack", "icon": "🍪"},
    {"slot": "B3", "name": "Chocolate", "price": 25, "stock": 7, "category": "snack", "icon": "🍫"},
]
# Accepted coin denominations for payment
DENOMINATIONS = [5, 10, 20, 50]
# Canonical coin denominations for optimal greedy change return
CHANGE_DENOMINATIONS = [50, 20, 10, 5, 2, 1]
# Threshold below which an item triggers the low-stock warning predicate (R)
LOW_STOCK_THRESHOLD = 2


def rows_from(response):
    """Safely extracts data list from a Supabase PostgREST response."""
    return response.data or []


def inventory_rows():
    """Fetches all inventory slots from Supabase, with offline fallback."""
    try:
        return rows_from(
            supabase.table("inventory").select("*").order("slot").execute()
        )
    except Exception:
        return copy.deepcopy(INITIAL_ITEMS)


def item(slot):
    """Fetches a single inventory item by slot ID (e.g. 'A1')."""
    data = rows_from(
        supabase.table("inventory").select("*").eq("slot", slot.upper()).limit(1).execute()
    )
    return data[0] if data else None


def machine_counter():
    """Fetches the persistent daily collection count from Supabase."""
    data = rows_from(
        supabase.table("machine_counter").select("*").eq("id", 1).limit(1).execute()
    )
    return data[0] if data else {"id": 1, "receipt_count": 0, "last_receipt_date": None}


def combo_config():
    """Fetches CFG combo grammar and discount mappings from Supabase or local cache."""
    try:
        data = rows_from(
            supabase.table("combo_deal_config").select("*").eq("id", 1).limit(1).execute()
        )
        if data:
            return data[0]
    except Exception:
        pass
    config_file = os.path.join(BASE, "combo_deal_config.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"id": 1, "rules": DEFAULT_RULES, "discounts": DEFAULT_DISCOUNTS}


def combo_analysis(cart):
    """
    Evaluates a shopping cart against the CFG combo deals pricing engine.
    
    Concept: Context-Free Grammars & CYK Algorithm (Unit V).
    Turns cart items into an ordered category sequence (e.g. ['snack', 'beverage']),
    runs CYK parsing in Chomsky Normal Form, and computes the discount percentage.
    If the sequence does not match the grammar, discount is 0 (pricing engine, not a validator).
    
    Input: cart list of dicts [{'slot': 'A1', 'quantity': 1}, ...].
    Output: tuple of (requested_slots_dict, deal_analysis_dict).
    """
    if not isinstance(cart, list) or not cart:
        return {}, {
            "matched": False,
            "ambiguous": False,
            "discount_options": {},
            "discount_percent": 0,
            "gross_total": 0,
            "discount_amount": 0,
            "total": 0,
            "category_sequence": [],
            "parse_count": 0,
            "tree": None,
            "derivation": [],
            "tokens": [],
            "normalization_steps": [],
            "normalized_grammar": "",
            "intermediate_grammars": {},
        }
    all_items = inventory_rows()
    by_slot = {row["slot"].upper(): row for row in all_items}
    requested = {}
    categories = []
    gross_total = 0
    for row in cart:
        slot = str(row.get("slot", "")).upper()
        quantity = int(row.get("quantity", 0))
        current = by_slot.get(slot)
        if not current or quantity <= 0:
            raise ValueError("Invalid cart item.")
        requested[slot] = requested.get(slot, 0) + quantity
        if requested[slot] > current["stock"]:
            raise ValueError(f"Only {current['stock']} {current['name']} left in stock.")
        gross_total += current["price"] * quantity
        categories.extend([current["category"].casefold()] * quantity)

    if len(categories) > MAX_CART_ITEMS:
        raise ValueError(f"Cart category sequence exceeds maximum evaluation length of {MAX_CART_ITEMS} items.")

    config = combo_config()
    valid_categories = sorted({row["category"].casefold() for row in all_items})
    # Evaluate category sequence with CYK parser using Best-Discount policy
    result = evaluate(
        categories,
        config["rules"],
        config.get("discounts", DEFAULT_DISCOUNTS),
        valid_categories,
        policy="best-discount",
    )

    # Compute monetary discount amount based on matched percentage
    percent = result["discount_percent"] if result["matched"] else 0
    discount_amount = gross_total * percent // 100
    result.update({
        "category_sequence": categories,
        "gross_total": gross_total,
        "discount_amount": discount_amount,
        "total": gross_total - discount_amount,
        "discount_percent": percent,
    })
    return requested, result


def sets_relations():
    """
    Constructs mathematical sets and binary relations from live inventory.
    
    Concept: Sets & Binary Relations (Unit II).
    - Sets: Slots, Item Names, Prices, Stock Values, Categories.
    - Relations: Subsets of Cartesian products, e.g. Slot x Item, Item x Price.
    
    Output: dict with 'sets' and 'relations' keys.
    """
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
    """
    Computes optimal change return using the Greedy Algorithm.
    
    Concept: Greedy Combinatorial Optimization & Canonical Coin Systems (Unit I/IV).
    Because [50, 20, 10, 5, 2, 1] is canonical, greedy selection of the largest
    possible denomination always yields the minimum total coin count.
    
    Input: amount (int, change owed in rupees).
    Output: list of coin denominations (e.g. 48 -> [20, 20, 5, 2, 1]).
    """
    result = []
    for d in CHANGE_DENOMINATIONS:
        while amount >= d:
            result.append(d)
            amount -= d
    if amount:
        raise ValueError("Exact change cannot be represented.")
    return result


def fsm(coins, price):
    """
    Simulates Moore and Mealy Finite State Machines side-by-side.
    
    Concept: Finite Automata & Sequential Circuits (Unit III).
    - States Q = {WAITING, ACCEPTING, READY}.
    - Inputs Σ = {5, 10, 20, 50}.
    - Outputs Δ = {WAIT, DISPENSE}.
    - Moore Machine: Output depends strictly on current state (DISPENSE if state == READY).
    - Mealy Machine: Output depends on state AND input transition edge (DISPENSE only on
      the exact step balance crosses price threshold).
    
    Input: coins list (e.g. [10, 20]), price (int).
    Output: list of trace row dicts showing step-by-step state and outputs.
    """
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
    """
    Access Control Guard: checks if the admin session has unlocked access.
    
    Input: kind ('inventory' or 'receipt').
    Output: None if unlocked; JSON 403 response if locked.
    """
    key = "inventory_unlocked" if kind == "inventory" else "receipt_unlocked"
    if not session.get(key, False):
        return jsonify({"error": f"{kind.title()} management is locked. Unlock it first."}), 403
    return None


def local_day_bounds():
    """Calculates start and end timestamps for the current local calendar day."""
    now = datetime.now().astimezone()
    start = datetime.combine(now.date(), time.min, tzinfo=now.tzinfo)
    end = start + timedelta(days=1)
    return start, end


@app.get("/")
def index():
    """Portal page: serves login.html with links to Customer and Admin views."""
    return send_from_directory("frontend", "login.html")


@app.get("/customer")
def customer():
    """Customer vending page: serves index.html with interactive simulation."""
    return send_from_directory("frontend", "index.html")


@app.get("/admin")
def admin():
    """Admin page: serves admin.html with inventory and CFG management tools."""
    return send_from_directory("frontend", "admin.html")


@app.get("/api/health")
def health():
    """
    Health check endpoint: verifies Flask server is running and ready.
    Does not block or fail deploy on cold external database queries.
    
    Output: JSON {"ok": true, "database": "Supabase PostgreSQL" | "connecting"} (200).
    """
    db_ok = False
    try:
        supabase.table("machine_counter").select("id").eq("id", 1).limit(1).execute()
        db_ok = True
    except Exception:
        db_ok = False
    return jsonify({
        "ok": True,
        "database": "Supabase PostgreSQL" if db_ok else "connecting",
        "status": "ready"
    }), 200


@app.get("/api/inventory")
def get_inventory():
    """
    Public inventory endpoint: returns all vending machine slots and stock.
    
    Output: JSON with items list, accepted denominations, and low stock threshold.
    """
    return jsonify({
        "items": inventory_rows(),
        "accepted_denominations": DENOMINATIONS,
        "low_stock_threshold": LOW_STOCK_THRESHOLD,
    })


@app.get("/api/sets-relations")
def get_sets_relations():
    """
    Unit II Sets & Relations endpoint: returns sets and relation pairs.
    
    Output: JSON with 'sets' (slots, items, prices, stock, categories)
            and 'relations' (slot_to_item, item_to_price, etc.).
    """
    return jsonify(sets_relations())


@app.get("/api/access-status")
def access_status():
    """
    Session status endpoint: returns admin unlock state and receipt counter.
    
    Output: JSON with inventory_unlocked, receipt_unlocked, receipt_count.
    """
    counter = machine_counter()
    return jsonify({
        "inventory_unlocked": bool(session.get("inventory_unlocked", False)),
        "receipt_unlocked": bool(session.get("receipt_unlocked", False)),
        "receipt_count": counter["receipt_count"],
        "last_receipt_date": counter["last_receipt_date"],
    })


@app.get("/api/combo-config")
def get_combo_config():
    """
    Unit V CFG endpoint: returns active grammar rules and discount mappings.
    
    Output: JSON with 'rules' (BNF string) and 'discounts' (dict).
    """
    config = combo_config()
    return jsonify({"rules": config["rules"], "discounts": config["discounts"]})


@app.post("/api/combo-config")
def update_combo_config():
    """
    Admin CFG update endpoint (Protected): parses, normalizes, and saves new grammar.
    
    Concept: 4-stage CNF Normalization Pipeline (Unit V).
    Input: JSON {"rules": "...", "discounts": {"rule": percent}}.
    Output: JSON with success status, intermediate grammars, and CNF output.
    """
    blocked = require_unlock("inventory")
    if blocked:
        return blocked
    data = request.get_json(silent=True) or {}
    try:
        rules = str(data.get("rules", ""))
        categories = sorted({row["category"].casefold() for row in inventory_rows()})
        grammar = parse_rules(rules, categories)
        cnf, terminals, binaries, stages, intermediates = normalize(grammar, categories)
        raw_discounts = data.get("discounts", {})
        if not isinstance(raw_discounts, dict):
            raise GrammarError("Discounts must map deal rules/branches to percentages.")
        discounts = {}
        for name, value in raw_discounts.items():
            val = int(value)
            if val < 0 or val > 90:
                raise GrammarError("Discount percentages must be between 0 and 90.")
            discounts[str(name)] = val

        config_payload = {"id": 1, "rules": rules, "discounts": discounts}
        config_file = os.path.join(BASE, "combo_deal_config.json")
        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config_payload, f, indent=2)
        except Exception:
            pass

        try:
            supabase.table("combo_deal_config").upsert(config_payload).execute()
        except Exception:
            pass

        return jsonify({
            "success": True,
            "rules": rules,
            "discounts": discounts,
            "normalization_steps": stages,
            "intermediate_grammars": intermediates,
            "normalized_grammar": intermediates.get("4_cnf", ""),
        })
    except (ValueError, TypeError, GrammarError) as error:
        return jsonify({"error": str(error)}), 400
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.post("/api/combo-cnf-steps")
def combo_cnf_steps():
    """
    Unit V Verification endpoint: previews the 4-stage CNF normalization pipeline.
    
    Input: JSON {"rules": "..."}.
    Output: JSON with stages list and intermediate grammars (0_orig, 1_eps, 2_unit, 3_useless, 4_cnf).
    """
    data = request.get_json(silent=True) or {}
    rules = str(data.get("rules", ""))
    try:
        categories = sorted({row["category"].casefold() for row in inventory_rows()})
        grammar = parse_rules(rules, categories)
        cnf, terminals, binaries, stages, intermediates = normalize(grammar, categories)
        return jsonify({
            "success": True,
            "stages": stages,
            "intermediate_grammars": intermediates,
            "normalized_grammar": intermediates.get("4_cnf", ""),
        })
    except (ValueError, TypeError, GrammarError) as error:
        return jsonify({"error": str(error)}), 400
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.post("/api/combo-preview")
def combo_preview():
    """
    Customer combo preview endpoint: checks shopping cart with CYK parser.
    
    Input: JSON {"cart": [{"slot": "A1", "quantity": 1}, ...]}.
    Output: JSON with matched (bool), discount_percent, discount_amount, tree, derivation.
    """
    data = request.get_json(silent=True) or {}
    cart = data.get("cart", [])
    if not cart:
        return jsonify({
            "matched": False,
            "ambiguous": False,
            "discount_options": {},
            "discount_percent": 0,
            "gross_total": 0,
            "discount_amount": 0,
            "total": 0,
            "category_sequence": [],
            "parse_count": 0,
            "tree": None,
            "derivation": [],
            "tokens": [],
            "normalization_steps": [],
            "normalized_grammar": "",
            "intermediate_grammars": {},
        })
    try:
        _, analysis = combo_analysis(cart)
        return jsonify(analysis)
    except (ValueError, TypeError, GrammarError) as error:
        return jsonify({"error": str(error)}), 400


@app.post("/api/unlock")
def unlock():
    """
    Admin authentication endpoint: verifies admin password and unlocks session.
    
    Input: JSON {"password": "...", "target": "inventory"|"receipt"|"both"}.
    Output: JSON with unlock flags (200) or error (401/400).
    """
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
    """Admin sign-out endpoint: clears unlocked permissions from the Flask session."""
    session.pop("inventory_unlocked", None)
    session.pop("receipt_unlocked", None)
    return jsonify({"success": True})


@app.get("/api/compare")
def compare():
    """
    Unit III FSM comparison endpoint: returns Moore and Mealy traces for given coins.
    
    Query Params: ?slot=A1&coins=10,20
    Output: JSON {"rows": [fsm_step_1, fsm_step_2, ...]}.
    """
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
    """
    Single-item purchase endpoint: calls PostgreSQL process_purchase stored procedure.
    
    Concepts:
      - Unit I: Propositional logic predicates P, Q, P ∧ Q, and R.
      - Unit III: Moore vs Mealy trace generation.
      - Unit IV: Greedy change-making breakdown.
    
    Input: JSON {"slot": "A1", "coins": [20]}.
    Output: JSON with dispensed item, change breakdown, logic truth values, FSM trace.
    """
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
        # Propositional logic authorization predicates
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
    """
    Multi-item cart purchase endpoint: applies CFG combo deals and dispenses items.
    
    Concepts:
      - Unit V: CFG combo deal evaluation and discount calculation.
      - Unit I: Propositional logic conditions across all cart items.
      - Unit IV: Greedy change calculation on final discounted total.
      - Supabase PostgreSQL atomic stored procedure `process_cart_purchase`.
    
    Input: JSON {"cart": [{"slot": "B1", "quantity": 1}, ...], "coins": [50]}.
    Output: JSON with dispensed items, applied combo discount, change breakdown, receipt.
    """
    data = request.get_json(silent=True) or {}
    cart = data.get("cart", [])
    coins = data.get("coins", [])
    try:
        coins = [int(x) for x in coins]
        if not cart:
            raise ValueError("Cart is empty.")
        if not coins or any(c not in DENOMINATIONS for c in coins):
            raise ValueError("Invalid denomination.")

        requested, deal = combo_analysis(cart)
        if deal.get("ambiguous") and not deal.get("discount_percent"):
            raise ValueError("This cart matches CFG deal branches with different discounts. Ask the admin to fix the ambiguous grammar before checkout.")

        paid = sum(coins)
        transaction_id = uuid.uuid4().hex
        result = supabase.rpc(
            "process_cart_purchase",
            {
                "p_cart": [{"slot": slot, "quantity": qty} for slot, qty in requested.items()],
                "p_paid": paid,
                "p_transaction_id": transaction_id,
                "p_discount_amount": deal["discount_amount"],
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
        receipt.append(f"SUBTOTAL : ₹{deal['gross_total']}")
        if deal["discount_amount"]:
            receipt.append(f"CFG COMBO ({deal['discount_percent']}%): -₹{deal['discount_amount']}")
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
            "gross_total": deal["gross_total"], "discount_amount": deal["discount_amount"],
            "combo": deal,
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
    """
    Admin Restock endpoint (Protected): adds units to an item's current stock.
    
    Input: JSON {"slot": "A1", "amount": 5}.
    Output: JSON {"success": true, "item": updated_item}.
    """
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
    """
    Admin Set Stock endpoint (Protected): directly overwrites an item's stock count.
    
    Input: JSON {"slot": "A1", "stock": 10}.
    Output: JSON {"success": true, "item": updated_item}.
    """
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
    """
    Admin Daily Sales endpoint (Protected): returns all transaction records for today.
    
    Output: JSON {"date": "YYYY-MM-DD", "sales": [...], "count": N}.
    """
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
    """
    Admin End-of-Day endpoint (Protected): calls atomic collect_end_day stored procedure.
    
    Summarizes today's revenue, increments collection counter, archives sales, and returns receipt.
    Output: JSON with receipt array, collection count, cash received, change returned.
    """
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
    """
    Development/Demo Reset endpoint: restores initial 6 items and resets counters.
    
    Calls Supabase stored procedure `reset_machine()`.
    Output: JSON {"success": true, "items": [...]}.
    """
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
