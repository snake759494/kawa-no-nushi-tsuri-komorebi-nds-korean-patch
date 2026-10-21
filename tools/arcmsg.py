import struct
def read(fn):
    h=open(fn,'rb').read()
    n=struct.unpack_from('<I',h,0x20)[0]; offs=list(struct.unpack_from('<%dI'%n,h,0x24)); base=0x24+4*n
    tot=(len(h)-base)//2
    ws=struct.unpack_from('<%dH'%tot,h,base)
    out=[]
    for i in range(n):
        e=offs[i+1] if i+1<n else tot
        out.append(list(ws[offs[i]:e]))
    return h[:0x20],out
