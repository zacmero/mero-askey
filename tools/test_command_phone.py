"""Check target selection and FastAGI authorization without changing displays."""
from command_phone import authorized, bravia
from command_phone import ACCOUNT
import json
import subprocess
import sys


def test_dispatch_guards():
    monitors = [{'name': 'HDMI-A-1', 'make': 'LG', 'model': '23MP55', 'focused': True},
                {'name': 'DP-1', 'make': 'Sony', 'model': 'SONY TV', 'focused': False}]
    assert bravia(monitors) == 'DP-1'
    try:
        bravia(monitors + [dict(monitors[1], name='DP-9')])
    except RuntimeError:
        pass
    else:
        raise AssertionError('Ambiguous physical target must fail')
    config = {'peer': '172.21.0.2', 'token': 'test-token'}
    assert authorized(config, config['peer'], 'agi://172.21.0.1:4573/test-token/cinema_on')
    assert not authorized(config, '192.168.1.9', 'agi://172.21.0.1:4573/test-token/cinema_on')
    assert not authorized(config, config['peer'], 'agi://172.21.0.1:4573/wrong/cinema_on')
    assert not authorized(config, config['peer'], 'agi://172.21.0.1:4573/test-token/arbitrary-command')


if __name__ == '__main__':
    test_dispatch_guards()
    print('PASS: explicit Bravia targeting, peer/token checks and fixed command names')
    if '--live' in sys.argv:
        config = json.loads(ACCOUNT.read_text())
        # Token travels in private stdin, never in command arguments or stdout.
        script = ('exec 3<>/dev/tcp/' + config['bind'] + '/' + str(config['port']) + '\n'
                  + "printf '%s\\n\\n' 'agi_request: agi://" + config['bind'] + ':' + str(config['port'])
                  + '/' + config['token'] + "/cinema_status' >&3\n"
                  + "IFS= read -r reply <&3\nprintf '200 result=1\\n' >&3\nprintf '%s\\n' \"$reply\"\n")
        result = subprocess.run(['docker', 'exec', '-i', 'mero-askey-pbx', 'timeout', '8', 'bash'],
                                input=script, text=True, capture_output=True, timeout=12, check=True)
        assert result.stdout.strip() in ('SET VARIABLE PHONE_COMMAND_RESULT "on"', 'SET VARIABLE PHONE_COMMAND_RESULT "off"')
        print('PASS: authenticated PBX-to-user-worker status request; no display changes')
