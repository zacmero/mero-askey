#!/usr/bin/env python3
"""Host-side allowlisted phone commands. No router configuration or arbitrary shell API."""
import argparse
import hmac
import json
import os
from pathlib import Path
import secrets
import socketserver
import subprocess
import threading
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ACCOUNT = ROOT / '.local/telephony-command/account.json'
CINEMA = Path.home() / '.config/archmeros/scripts/archmeros-cinema-mode.sh'
CINEMA_ACTIONS = {'cinema_on': 'enter', 'cinema_off': 'restore', 'cinema_status': 'status'}
LOCK = threading.Lock()


def capture(args, env=None):
    return subprocess.check_output(args, text=True, env=env, timeout=5)


def bravia(monitors):
    matches = [m for m in monitors if m.get('make') == 'Sony' and m.get('model') == 'SONY TV' and not m.get('disabled')]
    if len(matches) != 1:
        raise RuntimeError('Expected exactly one connected Sony TV; refusing a cursor-based fallback')
    return matches[0]['name']


def plan(name):
    if name not in CINEMA_ACTIONS:
        raise ValueError('This preview supports only cinema actions')
    env = os.environ.copy()
    instances = json.loads(capture(['hyprctl', '-j', 'instances']))
    if len(instances) != 1:
        raise RuntimeError('Expected one Hyprland session')
    env.update(HYPRLAND_INSTANCE_SIGNATURE=instances[0]['instance'],
               WAYLAND_DISPLAY=instances[0]['wl_socket'], XDG_RUNTIME_DIR=f'/run/user/{os.getuid()}')
    monitor = bravia(json.loads(capture(['hyprctl', '-j', 'monitors'], env)))
    args = [str(CINEMA), CINEMA_ACTIONS[name]]
    if name == 'cinema_on':
        args += ['--monitor', monitor]
    return args, env, monitor


def cinema(name):
    args, env, monitor = plan(name)
    before = json.loads(capture([str(CINEMA), 'status'], env))
    if name == 'cinema_on' and before.get('keep') and before['keep'] != monitor:
        raise RuntimeError('Cinema is already active on another display; restore it first')
    subprocess.run(args, env=env, check=True, capture_output=True, text=True, timeout=25)
    state = json.loads(capture([str(CINEMA), 'status'], env))
    active = state.get('keep') == monitor
    if name == 'cinema_on' and not active:
        raise RuntimeError('Bravia cinema state was not observed')
    if name == 'cinema_off' and state.get('keep'):
        raise RuntimeError('Cinema restoration did not complete')
    return 'on' if active else 'off'


# Add another explicitly named, argument-free function here for each new action.
# Neither command names nor arguments are evaluated as Python or shell text.
COMMANDS = {name: (lambda name=name: cinema(name)) for name in CINEMA_ACTIONS}


def execute(name):
    if name not in COMMANDS:
        raise ValueError('Unknown fixed phone command')
    with LOCK:
        return COMMANDS[name]()


def authorized(config, peer, request):
    parts = urlsplit(request).path.strip('/').split('/')
    return (peer == config['peer'] and len(parts) == 2
            and hmac.compare_digest(parts[0], config['token']) and parts[1] in COMMANDS)


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        config = self.server.config
        self.request.settimeout(5)
        if self.client_address[0] != config['peer']:
            return
        environment = {}
        for _ in range(80):
            line = self.rfile.readline(2048)
            if line in (b'\n', b'\r\n', b''):
                break
            key, _, value = line.decode('utf-8', 'replace').partition(':')
            environment[key] = value.strip()
        request = environment.get('agi_request', '')
        if not authorized(config, self.client_address[0], request):
            return
        action = urlsplit(request).path.strip('/').split('/')[1]
        result = 'failed'
        try:
            result = execute(action)
        except (RuntimeError, subprocess.SubprocessError, ValueError, OSError) as error:
            # Never log the authenticated URI/token or command output.
            print(json.dumps({'action': action, 'result': 'failed', 'error_type': type(error).__name__}), flush=True)
        else:
            print(json.dumps({'action': action, 'result': result}), flush=True)
        self.wfile.write(('SET VARIABLE PHONE_COMMAND_RESULT "' + result + '"\n').encode())
        self.wfile.flush()
        self.rfile.readline(2048)


def configure():
    networks = json.loads(capture(['docker', 'inspect', '--format', '{{json .NetworkSettings.Networks}}', 'mero-askey-pbx']))
    network = networks['telephony_default']
    ACCOUNT.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    config = json.loads(ACCOUNT.read_text()) if ACCOUNT.exists() else {'token': secrets.token_hex(32)}
    config.update(bind=network['Gateway'], peer=network['IPAddress'], port=4573)
    ACCOUNT.write_text(json.dumps(config, indent=2) + '\n')
    ACCOUNT.chmod(0o600)
    print('Configured private Docker-network FastAGI endpoint; token retained in', ACCOUNT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['configure', 'serve', 'list', 'plan', 'run'])
    parser.add_argument('action', nargs='?', choices=sorted(COMMANDS))
    args = parser.parse_args()
    if args.operation == 'configure':
        configure()
    elif args.operation == 'list':
        print(json.dumps(sorted(COMMANDS), indent=2))
    elif args.operation == 'plan':
        command, _, monitor = plan(args.action)
        print(json.dumps({'action': args.action, 'monitor': monitor, 'argv': command}, indent=2))
    elif args.operation == 'run':
        print(execute(args.action))
    else:
        config = json.loads(ACCOUNT.read_text())
        class Server(socketserver.ThreadingTCPServer):
            allow_reuse_address = True
            daemon_threads = True
        with Server((config['bind'], config['port']), Handler) as server:
            server.config = config
            print('Phone command worker listening on private Docker bridge', flush=True)
            server.serve_forever()


if __name__ == '__main__':
    main()
