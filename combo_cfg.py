"""
SmartVend - Combo CFG Backward-Compatibility Adapter.

Re-exports pure CFG functions from cfg_engine.py for backwards compatibility
with legacy test imports and modules. All core logic lives in cfg_engine.py.
"""

from cfg_engine import (
    DEFAULT_DISCOUNTS,
    DEFAULT_RULES,
    GrammarError,
    parse_rules,
    eliminate_epsilon,
    eliminate_unit,
    eliminate_useless,
    convert_to_cnf,
    normalize,
    cyk_parse,
    unwrap_cnf_tree,
    generate_leftmost_derivation,
    serialize_tree,
    evaluate,
    format_grammar,
)

__all__ = [
    "DEFAULT_DISCOUNTS",
    "DEFAULT_RULES",
    "GrammarError",
    "parse_rules",
    "eliminate_epsilon",
    "eliminate_unit",
    "eliminate_useless",
    "convert_to_cnf",
    "normalize",
    "cyk_parse",
    "unwrap_cnf_tree",
    "generate_leftmost_derivation",
    "serialize_tree",
    "evaluate",
    "format_grammar",
]
