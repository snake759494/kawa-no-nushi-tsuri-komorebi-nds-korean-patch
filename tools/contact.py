import os,sys
from PIL import Image,ImageDraw
fs=sorted(os.listdir('gfxview'))
skip=tuple(sys.argv[1].split(',')) if len(sys.argv)>1 else ()
items=[]
for f in fs:
    if f.startswith(skip) or f.startswith('ov_'): continue
    im=Image.open('gfxview/'+f).convert('RGB')
    px=im.load(); W,H=im.size
    mask=Image.new('L',im.size,0); mp=mask.load()
    for y in range(H):
        for x in range(W):
            if px[x,y]!=(255,0,255): mp[x,y]=255
    bb=mask.getbbox()
    if not bb: continue
    items.append((f,im.crop(bb)))
os.makedirs('gfxview/ov',exist_ok=True)
page=0;x=y=0;rowh=0;out=Image.new('RGB',(1024,1024),(40,40,40));dr=ImageDraw.Draw(out)
for f,im in items:
    w,h=im.size
    if w>1000: im=im.crop((0,0,1000,h)); w=1000
    if x+w>1024: x=0;y+=rowh+12;rowh=0
    if y+h+12>1024:
        out.save('gfxview/ov/ov_%02d.png'%page);page+=1
        out=Image.new('RGB',(1024,1024),(40,40,40));dr=ImageDraw.Draw(out);x=y=0;rowh=0
    dr.text((x,y),f[:40],fill=(255,255,0))
    out.paste(im,(x,y+10)); x+=max(w,len(f[:40])*6)+6; rowh=max(rowh,h)
out.save('gfxview/ov/ov_%02d.png'%page)
print(page+1,len(items))
