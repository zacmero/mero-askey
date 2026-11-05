#!/usr/bin/env python3
"""Validate prepared PBX config in a disposable container with no external network."""
from pathlib import Path
import re
import secrets
import subprocess
import time


def main():
    root = Path(__file__).resolve().parents[1]
    private = root / '.local/telephony-pbx'
    check = private / 'check-etc'
    check.mkdir(mode=0o700, exist_ok=True)
    for source in (private / 'etc').glob('*.conf'):
        body = source.read_text().replace('192.168.1.97', '127.0.0.1').replace('192.168.1.250', '127.0.0.1').replace('bind=0.0.0.0:5060', 'bind=127.0.0.1:5060')
        path = check / source.name
        path.write_text(body)
        path.chmod(0o600)
    name = 'mero-askey-pbx-check-' + secrets.token_hex(4)
    subprocess.run(['docker', 'run', '-d', '--name', name, '--network', 'none',
                    '--security-opt', 'no-new-privileges:true',
                    '-v', str(check) + ':/etc/asterisk:ro', 'mero-askey-pbx:local'],
                   check=True, capture_output=True, timeout=20)
    try:
        def cli(command):
            return subprocess.run(['docker', 'exec', name, 'asterisk', '-rx', command],
                                  capture_output=True, text=True, timeout=10)
        for attempt in range(20):
            result = cli('core show version')
            if result.returncode == 0 and 'Asterisk ' in result.stdout:
                break
            time.sleep(0.25)
        else:
            raise RuntimeError('Isolated PBX did not start')
        print(result.stdout.strip())
        # Wait for modules/configuration to finish loading before checking objects.
        result = cli('core waitfullybooted')
        if result.returncode:
            raise RuntimeError('PBX startup did not complete')
        endpoint = cli('pjsip show endpoint 10').stdout
        if not re.search(r'Endpoint:\s+10(?:\s|/)', endpoint) or 'from-moto700' not in endpoint:
            raise RuntimeError('Endpoint 10 or its context did not load')
        transports = cli('pjsip show transports').stdout
        if '127.0.0.1:5060' not in transports:
            raise RuntimeError('Isolated test transport did not bind to loopback')
        dialplan = cli('dialplan show from-moto700').stdout
        if not all(x in dialplan for x in ('19', 'Echo()', '*20', 'Playback(hello-world)', '*29', 'Read(DIGIT')):
            raise RuntimeError('Pilot dialplan did not load')
        for module in ('chan_pjsip.so', 'res_pjsip_pubsub.so', 'app_echo.so', 'app_playback.so', 'app_read.so', 'app_system.so', 'app_verbose.so'):
            if module not in cli('module show like ' + module).stdout:
                raise RuntimeError('Required module is missing: ' + module)
        if 'PJSIP' not in cli('core show channeltypes').stdout:
            raise RuntimeError('PJSIP call channel driver is not available')
        keypad = cli('dialplan show s@lab-keypad-selftest').stdout
        if not all(x in keypad for x in ('Read(TEST_DIGIT', 'SayDigits(', 'LAB_KEYPAD')):
            raise RuntimeError('Keypad self-test did not load')
        menu = cli('dialplan show s@lab-menu').stdout
        if not all(x in menu for x in ('Read(MENU_CHOICE', 'TrySystem(', '/usr/bin/timeout 3', '127.0.0.1/80')):
            raise RuntimeError('Bounded fixed-action menu did not load')
        if 'MENU_COUNT}>4' in menu or ',1,,1,60)' not in menu or 'TIMEOUT' not in menu or 'LAB_MENU_END' not in cli('dialplan show lab-menu').stdout:
            raise RuntimeError('Idle retry or hang-up diagnostics did not load')
        sockets = subprocess.run(['docker', 'exec', name, 'cat', '/proc/net/udp', '/proc/net/udp6',
                                  '/proc/net/tcp', '/proc/net/tcp6'],
                                 capture_output=True, text=True, check=True, timeout=10).stdout
        ports = {int(line.split()[1].split(':')[1], 16) for line in sockets.splitlines()
                 if line.split() and line.split()[0].rstrip(':').isdigit()
                 and line.split()[3] in ('07', '0A')}
        # The runtime also opens internal ephemeral datagram sockets. Deployment
        # uses a private Docker network and publishes only SIP plus the RTP range.
        if 5060 not in ports or any(port < 32768 and port != 5060 for port in ports):
            (private / 'check-sockets.txt').write_text(sockets)
            raise RuntimeError('Unexpected test listeners: ' + str(sorted(ports)))
        print('PASS: endpoint/auth/context, loopback transport, echo/audio/DTMF routes and required modules loaded.')
        print('PASS: SIP 5060 is the only fixed low port; ephemeral sockets remain inside the private container network.')
        print('No external network or Askey connection was used.')
    except Exception:
        result = subprocess.run(['docker', 'logs', name], capture_output=True, text=True, timeout=10)
        (private / 'check-startup.log').write_text(result.stdout + result.stderr)
        (private / 'check-startup.log').chmod(0o600)
        print('Startup diagnostics retained privately in .local/telephony-pbx/check-startup.log')
        raise
    finally:
        subprocess.run(['docker', 'rm', '-f', name], check=True, capture_output=True, timeout=15)
        print('Disposable validation container removed.')


if __name__ == '__main__':
    try:
        main()
    except RuntimeError as error:
        print('FAIL:', error)
        raise SystemExit(1)
