"""Pytest-discoverable wrappers around the executable smoke checks."""

from smoke_tests import (
    test_contract_artifacts,
    test_historical_descriptors,
    test_imports,
    test_method_contract,
    test_repository_layout,
)


def test_import_contract() -> None:
    test_imports.main()


def test_public_method_contract() -> None:
    test_method_contract.main()


def test_historical_descriptor_contract() -> None:
    test_historical_descriptors.main()


def test_release_layout() -> None:
    test_repository_layout.main()


def test_canonical_artifact_regeneration() -> None:
    test_contract_artifacts.main()
