"""Unit tests for the ``run_actions`` dispatcher."""
from __future__ import annotations

import argparse
from importlib import import_module
from unittest import mock, TestCase

assassin = import_module("assassin")


def build_args(**overrides):
    """Create an ``argparse.Namespace`` with defaults matching the CLI."""

    defaults = dict(
        scan=None,
        target=None,
        check=None,
        mode=None,
        cert=None,
        filetype=None,
        user=None,
        secret=None,
        host=None,
        auto=None,
        post=None,
        db=None,
        key=None,
        log=None,
        silent=False,
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


class RunActionsTests(TestCase):
    """Validate how ``run_actions`` delegates to helper routines."""

    def test_basic_scan_dispatches_to_scan_helper(self) -> None:
        args = build_args(scan="basic", target="10.0.0.1")

        with mock.patch.object(assassin, "scan") as mocked_scan:
            assassin.run_actions(args)

        mocked_scan.assert_called_once_with("10.0.0.1")

    def test_advanced_scan_requests_exit_after_completion(self) -> None:
        args = build_args(scan="advanced", target="10.0.0.2")

        with mock.patch.object(assassin, "advanced") as mocked_advanced:
            with self.assertRaises(SystemExit) as exc_info:
                assassin.run_actions(args)

        mocked_advanced.assert_called_once_with("10.0.0.2")
        self.assertEqual(exc_info.exception.code, 0)

    def test_ssh_auth_flow_invokes_prepare_and_stats(self) -> None:
        args = build_args(check="ssh", mode="auth")

        fake_prepare = mock.Mock()
        fake_prepare.looted_user = mock.Mock()
        fake_prepare.clarify = mock.Mock()
        fake_prepare.root = mock.Mock()

        fake_stat = mock.Mock()
        fake_stat.userxxx = mock.Mock()
        fake_stat.machinexxx = mock.Mock()

        with (
            mock.patch.object(assassin, "safe_import", side_effect=[fake_prepare, fake_stat]) as mocked_import,
            mock.patch.object(assassin.os, "system") as mocked_system,
            mock.patch.object(assassin.time, "sleep") as mocked_sleep,
        ):
            with self.assertRaises(SystemExit) as exc_info:
                assassin.run_actions(args)

        mocked_import.assert_has_calls(
            [
                mock.call("post.prepare", "post exploitation preparation module"),
                mock.call("check.vuln.pub.stat", "statistics module"),
            ]
        )
        fake_prepare.looted_user.assert_called_once_with()
        fake_prepare.clarify.assert_called_once_with()
        fake_prepare.root.assert_called_once_with()
        fake_stat.userxxx.assert_called_once_with()
        fake_stat.machinexxx.assert_called_once_with()
        mocked_system.assert_called_once()
        self.assertIn("./check/vuln/pub/reauth", mocked_system.call_args.args[0])
        self.assertEqual(mocked_sleep.call_count, 3)
        self.assertEqual(exc_info.exception.code, 0)

    def test_ssh_backdoor_flow_runs_backdoor_module(self) -> None:
        args = build_args(check="ssh", mode="backdoor")

        fake_pka = mock.Mock()
        fake_pka.prep = mock.Mock()
        fake_pka.process = mock.Mock()
        fake_pka.add_backdoor = mock.Mock()
        fake_pka.clean = mock.Mock()

        with (
            mock.patch.object(assassin, "safe_import", return_value=fake_pka) as mocked_import,
            mock.patch.object(assassin.time, "sleep") as mocked_sleep,
        ):
            with self.assertRaises(SystemExit) as exc_info:
                assassin.run_actions(args)

        mocked_import.assert_called_once_with("post.pka", "post exploitation automation module")
        fake_pka.prep.assert_called_once_with()
        fake_pka.process.assert_called_once_with()
        fake_pka.add_backdoor.assert_called_once_with()
        fake_pka.clean.assert_called_once_with()
        self.assertEqual(mocked_sleep.call_count, 3)
        self.assertEqual(exc_info.exception.code, 0)
