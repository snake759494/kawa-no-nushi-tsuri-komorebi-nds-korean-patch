import struct
ARM9='ext/arm9.bin'
def table():
    d=open(ARM9,'rb').read()
    s=0x122ac4; e=d.find(b'\x00',s)
    return d[s:e].decode('cp932')
TBL=table()
def dec(words):
    t=''
    for c in words:
        if c>=0x8000: t+='{%x}'%c
        elif c<len(TBL): t+=TBL[c]
        else: t+='[%x]'%c
    return t
def scripts():
    d=open('ext/script_data.bin','rb').read()
    n=struct.unpack_from('<I',d,0)[0]
    return [d[o:o+s] for o,s in (struct.unpack_from('<2I',d,4+8*i) for i in range(n))]
