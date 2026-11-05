#!/usr/bin/env python3
"""Apply or restore the reviewed native voice form; no settings import or reboot command.

Requires operation-specific owner approval. Fresh export must match the proposal
before apply. Request/response/settings evidence remains private.
"""
import argparse
import hashlib
from http.client import HTTPConnection
from http.cookies import SimpleCookie
import json
from pathlib import Path
import subprocess
import time
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

from inspect_telephony import Forms
from prepare_voice_trial import VoiceForm


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['apply', 'rollback'])
    parser.add_argument('proposal', type=Path)
    parser.add_argument('--resume-reviewed', action='store_true', help='Continue only if partial state contains the same approved lab identity and voice fields')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    proposal_path = args.proposal.resolve()
    if not proposal_path.is_relative_to(root / '.local/askey-voice-001'):
        raise ValueError('Proposal must be private audit evidence')
    proposal = json.loads(proposal_path.read_text())
    if proposal['router'] != '192.168.1.250' or proposal['action'] != 'form2VoipBasic.cgi':
        raise ValueError('Unexpected proposal target or action')
    target = json.loads((root / '.local/capture-target.json').read_text())
    auth = json.loads((root / '.local/router-login.json').read_text())
    route = json.loads(subprocess.check_output(['ip', '-j', 'route', 'get', proposal['router']]))[0]
    neighbors = json.loads(subprocess.check_output(['ip', '-j', 'neigh', 'show', proposal['router']]))
    if route.get('dev') != 'enp5s0' or route.get('prefsrc') != '192.168.1.97':
        raise RuntimeError('Lab route changed')
    if not any(n.get('dev') == 'enp5s0' and n.get('lladdr', '').lower() == target['mac'].lower() for n in neighbors):
        raise RuntimeError('Router identity not verified')
    out = proposal_path.parent / (args.operation + '-' + str(time.time_ns()))
    out.mkdir(mode=0o700)
    cookies = SimpleCookie()

    def save(name, data):
        path = out / name
        path.write_bytes(data)
        path.chmod(0o600)

    def request(path, data=None):
        if path not in {'padrao', 'login.cgi', 'saveconf.htm', 'voip_basic.htm', 'form2saveConf.cgi', 'form2VoipBasic.cgi'}:
            raise ValueError('Request outside voice trial allowlist')
        connection = HTTPConnection(proposal['router'], timeout=12)
        connection._http_vsn, connection._http_vsn_str = 10, 'HTTP/1.0'
        headers = {'Connection': 'close', 'Referer': 'http://' + proposal['router'] + '/voip_basic.htm'}
        if cookies:
            headers['Cookie'] = '; '.join(k + '=' + v.value for k, v in cookies.items())
        if data is not None:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        try:
            connection.request('GET' if data is None else 'POST', '/' + path,
                               urlencode(data) if data is not None else None, headers)
            response = connection.getresponse()
            body = response.read(1024 * 1024 + 1)
            if path == 'form2VoipBasic.cgi':
                save('native-response.html', body)
                save('native-response-status.json', json.dumps({'status': response.status,
                                                              'location': response.getheader('Location')}).encode())
            if response.status not in ((200, 301, 302, 303) if path == 'form2VoipBasic.cgi' else (200,)) or len(body) > 1024 * 1024:
                raise RuntimeError('Unexpected HTTP response status: ' + str(response.status))
            for key, value in response.getheaders():
                if key.lower() == 'set-cookie':
                    cookies.load(value)
            return body
        finally:
            connection.close()

    def export():
        form = Forms()
        form.feed(request('saveconf.htm').decode(errors='replace'))
        matches = [f for f in form.forms if f['action'].lstrip('/') == 'form2saveConf.cgi']
        if len(matches) != 1:
            raise RuntimeError('Authenticated export form missing')
        data = request('form2saveConf.cgi', matches[0]['inputs'])
        if ET.fromstring(data).tag != 'Config_Information_File_8671':
            raise RuntimeError('Unexpected settings export')
        return data

    request('padrao')
    request('login.cgi', {'usernameEncrypt': hashlib.md5(b'support').hexdigest(),
                         'passwordEncrypt': hashlib.md5(auth['password'].encode()).hexdigest(),
                         'loginW': '0', 'loginfrompadrao': '1', 'submit.htm?idx_select.htm': 'Send'})
    before = export()
    save('config-before.img', before)
    if args.operation == 'apply' and hashlib.sha256(before).hexdigest() != proposal['baseline_export_sha256']:
        if not args.resume_reviewed:
            raise RuntimeError('Baseline changed; proposal requires review before applying')
        def vals(raw):
            return {e.get('N'): e.get('V', '') for e in ET.fromstring(raw).iter('V')}
        original = vals(proposal_path.with_name('config-current.img').read_bytes())
        current = vals(before)
        line = 'VOIP.PORT[0].PROXIES['
        identities = {'PROXY_DISPLAY_NAME': proposal['after']['sip0_number'],
                      'PROXY_NUMBER': proposal['after']['sip0_number'],
                      'PROXY_LOGIN_ID': proposal['after']['sip0_login_id'],
                      'PROXY_PASSWORD': proposal['after']['sip0_password']}
        permitted = {line + str(i) + '].' + field: value for i in (0, 1) for field, value in identities.items()}
        permitted['VOIP.INTERFACE'] = proposal['after']['voipinterface']
        permitted[line + '0].PROXY_ADDR'] = proposal['after']['proxy0_addr']
        for key in original.keys() | current.keys():
            if original.get(key) != current.get(key) and (key not in permitted or current.get(key) != permitted[key]):
                raise RuntimeError('Partial state differs from approved lab values: ' + str(key))
    fields = dict(proposal['after' if args.operation == 'apply' else 'before'])
    # CSRF keys must come from this authenticated session, not archived HTML.
    fresh_form = VoiceForm()
    fresh_page = request('voip_basic.htm')
    save('native-form-before.html', fresh_page)
    fresh_form.feed(fresh_page.decode(errors='replace'))
    if fresh_form.action != proposal['action']:
        raise RuntimeError('Live native voice form differs from reviewed action')
    csrf = 'submit.htm?voip_basic.htm'
    if csrf not in fresh_form.fields:
        raise RuntimeError('Fresh native voice CSRF field missing')
    fields[csrf] = fresh_form.fields[csrf]
    # Preserve browser DOM order, including the final dispatch/CSRF marker.
    # A newly checked field must not be appended after that marker.
    if not set(fields).issubset(fresh_form.order):
        raise RuntimeError('Proposal contains controls absent from live native form')
    fields = {name: fields[name] for name in fresh_form.order if name in fields}
    # Record intent before the one settings submission. Never repeat after timeout.
    save('operation.json', json.dumps({'operation': args.operation, 'started_unix': time.time(),
                                     'action': proposal['action']}).encode())
    result = request(proposal['action'], fields)
    save('native-response.html', result)
    time.sleep(2)
    after = export()
    save('config-after.img', after)

    def values(raw):
        return {e.get('N'): e.get('V', '') for e in ET.fromstring(raw).iter('V')}

    old, new = values(before), values(after)
    changed = sorted(k for k in old.keys() | new.keys() if old.get(k) != new.get(k))
    summary = {'operation': args.operation, 'before_sha256': hashlib.sha256(before).hexdigest(),
               'after_sha256': hashlib.sha256(after).hexdigest(), 'changed_field_names': changed,
               'voice_interface': new.get('VOIP.INTERFACE'),
               'proxy0_enable': new.get('VOIP.PORT[0].PROXIES[0].PROXY_ENABLE'),
               'lan_ip': new.get('LAN_PRIMARY_IP'), 'dhcp': new.get('CONFIG_SERVICE_DHCP')}
    save('summary.json', (json.dumps(summary, indent=2) + '\n').encode())
    cookies.clear()
    print(json.dumps(summary, indent=2))
    print('Private evidence:', out)
    allowed = {'VOIP.INTERFACE'} | {'VOIP.PORT[0].PROXIES[0].' + field for field in
                                  ('PROXY_ADDR', 'PROXY_ENABLE', 'PROXY_DISPLAY_NAME',
                                   'PROXY_NUMBER', 'PROXY_LOGIN_ID', 'PROXY_PASSWORD')}
    # The native form shares one line identity between its main/backup proxies.
    allowed |= {'VOIP.PORT[0].PROXIES[1].' + field for field in
                ('PROXY_DISPLAY_NAME', 'PROXY_NUMBER', 'PROXY_LOGIN_ID', 'PROXY_PASSWORD')}
    if not set(changed).issubset(allowed):
        raise RuntimeError('Additional changed fields recorded; inspect evidence before further action')
    if args.operation == 'apply' and (new.get('VOIP.INTERFACE') != 'br0' or new.get('VOIP.PORT[0].PROXIES[0].PROXY_ENABLE') == '0'):
        raise RuntimeError('Requested voice state was not observed; do not repeat blindly')


if __name__ == '__main__':
    try:
        main()
    except RuntimeError as error:
        print('FAIL:', error)
        raise SystemExit(1)
