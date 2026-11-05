"""Regression check: newly checked controls must precede the native dispatch key."""
from urllib.parse import urlencode, parse_qsl
from prepare_voice_trial import VoiceForm


def test_browser_control_order():
    parser = VoiceForm()
    parser.feed('''<form action="form2VoipBasic.cgi">
<select name="voipinterface"><option value="any" selected>Any</option><option value="br0">LAN</option></select>
<input type="checkbox" name="sip0_enable">
<input name="sip0_number" value="">
<input type="checkbox" name="proxy1_Enable">
<input type="hidden" name="submit.htm?voip_basic.htm" value="fresh-session-key">
</form>''')
    assert 'sip0_enable' not in parser.fields
    assert 'proxy1_Enable' not in parser.fields
    assert parser.fields['voipinterface'] == 'any'
    fields = dict(parser.fields, sip0_enable='on', sip0_number='10', voipinterface='br0')
    ordered = {name: fields[name] for name in parser.order if name in fields}
    submitted = parse_qsl(urlencode(ordered), keep_blank_values=True)
    names = [name for name, value in submitted]
    assert names.index('sip0_enable') < names.index('sip0_number')
    assert names[-1] == 'submit.htm?voip_basic.htm'
    assert dict(submitted)['sip0_enable'] == 'on'
    assert 'proxy1_Enable' not in dict(submitted)


if __name__ == '__main__':
    test_browser_control_order()
    print('PASS: checkbox presence, native DOM order and final dispatch marker')
