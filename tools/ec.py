import sys,urllib.request
port=int(sys.argv[1]); path='/'+sys.argv[2]
data=open(sys.argv[3],'rb').read() if len(sys.argv)>3 else b'[]'
r=urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:%d%s'%(port,path),data=data,method='POST'),timeout=3000)
print(r.read().decode())
