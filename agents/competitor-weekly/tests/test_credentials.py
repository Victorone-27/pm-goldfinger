import subprocess

import pytest

from src import credentials


def forbidden(*args, **kwargs):
    raise AssertionError("Keychain must not be accessed")


def test_environment_key_takes_priority(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", " env-test-placeholder \n")
    monkeypatch.setattr(credentials.sys, "platform", "darwin")
    monkeypatch.setattr(credentials.subprocess, "run", forbidden)
    assert credentials.read_api_key() == "env-test-placeholder"


@pytest.mark.parametrize("empty_environment", [None, " \n"])
def test_fallback_to_named_keychain_service(monkeypatch, empty_environment, capsys):
    if empty_environment is None:
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    else:
        monkeypatch.setenv("DEEPSEEK_API_KEY", empty_environment)
    monkeypatch.setattr(credentials.sys, "platform", "darwin")
    calls = []

    def keychain(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="keychain-test-placeholder\n")

    monkeypatch.setattr(credentials.subprocess, "run", keychain)
    assert credentials.read_api_key() == "keychain-test-placeholder"
    assert len(calls) == 1
    assert calls[0][0] == ["/usr/bin/security", "find-generic-password", "-s", "pm-goldfinger-deepseek", "-w"]
    assert calls[0][1]["stderr"] is subprocess.DEVNULL
    assert calls[0][1]["timeout"] == 5
    output = capsys.readouterr()
    assert not output.out and not output.err


@pytest.mark.parametrize("failure", ["missing", "denied", "empty", "timeout", "unavailable"])
def test_unavailable_keychain_returns_no_key_without_logging(monkeypatch, capsys, failure):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr(credentials.sys, "platform", "darwin")

    def keychain(command, **kwargs):
        if failure == "timeout":
            raise subprocess.TimeoutExpired(command, 5, output="private-test-placeholder")
        if failure == "unavailable":
            raise FileNotFoundError("private-test-placeholder")
        return subprocess.CompletedProcess(command, {"missing": 44, "denied": 36, "empty": 0}[failure], stdout="")

    monkeypatch.setattr(credentials.subprocess, "run", keychain)
    assert credentials.read_api_key() is None
    output = capsys.readouterr()
    assert not output.out and not output.err


def test_non_macos_without_environment_does_not_run_security(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr(credentials.sys, "platform", "linux")
    monkeypatch.setattr(credentials.subprocess, "run", forbidden)
    assert credentials.read_api_key() is None
