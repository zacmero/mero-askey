#!/usr/bin/env python3
"""Read-only voice audit: authenticate, export settings, and GET known voice pages.

Never imports settings, submits a voice form, restarts a service or starts a PBX.
Raw pages/settings remain in ignored .local/; stdout contains only a safe summary.
"""
import argparse
import hashlib
from html.parser import HTMLParser
from http.client import HTTPConnection
from http.cookies import SimpleCookie
import json
import os
from pathlib import Path
import subprocess
import time
from urllib.parse import urlencode
import xml.etree.ElementTree as ET


class Forms(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'form':
            self.current = {'action': attrs.get('action', ''), 'inputs': {}}
            self.forms.append(self.current)
        elif tag == 'input' and self.current is not None and attrs.get('name'):
            self.current['inputs'][attrs['name']] = attrs.get('value', '')

    def handle_endtag(self, tag):
        if tag == 'form':
            self.current = None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ip', default='192.168.1.250')
    parser.add_argument('--interface', default='enp5s0')
    parser.add_argument('--source', default='192.168.1.97')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    target = json.loads((root / '.local/capture-target.json').read_text())
    auth = json.loads((root / '.local/router-login.json').read_text())
    route = json.loads(subprocess.check_output(['ip', '-j', 'route', 'get', args.ip]))[0]
    neighbors = json.loads(subprocess.check_output(['ip', '-j', 'neigh', 'show', args.ip]))
    if route.get('dev') != args.interface or route.get('prefsrc') != args.source:
        raise RuntimeError('Route differs from the reviewed lab path')
    if not any(n.get('dev') == args.interface and n.get('lladdr', '').lower() == target['mac'].lower() for n in neighbors):
        raise RuntimeError('Target neighbor identity is not verified')
    out = root / '.local/askey-voice-001' / str(time.time_ns())
    out.mkdir(mode=0o700, parents=True)
    cookies = SimpleCookie()
    hashes = {}

    def request(path, data=None):
        allowed_get = {'padrao', 'saveconf.htm', 'voip_status.htm', 'voip_basic.htm', 'voip_advanced.htm'}
        allowed_post = {'login.cgi', 'form2saveConf.cgi'}
        if path not in (allowed_post if data is not None else allowed_get):
            raise RuntimeError('Request outside the read-only audit allowlist')
        conn = HTTPConnection(args.ip, timeout=8)
        conn._http_vsn, conn._http_vsn_str = 10, 'HTTP/1.0'
        headers = {'Connection': 'close', 'Referer': 'http://' + args.ip + '/padrao'}
        if cookies:
            headers['Cookie'] = '; '.join(k + '=' + v.value for k, v in cookies.items())
        if data is not None:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        try:
            conn.request('POST' if data is not None else 'GET', '/' + path, urlencode(data) if data is not None else None, headers)
            response = conn.getresponse()
            body = response.read(1024 * 1024 + 1)
            if response.status != 200 or len(body) > 1024 * 1024:
                raise RuntimeError('Unexpected HTTP response status/size')
            for key, value in response.getheaders():
                if key.lower() == 'set-cookie':
                    cookies.load(value)
            return body
        finally:
            conn.close()

    def retain(name, body):
        path = out / name
        path.write_bytes(body)
        os.chmod(path, 0o600)
        hashes[name] = hashlib.sha256(body).hexdigest()

    request('padrao')
    request('login.cgi', {'usernameEncrypt': hashlib.md5(b'support').hexdigest(),
                         'passwordEncrypt': hashlib.md5(auth['password'].encode()).hexdigest(),
                         'loginW': '0', 'loginfrompadrao': '1', 'submit.htm?idx_select.htm': 'Send'})
    page = request('saveconf.htm')
    forms = Forms()
    forms.feed(page.decode(errors='replace'))
    downloads = [f for f in forms.forms if f['action'].lstrip('/') == 'form2saveConf.cgi']
    if len(downloads) != 1:
        raise RuntimeError('Authenticated native export form was not found')
    export = request('form2saveConf.cgi', downloads[0]['inputs'])
    config = ET.fromstring(export)
    if config.tag != 'Config_Information_File_8671':
        raise RuntimeError('Unexpected settings container')
    retain('config-current.img', export)
    values = {e.get('N'): e.get('V', '') for e in config.iter('V')}
    safe = ['LAN_PRIMARY_IP', 'CONFIG_SERVICE_DHCP', 'VOIP.INTERFACE',
            'VOIP.PORT[0].SIP_PORT', 'VOIP.PORT[0].MEDIA_PORT', 'VOIP.PORT[0].DTMF_MODE',
            'VOIP.PORT[0].PROXIES[0].PROXY_ENABLE', 'VOIP.PORT[0].PROXIES[0].PROXY_PORT',
            'VOIP.PORT[0].PROXIES[0].PROXY_REGISTRARSERVER_PORT', 'VOIP.WAN_VLAN_ENABLE']
    private = ['PROXY_ADDR', 'PROXY_REGISTRARSERVER_ADDR', 'PROXY_LOGIN_ID', 'PROXY_PASSWORD']
    summary = {'observed_unix': time.time(), 'router': args.ip, 'source': args.source,
               'safe_settings': {k: values.get(k, '<absent>') for k in safe},
               'account_fields_present': {k: bool(values.get('VOIP.PORT[0].PROXIES[0].' + k)) for k in private}}
    for name in ('voip_status.htm', 'voip_basic.htm', 'voip_advanced.htm'):
        body = request(name)
        retain(name, body)
        forms = Forms()
        forms.feed(body.decode(errors='replace'))
        summary[name] = [{'action': f['action'], 'input_names': sorted(f['inputs'])} for f in forms.forms]
    summary['artifact_sha256'] = hashes
    retain('summary.json', (json.dumps(summary, indent=2) + '\n').encode())
    cookies.clear()
    print(json.dumps(summary, indent=2))
    print('Private evidence:', out)


if __name__ == '__main__':
    main()
