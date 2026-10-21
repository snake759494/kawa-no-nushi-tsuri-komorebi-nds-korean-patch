import sys,os; sys.path.insert(0,'tools')
import layer,json,struct
from PIL import Image,ImageDraw
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pre=os.path.join(W,'dumps',sys.argv[1]); eng=sys.argv[2]
lays=[('obj'+eng,layer.obj_layer(pre,eng))]+[('bg%s%d'%(eng,i),layer.bg_layer(pre,eng,i)) for i in range(4)]
S=3; out=Image.new('RGB',(len(lays)*(256*S+10),192*S+20),(30,30,30)); dr=ImageDraw.Draw(out)
for k,(n,(loc,v,_)) in enumerate(lays):
    im=Image.new('RGB',(256,192),(255,0,255))
    for (x,y),(b,h) in loc.items():
        val=(v[b]>>(4*h))&15; im.putpixel((x,y),(255-val*16,255-val*16,255-val*16))
    im=im.resize((256*S,192*S),0); d2=ImageDraw.Draw(im)
    for g in range(0,256,16): d2.line([(g*S,0),(g*S,192*S)],fill=(0,160,255) if g%64 else (255,0,0))
    for g in range(0,192,16): d2.line([(0,g*S),(256*S,g*S)],fill=(0,160,255) if g%64 else (255,0,0))
    out.paste(im,(k*(256*S+10),20)); dr.text((k*(256*S+10),2),n,fill=(255,255,0))
out.save(os.path.join(W,'shots','ins_%s_%s.png'%(sys.argv[1],eng)))
