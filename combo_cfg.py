"""
Backward-compatibility adapter for combo_cfg importing from cfg_engine.
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
