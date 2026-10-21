import re,json
d=open('ext/arm9.bin','rb').read()
pat=re.compile(rb'(?:[\x81-\x9f\xe0-\xef][\x40-\x7e\x80-\xfc]|[\x20-\x7e\n]){1,}\x00')
res=[]
for m in pat.finditer(d):
    b=m.group()[:-1]
    if m.start()<0x100000 or m.start()>=0x122ac4 and m.start()<0x1231e6: continue
    if m.start()%4!=0 and d[m.start()-1]!=0: continue
    try: s=b.decode('cp932')
    except: continue
    jp=sum(1 for ch in s if 0x3040<=ord(ch)<=0x30ff or 0x4e00<=ord(ch)<=0x9fff or 0xff00<=ord(ch)<=0xffef or ch in '・ー。、？！…「」')
    if jp<1 or jp<len(s)*0.5: continue
    res.append((m.start(),len(b),s))
json.dump(res,open('trans/arm9_sjis_raw.json','w',encoding='utf8'),ensure_ascii=False,indent=0)
print(len(res))
with open('trans/arm9_sjis_raw.txt','w',encoding='utf8') as f:
    for o,l,s in res: f.write('%x\t%d\t%s\n'%(o,l,s.replace('\n','\n')))
