"""원본 ROM에서 작업용 파일을 ext/로 꺼낸다(ARM9, 대사·메시지·폰트 파일)."""
import ndspy.rom,os,sys,glob
src=sys.argv[1] if len(sys.argv)>1 else glob.glob('../*(Japan).nds')[0]
r=ndspy.rom.NintendoDSRom.fromFile(src); os.makedirs('ext',exist_ok=True)
open('ext/arm9.bin','wb').write(r.arm9)
for n in ['script_data.bin','fon12_0s.arc','item_help_word.arc','work_memo_sysmes.arc','card_explanation.arc','common.arc']:
    open('ext/'+n,'wb').write(r.getFileByName(n))
print('ok')
