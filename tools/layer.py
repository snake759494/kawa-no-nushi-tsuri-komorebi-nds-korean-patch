"""덤프(emusrv oamdump)로 화면 레이어를 합성: 픽셀 → (VRAM 바이트, 니블). 스프라이트/BG 공통."""
import json,struct,os
SIZES={0:[(8,8),(16,16),(32,32),(64,64)],1:[(16,8),(32,8),(32,16),(64,32)],2:[(8,16),(8,32),(16,32),(32,64)]}

def obj_layer(prefix,eng):
    d=json.load(open(prefix+'.json'))[eng]; v=open(prefix+'_%s_vram.bin'%eng,'rb').read()
    dc=d['dispcnt']; one_d=(dc>>4)&1; bnd=32<<((dc>>20)&3)
    loc={}; blocks=[]
    for s in d['sprites']:
        if s['bpp8']: continue
        w,h=SIZES[s['shape']][s['size']]
        base=s['tile']*(bnd if one_d else 32); blocks.append((base,w*h//2))
        for ty in range(h//8):
            for tx in range(w//8):
                toff=base+((ty*(w//8)+tx)*32 if one_d else (ty*32+tx)*32)
                for y in range(8):
                    for x in range(8):
                        b=toff+y*4+x//2; val=(v[b]>>(4*(x&1)))&15
                        X=(s['x']+tx*8+x)&511; Y=(s['y']+ty*8+y)&255
                        if X<256 and Y<192 and (X,Y) not in loc or (X<256 and Y<192 and val and v[loc[(X,Y)][0]]>>(4*loc[(X,Y)][1])&15==0): loc[(X,Y)]=(b,x&1)
    return loc,v,blocks

def bg_layer(prefix,eng,bgno):
    d=json.load(open(prefix+'.json'))['bg'][eng]; v=open(prefix+'_%s_bgvram.bin'%eng,'rb').read()
    dc=d['dispcnt']; cnt=d['bgcnt'][bgno]
    if not (dc>>(8+bgno))&1: return {},v,[]
    cb=((cnt>>2)&15)*0x4000; sb=((cnt>>8)&31)*0x800
    if eng=='A': cb+=((dc>>24)&7)*0x10000; sb+=((dc>>27)&7)*0x10000
    bpp8=(cnt>>7)&1; size=cnt>>14
    W=[256,512,256,512][size]//8
    loc={}; blocks=[]
    for ty in range(24):
        for tx in range(32):
            blk=(tx//32)+(ty//32)*(W//32)
            e=struct.unpack_from('<H',v,sb+blk*0x800+((ty%32)*32+(tx%32))*2)[0]
            t=e&0x3ff; hf=(e>>10)&1; vf=(e>>11)&1
            if bpp8: continue
            toff=cb+t*32
            if toff+32>len(v): continue
            for y in range(8):
                for x in range(8):
                    sx=7-x if hf else x; sy=7-y if vf else y
                    b=toff+sy*4+sx//2; val=(v[b]>>(4*(sx&1)))&15
                    loc[(tx*8+x,ty*8+y)]=(b,sx&1)
    return loc,v,blocks
