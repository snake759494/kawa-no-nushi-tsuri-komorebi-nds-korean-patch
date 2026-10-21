"""1D 32x32 스프라이트가 순서대로 이어 붙는 시트를 '스프라이트 순번 = 가로 위치'로 직접 패치."""
import rln,scrpatch
def loc_for(first,count,h=32):
    loc={}
    for i in range(count):
        for y in range(h):
            for x in range(32):
                t=(y//8)*4+x//8
                loc[(i*32+x,y)]=((first+i)*512+t*32+(y%8)*4+x//2,x&1)
    return loc
def patch(rom,fn,en,ops,etype=6):
    """ops: dict(first, count, box(x0,y0,x1,y1 in strip px), text, size, font, keep, fill, aa, outline, center)"""
    d=bytes(rom.getFileByName(fn)); comp=fn.endswith('.rln')
    if comp: d=rln.decode(d)
    d=bytearray(d)
    for e in rln.entries(bytes(d)):
        if e['name']!=en or e['type']!=etype: continue
        raw=bytearray(d[e['off']:e['off']+e['size']])
        for op in ops:
            loc=loc_for(op['first'],op['count'])
            item={'box':list(op['box']),'text':op['text'],'size':op.get('size',12),'center':op.get('center',True),'dy':op.get('dy',0)}
            if 'font' in op: item['font']=op['font']
            out=scrpatch.render_items(loc,bytes(raw),[item],tuple(op.get('keep',(1,9,12))),op.get('fill',1),op.get('aa',9),op.get('outline',12),'NanumSquareNeo-eHv.ttf',True)
            for (X,Y),val in out.items():
                b,hh=loc[(X,Y)]; raw[b]=(raw[b]&~(15<<(4*hh)))|(val<<(4*hh))
        d[e['off']:e['off']+e['size']]=raw
    rom.setFileByName(fn,rln.encode(bytes(d)) if comp else bytes(d))
