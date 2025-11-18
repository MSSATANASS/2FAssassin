"""Unit tests for the ``safe_import`` helper used by the CLI entry point."""
from __future__ import annotations

import builtins
from importlib import import_module
from unittest import mock, TestCase

assassin = import_module("assassin")


class SafeImportTests(TestCase):
    """Validate the defensive import wrapper."""

    def setUp(self) -> None:  # noqa: D401 - short explanation via docstring
        assassin._IMPORT_CACHE.clear()

    def test_safe_import_caches_module_results(self) -> None:
        """A module should only be imported once thanks to caching."""

        sentinel_module = object()
        with mock.patch.object(assassin.importlib, "import_module", return_value=sentinel_module) as mocked_import:
            first = assassin.safe_import("fake.module", "fake module")
            second = assassin.safe_import("fake.module", "fake module")

        self.assertIs(first, sentinel_module)
        self.assertIs(second, sentinel_module)
        mocked_import.assert_called_once_with("fake.module")

    def test_safe_import_exits_when_module_missing(self) -> None:
        """A helpful error message and exit should be triggered on ImportError."""

        with mock.patch.object(assassin.importlib, "import_module", side_effect=ImportError("boom")):
            with mock.patch.object(builtins, "print") as mocked_print:
                with self.assertRaises(SystemExit) as exc_info:
                    assassin.safe_import("missing.module", "missing module")

        mocked_print.assert_called_once_with("Unable to import missing module (missing.module). boom")
        self.assertEqual(exc_info.exception.code, 1)
        self.assertNotIn("missing.module", assassin._IMPORT_CACHE)
