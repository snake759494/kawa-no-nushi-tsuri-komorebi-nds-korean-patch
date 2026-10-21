import sys,capstone
d=open('ext/arm9.bin','rb').read()
start=int(sys.argv[1],16); n=int(sys.argv[2],16); thumb=len(sys.argv)>3
md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB if thumb else capstone.CS_MODE_ARM)
for i in md.disasm(d[start:start+n],0x2000000+start):
    print('%08x  %-8s %s'%(i.address,i.mnemonic,i.op_str))
