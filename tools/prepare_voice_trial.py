#!/usr/bin/env python3
"""Prepare native voice-form proposal/rollback privately; sends no device request."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path


class VoiceForm(HTMLParser):
    def __init__(self):
        super().__init__()
        self.action = None
        self.fields = {}
        self.order = []
        self.select = None
        self.options = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'form':
            if self.action is not None:
                raise ValueError('Expected one native voice form')
            self.action = a.get('action')
        elif tag == 'input' and a.get('name') and 'disabled' not in a:
            self.order.append(a['name'])
            kind = a.get('type', 'text').lower()
            if kind in ('checkbox', 'radio') and 'checked' not in a:
                return
            if kind not in ('reset', 'button', 'file'):
                self.fields[a['name']] = a.get('value', 'on' if kind in ('checkbox', 'radio') else '')
        elif tag == 'select':
            self.select, self.options = a.get('name'), []
            if self.select:
                self.order.append(self.select)
        elif tag == 'option' and self.select:
            self.options.append((a.get('value', ''), 'selected' in a))

    def handle_endtag(self, tag):
        if tag == 'select' and self.select:
            selected = [value for value, marked in self.options if marked]
            self.fields[self.select] = selected[0] if selected else self.options[0][0]
            self.select = None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('audit_dir', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    audit = args.audit_dir.resolve()
    if not audit.is_relative_to(root / '.local/askey-voice-001'):
        raise ValueError('Use the retained private voice audit directory')
    summary = json.loads((audit / 'summary.json').read_text())
    safe = summary['safe_settings']
    if safe['VOIP.PORT[0].PROXIES[0].PROXY_ENABLE'] != '0' or any(summary['account_fields_present'].values()):
        raise ValueError('Existing voice account needs a new review; refusing to overwrite it')
    form = VoiceForm()
    form.feed((audit / 'voip_basic.htm').read_text())
    if form.action != 'form2VoipBasic.cgi' or form.fields.get('voipinterface') != 'any':
        raise ValueError('Native form differs from the inspected baseline')
    account = json.loads((root / '.local/telephony-pbx/account.json').read_text())
    before = dict(form.fields)
    changes = {'voipinterface': 'br0', 'sip0_enable': 'on',
               'sip0_number': account['extension'], 'sip0_login_id': account['extension'],
               'sip0_password': account['password'], 'proxy0_addr': account['server']}
    if not set(changes).difference({'voipinterface', 'sip0_enable'}).issubset(form.fields):
        raise ValueError('Expected native first-account controls are missing')
    after = dict(before, **changes)
    proposal = {'router': summary['router'], 'action': form.action,
                'baseline_export_sha256': summary['artifact_sha256']['config-current.img'],
                'before': before, 'after': after}
    path = audit / 'voice-form-proposal.json'
    path.write_text(json.dumps(proposal, indent=2) + '\n')
    path.chmod(0o600)
    print('Prepared only; no device request was sent.')
    for key, value in changes.items():
        print(key + ': ' + ('<new private lab password>' if key.endswith('password') else value))
    print('Other native form fields preserved, including second-account controls.')
    print('Private proposal and original form values:', path)


if __name__ == '__main__':
    main()
