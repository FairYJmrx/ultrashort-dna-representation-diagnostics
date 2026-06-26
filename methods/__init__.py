"""Lightweight k-mer informatics experiment utilities."""

from .ck4p_msp import (
    CK4PMSPConfig,
    CK4PMSPFeatures,
    build_ck4_block,
    build_ck4p_msp,
    build_ck4p_msp_features,
    build_msp_block,
    build_p_block,
    expected_dimensions,
    paired_cosine,
    standardized_diagnostic_drift,
)

__all__ = [
    "CK4PMSPConfig",
    "CK4PMSPFeatures",
    "build_ck4_block",
    "build_ck4p_msp",
    "build_ck4p_msp_features",
    "build_msp_block",
    "build_p_block",
    "expected_dimensions",
    "paired_cosine",
    "standardized_diagnostic_drift",
]

