#!/usr/bin/env python3
"""Owned-file inert RAM placement/readback; never invokes native code."""
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
parser.add_argument('phase', choices=['preflight', 'create', 'write', 'read', 'cleanup'])
parser.add_argument('--run-dir', default='.local/ram-placement-probe')
options = parser.parse_args()
if not __debug__:
    raise RuntimeError('Run without Python optimization; ownership and bounds assertions are required')
ROOT = Path(__file__).resolve().parents[1]
OUT = (ROOT / options.run_dir).resolve()
assert OUT.is_relative_to((ROOT / '.local').resolve()), 'Raw probe evidence must remain in ignored .local/'
OUT.mkdir(mode=0o700, parents=True, exist_ok=True)
PARSER = inspect.getsource(runpy.run_path(str(ROOT / 'tools/capture_flash.py'))['parse_dump'])
REMOTE = '''import base64,hashlib,json,re,struct,subprocess,sys,telnetlib,time
''' + PARSER + r'''
if not __debug__:raise RuntimeError('Remote Python optimization disables required guards')
c=json.loads(sys.stdin.readline());t=c['target'];phase=c['phase'];name=c['name']
assert phase in ('preflight','create','write','read','cleanup')
assert re.fullmatch(r'mero_native_009_[0-9a-f]{8}',name)
route=json.loads(subprocess.check_output(['ip','-j','route','get',t['ip']]))[0]
neighbor=json.loads(subprocess.check_output(['ip','-j','neigh','show',t['ip']]))[0]
assert route['dev']==t['interface'] and route['prefsrc']==t['source']
assert neighbor['lladdr'].lower()==t['mac'].lower()
def emit(value):print(json.dumps(value),flush=True)
def expect(pattern,timeout=8):
 i,m,d=tn.expect([pattern],timeout)
 if i<0:raise RuntimeError('Expected prompt not received')
 return d
def command(text):
 tn.write(text.encode('ascii')+b'\r\n');raw=expect(br'(?:^|[\r\n])XDSL[#>]')
 emit({'type':'response','command':text,'raw_b64':base64.b64encode(raw).decode()})
 return raw
def dump(address,length):
 assert 16<=length<=256 and length%16==0
 assert (0x8094cde8<=address and address+length<=0x82004df8) or (0x8060aaf0<=address and address+length<=0x8060b2f8) or (0x8091eb68<=address and address+length<=0x8091ec68) or (address==0xb4010000 and length==64)
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
 elif phase in ('write','read'):
  lease=c['lease'];check(lease)
  if phase=='write':
   code=base64.b64decode(c['code_marker_b64']);mail=base64.b64decode(c['mailbox_b64']);assert len(code)==len(mail)==64
   original_code=dump(lease['data'],64);original_mail=dump(lease['mailbox'],64)
   emit({'type':'original','code_b64':base64.b64encode(original_code).decode(),'mailbox_b64':base64.b64encode(original_mail).decode()})
   assert original_code[:4]!=code[:4]
   def store(address,value):
    assert address%4==0
    assert lease['data']<=address<lease['data']+64 or lease['mailbox']<=address<lease['mailbox']+64
    command(f'memory set long 0x{address:x} value 0x{value:08x}')
   store(lease['data'],int.from_bytes(code[:4],'big'))
   assert dump(lease['data'],16)[:4]==code[:4],'Pilot write did not read back'
   for offset in range(4,64,4):store(lease['data']+offset,int.from_bytes(code[offset:offset+4],'big'))
   for offset in range(0,64,4):store(lease['mailbox']+offset,int.from_bytes(mail[offset:offset+4],'big'))
   assert dump(lease['data'],64)==code and dump(lease['mailbox'],64)==mail
  check(lease)
  emit({'type':'readback','code_b64':base64.b64encode(dump(lease['data'],64)).decode(),'mailbox_b64':base64.b64encode(dump(lease['mailbox'],64)).decode()});success=True
 else:
  lease=c['lease'];check(lease);command('xfile close '+name);command('xfile delete '+name)
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
    name = 'mero_native_009_' + secrets.token_hex(4)
    config = {'phase': phase, 'name': name}
else:
    lease = json.loads((OUT / 'lease.json').read_text())
    config = {'phase': phase, 'name': lease['name'], 'lease': lease}
if phase == 'write':
    nonce = secrets.token_bytes(16)
    code = (nonce + b'INERT_PLACEMENT_DATA_ONLY_009').ljust(64, b'.')
    mailbox = b'MRO9' + struct.pack('>I', 1) + nonce + bytes(40)
    assert len(code) == len(mailbox) == 64
    config.update(code_marker_b64=base64.b64encode(code).decode(), mailbox_b64=base64.b64encode(mailbox).decode())
    (OUT / 'expected-readback.json').write_text(json.dumps({'code_b64': config['code_marker_b64'], 'mailbox_b64': config['mailbox_b64']}, indent=2)+'\n')
    os.chmod(OUT / 'expected-readback.json', 0o600)
config.update(target=target, auth=auth)
ssh_args = ['ssh', '-i', target['key'], '-o', 'IdentitiesOnly=yes', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=6', target['ssh'], 'python3 -c ' + shlex.quote(REMOTE)]
logstem = phase + '-' + str(time.time_ns())
r = subprocess.run(ssh_args, input=json.dumps(config)+'\n', capture_output=True, text=True, timeout=100)
for filename, text in [(logstem+'.jsonl', r.stdout), (logstem+'-stderr.txt', r.stderr)]:
    (OUT / filename).write_text(text)
    os.chmod(OUT / filename, 0o600)
assert r.returncode == 0, 'Probe failed; inspect private log before further operations'
records = [json.loads(line) for line in r.stdout.splitlines()]
assert records[-1]['type'] == 'logged_out'
if phase == 'preflight':
    assert any(x['type'] == 'preflight_verified' for x in records)
    print('Target route, neighbor, firmware header and Telnet inventory verified; no file operation issued')
elif phase == 'create':
    lease = next(x['lease'] for x in records if x['type'] == 'lease')
    lease.update(created_unix=time.time(), held=True)
    (OUT / 'lease.json').write_text(json.dumps(lease, indent=2)+'\n')
    os.chmod(OUT / 'lease.json', 0o600)
    print('Owned allocation verified:', {k: hex(lease[k]) for k in ['ccb','backing','data','mailbox']})
elif phase in ('write', 'read'):
    observed = next(x for x in records if x['type'] == 'readback')
    expected = json.loads((OUT / 'expected-readback.json').read_text())
    assert all(observed[k] == expected[k] for k in expected)
    print(phase, 'nonce-bearing data and mailbox match exactly; owner/pointers revalidated; clean logout')
else:
    assert any(x['type'] == 'cleaned_up' for x in records)
    lease['held'] = False
    (OUT / 'lease.json').write_text(json.dumps(lease, indent=2)+'\n')
    print('Owned allocation released; original inventory restored; clean logout')
print('Evidence', str(OUT / (logstem+'.jsonl')))
print('Evidence SHA256', hashlib.sha256((OUT / (logstem+'.jsonl')).read_bytes()).hexdigest())
