"""CFG normalization and CYK parsing for category-based combo deals."""

from itertools import product
import re


DEFAULT_RULES = """Deal -> SnackDrink | SnackPairDrink
SnackDrink -> snack beverage
SnackPairDrink -> snack snack beverage"""
DEFAULT_DISCOUNTS = {"SnackDrink": 10, "SnackPairDrink": 15}
MAX_TREES_PER_CELL = 64


class GrammarError(ValueError):
    pass


def parse_rules(source, categories):
    grammar = {}
    for line_number, line in enumerate(source.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        if "->" not in line:
            raise GrammarError(f"Line {line_number}: expected 'Nonterminal -> production'.")
        lhs, rhs_text = (part.strip() for part in line.split("->", 1))
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", lhs):
            raise GrammarError(f"Line {line_number}: invalid nonterminal '{lhs}'.")
        alternatives = [alt.strip() for alt in rhs_text.split("|")]
        if any(not alt for alt in alternatives):
            raise GrammarError(f"Line {line_number}: empty alternatives are not allowed; write ε explicitly.")
        grammar.setdefault(lhs, [])
        for alternative in alternatives:
            rhs = () if alternative in {"ε", "epsilon", "EPSILON"} else tuple(alternative.split())
            grammar[lhs].append(rhs)

    if "Deal" not in grammar:
        raise GrammarError("The start symbol must be Deal.")
    category_set = {str(category).casefold() for category in categories}
    nonterminals = set(grammar)
    for lhs, alternatives in grammar.items():
        for rhs in alternatives:
            for symbol in rhs:
                if symbol not in nonterminals and symbol.casefold() not in category_set:
                    raise GrammarError(f"Unknown symbol '{symbol}' in rule {lhs} -> {' '.join(rhs)}.")
    branches = grammar["Deal"]
    if not branches or any(len(rhs) != 1 or rhs[0] not in nonterminals for rhs in branches):
        raise GrammarError("Each Deal alternative must name one deal nonterminal, such as Deal -> SnackDrink | SnackPairDrink.")
    if len({rhs[0] for rhs in branches}) != len(branches):
        raise GrammarError("Deal alternatives must name distinct deal nonterminals.")
    return grammar


def normalize(grammar, categories):
    """Remove epsilon/unit/useless rules and convert remaining grammar to CNF."""
    source = {lhs: list(rules) for lhs, rules in grammar.items()}
    original_nt = set(source)
    stages = []

    nullable = {lhs for lhs, rules in source.items() if () in rules}
    changed = True
    while changed:
        changed = False
        for lhs, rules in source.items():
            if lhs not in nullable and any(rhs and all(symbol in nullable for symbol in rhs) for rhs in rules):
                nullable.add(lhs)
                changed = True
    no_epsilon = {}
    for lhs, rules in source.items():
        generated = set()
        for rhs in rules:
            if not rhs:
                continue
            positions = [i for i, symbol in enumerate(rhs) if symbol in nullable]
            for mask in product((False, True), repeat=len(positions)):
                removed = {positions[i] for i, take in enumerate(mask) if take}
                candidate = tuple(symbol for i, symbol in enumerate(rhs) if i not in removed)
                if candidate:
                    generated.add(candidate)
        if generated:
            no_epsilon[lhs] = [tuple(rhs) for rhs in sorted(generated)]
    source = no_epsilon
    stages.append("Removed ε-productions" if nullable else "No ε-productions to remove")

    unit_closure = {}
    for lhs in source:
        closure = {lhs}
        pending = [lhs]
        while pending:
            current = pending.pop()
            for rhs in source.get(current, []):
                if len(rhs) == 1 and rhs[0] in original_nt and rhs[0] not in closure:
                    closure.add(rhs[0])
                    pending.append(rhs[0])
        unit_closure[lhs] = closure
    no_unit = {}
    for lhs, closure in unit_closure.items():
        rules = {rhs for member in closure for rhs in source.get(member, [])
                 if not (len(rhs) == 1 and rhs[0] in original_nt)}
        if rules:
            no_unit[lhs] = sorted(rules)
    source = no_unit
    stages.append("Removed unit productions")

    generating = {lhs for lhs, rules in source.items()
                  if any(all(symbol not in original_nt for symbol in rhs) for rhs in rules)}
    changed = True
    while changed:
        changed = False
        for lhs, rules in source.items():
            if lhs not in generating and any(all(symbol not in original_nt or symbol in generating for symbol in rhs) for rhs in rules):
                generating.add(lhs)
                changed = True
    source = {lhs: [rhs for rhs in rules if all(symbol not in original_nt or symbol in generating for symbol in rhs)]
              for lhs, rules in source.items() if lhs in generating}

    reachable = {"Deal"}
    pending = ["Deal"]
    while pending:
        current = pending.pop()
        for rhs in source.get(current, []):
            for symbol in rhs:
                if symbol in source and symbol not in reachable:
                    reachable.add(symbol)
                    pending.append(symbol)
    source = {lhs: rules for lhs, rules in source.items() if lhs in reachable}
    if "Deal" not in source or not source["Deal"]:
        raise GrammarError("Deal cannot derive a category sequence with the current rules.")
    stages.append("Removed non-generating and unreachable symbols")

    terminal_rules = {}
    binary_rules = {}
    used_names = set(source)

    def fresh(base):
        name = base
        suffix = 1
        while name in used_names:
            name = f"{base}_{suffix}"
            suffix += 1
        used_names.add(name)
        return name

    terminal_symbols = {}
    cnf = {}
    for lhs, rules in source.items():
        cnf[lhs] = []
        for rhs in rules:
            rhs = tuple(symbol.casefold() if symbol.casefold() in {c.casefold() for c in categories} else symbol
                        for symbol in rhs)
            if len(rhs) == 1:
                cnf[lhs].append(rhs)
                terminal_rules.setdefault(rhs[0], []).append(lhs)
                continue
            replaced = []
            for symbol in rhs:
                if symbol.casefold() in {c.casefold() for c in categories}:
                    if symbol not in terminal_symbols:
                        name = fresh(f"T_{symbol}")
                        terminal_symbols[symbol] = name
                        cnf[name] = [(symbol,)]
                        terminal_rules.setdefault(symbol, []).append(name)
                    replaced.append(terminal_symbols[symbol])
                else:
                    replaced.append(symbol)
            while len(replaced) > 2:
                name = fresh("BIN")
                cnf[name] = [tuple(replaced[-2:])]
                replaced = replaced[:-2] + [name]
            cnf[lhs].append(tuple(replaced))

    binary_rules = {}
    terminal_rules = {}
    for lhs, rules in cnf.items():
        for rhs in rules:
            if len(rhs) == 1:
                terminal_rules.setdefault(rhs[0], []).append(lhs)
            elif len(rhs) == 2:
                binary_rules.setdefault(rhs, []).append(lhs)
            else:
                raise GrammarError("Could not convert one or more productions into Chomsky Normal Form.")
    stages.append("Converted productions to Chomsky Normal Form")
    return cnf, terminal_rules, binary_rules, stages


def format_grammar(grammar):
    return "\n".join(f"{lhs} -> " + " | ".join(" ".join(rhs) if rhs else "ε" for rhs in rules)
                     for lhs, rules in grammar.items())


def serialize_tree(node):
    return {"symbol": node[0], "children": [serialize_tree(child) for child in node[1]]}


def cyk_parse(tokens, grammar, terminal_rules, binary_rules):
    if not tokens:
        return []
    size = len(tokens)
    chart = [[{} for _ in range(size + 1)] for _ in range(size)]
    for i, token in enumerate(tokens):
        for lhs in terminal_rules.get(token, []):
            chart[i][i + 1].setdefault(lhs, []).append((lhs, ((token, ()),)))
    for width in range(2, size + 1):
        for start in range(size - width + 1):
            end = start + width
            for split in range(start + 1, end):
                left, right = chart[start][split], chart[split][end]
                for (left_symbol, right_symbol), parents in binary_rules.items():
                    if left_symbol not in left or right_symbol not in right:
                        continue
                    for lhs in parents:
                        cell = chart[start][end].setdefault(lhs, [])
                        room = MAX_TREES_PER_CELL - len(cell)
                        if room > 0:
                            for left_tree in left[left_symbol][:room]:
                                for right_tree in right[right_symbol][:room]:
                                    if len(cell) >= MAX_TREES_PER_CELL:
                                        break
                                    cell.append((lhs, (left_tree, right_tree)))
    return chart[0][size]


def evaluate(sequence, source, discounts, categories):
    category_set = {str(category).casefold() for category in categories}
    tokens = [str(token).casefold() for token in sequence]
    if any(token not in category_set for token in tokens):
        raise GrammarError("The cart contains a category that is not in the current inventory.")
    parsed = parse_rules(source, categories)
    cnf, terminals, binaries, stages = normalize(parsed, categories)
    chart_matches = cyk_parse(tokens, cnf, terminals, binaries)
    choices = {}
    tree = None
    parse_count = 0
    for branch in [rhs[0] for rhs in parsed["Deal"]]:
        branch_trees = chart_matches.get(branch, [])
        if branch_trees and branch not in discounts:
            raise GrammarError(f"Set a discount percentage for deal branch '{branch}'.")
        if branch_trees:
            choices[branch] = int(discounts[branch])
            parse_count += len(branch_trees)
            if tree is None:
                tree = ("Deal", ((branch, branch_trees[0][1]),))
    choices = {branch: int(discounts[branch]) for branch in choices}
    if any(rate < 0 or rate > 90 for rate in choices.values()):
        raise GrammarError("Discount percentages must be between 0 and 90.")
    return {
        "matched": bool(choices),
        "ambiguous": len(set(choices.values())) > 1,
        "discount_options": choices,
        "discount_percent": next(iter(set(choices.values()))) if len(set(choices.values())) == 1 else None,
        "parse_count": parse_count,
        "tree": serialize_tree(tree) if tree else None,
        "tree_truncated": any(len(chart_matches.get(branch, [])) >= MAX_TREES_PER_CELL for branch in choices),
        "normalized_grammar": format_grammar(cnf),
        "normalization_steps": stages,
        "tokens": tokens,
    }
