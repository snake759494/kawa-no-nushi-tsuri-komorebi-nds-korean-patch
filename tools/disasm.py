import struct,collections
def parse(b):
    """[SCR103] 헤더 16바이트 뒤 명령 목록: (off, op, size, raw)"""
    assert b[:8]==b'[SCR103]',b[:8]
    hdr=b[8:12]
    out=[];p=12
    while p<len(b):
        w=struct.unpack_from('<I',b,p)[0]
        op=w&0xff; sz=(w>>8)&0xff
        if op in (0x16,0x1f):
            ln=struct.unpack_from('<I',b,p+4)[0]
            size=8+ln
        else:
            size=sz
        if size==0: raise ValueError('zero size at %x op %x'%(p,w))
        out.append((p,w,b[p:p+size])); p+=size
    return hdr,out
