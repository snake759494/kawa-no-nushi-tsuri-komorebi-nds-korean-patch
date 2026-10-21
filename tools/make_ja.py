"""원본 ROM에서 빌드에 필요한 일본어 원문 목록(trans/ja_all.txt, trans/script_rows.json)을 다시 만든다.
사용: python -X utf8 tools/extract_script.py && python -X utf8 tools/make_ja.py"""
import json
rows=json.load(open('trans/script_rows.json',encoding='utf8'))
uniq={};order=[]
for r in rows:
    if r['ja'] not in uniq: uniq[r['ja']]=len(order); order.append(r)
with open('trans/ja_all.txt','w',encoding='utf8') as f:
    for i,r in enumerate(order): f.write('%d\t%d\t%s\n'%(i,r['s'],r['ja']))
print(len(order))
