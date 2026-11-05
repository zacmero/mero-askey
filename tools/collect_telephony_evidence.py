#!/usr/bin/env python3
"""Save PBX status/logs and optionally an existing test recording privately.

Does not change calls or enable SIP/audio capture.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import wave


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recording', action='store_true', help='Retain the existing, owner-authorized six-second self-test recording')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = root / '.local/askey-voice-001' / ('pbx-' + str(time.time_ns()))
    out.mkdir(mode=0o700, parents=True)
    queries = {'contacts.txt': ['docker', 'exec', 'mero-askey-pbx', 'asterisk', '-rx', 'pjsip show contacts'],
               'channels.txt': ['docker', 'exec', 'mero-askey-pbx', 'asterisk', '-rx', 'core show channels concise'],
               'channeltypes.txt': ['docker', 'exec', 'mero-askey-pbx', 'asterisk', '-rx', 'core show channeltypes'],
               'dialplan.txt': ['docker', 'exec', 'mero-askey-pbx', 'asterisk', '-rx', 'dialplan show from-moto700'],
               'pbx.log': ['docker', 'logs', '--timestamps', 'mero-askey-pbx'],
               'image-id.txt': ['docker', 'inspect', '--format', '{{.Image}}', 'mero-askey-pbx']}
    hashes = {}
    for name, command in queries.items():
        result = subprocess.run(command, capture_output=True, timeout=15, check=True)
        data = result.stdout + result.stderr
        path = out / name
        path.write_bytes(data)
        path.chmod(0o600)
        hashes[name] = hashlib.sha256(data).hexdigest()
    if args.recording:
        recording = out / 'moto700-selftest-001.wav'
        subprocess.run(['docker', 'cp', 'mero-askey-pbx:/var/spool/asterisk/monitor/moto700-selftest-001.wav',
                        str(recording)], check=True, capture_output=True, timeout=15)
        recording.chmod(0o600)
        hashes[recording.name] = hashlib.sha256(recording.read_bytes()).hexdigest()
        with wave.open(str(recording), 'rb') as audio:
            metadata = {'channels': audio.getnchannels(), 'sample_rate': audio.getframerate(),
                        'sample_width_bytes': audio.getsampwidth(), 'frames': audio.getnframes(),
                        'duration_seconds': audio.getnframes() / audio.getframerate()}
        (out / 'recording-metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
        (out / 'recording-metadata.json').chmod(0o600)
        print('Existing test recording retained privately:', metadata)
    (out / 'hashes.json').write_text(json.dumps(hashes, indent=2) + '\n')
    (out / 'hashes.json').chmod(0o600)
    print('Private PBX evidence:', out)
    print(json.dumps(hashes, indent=2))


if __name__ == '__main__':
    main()
