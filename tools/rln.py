"""rln: ARM9 0x02097f90의 RLE. 같은 바이트가 두 번 연속되면 다음 바이트가 추가 반복 횟수."""
import struct

def decode(src):
    out=bytearray(); prev=(src[0]+1)&0xff; i=0; n=len(src)
    while i<n:
        b=src[i]
        if b==prev:
            out.append(b); cnt=src[i+1]; out+=bytes([b])*cnt
            i+=1
            prev=(src[i+1]+1)&0xff if i+1<n else -1
        else:
            out.append(b); prev=b
        i+=1
    return bytes(out)

def encode(data):
    out=bytearray(); i=0; n=len(data)
    while i<n:
        b=data[i]; j=i
        while j<n and data[j]==b and j-i<257: j+=1
        run=j-i
        if run>=2:
            out+=bytes([b,b,run-2]); i=j
            # 다음 바이트가 run 뒤 비교값과 같아도 해제기는 (count+1... ) 규칙상 다음 바이트와 비교값이
            # (다음바이트+1)이므로 항상 리터럴로 처리된다.
        else:
            out.append(b); i+=1
    return bytes(out)

def entries(data):
    """arc 형식: [이름8][a][b][type u16][size u32][패딩16][데이터 size]..."""
    out=[];p=0
    while p+0x20<=len(data):
        name=data[p:p+8].split(b'\0')[0].decode('latin1')
        a,b,t,sz=struct.unpack_from('<BBHI',data,p+8)
        if sz==0 or p+0x20+sz>len(data)+0x20: break
        out.append({'name':name,'a':a,'b':b,'type':t,'size':sz,'off':p+0x20})
        p+=0x20+sz
    return out
