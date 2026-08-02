"""Shared visual contract for manuscript figures.

Quantitative panels must use these method colours consistently. Conceptual
schematics may use channel colours, but should not remap a quantitative method
mark to a different saturated hue.
"""

from __future__ import annotations


METHOD_COLORS = {
    "CK4": "#5B677A",
    "P": "#70A5D8",
    "MSP": "#5DBA9B",
    "CK4+P": "#2F6BDE",
    "CK4+MSP": "#009E73",
    "P+MSP": "#7C6EA8",
    "CK4P-MSP": "#B83A62",
    "CK5": "#7456A4",
    "Hashed k=15": "#D17A22",
    "Sparse RP k=15": "#7768AE",
    "PseKNC": "#D17A22",
    "PseEIIP": "#CC79A7",
    "NCP+ANF": "#56B4E9",
}


METHOD_MARKERS = {
    "CK4": "o",
    "CK4+P": "s",
    "CK4+MSP": "^",
    "CK4P-MSP": "D",
    "CK5": "P",
}


SUPPORT_COLORS = {
    "ink": "#20262E",
    "neutral_dark": "#5B677A",
    "neutral_mid": "#929BA8",
    "neutral_point": "#AEB6C1",
    "neutral_line": "#D7DCE2",
    "grid": "#E1E4E8",
}
