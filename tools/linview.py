import sys
from PIL import Image
d=open(sys.argv[1],'rb').read()[int(sys.argv[2],0):int(sys.argv[2],0)+int(sys.argv[5],0)]
w=int(sys.argv[3]); bpp=int(sys.argv[4])
px=[]
for b in d:
  for k in range(8//bpp): px.append((b>>(k*bpp))&((1<<bpp)-1))
h=len(px)//w
im=Image.new('L',(w,h)); im.putdata([255-min(v,3)*85 for v in px[:w*h]])
cols=int(sys.argv[7]) if len(sys.argv)>7 else 1
if cols>1:
  ch=(h+cols-1)//cols; out=Image.new('L',(w*cols+cols*4,ch),128)
  for c in range(cols): out.paste(im.crop((0,c*ch,w,c*ch+ch)),(c*(w+4),0))
  im=out
im.resize((im.width*2,im.height*2),0).save(sys.argv[6])
