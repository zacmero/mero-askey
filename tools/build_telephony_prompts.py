#!/usr/bin/env python3
"""Generate fixed local eSpeak prompts, then install them in the running lab PBX."""
from pathlib import Path
import subprocess
import json


def main():
    root = Path(__file__).resolve().parents[1]
    out = root / '.local/telephony-pbx/sounds'
    out.mkdir(mode=0o700, parents=True, exist_ok=True)
    prompts = {
        'lab-menu': 'Welcome to your private lab. Press one for an audio test. Press two to check the Askey web connection. Press nine to repeat this menu. Press zero to hang up.',
        'lab-network-up': 'The Askey web port is reachable. This checks the local connection, not internet access.',
        'lab-network-down': 'The Askey web port did not respond within three seconds.',
        'lab-invalid': 'That key has no action.',
    }
    for name, text in prompts.items():
        speech = subprocess.run(['docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'espeak-ng',
                                 'mero-askey-pbx:local', '--stdout', '-s', '155', text],
                                capture_output=True, check=True, timeout=20).stdout
        path = out / (name + '.wav')
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', 'pipe:0',
                        '-ar', '8000', '-ac', '1', '-c:a', 'pcm_s16le', str(path)],
                       input=speech, check=True, timeout=20)
        path.chmod(0o600)
    mounts = json.loads(subprocess.check_output(['docker', 'inspect', '--format', '{{json .Mounts}}', 'mero-askey-pbx'], text=True))
    if not any(m['Destination'] == '/usr/share/asterisk/sounds/custom' for m in mounts):
        # Existing pilot containers predate the persistent prompt mount.
        subprocess.run(['docker', 'exec', 'mero-askey-pbx', 'mkdir', '-p', '/usr/share/asterisk/sounds/custom'], check=True)
        for name in prompts:
            subprocess.run(['docker', 'cp', str(out / (name + '.wav')),
                            'mero-askey-pbx:/usr/share/asterisk/sounds/custom/'], check=True, capture_output=True)
    print('Four fixed prompts generated locally and installed. No external speech service used.')


if __name__ == '__main__':
    main()
