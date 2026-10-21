import ndspy.rom,sys,struct
r=ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
for i,f in enumerate(r.files):
  n=r.filenames.filenameOf(i)
  if n and not n.endswith('.rln') and not n.startswith('map/') and not n.startswith('obj/'):
    print(n,len(f),f[:32].hex(' ',4))
