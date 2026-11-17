"""
CFG Normalization, CYK Parsing, Parse Tree Generation, and Derivation Engine
for SmartVend Combo Deals (Unit V - Context-Free Grammars).

This module implements:
1. Context-Free Grammar (CFG) parsing in standard Backus-Naur Form (BNF).
2. A 4-stage pipeline to convert any CFG to Chomsky Normal Form (CNF):
   - Stage 1: Eliminate epsilon (empty) productions.
   - Stage 2: Eliminate unit productions (A -> B).
   - Stage 3: Eliminate useless symbols (non-generating and unreachable).
   - Stage 4: Convert remaining rules to CNF (A -> BC or A -> a).
3. The Cocke-Younger-Kasami (CYK) dynamic programming parsing algorithm.
4. Parse tree unwrapping and step-by-step leftmost derivation generation.
5. Ambiguity detection and Best-Discount resolution policy.
"""

from collections import defaultdict
import copy
import itertools
import re


DEFAULT_RULES = """Deal -> Combo | Combo Deal
Combo -> snack beverage | snack snack beverage | beverage Combo2
Combo2 -> snack"""

DEFAULT_DISCOUNTS = {
    "snack beverage": 10,
    "snack snack beverage": 15,
    "beverage Combo2": 10,
    "beverage snack": 10,
    "Combo": 10,
    "Deal": 10,
}

MAX_TREES = 100
MAX_CART_ITEMS = 20


class GrammarError(ValueError):
    """Raised when a context-free grammar is malformed or invalid."""
    pass


def parse_rules(source, categories=None):
    """
    Parses a CFG text written in Backus-Naur Form (BNF).
    
    Concept: Context-Free Grammar definition G = (V, Σ, R, S) (Unit V).
    - V (Variables/Nonterminals): capital identifiers on the LHS, e.g. Deal, Combo.
    - Σ (Terminals): product category tokens, e.g. snack, beverage.
    - R (Rules): productions of the form Nonterminal -> alternative | alternative.
    - S (Start Symbol): 'Deal'.
    
    Input:
      source: str, multi-line grammar text.
      categories: optional list of valid terminal names to validate against.
    Output:
      dict mapping each LHS symbol (str) to a list of RHS tuples (tuple of str).
    """
    if not isinstance(source, str) or not source.strip():
        raise GrammarError("Grammar text cannot be empty.")

    grammar = {}
    lines = source.strip().splitlines()
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "->" not in line:
            raise GrammarError(f"Line {line_num}: expected 'Nonterminal -> production', got '{line}'")
        lhs, rhs_part = line.split("->", 1)
        lhs = lhs.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", lhs):
            raise GrammarError(f"Line {line_num}: invalid nonterminal name '{lhs}'")

        if lhs not in grammar:
            grammar[lhs] = []

        alts = [alt.strip() for alt in rhs_part.split("|")]
        if any(not alt for alt in alts):
            raise GrammarError(f"Line {line_num}: empty alternatives are not allowed; write 'ε' explicitly.")

        for alt in alts:
            if alt in {"ε", "epsilon", "EPSILON", "''", '""'}:
                grammar[lhs].append(())
            else:
                symbols = tuple(alt.split())
                grammar[lhs].append(symbols)

    if "Deal" not in grammar:
        raise GrammarError("The grammar must contain the start symbol 'Deal'.")

    # Validate terminals if category domain is provided
    if categories is not None:
        cat_set = {str(c).lower() for c in categories}
        nonterm_set = set(grammar.keys())
        for lhs, prods in grammar.items():
            for rhs in prods:
                for sym in rhs:
                    if sym not in nonterm_set and sym.lower() not in cat_set:
                        raise GrammarError(
                            f"Unknown symbol '{sym}' in rule '{lhs} -> {' '.join(rhs)}'. "
                            f"Valid terminals are: {sorted(list(cat_set))}"
                        )

    return grammar


def format_grammar(grammar):
    """Formats a grammar dictionary into human-readable text."""
    lines = []
    for lhs, prods in grammar.items():
        alts = []
        for rhs in prods:
            if not rhs:
                alts.append("ε")
            else:
                alts.append(" ".join(rhs))
        lines.append(f"{lhs} -> " + " | ".join(alts))
    return "\n".join(lines)


def eliminate_epsilon(grammar, start_symbol="Deal"):
    """
    Stage 1 of CNF Normalization: Eliminate epsilon (empty, ε) productions.
    
    Concept: Nullable variables (Unit V).
    A variable A is nullable if it can derive the empty string: A =>* ε.
    For every rule containing nullable variables, we generate all subsets
    with and without them, then discard the empty rule ε.
    
    Input: grammar dictionary, start symbol name.
    Output: (new_grammar, nullable_set).
    """
    nullable = set()
    changed = True
    while changed:
        changed = False
        for lhs, prods in grammar.items():
            if lhs not in nullable:
                for rhs in prods:
                    if len(rhs) == 0 or all(sym in nullable for sym in rhs):
                        nullable.add(lhs)
                        changed = True
                        break

    new_grammar = {}
    for lhs, prods in grammar.items():
        new_prods = set()
        for rhs in prods:
            if not rhs:
                continue
            null_indices = [i for i, s in enumerate(rhs) if s in nullable]
            # Form all combinations of omitting nullable symbols
            for k in range(len(null_indices) + 1):
                for remove_subset in itertools.combinations(null_indices, k):
                    candidate = tuple(s for i, s in enumerate(rhs) if i not in remove_subset)
                    if candidate:
                        new_prods.add(candidate)
        if new_prods:
            new_grammar[lhs] = sorted(list(new_prods))

    # Preserve start symbol even if only nullable (non-empty language)
    if start_symbol not in new_grammar:
        new_grammar[start_symbol] = []

    return new_grammar, nullable


def eliminate_unit(grammar, start_symbol="Deal"):
    """
    Stage 2 of CNF Normalization: Eliminate unit productions (A -> B).
    
    Concept: Unit Closure (Unit V).
    A unit production has a single nonterminal on the right-hand side.
    We compute the unit closure Unit(A) = {B in V | A =>* B}, then add all
    non-unit productions of B directly to A and delete the unit rule.
    
    Input: grammar dictionary, start symbol name.
    Output: (new_grammar, unit_closure_dict).
    """
    nonterminals = set(grammar.keys())
    unit_closure = {lhs: {lhs} for lhs in nonterminals}

    for lhs in nonterminals:
        changed = True
        while changed:
            changed = False
            current_closure = list(unit_closure[lhs])
            for b in current_closure:
                for rhs in grammar.get(b, []):
                    if len(rhs) == 1 and rhs[0] in nonterminals:
                        if rhs[0] not in unit_closure[lhs]:
                            unit_closure[lhs].add(rhs[0])
                            changed = True

    new_grammar = {}
    for lhs in nonterminals:
        non_unit_prods = set()
        for b in unit_closure[lhs]:
            for rhs in grammar.get(b, []):
                # Omit unit rules A -> B
                if not (len(rhs) == 1 and rhs[0] in nonterminals):
                    if rhs != ():
                        non_unit_prods.add(rhs)
        if non_unit_prods:
            new_grammar[lhs] = sorted(list(non_unit_prods))

    if start_symbol not in new_grammar:
        new_grammar[start_symbol] = []

    return new_grammar, unit_closure


def eliminate_useless(grammar, start_symbol="Deal", categories=None):
    """
    Stage 3 of CNF Normalization: Eliminate useless symbols.
    
    Concept: Generating and Reachable symbols (Unit V).
    A symbol is useful only if it can derive a terminal string (generating)
    AND can be reached starting from 'Deal' (reachable).
    - 3a: Bottom-up search for generating symbols.
    - 3b: Top-down graph reachability from start_symbol.
    
    Input: grammar dictionary, start symbol name, optional category terminals.
    Output: new_grammar containing only useful symbols.
    """
    nonterminals = set(grammar.keys())
    if categories is not None:
        terminals = {str(c).lower() for c in categories}
    else:
        terminals = set()
        for prods in grammar.values():
            for rhs in prods:
                for s in rhs:
                    if s not in nonterminals:
                        terminals.add(s.lower())

    # 3a. Generating symbols
    generating = set()
    changed = True
    while changed:
        changed = False
        for lhs, prods in grammar.items():
            if lhs not in generating:
                for rhs in prods:
                    if all((sym not in nonterminals) or (sym in generating) for sym in rhs):
                        generating.add(lhs)
                        changed = True
                        break

    gen_grammar = {}
    for lhs in generating:
        valid_prods = []
        for rhs in grammar.get(lhs, []):
            if all((sym not in nonterminals) or (sym in generating) for sym in rhs):
                valid_prods.append(rhs)
        if valid_prods:
            gen_grammar[lhs] = valid_prods

    if start_symbol not in gen_grammar:
        return {start_symbol: []}

    # 3b. Reachable symbols
    reachable = {start_symbol}
    changed = True
    while changed:
        changed = False
        current_reachable = list(reachable)
        for sym in current_reachable:
            if sym in gen_grammar:
                for rhs in gen_grammar[sym]:
                    for s in rhs:
                        if s in gen_grammar and s not in reachable:
                            reachable.add(s)
                            changed = True

    new_grammar = {lhs: prods for lhs, prods in gen_grammar.items() if lhs in reachable}
    if start_symbol not in new_grammar:
        new_grammar[start_symbol] = []

    return new_grammar


def convert_to_cnf(grammar, start_symbol="Deal", categories=None):
    """
    Stage 4 of CNF Normalization: Convert all productions to Chomsky Normal Form.
    
    Concept: Chomsky Normal Form (CNF) (Unit V).
    Every rule in CNF must strictly be in one of two formats:
      1. A -> B C  (binary rule: exactly two nonterminals)
      2. A -> a    (unary terminal rule: exactly one terminal)
    
    Transformations:
      - Step 4a: Terminal isolation. Mixed rules (e.g. A -> snack B) get synthetic
        terminal variables (T_snack -> snack, so A -> T_snack B).
      - Step 4b: Binarization. Rules with length >= 3 are split into cascading
        binary pairs using helper variables (BIN_...).
      - Step 4c: Builds reverse lookup dictionaries for fast CYK parsing.
    
    Input: grammar dictionary, start symbol name, categories list.
    Output: (cnf_grammar, terminal_rules, binary_rules).
    """
    nonterminals = set(grammar.keys())
    if categories is not None:
        terminals = {str(c).lower() for c in categories}
    else:
        terminals = set()
        for prods in grammar.values():
            for rhs in prods:
                for s in rhs:
                    if s not in nonterminals:
                        terminals.add(s.lower())

    used_names = set(grammar.keys())

    def fresh_name(base):
        idx = 1
        name = f"{base}_{idx}"
        while name in used_names:
            idx += 1
            name = f"{base}_{idx}"
        used_names.add(name)
        return name

    cnf_grammar = {}
    term_to_nt = {}

    # Step 4a: Replace terminals in long rules with dedicated nonterminals
    temp_grammar = {}
    for lhs, prods in grammar.items():
        temp_grammar[lhs] = []
        for rhs in prods:
            if len(rhs) == 1:
                # Terminal rule: A -> a
                sym = rhs[0]
                temp_grammar[lhs].append((sym.lower() if sym.lower() in terminals else sym,))
            else:
                new_rhs = []
                for s in rhs:
                    if s in terminals or s.lower() in terminals:
                        s_term = s.lower()
                        if s_term not in term_to_nt:
                            t_nt = fresh_name(f"T_{s_term}")
                            term_to_nt[s_term] = t_nt
                            cnf_grammar[t_nt] = [(s_term,)]
                        new_rhs.append(term_to_nt[s_term])
                    else:
                        new_rhs.append(s)
                temp_grammar[lhs].append(tuple(new_rhs))

    # Step 4b: Binarize rules of length > 2
    for lhs, prods in temp_grammar.items():
        if lhs not in cnf_grammar:
            cnf_grammar[lhs] = []
        for rhs in prods:
            if len(rhs) <= 2:
                cnf_grammar[lhs].append(rhs)
            else:
                curr_lhs = lhs
                for i in range(len(rhs) - 2):
                    next_helper = fresh_name(f"BIN_{lhs}")
                    cnf_grammar[curr_lhs].append((rhs[i], next_helper))
                    cnf_grammar[next_helper] = []
                    curr_lhs = next_helper
                cnf_grammar[curr_lhs].append((rhs[-2], rhs[-1]))

    # Step 4c: Build fast lookup maps for CYK
    terminal_rules = defaultdict(list)
    binary_rules = defaultdict(list)
    for lhs, prods in cnf_grammar.items():
        for rhs in prods:
            if len(rhs) == 1:
                terminal_rules[rhs[0]].append(lhs)
            elif len(rhs) == 2:
                binary_rules[rhs].append(lhs)

    return cnf_grammar, dict(terminal_rules), dict(binary_rules)


def normalize(grammar, categories=None, start_symbol="Deal"):
    """
    Executes the complete 4-stage CFG normalization pipeline:
      Stage 1: Remove ε-productions
      Stage 2: Remove unit productions
      Stage 3: Remove useless symbols (non-generating, unreachable)
      Stage 4: Convert to Chomsky Normal Form (CNF)

    Returns:
      cnf_grammar (dict),
      terminal_rules (dict),
      binary_rules (dict),
      stages (list of str descriptions),
      intermediate_grammars (dict of stage_name -> formatted string)
    """
    stages = []
    intermediate_grammars = {}

    intermediate_grammars["0_original"] = format_grammar(grammar)

    # 1. Epsilon
    g_eps, nullable = eliminate_epsilon(grammar, start_symbol)
    stages.append("Removed ε-productions" if nullable else "No ε-productions to remove")
    intermediate_grammars["1_no_epsilon"] = format_grammar(g_eps)

    # 2. Unit
    g_unit, unit_closure = eliminate_unit(g_eps, start_symbol)
    stages.append("Removed unit productions")
    intermediate_grammars["2_no_unit"] = format_grammar(g_unit)

    # 3. Useless
    g_useless = eliminate_useless(g_unit, start_symbol, categories)
    if start_symbol not in g_useless or not g_useless[start_symbol]:
        raise GrammarError("The grammar cannot derive any category sequence from the start symbol 'Deal'.")
    stages.append("Removed non-generating and unreachable symbols")
    intermediate_grammars["3_no_useless"] = format_grammar(g_useless)

    # 4. CNF
    cnf_grammar, term_rules, bin_rules = convert_to_cnf(g_useless, start_symbol, categories)
    stages.append("Converted productions to Chomsky Normal Form")
    intermediate_grammars["4_cnf"] = format_grammar(cnf_grammar)

    return cnf_grammar, term_rules, bin_rules, stages, intermediate_grammars


def cyk_parse(tokens, terminal_rules, binary_rules, start_symbol="Deal", max_trees=MAX_TREES):
    """
    Cocke-Younger-Kasami (CYK) dynamic programming parsing algorithm.
    
    Concept: Tabular polynomial-time CFG membership recognition (Unit V).
    Time Complexity: O(n^3 * |R|) where n is sequence length and |R| is rule count.
    Space Complexity: O(n^2 * |V|) for the 2D triangular recognition table.
    
    How it works:
      - Base case (length 1): chart[i][i] stores nonterminals that produce token[i].
      - Inductive step (length 2 to n): for every split point k between i and j,
        checks if nonterminal B in chart[i][k] and C in chart[k+1][j] form a rule A -> BC.
      - If start_symbol ('Deal') appears in chart[0][n-1], the string is accepted!
      - Stores child pointers to reconstruct all valid parse trees.
    
    Input: list of tokens, terminal_rules dict, binary_rules dict, start_symbol.
    Output: list of parse tree tuples rooted at start_symbol.
    """
    n = len(tokens)
    if n == 0:
        return []

    chart = [[defaultdict(list) for _ in range(n)] for _ in range(n)]

    # Length 1 base case
    for i, token in enumerate(tokens):
        token_lower = str(token).lower()
        for nt in terminal_rules.get(token_lower, []):
            chart[i][i][nt].append((nt, ((token_lower, ()),)))

    # Length 2 to n
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            for k in range(i, j):
                left_cell = chart[i][k]
                right_cell = chart[k + 1][j]
                for (B, C), parents in binary_rules.items():
                    if B in left_cell and C in right_cell:
                        for A in parents:
                            cell = chart[i][j][A]
                            room = max_trees - len(cell)
                            if room > 0:
                                for left_tree in left_cell[B][:room]:
                                    for right_tree in right_cell[C][:room]:
                                        if len(cell) >= max_trees:
                                            break
                                        cell.append((A, (left_tree, right_tree)))

    return chart[0][n - 1].get(start_symbol, [])


def unwrap_cnf_tree(tree, original_grammar):
    """
    Reconstructs the original grammar parse tree from a CNF parse tree.
    
    Concept: Inverting synthetic CNF binarization nodes (Unit V).
    CYK operates on the CNF grammar with synthetic helper nodes like T_snack
    and BIN_Deal. This function inlines the binarization helpers and unwraps
    the terminal wrappers so the user sees their original BNF rules.
    
    Input: raw CNF parse tree tuple, original_grammar dict.
    Output: clean parse tree tuple matching original grammar nonterminals.
    """
    sym, children = tree
    if not children:
        return (sym, ())

    unwrapped_children = []
    for child in children:
        c_sym, c_kids = child
        if c_sym.startswith("T_") and len(c_kids) == 1 and not c_kids[0][1]:
            # Terminal wrapper node: unwrap to the terminal itself
            unwrapped_children.append((c_kids[0][0], ()))
        elif c_sym.startswith("BIN_"):
            # Binarization helper node: inline its children
            unwrapped_helper = unwrap_cnf_tree(child, original_grammar)
            unwrapped_children.extend(unwrapped_helper[1])
        else:
            unwrapped_children.append(unwrap_cnf_tree(child, original_grammar))

    return (sym, tuple(unwrapped_children))


def generate_leftmost_derivation(tree):
    """
    Generates the step-by-step leftmost derivation strings from a parse tree.
    
    Concept: Leftmost Derivation (Unit V).
    In a leftmost derivation (S => ... => w), the leftmost nonterminal variable
    in each sentential form is replaced first.
    
    Input: parse tree tuple (rooted at 'Deal').
    Output: list of strings representing each intermediate sentential form
            e.g. ['Deal', 'Combo', 'snack beverage'].
    """
    def get_frontier(nodes):
        res = []
        for n in nodes:
            if isinstance(n, tuple):
                res.append(n[0])
            else:
                res.append(str(n))
        return " ".join(res)

    steps = []
    current_nodes = [tree]
    steps.append(get_frontier(current_nodes))

    while True:
        replaced = False
        new_nodes = []
        for n in current_nodes:
            if not replaced and isinstance(n, tuple) and len(n[1]) > 0:
                new_nodes.extend(n[1])
                replaced = True
            else:
                new_nodes.append(n)
        if not replaced:
            break
        current_nodes = new_nodes
        step_str = get_frontier(current_nodes)
        if step_str != steps[-1]:
            steps.append(step_str)

    return steps


def serialize_tree(node):
    """Recursively serializes a parse tree tuple to JSON-compatible dict."""
    if not node:
        return None
    sym, children = node
    return {
        "symbol": sym,
        "children": [serialize_tree(c) for c in children]
    }


def find_matched_combo_rules(tree):
    """
    Walks a parse tree and collects all matched Combo and Deal production rules.
    """
    rules = []
    sym, children = tree
    if children:
        child_symbols = tuple(c[0] for c in children)
        rules.append((sym, child_symbols))
        for child in children:
            rules.extend(find_matched_combo_rules(child))
    return rules


def calculate_discount_for_tree(tree, discounts):
    """
    Computes the discount percentage associated with a specific parse tree.
    Supports discounts keyed by:
      - Nonterminal names (e.g. 'SnackDrink', 'Combo', 'Deal')
      - Rule production signatures (e.g. 'snack beverage')
    """
    matched_rules = find_matched_combo_rules(tree)
    rates = []

    for lhs, rhs in matched_rules:
        rhs_str = " ".join(rhs)
        # Check rule signature
        if rhs_str in discounts:
            rates.append(int(discounts[rhs_str]))
        # Check LHS nonterminal
        elif lhs in discounts:
            rates.append(int(discounts[lhs]))
        # Check if single nonterminal child has discount
        elif len(rhs) == 1 and rhs[0] in discounts:
            rates.append(int(discounts[rhs[0]]))

    if rates:
        # For multiple combos, choose maximum or combined discount
        return max(rates)
    return 10  # default combo discount fallback


def evaluate(sequence, source, discounts=None, categories=None, policy="best-discount"):
    """
    Evaluates a cart category sequence against the CFG combo rules.
    
    Concepts Used (Unit V):
      - Context-Free Grammar membership check via CYK algorithm.
      - Grammar Ambiguity Detection: checks if multiple distinct parse trees exist
        that produce conflicting discount percentages.
      - Best-Discount Policy: when ambiguous, awards the highest discount rate
        to the customer so checkout proceeds smoothly while reporting the ambiguity.
    
    Input:
      sequence: list of str category tokens (e.g. ['snack', 'beverage']).
      source: str, BNF grammar text.
      discounts: dict mapping rule/nonterminal names to int discount percentages.
      categories: list of catalogued categories.
      policy: str, 'best-discount' (resolves ambiguity in customer's favor).
    Output:
      dict with keys: matched (bool), ambiguous (bool), discount_percent (int),
      parse_count (int), tree (dict), derivation (list of str), normalization_steps (list),
      intermediate_grammars (dict).
    """
    if discounts is None:
        discounts = DEFAULT_DISCOUNTS

    tokens = [str(token).lower() for token in sequence]
    if len(tokens) > MAX_CART_ITEMS:
        raise GrammarError(f"Cart category sequence exceeds maximum evaluation length of {MAX_CART_ITEMS} items.")

    if not tokens:
        return {
            "matched": False,
            "ambiguous": False,
            "discount_options": {},
            "discount_percent": 0,
            "parse_count": 0,
            "tree": None,
            "derivation": [],
            "tokens": [],
            "normalization_steps": [],
            "normalized_grammar": "",
            "intermediate_grammars": {},
        }

    # Validate categories
    if categories is not None:
        cat_set = {str(c).lower() for c in categories}
        if any(t not in cat_set for t in tokens):
            return {
                "matched": False,
                "ambiguous": False,
                "discount_options": {},
                "discount_percent": 0,
                "parse_count": 0,
                "tree": None,
                "derivation": [],
                "tokens": tokens,
                "message": "Cart contains items from uncatalogued categories.",
                "normalization_steps": [],
                "normalized_grammar": "",
                "intermediate_grammars": {},
            }

    parsed = parse_rules(source, categories)
    cnf, terminals, binaries, stages, intermediates = normalize(parsed, categories)
    trees = cyk_parse(tokens, terminals, binaries, start_symbol="Deal", max_trees=MAX_TREES)

    if not trees:
        return {
            "matched": False,
            "ambiguous": False,
            "discount_options": {},
            "discount_percent": 0,
            "parse_count": 0,
            "tree": None,
            "derivation": [],
            "tokens": tokens,
            "normalization_steps": stages,
            "normalized_grammar": intermediates.get("4_cnf", ""),
            "intermediate_grammars": intermediates,
        }

    # Reconstruct original parse trees and calculate discounts
    unwrapped_trees = [unwrap_cnf_tree(t, parsed) for t in trees]
    tree_discounts = [calculate_discount_for_tree(ut, discounts) for ut in unwrapped_trees]

    distinct_discounts = sorted(list(set(tree_discounts)))
    is_ambiguous = len(trees) > 1 and len(distinct_discounts) > 1

    # Selected tree based on policy
    if policy == "best-discount" and distinct_discounts:
        best_discount = max(distinct_discounts)
        best_idx = tree_discounts.index(best_discount)
        selected_tree = unwrapped_trees[best_idx]
        selected_discount = best_discount
    else:
        selected_tree = unwrapped_trees[0]
        selected_discount = tree_discounts[0]

    derivation_steps = generate_leftmost_derivation(selected_tree)

    discount_options = {f"Parse_{i+1}": rate for i, rate in enumerate(tree_discounts)}

    return {
        "matched": True,
        "ambiguous": is_ambiguous,
        "discount_options": discount_options,
        "discount_percent": selected_discount,
        "parse_count": len(trees),
        "tree": serialize_tree(selected_tree),
        "derivation": derivation_steps,
        "tokens": tokens,
        "normalization_steps": stages,
        "normalized_grammar": intermediates.get("4_cnf", ""),
        "intermediate_grammars": intermediates,
    }
