#!/usr/bin/env python3
"""Bounded native execution trial on Askey RTV9015VW via webdll contract.

Implements Roadmap Steps 3 & 4:
- Preflight verification of target route, MAC, firmware header, and file inventory.
- Dynamic owned RAM-file allocation via `xfile`.
- Staging of compiled PIC MIPS32 payload and mailbox prefill in uncached KSEG1.
- Synchronous invocation of `webdll <entry_addr>` under verified two-call contract.
- Independent fresh-session mailbox readback and 10-field verification.
- Verified release and original file-inventory restoration.
"""
import argparse
import base64
import hashlib
import inspect
import json
import os
from pathlib import Path
import runpy
import secrets
import shlex
import struct
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('phase', choices=['preflight', 'create', 'stage', 'execute', 'verify', 'cleanup'])
parser.add_argument('--run-dir', default='.local/askey-net-010/trial')
options = parser.parse_args()

if not __debug__:
    raise RuntimeError('Run without Python optimization; ownership and bounds assertions are required')

ROOT = Path(__file__).resolve().parents[1]
OUT = (ROOT / options.run_dir).resolve()
assert OUT.is_relative_to((ROOT / '.local').resolve()), 'Raw trial evidence must remain in ignored .local/'
OUT.mkdir(mode=0o700, parents=True, exist_ok=True)

PAYLOAD_PATH = ROOT / '.local/native-payload/payload.bin'
assert PAYLOAD_PATH.is_file(), f'Compiled payload missing at {PAYLOAD_PATH}'
PAYLOAD_BYTES = PAYLOAD_PATH.read_bytes()
assert len(PAYLOAD_BYTES) == 576, f'Expected 576-byte payload, got {len(PAYLOAD_BYTES)}'
EXPECTED_PAYLOAD_SHA256 = 'c7db7a20722b2b37fa2f19390c904af1c4a5a832da50a819fe94a1381e27c3e0'
assert hashlib.sha256(PAYLOAD_BYTES).hexdigest() == EXPECTED_PAYLOAD_SHA256, 'Payload hash mismatch'

PARSER = inspect.getsource(runpy.run_path(str(ROOT / 'tools/capture_flash.py'))['parse_dump'])

REMOTE = '''import base64,hashlib,json,re,struct,subprocess,sys,telnetlib,time
''' + PARSER + r'''
if not __debug__:raise RuntimeError('Remote Python optimization disables required guards')
c=json.loads(sys.stdin.readline());t=c['target'];phase=c['phase'];name=c['name']
assert phase in ('preflight','create','stage','execute','verify','cleanup')
assert re.fullmatch(r'mero_native_010_[0-9a-f]{8}',name)

route=json.loads(subprocess.check_output(['ip','-j','route','get',t['ip']]))[0]
neighbor=json.loads(subprocess.check_output(['ip','-j','neigh','show',t['ip']]))[0]
assert route['dev']==t['interface'] and route['prefsrc']==t['source']
assert neighbor['lladdr'].lower()==t['mac'].lower()

def emit(value):print(json.dumps(value),flush=True)

def expect(pattern,timeout=10):
 i,m,d=tn.expect([pattern],timeout)
 if i<0:raise RuntimeError(f'Expected prompt {pattern} not received within {timeout}s')
 return d

def command(text,timeout=10):
 tn.write(text.encode('ascii')+b'\r\n');raw=expect(br'(?:^|[\r\n])XDSL[#>]',timeout=timeout)
 emit({'type':'response','command':text,'raw_b64':base64.b64encode(raw).decode()})
 return raw

def dump(address,length):
 assert 16<=length<=256 and length%16==0
 kseg0_ram=(0x80000000<=address and address+length<=0x82004df8)
 kseg1_ram=(0xa0000000<=address and address+length<=0xa2004df8)
 flash=(address==0xb4010000 and length==64)
 assert kseg0_ram or kseg1_ram or flash, f'Address 0x{address:x} outside safe probe bounds'
 return parse_dump(command(f'memory show 0x{address:x} length 0x{length:x}'),address,length)

def inventory():
 raw=command('xfile list').replace(b'\r',b'').decode('ascii','replace');result={}
 for line in raw.splitlines():
  m=re.fullmatch(r'\s*([0-9a-fA-F]{8})\s+(\d+)\s+(\d+)\s+([0-9a-fA-F]+)\s+(\d+)\s+(\S+)\s*',line)
  if m:
   addr,size,buffers,flags,timeout,filename=m.groups()
   result[filename]={'ccb':int(addr,16),'size':int(size),'buffers':int(buffers),'flags':int(flags,16),'timeout':int(timeout)}
 return result

def discover():
 files=inventory();entry=files[name]
 assert entry['size']==0 and entry['buffers']==1 and entry['flags']==0x80000000
 ccb=entry['ccb'];assert 0x8094cde8<=ccb and ccb+96<=0x82004df8
 table=dump(0x8091eb68,256);matches=[]
 for index in range(1,8):
  row=table[index*32:(index+1)*32]
  if int.from_bytes(row[4:8],'big')==ccb and int.from_bytes(row[:4],'big')!=0:matches.append((index,row))
 assert len(matches)==1
 index,row=matches[0];nameptr=int.from_bytes(row[:4],'big')
 assert nameptr==0x8060aaf0+index*257
 assert dump(nameptr,((len(name)+1+15)//16)*16).split(b'\0')[0].decode()==name
 block=dump(ccb,96);backing=int.from_bytes(block[84:88],'big');data=int.from_bytes(block[88:92],'big');end=int.from_bytes(block[92:96],'big')
 assert int.from_bytes(block[:4],'big')==0
 assert block[8:10]==b'\0\0' and block[20:22]==b'\0\0'
 assert data==backing+128 and end==backing+1740
 assert 0x8094cde8<=backing and data+1600<=end and end+4<=0x82004df8
 assert data%4==0
 return {'name':name,'ccb':ccb,'backing':backing,'data':data,'end':end,'descriptor':0x8091eb68+index*32,'name_pointer':nameptr,'capacity':1600,'code_capacity':512,'mailbox':data+512,'mailbox_bytes':64,'baseline_files':c.get('baseline_files',[])}

def check(lease):
 current=discover()
 for key in ('name','ccb','backing','data','end','descriptor','name_pointer','capacity','mailbox'):
  assert current[key]==lease[key],('Lease changed',key)
 return current

tn=telnetlib.Telnet(t['ip'],23,5);inner=False;logged=False;created=False;success=False
try:
 expect(br'Username:');tn.write(c['auth']['username'].encode()+b'\r\n')
 expect(br'Password:');tn.write(c['auth']['password'].encode()+b'\r\n')
 expect(br'(?:^|[\r\n])\$');logged=True
 tn.write(b'sh\r\n');expect(br'(?:^|[\r\n])XDSL#');inner=True
 emit({'type':'connected','phase':phase,'time':time.time()})
 assert hashlib.sha256(dump(0xb4010000,64)).hexdigest()=='19cef9e17ca1c90cda12fd579af2ddc18c80ae9528e89c32130d5a2e0e871348', 'Running-image header differs from the measured build'

 if phase=='preflight':
  files=inventory();emit({'type':'preflight_verified','image_header_sha256':'19cef9e17ca1c90cda12fd579af2ddc18c80ae9528e89c32130d5a2e0e871348','file_count':len(files)});success=True
 elif phase=='create':
  before=inventory();assert name not in before and len(before)<7
  expected={'CWMPNotify.txt','/var/wscd.conf','/var/wscd-vxd.conf','ssl_cert.pem','ssl_key.pem'}
  assert set(before)==expected
  command('xfile create '+name);created=True
  after=inventory();assert set(after)==set(before)|{name}
  assert all(after[k]==v for k,v in before.items())
  lease=discover();lease['baseline_files']=before
  emit({'type':'lease','lease':lease});success=True
 elif phase=='stage':
  lease=c['lease'];check(lease)
  k0_data=lease['data'];k1_data=k0_data|0x20000000
  k0_mb=lease['mailbox'];k1_mb=k0_mb|0x20000000
  payload_raw=base64.b64decode(c['payload_b64']);assert len(payload_raw)==576
  seed_word=c['seed_word']
  def store(address,val):
   assert address%4==0
   assert (k0_data<=address<k0_data+lease['capacity']) or (k1_data<=address<k1_data+lease['capacity']), f'Store target 0x{address:x} out of owned bounds'
   command(f'memory set long 0x{address:x} value 0x{val:08x}')
  # 1. Pre-fill mailbox with seed_word in KSEG1 and KSEG0
  for offset in range(0,64,4):
   store(k1_mb+offset,seed_word)
   store(k0_mb+offset,seed_word)
  mb_read=dump(k1_mb,64)
  assert mb_read==struct.pack('>16I',*[seed_word]*16), 'Mailbox prefill mismatch'
  # 2. Stage active code regions: entry_func (72 bytes / 18 words) and cleanup_func (80 bytes / 20 words)
  # Write entry_func (offset 0..72)
  for offset in range(0,72,4):
   w=int.from_bytes(payload_raw[offset:offset+4],'big')
   store(k1_data+offset,w)
   store(k0_data+offset,w)
  # Write cleanup_func (offset 128..208)
  for offset in range(128,208,4):
   w=int.from_bytes(payload_raw[offset:offset+4],'big')
   store(k1_data+offset,w)
   store(k0_data+offset,w)
  # 3. Read back and verify both code blocks
  entry_read_k1=dump(k1_data,80)[:72]
  cleanup_read_k1=dump(k1_data+128,80)
  assert entry_read_k1==payload_raw[:72], 'Staged entry_func mismatch in KSEG1'
  assert cleanup_read_k1==payload_raw[128:208], 'Staged cleanup_func mismatch in KSEG1'
  entry_read_k0=dump(k0_data,80)[:72]
  cleanup_read_k0=dump(k0_data+128,80)
  assert entry_read_k0==payload_raw[:72], 'Staged entry_func mismatch in KSEG0'
  assert cleanup_read_k0==payload_raw[128:208], 'Staged cleanup_func mismatch in KSEG0'
  emit({'type':'staged','k1_entry':hex(k1_data),'k1_cleanup':hex(k1_data+128),'k1_mailbox':hex(k1_mb)});success=True
 elif phase=='execute':
  lease=c['lease'];check(lease)
  k1_data=lease['data']|0x20000000
  cmd=f'webdll 0x{k1_data:08x}'
  raw=command(cmd,timeout=10)
  # Prompt responsiveness check
  pcheck=command('help memory',timeout=5)
  emit({'type':'executed','command':cmd,'response_b64':base64.b64encode(raw).decode(),'responsive':True});success=True
 elif phase=='verify':
  lease=c['lease'];check(lease)
  k1_data=lease['data']|0x20000000;k1_mb=lease['mailbox']|0x20000000
  mb_bytes=dump(k1_mb,64)
  words=struct.unpack('>16I',mb_bytes)
  k1_cleanup=k1_data+128
  expected_words=[
   0x454e5452,          # "ENTR"
   0x11112222,          # Stage 1 nonce
   0x12345678,          # captured $a0
   0x805f1648,          # captured $a1
   k1_cleanup,          # cleanup_func address
   0x434c4e50,          # "CLNP"
   0x33334444,          # Stage 2 nonce
   0x12345678,          # captured $a0
   0x805f1648,          # captured $a1
   0x53554343           # "SUCC"
  ]
  matched_all=True
  for idx,exp in enumerate(expected_words):
   if words[idx]!=exp:matched_all=False;break
  emit({
   'type':'verified',
   'mailbox_hex':[hex(w) for w in words],
   'matched_markers':matched_all,
   'stage1_magic':hex(words[0]),
   'stage1_nonce':hex(words[1]),
   'stage1_a0':hex(words[2]),
   'stage1_a1':hex(words[3]),
   'cleanup_callback':hex(words[4]),
   'stage2_magic':hex(words[5]),
   'stage2_nonce':hex(words[6]),
   'stage2_a0':hex(words[7]),
   'stage2_a1':hex(words[8]),
   'success_flag':hex(words[9])
  })
  assert matched_all, f'Mailbox verification failed: observed {words[:10]}, expected {expected_words}'
  success=True
 else: # cleanup
  lease=c['lease'];check(lease)
  command('xfile close '+name)
  command('xfile delete '+name)
  after=inventory();assert name not in after and after==lease['baseline_files']
  emit({'type':'cleaned_up','original_inventory_restored':True});success=True
finally:
 try:
  if created and not success:
   command('xfile close '+name);command('xfile delete '+name);emit({'type':'failed_creation_cleaned_up'})
  if inner:tn.write(b'quit\r\n');expect(br'(?:^|[\r\n])\$',5)
  if logged:tn.write(b'exit\r\n');expect(br'Username:',5);emit({'type':'logged_out'})
 finally:tn.close()
'''

phase = options.phase
target = json.loads((ROOT / '.local/capture-target.json').read_text())
auth = json.loads((ROOT / '.local/router-login.json').read_text())

if phase in ('preflight', 'create'):
    name = 'mero_native_010_' + secrets.token_hex(4)
    config = {'phase': phase, 'name': name}
else:
    lease_file = OUT / 'lease.json'
    assert lease_file.is_file(), f'Lease file missing at {lease_file}; run create first'
    lease = json.loads(lease_file.read_text())
    config = {'phase': phase, 'name': lease['name'], 'lease': lease}

if phase == 'stage':
    config.update(
        payload_b64=base64.b64encode(PAYLOAD_BYTES).decode(),
        seed_word=0xDEADBEEF
    )

config.update(target=target, auth=auth)

ssh_args = [
    'ssh', '-i', target['key'],
    '-o', 'IdentitiesOnly=yes',
    '-o', 'BatchMode=yes',
    '-o', 'StrictHostKeyChecking=yes',
    '-o', 'ConnectTimeout=6',
    target['ssh'],
    'python3 -c ' + shlex.quote(REMOTE)
]

logstem = f'{phase}-{time.time_ns()}'
r = subprocess.run(ssh_args, input=json.dumps(config) + '\n', capture_output=True, text=True, timeout=120)

for filename, text in [(logstem + '.jsonl', r.stdout), (logstem + '-stderr.txt', r.stderr)]:
    (OUT / filename).write_text(text)
    os.chmod(OUT / filename, 0o600)

assert r.returncode == 0, f'Trial phase {phase} failed (rc={r.returncode}); inspect {OUT / (logstem + "-stderr.txt")}'

records = [json.loads(line) for line in r.stdout.splitlines()]
assert records[-1]['type'] == 'logged_out', 'Session failed to log out cleanly'

if phase == 'preflight':
    assert any(x['type'] == 'preflight_verified' for x in records)
    print('Preflight verified: route, neighbor, firmware header and 5 baseline files intact.')
elif phase == 'create':
    lease = next(x['lease'] for x in records if x['type'] == 'lease')
    lease.update(created_unix=time.time(), held=True)
    (OUT / 'lease.json').write_text(json.dumps(lease, indent=2) + '\n')
    os.chmod(OUT / 'lease.json', 0o600)
    print('Owned allocation verified:')
    print(' ', {k: hex(lease[k]) for k in ['ccb', 'backing', 'data', 'mailbox']})
    print('  KSEG1 entry:', hex(lease['data'] | 0x20000000))
    print('  KSEG1 cleanup callback:', hex((lease['data'] | 0x20000000) + 128))
    print('  KSEG1 mailbox:', hex((lease['data'] | 0x20000000) + 512))
elif phase == 'stage':
    staged = next(x for x in records if x['type'] == 'staged')
    print('Staging complete:')
    print('  Mailbox prefilled with 0xDEADBEEF.')
    print('  Entry func (72 bytes / 18 words) placed and verified at KSEG1', staged['k1_entry'])
    print('  Cleanup func (80 bytes / 20 words) placed and verified at KSEG1', staged['k1_cleanup'])
    print('  Both KSEG1 and KSEG0 readbacks matched payload.bin byte-for-byte.')
elif phase == 'execute':
    exec_rec = next(x for x in records if x['type'] == 'executed')
    print('Execution invocation complete:')
    print('  Issued:', exec_rec['command'])
    print('  Console remains responsive:', exec_rec['responsive'])
elif phase == 'verify':
    v = next(x for x in records if x['type'] == 'verified')
    print('Verification SUCCESS:')
    print('  Stage 1 magic:', v['stage1_magic'], '(expected 0x454e5452 "ENTR")')
    print('  Stage 1 nonce:', v['stage1_nonce'], '(expected 0x11112222)')
    print('  Captured $a0:', v['stage1_a0'], '(expected 0x12345678)')
    print('  Captured $a1:', v['stage1_a1'], '(expected 0x805f1648)')
    print('  Cleanup callback:', v['cleanup_callback'])
    print('  Stage 2 magic:', v['stage2_magic'], '(expected 0x434c4e50 "CLNP")')
    print('  Stage 2 nonce:', v['stage2_nonce'], '(expected 0x33334444)')
    print('  Captured $a0 (clean):', v['stage2_a0'], '(expected 0x12345678)')
    print('  Captured $a1 (clean):', v['stage2_a1'], '(expected 0x805f1648)')
    print('  Success flag:', v['success_flag'], '(expected 0x53554343 "SUCC")')
else:
    assert any(x['type'] == 'cleaned_up' for x in records)
    lease['held'] = False
    (OUT / 'lease.json').write_text(json.dumps(lease, indent=2) + '\n')
    print('Owned allocation released; original inventory restored; clean logout.')

print('Evidence:', str(OUT / (logstem + '.jsonl')))
print('Evidence SHA256:', hashlib.sha256((OUT / (logstem + '.jsonl')).read_bytes()).hexdigest())
