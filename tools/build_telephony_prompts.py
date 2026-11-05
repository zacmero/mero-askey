#!/usr/bin/env python3
"""Generate fixed local TTS prompts, then install them in the running lab PBX."""
import argparse
from pathlib import Path
import subprocess
import json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=['piper', 'espeak'], default='piper')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = root / '.local/telephony-pbx/sounds'
    out.mkdir(mode=0o700, parents=True, exist_ok=True)
    staging = out / 'staging'
    staging.mkdir(mode=0o700, exist_ok=True)
    prompts = {
        'lab-menu': 'Welcome back. You have reached your private line. Press one for an audio test. Press two to check the Askey connection. Press three for cinema on the Bravia. Press four to restore your screens. Press nine to hear your choices again. Press zero when you wish to leave.',
        'lab-network-up': 'The Askey web port is reachable. This checks the local connection, not internet access.',
        'lab-network-down': 'The Askey web port did not respond within three seconds.',
        'lab-invalid': 'That key has no action.',
        'lab-idle': 'The line is still open. Let me repeat your choices.',
        'lab-cinema-on': 'Cinema mode is ready on your Bravia. Enjoy the show.',
        'lab-cinema-off': 'Your screens have been restored.',
        'lab-command-failed': 'That command could not be completed. Your command log has the details.',
    }
    active = subprocess.check_output(['docker', 'exec', 'mero-askey-pbx', 'asterisk', '-rx', 'core show channels concise'], text=True)
    if active.strip():
        raise RuntimeError('Wait for the active call to end before replacing prompts')
    for name, text in prompts.items():
        if args.engine == 'piper':
            python = root / '.local/telephony-tts-venv/bin/python'
            model = root / '.local/telephony-pbx/voices/en_US-lessac-medium.onnx'
            if not python.exists() or not model.exists():
                raise RuntimeError('Install the documented local Piper environment and voice first')
            speech = subprocess.run([str(python), '-m', 'piper', '-m', str(model), '-f', '-',
                                     '--length-scale', '1.12', '--sentence-silence', '0.25'],
                                    input=text.encode(), capture_output=True, check=True, timeout=90).stdout
        else:
            speech = subprocess.run(['docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'espeak-ng',
                                 'mero-askey-pbx:local', '--stdout', '-s', '155', text],
                                capture_output=True, check=True, timeout=20).stdout
        path = staging / (name + '.wav')
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', 'pipe:0',
                        '-ar', '8000', '-ac', '1', '-c:a', 'pcm_s16le', str(path)],
                       input=speech, check=True, timeout=20)
        path.chmod(0o600)
    for name in prompts:
        (staging / (name + '.wav')).replace(out / (name + '.wav'))
    mounts = json.loads(subprocess.check_output(['docker', 'inspect', '--format', '{{json .Mounts}}', 'mero-askey-pbx'], text=True))
    if not any(m['Destination'] == '/usr/share/asterisk/sounds/custom' for m in mounts):
        # Existing pilot containers predate the persistent prompt mount.
        subprocess.run(['docker', 'exec', 'mero-askey-pbx', 'mkdir', '-p', '/usr/share/asterisk/sounds/custom'], check=True)
        for name in prompts:
            subprocess.run(['docker', 'cp', str(out / (name + '.wav')),
                            'mero-askey-pbx:/usr/share/asterisk/sounds/custom/'], check=True, capture_output=True)
    print(str(len(prompts)) + ' fixed prompts generated locally with ' + args.engine + ' and installed. No external speech service used.')


if __name__ == '__main__':
    main()
