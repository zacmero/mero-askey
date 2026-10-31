#!/usr/bin/env python3
"""Build and verify minimal position-independent MIPS32 entry/cleanup payload for webdll."""
import argparse
import hashlib
import os
from pathlib import Path
import struct
import subprocess
import sys

PAYLOAD_ASM = """
.set noreorder
.globl payload_start
.globl entry_func
.globl cleanup_func
.globl mailbox

.text
payload_start:

# -------------------------------------------------------------
# Entry Function: offset 0x00
# Expected args from webdll:
#   $a0 = 0x12345678 (magic constant)
#   $a1 = 0x805f1648 (interface pointer)
#   $ra = return address to webdll (MIPS16 tagged address)
# Returns:
#   $v0 = address of cleanup_func
# -------------------------------------------------------------
entry_func:
    move    $t9, $ra            # 0x00: preserve caller return address
    bal     entry_get_pc        # 0x04: PC-relative branch-and-link
    nop                         # 0x08: branch delay slot
entry_get_pc:
    move    $t0, $ra            # 0x0c: $t0 = address of entry_get_pc
    addiu   $t1, $t0, (mailbox - entry_get_pc)      # 0x10: $t1 = mailbox address
    addiu   $v0, $t0, (cleanup_func - entry_get_pc) # 0x14: $v0 = cleanup_func address
    
    lui     $t2, 0x454e         # 0x18: "EN"
    ori     $t2, $t2, 0x5452    # 0x1c: "TR" -> "ENTR"
    sw      $t2, 0($t1)         # 0x20: mailbox[0] = stage 1 magic
    
    lui     $t2, 0x1111         # 0x24
    ori     $t2, $t2, 0x2222    # 0x28: nonce 0x11112222
    sw      $t2, 4($t1)         # 0x2c: mailbox[1] = stage 1 nonce
    sw      $a0, 8($t1)         # 0x30: mailbox[2] = captured $a0
    sw      $a1, 12($t1)        # 0x34: mailbox[3] = captured $a1
    sw      $v0, 16($t1)        # 0x38: mailbox[4] = returned cleanup_func address
    
    move    $ra, $t9            # 0x3c: restore caller return address
    jr      $ra                 # 0x40: return to webdll (switches back to MIPS16)
    nop                         # 0x44: delay slot

.align 6                        # Align to offset 0x80 (128 bytes)

# -------------------------------------------------------------
# Cleanup Function: offset 0x80
# Called immediately by webdll:
#   $a0 = 0x12345678 (magic constant)
#   $a1 = 0x805f1648 (interface pointer)
#   $ra = return address to webdll (MIPS16 tagged address)
# Returns:
#   $v0 = 0 (status)
# -------------------------------------------------------------
cleanup_func:
    move    $t9, $ra            # 0x80: preserve caller return address
    bal     cleanup_get_pc      # 0x84: PC-relative branch-and-link
    nop                         # 0x88: branch delay slot
cleanup_get_pc:
    move    $t0, $ra            # 0x8c: $t0 = address of cleanup_get_pc
    addiu   $t1, $t0, (mailbox - cleanup_get_pc) # 0x90: $t1 = mailbox address
    
    lui     $t2, 0x434c         # 0x94: "CL"
    ori     $t2, $t2, 0x4e50    # 0x98: "NP" -> "CLNP"
    sw      $t2, 20($t1)        # 0x9c: mailbox[5] = stage 2 magic
    
    lui     $t2, 0x3333         # 0xa0
    ori     $t2, $t2, 0x4444    # 0xa4: nonce 0x33334444
    sw      $t2, 24($t1)        # 0xa8: mailbox[6] = stage 2 nonce
    sw      $a0, 28($t1)        # 0xac: mailbox[7] = captured $a0
    sw      $a1, 32($t1)        # 0xb0: mailbox[8] = captured $a1
    
    lui     $t2, 0x5355         # 0xb4: "SU"
    ori     $t2, $t2, 0x4343    # 0xb8: "CC" -> "SUCC"
    sw      $t2, 36($t1)        # 0xbc: mailbox[9] = confirmation flag
    
    li      $v0, 0              # 0xc0: return 0
    move    $ra, $t9            # 0xc4: restore caller return address
    jr      $ra                 # 0xc8: return to webdll
    nop                         # 0xcc: delay slot

.org 0x200                      # Mailbox reservation at offset 512 (0x200)
mailbox:
    .space 64                   # 64 bytes
"""

def build_payload(root_dir: Path, out_dir: Path) -> dict:
    tool_bin = root_dir / ".local/askey-net-006/analysis/cli-agent/usr/bin"
    tool_lib = root_dir / ".local/askey-net-006/analysis/cli-agent/usr/lib/x86_64-linux-gnu"
    as_path = tool_bin / "mips-linux-gnu-as"
    objcopy_path = tool_bin / "mips-linux-gnu-objcopy"
    objdump_path = tool_bin / "mips-linux-gnu-objdump"
    
    assert as_path.exists(), f"Assembler not found at {as_path}"
    assert objcopy_path.exists(), f"Objcopy not found at {objcopy_path}"
    assert objdump_path.exists(), f"Objdump not found at {objdump_path}"
    
    env = dict(os.environ, LD_LIBRARY_PATH=str(tool_lib))
    out_dir.mkdir(parents=True, exist_ok=True)
    
    src_file = out_dir / "payload.s"
    obj_file = out_dir / "payload.o"
    bin_file = out_dir / "payload.bin"
    dis_file = out_dir / "payload.dis"
    
    src_file.write_text(PAYLOAD_ASM)
    
    subprocess.check_call([str(as_path), "-EB", "-mips32r2", "-o", str(obj_file), str(src_file)], env=env)
    subprocess.check_call([str(objcopy_path), "-O", "binary", "-j", ".text", str(obj_file), str(bin_file)], env=env)
    
    dis_out = subprocess.check_output([str(objdump_path), "-d", str(obj_file)], env=env, text=True)
    dis_file.write_text(dis_out)
    
    raw_bytes = bin_file.read_bytes()
    assert len(raw_bytes) == 576, f"Expected 576 bytes (512 code + 64 mailbox), got {len(raw_bytes)}"
    
    # Verify symbol offsets
    nm_path = tool_bin / "mips-linux-gnu-nm"
    nm_out = subprocess.check_output([str(nm_path), str(obj_file)], env=env, text=True)
    symbols = {}
    for line in nm_out.splitlines():
        parts = line.strip().split()
        if len(parts) >= 3:
            addr, sym_type, name = parts[0], parts[1], parts[2]
            symbols[name] = int(addr, 16)
            
    assert symbols.get("entry_func") == 0x00, f"entry_func at 0x{symbols.get('entry_func', 0):x}, expected 0x00"
    assert symbols.get("cleanup_func") == 0x80, f"cleanup_func at 0x{symbols.get('cleanup_func', 0):x}, expected 0x80"
    assert symbols.get("mailbox") == 0x200, f"mailbox at 0x{symbols.get('mailbox', 0):x}, expected 0x200"
    
    # Verify relocations: PIC code must have zero relocations
    readelf_path = tool_bin / "mips-linux-gnu-readelf"
    rel_out = subprocess.check_output([str(readelf_path), "-r", str(obj_file)], env=env, text=True)
    assert "There are no relocations in this file." in rel_out, "Payload contains unexpected relocations"
    
    # Extract active store instructions
    entry_words = [struct.unpack_from(">I", raw_bytes, i)[0] for i in range(0x00, 0x48, 4)]
    cleanup_words = [struct.unpack_from(">I", raw_bytes, i)[0] for i in range(0x80, 0xd0, 4)]
    
    sha256 = hashlib.sha256(raw_bytes).hexdigest()
    
    return {
        "binary_size": len(raw_bytes),
        "code_size": 512,
        "mailbox_size": 64,
        "entry_offset": 0x00,
        "entry_instructions": len(entry_words),
        "cleanup_offset": 0x80,
        "cleanup_instructions": len(cleanup_words),
        "mailbox_offset": 0x200,
        "sha256": sha256,
        "entry_words": entry_words,
        "cleanup_words": cleanup_words,
        "obj_file": str(obj_file),
        "bin_file": str(bin_file),
        "dis_file": str(dis_file)
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default=".local/native-payload", help="Output directory in .local/")
    args = parser.parse_args()
    
    root_dir = Path(__file__).resolve().parents[1]
    out_dir = (root_dir / args.out_dir).resolve()
    assert out_dir.is_relative_to((root_dir / ".local").resolve()), "Output must remain in ignored .local/"
    
    res = build_payload(root_dir, out_dir)
    print("MIPS32 webdll entry/cleanup payload built successfully.")
    print(f"Total binary: {res['binary_size']} bytes (SHA-256: {res['sha256']})")
    print(f"  entry_func:   offset 0x{res['entry_offset']:02x} ({res['entry_instructions']} instructions, {res['entry_instructions']*4} bytes)")
    print(f"  cleanup_func: offset 0x{res['cleanup_offset']:02x} ({res['cleanup_instructions']} instructions, {res['cleanup_instructions']*4} bytes)")
    print(f"  mailbox:      offset 0x{res['mailbox_offset']:03x} ({res['mailbox_size']} bytes)")
    print(f"Disassembly saved to {res['dis_file']}")

if __name__ == "__main__":
    main()
