import sys,struct,json; sys.path.insert(0,'tools')
from common import *; from disasm import parse
sc=scripts(); rows=[]; uniq={}
for i,b in enumerate(sc):
  h,ins=parse(b)
  for p,w,r in ins:
    op=w&0xff
    if op in (0x16,0x1f):
      ln=struct.unpack_from('<I',r,4)[0]
      ws=struct.unpack('<%dH'%(ln//2),r[8:8+ln])
      # 0x8000 종료 뒤 패딩 제거
      e=ws.index(0x8000)
      t=dec(ws[:e])
      assert all(x==0 for x in ws[e+1:]),(i,p,ws)
      rows.append({'s':i,'off':p,'op':op,'ja':t})
      uniq.setdefault(t,len(uniq))
json.dump(rows,open('trans/script_rows.json','w',encoding='utf8'),ensure_ascii=False,indent=0)
print(len(rows),len(uniq),sum(len(t) for t in uniq))
