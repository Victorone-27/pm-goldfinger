#!/usr/bin/env python3
"""Own one macOS test-browser process; reject daily Chrome and unverified CDP."""

import argparse
import json
import os
from pathlib import Path
import plistlib
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit
from urllib.request import urlopen


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def command(args):
    return subprocess.run(args, capture_output=True, text=True, check=False)


def approved_binary(value):
    binary = Path(value).resolve(strict=True)
    app = next((p for p in binary.parents if p.suffix == '.app'), None)
    require(app is not None, 'Expected a Chrome for Testing or Chromium macOS app')
    allowed = {'Google Chrome for Testing.app': 'com.google.chrome.for.testing',
               'Chromium.app': 'org.chromium.Chromium'}
    require(app.name in allowed, 'Daily Google Chrome and other browsers are forbidden')
    with (app / 'Contents/Info.plist').open('rb') as handle:
        info = plistlib.load(handle)
    require(info.get('CFBundleIdentifier') == allowed[app.name], 'Bundle identity mismatch')
    require(binary == app / 'Contents/MacOS' / info['CFBundleExecutable'],
            'Executable does not match the approved application bundle')
    require(os.access(binary, os.X_OK), 'Browser is not executable')
    return binary, info


def process_identity(pid):
    result = command(['/bin/ps', '-p', str(pid), '-o', 'lstart=', '-o', 'command='])
    require(result.returncode == 0 and result.stdout.strip(), 'Owned browser process is absent')
    return result.stdout.strip()


def listeners(pid):
    result = command(['/usr/sbin/lsof', '-nP', '-a', '-p', str(pid),
                      '-iTCP', '-sTCP:LISTEN', '-Fn'])
    return [line[1:] for line in result.stdout.splitlines() if line.startswith('n')]


def verify(state):
    binary, _ = approved_binary(state['binary'])
    endpoint = urlsplit(state['endpoint'])
    require(endpoint.scheme == 'http' and endpoint.hostname == '127.0.0.1'
            and endpoint.port and endpoint.path in ('', '/') and not endpoint.query
            and not endpoint.fragment and not endpoint.username and not endpoint.password,
            'CDP must use an explicit port on literal 127.0.0.1')
    identity = process_identity(state['pid'])
    require(identity == state['process_identity'], 'Owned PID identity changed')
    require(str(binary) in identity and f"--user-data-dir={state['profile']}" in identity,
            'Process executable/profile mismatch')
    require(os.getpgid(state['pid']) == state['pid'], 'Unexpected process group')
    require(listeners(state['pid']) == [f'127.0.0.1:{endpoint.port}'],
            'Listener is absent, non-loopback, or ambiguous')
    # Only now connect, after process and listener ownership are established.
    with urlopen(state['endpoint'] + '/json/version', timeout=3) as response:
        version = json.load(response)
    websocket = urlsplit(version['webSocketDebuggerUrl'])
    require(websocket.scheme == 'ws' and websocket.hostname == '127.0.0.1'
            and websocket.port == endpoint.port, 'Unexpected debugger WebSocket authority')
    return {'verified': True, 'endpoint': state['endpoint'], 'pid': state['pid'],
            'bundle_id': state['bundle_id'], 'browser_version': version['Browser']}


def launch(args):
    binary, info = approved_binary(args.binary)
    state_file = Path(args.state).resolve()
    require(not state_file.exists(), 'State file exists; verify/stop it before launching again')
    runs = Path(args.runs).resolve()
    runs.mkdir(parents=True, exist_ok=True)
    profile = Path(tempfile.mkdtemp(prefix='teardown-', dir=runs))
    proc = None
    try:
        argv = [str(binary), f'--user-data-dir={profile}', '--headless=new',
                '--remote-debugging-address=127.0.0.1', '--remote-debugging-port=0',
                '--no-first-run', '--no-default-browser-check', '--disable-sync',
                '--disable-extensions', '--window-size=1440,1000', 'about:blank']
        proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, start_new_session=True)
        active_port = profile / 'DevToolsActivePort'
        deadline = time.monotonic() + 20
        while not active_port.exists() and time.monotonic() < deadline:
            require(proc.poll() is None, 'Test browser exited during startup')
            time.sleep(0.1)
        require(active_port.exists(), 'Test browser did not expose an owned debug port')
        port = int(active_port.read_text().splitlines()[0])
        state = {'pid': proc.pid, 'binary': str(binary), 'profile': str(profile),
                 'bundle_id': info['CFBundleIdentifier'],
                 'endpoint': f'http://127.0.0.1:{port}',
                 'process_identity': process_identity(proc.pid)}
        checked = verify(state)
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(state, indent=2) + '\n')
        state_file.chmod(0o600)
        return checked
    except BaseException:
        if proc is not None and proc.poll() is None:
            os.killpg(proc.pid, signal.SIGTERM)
            proc.wait(timeout=10)
        shutil.rmtree(profile)
        raise


def stop(state, state_file):
    checked = verify(state)
    os.killpg(state['pid'], signal.SIGTERM)
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        group = command(['/usr/bin/pgrep', '-g', str(state['pid'])])
        if group.returncode == 1:
            break
        time.sleep(0.1)
    require(group.returncode == 1, 'Owned browser group still running; profile retained')
    port = urlsplit(state['endpoint']).port
    result = command(['/usr/sbin/lsof', '-nP', f'-iTCP:{port}', '-sTCP:LISTEN'])
    require(result.returncode == 1 and not result.stdout, 'Debug port still listening')
    shutil.rmtree(state['profile'])
    Path(state_file).unlink()
    return {**checked, 'stopped': True, 'listener_closed': True, 'profile_deleted': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['launch', 'verify', 'stop'])
    parser.add_argument('--state', required=True)
    parser.add_argument('--binary')
    parser.add_argument('--runs')
    args = parser.parse_args()
    if args.action == 'launch':
        require(args.binary and args.runs, 'launch requires --binary and --runs')
        result = launch(args)
    else:
        state = json.loads(Path(args.state).read_text())
        result = verify(state) if args.action == 'verify' else stop(state, args.state)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Isolation check failed: {exc}', file=sys.stderr)
        sys.exit(1)
