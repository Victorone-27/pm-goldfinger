import subprocess

import pytest


@pytest.fixture(autouse=True)
def block_real_keychain_access(monkeypatch):
    original_run = subprocess.run

    def guarded_run(command, *args, **kwargs):
        if isinstance(command, (list, tuple)) and command and command[0] == "/usr/bin/security":
            raise AssertionError("Tests must mock Keychain access; never read a real key")
        return original_run(command, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", guarded_run)
