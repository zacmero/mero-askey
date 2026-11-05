#!/usr/bin/env python3
"""Prepare private Asterisk pilot configs; does not start services or alter Askey."""
import json
import os
from pathlib import Path
import secrets


def main():
    root = Path(__file__).resolve().parents[1]
    out = root / '.local/telephony-pbx'
    out.mkdir(mode=0o700, parents=True, exist_ok=True)
    (out / 'sounds').mkdir(mode=0o700, exist_ok=True)
    account = out / 'account.json'
    if account.exists():
        credentials = json.loads(account.read_text())
    else:
        credentials = {'extension': '10', 'password': secrets.token_urlsafe(24),
                       'server': '192.168.1.97', 'phone': '192.168.1.250'}
        account.write_text(json.dumps(credentials, indent=2) + '\n')
        os.chmod(account, 0o600)
    if credentials['server'] != '192.168.1.97' or credentials['phone'] != '192.168.1.250':
        raise RuntimeError('Re-review the bind address and phone ACL before preparing configs')
    configs = {
        'pjsip.conf': '''[transport-lab]
type=transport
protocol=udp
bind=0.0.0.0:5060
external_signaling_address=192.168.1.97
external_media_address=192.168.1.97
local_net=127.0.0.0/8

[10]
type=endpoint
transport=transport-lab
context=from-moto700
disallow=all
allow=alaw,ulaw
auth=auth10
aors=10
direct_media=no
media_address=192.168.1.97
bind_rtp_to_media_address=no
force_rport=yes
rewrite_contact=yes
rtp_symmetric=yes
deny=0.0.0.0/0
permit=192.168.1.250/32

[auth10]
type=auth
auth_type=userpass
username=10
password=PASSWORD_PLACEHOLDER

[10]
type=aor
max_contacts=1
remove_existing=yes
'''.replace('PASSWORD_PLACEHOLDER', credentials['password']),
        'extensions.conf': '''[general]
static=yes
writeprotect=yes

[from-moto700]
exten => 19,1,Answer()
 same => n,Echo()
 same => n,Hangup()

exten => 10,1,Dial(PJSIP/10,20)
 same => n,Hangup()

exten => 20,1,Goto(lab-menu,s,1)

; This is a fixed audio test, not live service status.
exten => *20,1,Answer()
 same => n,Playback(hello-world)
 same => n,Hangup()

exten => *29,1,Answer()
 same => n,Read(DIGIT,beep,1,,1,5)
 same => n,SayDigits(${DIGIT})
 same => n,Hangup()

exten => i,1,Hangup()
exten => t,1,Hangup()

[lab-audio-selftest]
exten => s,1,Answer()
 same => n,Playback(beep)
 same => n,Record(/var/spool/asterisk/monitor/moto700-selftest-001.wav,0,6,q)
 same => n,Playback(/var/spool/asterisk/monitor/moto700-selftest-001)
 same => n,Hangup()

[lab-keypad-selftest]
exten => s,1,Answer()
 same => n,Read(TEST_DIGIT,beep,1,,1,15)
 same => n,NoOp(LAB_KEYPAD status=${READSTATUS} digit=${TEST_DIGIT})
 same => n,GotoIf($["${READSTATUS}" = "OK"]?speak:done)
 same => n(speak),SayDigits(${TEST_DIGIT})
 same => n(done),Hangup()

[lab-menu]
exten => s,1,Answer()
 same => n,Set(MENU_COUNT=0)
 same => n(menu),Set(MENU_COUNT=$[${MENU_COUNT}+1])
 same => n,GotoIf($[${MENU_COUNT}>4]?done)
 same => n,Read(MENU_CHOICE,custom/lab-menu,1,,1,15)
 same => n,GotoIf($["${READSTATUS}" != "OK"]?done)
 same => n,GotoIf($["${MENU_CHOICE}" = "0"]?done)
 same => n,GotoIf($["${MENU_CHOICE}" = "9"]?menu)
 same => n,GotoIf($["${MENU_CHOICE}" = "1"]?audio)
 same => n,GotoIf($["${MENU_CHOICE}" = "2"]?network)
 same => n,Playback(custom/lab-invalid)
 same => n,Goto(menu)
 same => n(audio),Playback(hello-world)
 same => n,Goto(menu)
; Fixed target and command. No keypad input is interpolated into the shell.
 same => n(network),TrySystem(/usr/bin/timeout 3 /bin/bash -c 'exec 3<>/dev/tcp/192.168.1.250/80')
 same => n,NoOp(LAB_ACTION askey_http_port status=${SYSTEMSTATUS})
 same => n,GotoIf($["${SYSTEMSTATUS}" = "SUCCESS"]?up:down)
 same => n(up),Playback(custom/lab-network-up)
 same => n,Goto(menu)
 same => n(down),Playback(custom/lab-network-down)
 same => n,Goto(menu)
 same => n(done),Hangup()
''',
        'rtp.conf': '[general]\nrtpstart=10000\nrtpend=10019\nstrictrtp=yes\n',
        'modules.conf': '''[modules]
autoload=no
load=res_sorcery_config.so
load=res_sorcery_memory.so
load=res_sorcery_astdb.so
load=res_pjproject.so
load=res_pjsip.so
load=res_pjsip_acl.so
load=res_pjsip_authenticator_digest.so
load=res_pjsip_endpoint_identifier_user.so
load=res_pjsip_registrar.so
load=res_pjsip_session.so
load=res_pjsip_pubsub.so
load=res_pjsip_sdp_rtp.so
load=res_pjsip_dtmf_info.so
load=res_rtp_asterisk.so
load=chan_pjsip.so
load=res_timing_timerfd.so
load=pbx_config.so
load=codec_alaw.so
load=codec_ulaw.so
load=codec_gsm.so
load=format_gsm.so
load=format_pcm.so
load=format_wav.so
load=bridge_simple.so
load=app_dial.so
load=app_echo.so
load=app_playback.so
load=app_read.so
load=app_record.so
load=app_system.so
load=res_clioriginate.so
''',
        'logger.conf': '[logfiles]\nconsole => notice,warning,error,verbose\n',
        'http.conf': '[general]\nenabled=no\n',
        'manager.conf': '[general]\nenabled=no\n',
        'asterisk.conf': '''[directories]
astetcdir => /etc/asterisk
astmoddir => /usr/lib/x86_64-linux-gnu/asterisk/modules
astvarlibdir => /var/lib/asterisk
astdbdir => /var/lib/asterisk
astkeydir => /var/lib/asterisk
astdatadir => /usr/share/asterisk
astagidir => /usr/share/asterisk/agi-bin
astspooldir => /var/spool/asterisk
astrundir => /tmp
astlogdir => /var/log/asterisk
''',
    }
    etc = out / 'etc'
    etc.mkdir(mode=0o700, exist_ok=True)
    for name, body in configs.items():
        path = etc / name
        path.write_text(body)
        os.chmod(path, 0o600)
    print('Prepared endpoint 10 at 192.168.1.97:5060; phone ACL 192.168.1.250/32.')
    print('Dialplan: 20 menu, 19 echo, *20 audio, *29 digit playback. Menu 2 performs only the fixed, bounded Askey TCP-port check.')
    print('Credentials retained privately:', account)


if __name__ == '__main__':
    main()
