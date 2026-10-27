#!/usr/bin/env python3
"""Capture the measured Askey flash map through its read-only Telnet command."""

import argparse
import base64
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import time


REMOTE = r'''
import base64, json, re, socket, subprocess, sys, telnetlib, time
c = json.loads(sys.stdin.readline())
t = c['target']
route = json.loads(subprocess.check_output(['ip', '-j', 'route', 'get', t['ip']]))[0]
neighbor = json.loads(subprocess.check_output(['ip', '-j', 'neigh', 'show', t['ip']]))[0]
assert route['dev'] == t['interface'] and route['prefsrc'] == t['source']
assert neighbor['lladdr'].lower() == t['mac'].lower()
assert 0xb4000000 <= c['start'] < c['end'] <= 0xb4800000
assert 16 <= c['chunk'] <= 1024 and c['chunk'] % 16 == 0
def emit(x):
    print(json.dumps(x), flush=True)
def expect(pattern, timeout=20):
    i, match, data = tn.expect([pattern], timeout)
    if i != 0:
        raise RuntimeError('Expected console prompt not received: ' + repr(data[-160:]))
    return data
tn = telnetlib.Telnet(t['ip'], 23, 5)
tn.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
original_fill = tn.fill_rawq
def fill_rawq():
    original_fill()
    tn.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
tn.fill_rawq = fill_rawq
inner = False
try:
    expect(br'Username:')
    tn.write(c['auth']['username'].encode('ascii') + b'\r\n')
    expect(br'Password:')
    tn.write(c['auth']['password'].encode('ascii') + b'\r\n')
    expect(br'(?:^|[\r\n])\$')
    tn.write(b'sh\r\n')
    expect(br'(?:^|[\r\n])XDSL>')
    inner = True
    emit({'type': 'connected', 'started_unix': time.time(), 'route': route})
    for address in range(c['start'], c['end'], c['chunk']):
        count = min(c['chunk'], c['end'] - address)
        command = f'memory show 0x{address:x} length 0x{count:x}'
        started = time.monotonic()
        tn.write(command.encode('ascii') + b'\r\n')
        response = expect(br'(?:^|[\r\n])XDSL>')
        emit({'type': 'chunk', 'address': address, 'length': count,
              'seconds': time.monotonic() - started,
              'raw_b64': base64.b64encode(response).decode('ascii')})
        time.sleep(c['pause'])
    emit({'type': 'complete', 'finished_unix': time.time()})
finally:
    if inner:
        try:
            tn.write(b'quit\r\n')
            expect(br'(?:^|[\r\n])\$', 5)
            tn.write(b'exit\r\n')
            expect(br'Username:', 5)
            emit({'type': 'logged_out'})
        except Exception:
            emit({'type': 'logout_unconfirmed'})
    tn.close()
'''


def parse_dump(raw, address, length):
    """Accept only complete, contiguous, byte-formatted display rows."""
    result = bytearray()
    for line in raw.decode('ascii', errors='replace').splitlines():
        match = re.match(r'^\s*(0x[0-9a-fA-F]+):\s+(.*)$', line)
        if not match:
            continue
        if int(match[1], 16) != address + len(result):
            raise ValueError('Noncontiguous or repeated dump address')
        count = min(16, length - len(result))
        if count <= 0:
            raise ValueError('More dump rows than requested')
        cells = match[2].split()[:count]
        if len(cells) != count or any(not re.fullmatch(r'[0-9a-fA-F]{2}', x) for x in cells):
            raise ValueError('Truncated or malformed byte row')
        result.extend(bytes.fromhex(' '.join(cells)))
    if len(result) != length:
        raise ValueError(f'Expected {length} bytes, received {len(result)}')
    return bytes(result)


def self_test():
    row = b'0xb4010000: a0 00 00 03 80 00 00 00 00 2d 15 80 80 94 92 88 ....\r\n'
    expected = bytes.fromhex('a000000380000000002d158080949288')
    assert parse_dump(b'memory show ignored\r\n' + row + b'XDSL>', 0xb4010000, 16) == expected
    for bad in [row + row, row.replace(b'b4010000', b'b4010010'), row.replace(b'92 88', b'92 xx'), b'XDSL>']:
        try:
            parse_dump(bad, 0xb4010000, 16)
        except ValueError:
            pass
        else:
            raise AssertionError('Malformed dump accepted')
    print('Parser self-check passed')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--self-test', action='store_true')
    p.add_argument('--start', type=lambda x: int(x, 0), default=0xb4000000)
    p.add_argument('--size', type=lambda x: int(x, 0), default=0x800000)
    p.add_argument('--chunk', type=lambda x: int(x, 0), default=1024)
    p.add_argument('--pause', type=float, default=0.15)
    p.add_argument('--output', type=Path)
    p.add_argument('--resume', action='store_true')
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.output:
        p.error('--output is required')
    if not (0xb4000000 <= args.start < args.start + args.size <= 0xb4800000):
        p.error('Read must stay inside the device-reported 8 MiB flash map')
    if args.start % 16 or args.size % 16 or not (16 <= args.chunk <= 1024) or args.chunk % 16:
        p.error('Addresses/sizes must use 16-byte rows; chunk must be 16..1024 bytes')
    if args.pause < 0.05:
        p.error('Pause must be at least 0.05 seconds')
    root = Path(__file__).resolve().parents[1]
    target = json.loads((root / '.local/capture-target.json').read_text())
    auth = json.loads((root / '.local/router-login.json').read_text())
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = Path(str(output) + '.json')
    saved = 0
    digest = hashlib.sha256()
    if args.resume:
        state = json.loads(checkpoint.read_text())
        assert (state['start'], state['size'], state['chunk']) == (args.start, args.size, args.chunk)
        saved = state['captured']
        with output.open('r+b') as f:
            assert f.seek(0, 2) >= saved
            f.truncate(saved)
            f.seek(0)
            while block := f.read(1048576):
                digest.update(block)
        assert digest.hexdigest() == state['sha256'], 'Existing capture/checkpoint mismatch'
        if saved == args.size and state.get('complete'):
            print('Already complete:', digest.hexdigest())
            return
        if saved == args.size:
            saved -= min(args.chunk, saved)
            with output.open('r+b') as f:
                f.truncate(saved)
            digest = hashlib.sha256(output.read_bytes())
    elif output.exists() or checkpoint.exists():
        p.error('Output/checkpoint already exists; use --resume instead of overwriting')
    config = {'target': target, 'auth': auth, 'start': args.start + saved,
              'end': args.start + args.size, 'chunk': args.chunk, 'pause': args.pause}
    command = ['ssh', '-T', '-i', str(Path(target['key']).expanduser()),
               '-o', 'IdentitiesOnly=yes', '-o', 'BatchMode=yes',
               '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=5',
               '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=3',
               target['ssh'], 'python3 -W ignore::DeprecationWarning -c ' + shlex.quote(REMOTE)]
    started = time.monotonic()
    initial = saved
    last_print = started
    complete = False
    def save_state():
        state = {'start': args.start, 'size': args.size, 'chunk': args.chunk,
                 'captured': saved, 'sha256': digest.hexdigest(), 'complete': complete,
                 'updated_unix': time.time()}
        temp = Path(str(checkpoint) + '.tmp')
        temp.write_text(json.dumps(state, indent=2) + '\n')
        temp.chmod(0o600)
        temp.replace(checkpoint)
    with output.open('ab' if args.resume else 'xb') as data, \
            gzip.open(str(output) + '.jsonl.gz', 'at') as log, \
            open(str(output) + '.stderr', 'a') as stderr:
        output.chmod(0o600)
        save_state()
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=stderr, text=True)
        try:
            process.stdin.write(json.dumps(config) + '\n')
            process.stdin.close()
            for line in process.stdout:
                event = json.loads(line)
                log.write(line)
                if event['type'] == 'chunk':
                    assert event['address'] == args.start + saved
                    assert event['length'] == min(args.chunk, args.size - saved)
                    block = parse_dump(base64.b64decode(event['raw_b64']), event['address'], event['length'])
                    data.write(block)
                    data.flush()
                    os.fsync(data.fileno())
                    digest.update(block)
                    saved += len(block)
                    save_state()
                    now = time.monotonic()
                    if now - last_print >= 10 or saved == args.size:
                        rate = (saved - initial) / max(now - started, 0.001)
                        print(f'{saved}/{args.size} bytes ({100*saved/args.size:.2f}%), '
                              f'{rate:.0f} B/s, ETA {(args.size-saved)/max(rate,1):.0f}s', flush=True)
                        log.flush()
                        last_print = now
                elif event['type'] == 'complete':
                    assert saved == args.size
                    complete = True
                else:
                    print(event['type'], flush=True)
            if process.wait() != 0 or not complete:
                raise RuntimeError('Capture incomplete; inspect stderr and resume from checkpoint')
            save_state()
            print('SHA-256:', digest.hexdigest(), flush=True)
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


if __name__ == '__main__':
    main()
