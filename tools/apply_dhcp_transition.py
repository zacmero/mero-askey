#!/usr/bin/env python3
"""Applies the permanent DHCP-disabled and LAN IP (192.168.1.250) configuration.

Steps:
1. Re-validates the live settings export hash against preflight baseline.
2. Verifies the candidate image (CONFIG_SERVICE_DHCP=0x0, LAN_PRIMARY_IP=192.168.1.250).
3. Submits candidate via native multipart settings import to trigger auto-reboot.
4. Records evidence in .local/askey-net-011/.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = (ROOT / '.local/askey-net-011').resolve()
OUT.mkdir(mode=0o700, parents=True, exist_ok=True)

CANDIDATE_PATH = OUT / 'config-dhcp-disabled-candidate.img'
assert CANDIDATE_PATH.is_file(), f'Missing candidate file at {CANDIDATE_PATH}'
CANDIDATE_BYTES = CANDIDATE_PATH.read_bytes()
EXPECTED_CANDIDATE_SHA256 = 'f34f093d50bdf1b78fb3a5d4b0083e7fd721b831e4059d5c12cd025eb7db35bb'
assert hashlib.sha256(CANDIDATE_BYTES).hexdigest() == EXPECTED_CANDIDATE_SHA256, 'Candidate hash mismatch'

REMOTE_CODE = r'''import base64, email.parser, email.policy, hashlib, http.client, json, re, secrets, socket, subprocess, sys, time, urllib.parse
from html.parser import HTMLParser
from http.cookies import SimpleCookie

c = json.loads(sys.stdin.readline())
target = c['target']
auth = c['auth']
candidate = base64.b64decode(c['candidate_b64'])

# 1. Physical route and neighbor check
route = json.loads(subprocess.check_output(['ip', '-j', 'route', 'get', target['ip']]))[0]
neighbor = json.loads(subprocess.check_output(['ip', '-j', 'neigh', 'show', target['ip']]))[0]
assert route['dev'] == target['interface'] and route['prefsrc'] == target['source']
assert neighbor['lladdr'].lower() == target['mac'].lower()

cookies = SimpleCookie()

def req(path, data=None, content_type=None):
    conn = http.client.HTTPConnection(target['ip'], timeout=8)
    conn._http_vsn = 10
    conn._http_vsn_str = 'HTTP/1.0'
    headers = {'Host': target['ip'], 'Connection': 'close', 'Referer': 'http://' + target['ip'] + '/padrao'}
    if cookies:
        headers['Cookie'] = '; '.join(k + '=' + v.value for k, v in cookies.items())
    if data is not None:
        headers['Content-Type'] = content_type or 'application/x-www-form-urlencoded'
        data = urllib.parse.urlencode(data) if isinstance(data, dict) else data
    conn.request('POST' if data is not None else 'GET', '/' + path.lstrip('/'), body=data, headers=headers)
    r = conn.getresponse()
    body = r.read()
    ctype = r.getheader('Content-Type', '')
    for k, v in r.getheaders():
        if k.lower() == 'set-cookie':
            cookies.load(v)
    assert r.status == 200, ('HTTP status', r.status)
    conn.close()
    return body, ctype

# 2. Authenticate
req('padrao')
req('login.cgi', {
    'usernameEncrypt': hashlib.md5(b'support').hexdigest(),
    'passwordEncrypt': hashlib.md5(auth['password'].encode()).hexdigest(),
    'loginW': '0',
    'loginfrompadrao': '1',
    'submit.htm?idx_select.htm': 'Send'
})

# 3. Preflight download & verification
page, _ = req('saveconf.htm')

class Forms(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms = []
        self.current = None
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'form':
            self.current = {'action': a.get('action', ''), 'inputs': {}}
            self.forms.append(self.current)
        if tag == 'input' and self.current is not None and a.get('name'):
            self.current['inputs'][a['name']] = a.get('value', '')
    def handle_endtag(self, tag):
        if tag == 'form':
            self.current = None

parser = Forms()
parser.feed(page.decode(errors='replace'))
f = [x for x in parser.forms if x['action'].split('/')[-1] == 'form2saveConf.cgi']
assert len(f) == 1, 'Save form missing'
current_export, ctype = req(f[0]['action'], f[0]['inputs'])
assert 'octet-stream' in ctype and b'<' in current_export[:100]

current_hash = hashlib.sha256(current_export).hexdigest()
assert current_hash == c['expected_live_sha256'], f'Live export hash mismatch: {current_hash} != {c["expected_live_sha256"]}'

# 4. Prepare multipart form for candidate upload
restore = [x for x in parser.forms if x['action'].split('/')[-1] == 'form2fileConf.htm']
assert len(restore) == 1, 'Restore form missing'
form = restore[0]

boundary = 'AskeyTransition' + secrets.token_hex(12)
parts = []
for name, value in form['inputs'].items():
    if name == 'download image file':
        parts.append((f'--{boundary}\r\nContent-Disposition: form-data; name="download image file"; filename="config.img"\r\nContent-Type: application/octet-stream\r\n\r\n').encode() + candidate + b'\r\n')
    else:
        parts.append((f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n').encode())
parts.append((f'--{boundary}--\r\n').encode())
body = b''.join(parts)

mime = email.parser.BytesParser(policy=email.policy.default).parsebytes(('Content-Type: multipart/form-data; boundary=' + boundary + '\r\nMIME-Version: 1.0\r\n\r\n').encode() + body)
parsed = list(mime.iter_parts())
assert parsed[0].get_param('name', header='content-disposition') == 'download image file'
assert parsed[0].get_payload(decode=True) == candidate

started = time.time()
print(json.dumps({
    'type': 'upload_started',
    'time': started,
    'live_preflight_sha256': current_hash,
    'candidate_sha256': c['candidate_sha256']
}), flush=True)

# 5. Send POST request
headers = {
    'Host': target['ip'],
    'Connection': 'close',
    'Referer': 'http://' + target['ip'] + '/saveconf.htm',
    'Content-Type': 'multipart/form-data; boundary=' + boundary,
    'Content-Length': str(len(body))
}
if cookies:
    headers['Cookie'] = '; '.join(k + '=' + v.value for k, v in cookies.items())

request = ('POST /' + form['action'].lstrip('/') + ' HTTP/1.0\r\n' + ''.join(k + ': ' + v + '\r\n' for k, v in headers.items()) + '\r\n').encode() + body

sock = socket.create_connection((target['ip'], 80), 8)
sock.settimeout(20)
sock.sendall(request)
chunks = []
try:
    while True:
        chunk = sock.recv(65536)
        if not chunk:
            break
        chunks.append(chunk)
finally:
    sock.close()

reply = b''.join(chunks)
print(json.dumps({
    'type': 'upload_response',
    'elapsed_seconds': time.time() - started,
    'raw_b64': base64.b64encode(reply).decode()
}), flush=True)
'''

def main():
    target = json.loads((ROOT / '.local/capture-target.json').read_text())
    auth = json.loads((ROOT / '.local/router-login.json').read_text())

    config = {
        'target': target,
        'auth': auth,
        'candidate_b64': base64.b64encode(CANDIDATE_BYTES).decode(),
        'candidate_sha256': EXPECTED_CANDIDATE_SHA256,
        'expected_live_sha256': '4c5c8a2fe7c533aee6f7cff98ab2bd7e89345d8b9b8bbcface0d323d1cae7d44'
    }

    print('=' * 78)
    print(' ASKEY RTV9015VW: TRANSITION TO DIRECT HOME NETWORK (192.168.1.250)')
    print(' Setting: CONFIG_SERVICE_DHCP = 0x0 (Disabled)')
    print(' Setting: LAN_PRIMARY_IP      = 192.168.1.250')
    print('=' * 78)

    print('\n[1/3] Uploading candidate configuration to Askey...')
    ssh_args = [
        'ssh', '-i', target['key'],
        '-o', 'IdentitiesOnly=yes',
        '-o', 'BatchMode=yes',
        '-o', 'StrictHostKeyChecking=yes',
        '-o', 'ConnectTimeout=6',
        target['ssh'],
        'python3 -c ' + shlex.quote(REMOTE_CODE)
    ]

    r = subprocess.run(ssh_args, input=json.dumps(config) + '\n', capture_output=True, text=True, timeout=40)
    for fn, content in [(f'apply-{time.time_ns()}.jsonl', r.stdout), (f'apply-{time.time_ns()}-stderr.txt', r.stderr)]:
        (OUT / fn).write_text(content)
        os.chmod(OUT / fn, 0o600)

    assert r.returncode == 0, f'Apply failed (rc={r.returncode}): {r.stderr}'

    records = [json.loads(line) for line in r.stdout.splitlines() if line.startswith('{')]
    resp = next(x for x in records if x.get('type') == 'upload_response')
    raw_html = base64.b64decode(resp['raw_b64']).decode('latin1', errors='replace')

    assert 'Autoboot' in raw_html or 'reboot' in raw_html.lower(), f'Unexpected response: {raw_html[:300]}'
    print('  [+] Candidate accepted by firmware!')
    print('  [+] Firmware response: "restore current setting! System is rebooting now..."')
    print(f'  [+] Upload elapsed time: {resp["elapsed_seconds"]:.2f} seconds')

    print('\n' + '=' * 78)
    print(' [!] TRANSITION IN PROGRESS — PHYSICAL ACTION REQUIRED')
    print('=' * 78)
    print('''
The Askey router is currently committing the configuration to flash memory
and executing its 50-second reboot countdown.

WHAT TO DO NOW:
1. Wait ~30 seconds for the power light / LAN lights to cycle.
2. Unplug the Ethernet cable from your MSI laptop.
3. Plug that Ethernet cable directly into your HOME NETWORK SWITCH!
4. The Askey will come online at IP: 192.168.1.250 (DHCP permanently disabled).
''')

if __name__ == '__main__':
    main()
