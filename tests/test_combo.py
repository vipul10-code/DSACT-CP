"""
Automated Test Suite for SmartVend CFG Combo Deals (Unit V)
and Core Discrete Structures Requirements.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import copy
import pytest
from flask import session

import app as smartvend_app
from cfg_engine import (
    DEFAULT_DISCOUNTS,
    DEFAULT_RULES,
    GrammarError,
    convert_to_cnf,
    cyk_parse,
    eliminate_epsilon,
    eliminate_unit,
    eliminate_useless,
    evaluate,
    format_grammar,
    generate_leftmost_derivation,
    normalize,
    parse_rules,
)


@pytest.fixture
def client():
    smartvend_app.app.config["TESTING"] = True
    with smartvend_app.app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clean_config():
    # Ensure standard default config is active before each test
    config_file = os.path.join(smartvend_app.BASE, "combo_deal_config.json")
    smartvend_app.combo_config = lambda: {
        "id": 1,
        "rules": DEFAULT_RULES,
        "discounts": copy.deepcopy(DEFAULT_DISCOUNTS),
    }
    yield
    # Restore default rules in combo_deal_config.json
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            import json
            json.dump({"id": 1, "rules": DEFAULT_RULES, "discounts": DEFAULT_DISCOUNTS}, f, indent=2)
    except Exception:
        pass


# ==============================================================================
# TEST 1: Single combo in cart gives expected discount (10%), tree and derivation
# ==============================================================================
def test_single_combo_snack_beverage():
    cart = [
        {"slot": "B1", "quantity": 1},  # Chips: snack (price 20)
        {"slot": "A1", "quantity": 1},  # Water: beverage (price 20)
    ]
    requested, analysis = smartvend_app.combo_analysis(cart)
    assert requested == {"B1": 1, "A1": 1}
    assert analysis["matched"] is True
    assert analysis["ambiguous"] is False
    assert analysis["discount_percent"] == 10
    assert analysis["gross_total"] == 40
    assert analysis["discount_amount"] == 4
    assert analysis["total"] == 36
    assert analysis["category_sequence"] == ["snack", "beverage"]
    assert analysis["tree"] is not None
    assert analysis["tree"]["symbol"] == "Deal"
    assert len(analysis["derivation"]) >= 2
    assert analysis["derivation"][0] == "Deal"
    assert "snack beverage" in analysis["derivation"][-1]


# ==============================================================================
# TEST 2: Higher discount for 2 snacks + 1 beverage (15%)
# ==============================================================================
def test_higher_discount_snack_snack_beverage():
    cart = [
        {"slot": "B1", "quantity": 2},  # 2x Chips: snack, snack (price 20*2 = 40)
        {"slot": "A2", "quantity": 1},  # 1x Juice: beverage (price 30)
    ]
    requested, analysis = smartvend_app.combo_analysis(cart)
    assert requested == {"B1": 2, "A2": 1}
    assert analysis["matched"] is True
    assert analysis["discount_percent"] == 15
    assert analysis["gross_total"] == 70
    assert analysis["discount_amount"] == 70 * 15 // 100  # 10
    assert analysis["total"] == 60
    assert analysis["category_sequence"] == ["snack", "snack", "beverage"]
    assert "snack snack beverage" in analysis["derivation"][-1]


# ==============================================================================
# TEST 3: Combo2 rule handles beverage + snack (10%)
# ==============================================================================
def test_combo2_beverage_snack():
    cart = [
        {"slot": "A3", "quantity": 1},  # Soda: beverage (price 25)
        {"slot": "B2", "quantity": 1},  # Cookies: snack (price 15)
    ]
    requested, analysis = smartvend_app.combo_analysis(cart)
    assert analysis["matched"] is True
    assert analysis["discount_percent"] == 10
    assert analysis["gross_total"] == 40
    assert analysis["discount_amount"] == 4
    assert analysis["total"] == 36
    assert analysis["category_sequence"] == ["beverage", "snack"]
    assert analysis["tree"] is not None
    assert "beverage snack" in analysis["derivation"][-1]


# ==============================================================================
# TEST 4: Two combos in one cart both get discounted; parse tree covers sequence
# ==============================================================================
def test_chained_combos_in_cart():
    # [snack, beverage, beverage, snack]
    cart = [
        {"slot": "B1", "quantity": 1},  # snack
        {"slot": "A1", "quantity": 1},  # beverage
        {"slot": "A2", "quantity": 1},  # beverage
        {"slot": "B2", "quantity": 1},  # snack
    ]
    requested, analysis = smartvend_app.combo_analysis(cart)
    assert analysis["matched"] is True
    assert analysis["discount_percent"] == 10
    assert analysis["gross_total"] == 20 + 20 + 30 + 15  # 85
    assert analysis["discount_amount"] == 85 * 10 // 100  # 8
    assert analysis["total"] == 77
    assert analysis["category_sequence"] == ["snack", "beverage", "beverage", "snack"]
    assert analysis["tree"] is not None
    # Derivation must start at Deal and finish at all 4 terminals
    assert analysis["derivation"][0] == "Deal"
    assert analysis["derivation"][-1] == "snack beverage beverage snack"

    # Also test [snack, snack, beverage, snack, beverage]
    cart_mixed = [
        {"slot": "B1", "quantity": 2},  # snack, snack
        {"slot": "A1", "quantity": 1},  # beverage
        {"slot": "B2", "quantity": 1},  # snack
        {"slot": "A2", "quantity": 1},  # beverage
    ]
    _, analysis_mixed = smartvend_app.combo_analysis(cart_mixed)
    assert analysis_mixed["matched"] is True
    # Highest combo discount in cart is 15% (from snack snack beverage)
    assert analysis_mixed["discount_percent"] == 15
    assert analysis_mixed["derivation"][-1] == "snack snack beverage snack beverage"


# ==============================================================================
# TEST 5: Cart with no matching combo gets 0 discount and normal checkout
# ==============================================================================
def test_no_matching_combo():
    # [snack, snack] does not match any Deal rule
    cart = [
        {"slot": "B1", "quantity": 2},
    ]
    requested, analysis = smartvend_app.combo_analysis(cart)
    assert analysis["matched"] is False
    assert analysis["discount_percent"] == 0
    assert analysis["discount_amount"] == 0
    assert analysis["gross_total"] == 40
    assert analysis["total"] == 40
    assert analysis["tree"] is None
    assert analysis["derivation"] == []


# ==============================================================================
# TEST 6: Ambiguous grammar is detected; default grammar is unambiguous
# ==============================================================================
def test_ambiguity_detection_and_resolution():
    categories = ["snack", "beverage"]

    # 1. Shipped default grammar is unambiguous on representative inputs
    for seq in [
        ["snack", "beverage"],
        ["snack", "snack", "beverage"],
        ["beverage", "snack"],
        ["snack", "beverage", "beverage", "snack"],
    ]:
        res = evaluate(seq, DEFAULT_RULES, DEFAULT_DISCOUNTS, categories)
        assert res["matched"] is True
        assert res["ambiguous"] is False
        assert res["parse_count"] == 1

    # 2. Intentionally ambiguous grammar with two derivations yielding different discounts
    ambiguous_grammar = """Deal -> snack DealA | DealB beverage
DealA -> beverage
DealB -> snack"""
    ambiguous_discounts = {"DealA": 10, "DealB": 25}

    res_amb = evaluate(
        ["snack", "beverage"],
        ambiguous_grammar,
        ambiguous_discounts,
        categories,
        policy="best-discount",
    )
    assert res_amb["matched"] is True
    assert res_amb["ambiguous"] is True
    assert res_amb["parse_count"] == 2
    # Best-discount policy resolves ambiguity in customer's favor (25% instead of 10%)
    assert res_amb["discount_percent"] == 25
    assert set(res_amb["discount_options"].values()) == {10, 25}


# ==============================================================================
# TEST 7: CNF conversion steps on a suite of 5 different grammars
# ==============================================================================
def test_cnf_conversion_pipeline_five_grammars():
    cats = ["snack", "beverage"]

    # Grammar 1: Epsilon productions
    g1 = """Deal -> A beverage
A -> snack | ε"""
    p1 = parse_rules(g1, cats)
    cnf1, t1, b1, stages1, inter1 = normalize(p1, cats, start_symbol="Deal")
    assert "ε-productions" in stages1[0]
    # In CNF, all RHS must have length 1 (terminal) or 2 (nonterminals)
    for lhs, rhss in cnf1.items():
        for rhs in rhss:
            assert len(rhs) in (1, 2)
            if len(rhs) == 1:
                assert rhs[0] in cats
            else:
                assert all(sym not in cats for sym in rhs)

    # Grammar 2: Unit productions
    g2 = """Deal -> A
A -> B
B -> snack beverage"""
    p2 = parse_rules(g2, cats)
    cnf2, t2, b2, stages2, inter2 = normalize(p2, cats, start_symbol="Deal")
    assert "unit productions" in stages2[1]
    # Unit chain Deal -> A -> B -> snack beverage eliminated
    assert ("A",) not in cnf2.get("Deal", [])
    assert ("B",) not in cnf2.get("Deal", [])

    # Grammar 3: Useless symbols (non-generating X and unreachable Z)
    g3 = """Deal -> snack beverage
X -> X X
Z -> snack snack"""
    p3 = parse_rules(g3, cats)
    cnf3, t3, b3, stages3, inter3 = normalize(p3, cats, start_symbol="Deal")
    assert "X" not in cnf3
    assert "Z" not in cnf3

    # Grammar 4: Empty language properly rejected with clear GrammarError
    g4 = """Deal -> X
X -> X X"""
    p4 = parse_rules(g4, cats)
    with pytest.raises(GrammarError) as exc_info:
        normalize(p4, cats, start_symbol="Deal")
    assert "cannot derive any category sequence" in str(exc_info.value)

    # Grammar 5: Default SmartVend grammar
    p5 = parse_rules(DEFAULT_RULES, cats)
    cnf5, t5, b5, stages5, inter5 = normalize(p5, cats, start_symbol="Deal")
    assert "0_original" in inter5
    assert "1_no_epsilon" in inter5
    assert "2_no_unit" in inter5
    assert "3_no_useless" in inter5
    assert "4_cnf" in inter5
    # Verify CYK accepts valid strings in CNF
    assert len(cyk_parse(["snack", "beverage"], t5, b5, "Deal")) > 0
    assert len(cyk_parse(["beverage", "snack"], t5, b5, "Deal")) > 0
    assert len(cyk_parse(["snack", "snack"], t5, b5, "Deal")) == 0


# ==============================================================================
# TEST 8: Equivalence check: CYK results match recursive brute-force parser
# ==============================================================================
def test_cyk_vs_brute_force_equivalence():
    cats = ["snack", "beverage"]
    parsed = parse_rules(DEFAULT_RULES, cats)
    cnf, terminals, binaries, _, _ = normalize(parsed, cats, start_symbol="Deal")

    # Independent recursive brute-force parser on original grammar (depth-limited)
    def brute_force_matches(target_tokens, current_sentential=("Deal",), depth=0):
        if depth > 10:
            return False
        # If all terminals, check match
        all_terms = all(sym in cats for sym in current_sentential)
        if all_terms:
            return tuple(current_sentential) == tuple(target_tokens)
        if len(current_sentential) > len(target_tokens) + 2:
            return False

        # Find first nonterminal
        for idx, sym in enumerate(current_sentential):
            if sym not in cats:
                for rhs in parsed.get(sym, []):
                    expanded = current_sentential[:idx] + rhs + current_sentential[idx + 1 :]
                    if brute_force_matches(target_tokens, expanded, depth + 1):
                        return True
                return False
        return False

    # Test all possible token combinations of lengths 1, 2, 3
    test_vocab = ["snack", "beverage"]
    all_test_strings = []
    import itertools

    for length in range(1, 4):
        for combo in itertools.product(test_vocab, repeat=length):
            all_test_strings.append(list(combo))

    for tokens in all_test_strings:
        cyk_result = len(cyk_parse(tokens, terminals, binaries, "Deal")) > 0
        brute_result = brute_force_matches(tokens)
        assert cyk_result == brute_result, f"Mismatch for tokens {tokens}: CYK={cyk_result}, BruteForce={brute_result}"


# ==============================================================================
# TEST 9: Admin endpoints: authentication, validation, CNF steps preview
# ==============================================================================
def test_admin_endpoints(client):
    # 1. Unauthorized request to edit grammar is rejected (403)
    resp = client.post("/api/combo-config", json={"rules": DEFAULT_RULES, "discounts": {"Combo": 10}})
    assert resp.status_code == 403

    # 2. Unlock admin session with correct password
    unlock_resp = client.post("/api/unlock", json={"password": smartvend_app.ADMIN_PASSWORD, "target": "both"})
    assert unlock_resp.status_code == 200
    assert unlock_resp.json["inventory_unlocked"] is True

    # 3. Authorized request to edit grammar succeeds (200)
    save_resp = client.post(
        "/api/combo-config",
        json={"rules": DEFAULT_RULES, "discounts": {"Combo": 12, "snack beverage": 12}},
    )
    assert save_resp.status_code == 200
    assert save_resp.json["success"] is True
    assert "intermediate_grammars" in save_resp.json

    # 4. Preview CNF steps endpoint returns all pipeline stages
    preview_resp = client.post(
        "/api/combo-cnf-steps",
        json={"rules": "Deal -> Combo\nCombo -> snack beverage"},
    )
    assert preview_resp.status_code == 200
    data = preview_resp.json
    assert data["success"] is True
    assert len(data["stages"]) == 4
    assert "4_cnf" in data["intermediate_grammars"]

    # 5. Invalid grammar is rejected with 400 and clear error message
    bad_resp = client.post("/api/combo-cnf-steps", json={"rules": "Invalid line without arrow"})
    assert bad_resp.status_code == 400
    assert "error" in bad_resp.json


# ==============================================================================
# TEST 10: Regression check on existing features
# ==============================================================================
def test_regression_core_features(client):
    # Health endpoint
    h = client.get("/api/health")
    assert h.status_code in (200, 503)

    # Inventory endpoint
    inv = client.get("/api/inventory")
    assert inv.status_code == 200
    assert "items" in inv.json
    assert len(inv.json["items"]) >= 6

    # Sets and relations endpoint
    sr = client.get("/api/sets-relations")
    assert sr.status_code == 200
    assert "sets" in sr.json
    assert "slots" in sr.json["sets"]
    assert "slot_to_item" in sr.json["relations"]

    # Change breakdown greedy algorithm
    notes = smartvend_app.change_breakdown(48)
    assert notes == [20, 20, 5, 2, 1]
    assert sum(notes) == 48

    # Moore & Mealy FSM
    fsm_res = smartvend_app.fsm([10, 10, 10], 25)
    assert len(fsm_res) == 3
    # Step 1: 10 inserted (price 25) -> WAITING/ACCEPTING -> WAIT
    assert fsm_res[0]["moore_output"] == "WAIT"
    assert fsm_res[0]["mealy_output"] == "WAIT"
    # Step 3: balance reaches 30 >= 25 -> DISPENSE
    assert fsm_res[2]["moore_state"] == "READY"
    assert fsm_res[2]["moore_output"] == "DISPENSE"
    assert fsm_res[2]["mealy_state"] == "READY"
    assert fsm_res[2]["mealy_output"] == "DISPENSE"

    # Preview cart with empty list returns clean empty response without 400 error
    p = client.post("/api/combo-preview", json={"cart": []})
    assert p.status_code == 200
    assert p.json["matched"] is False
