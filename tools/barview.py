"""스프라이트 시트를 32x16(타일 8개) 블록 단위로 가로 배치해 보기. 블록 좌표 → 바이트 매핑 제공."""
import sys; sys.path.insert(0,'tools')
def bar_px(raw,per_row,X,Y,first=0):
    """화면 좌표(X,Y) → (바이트 오프셋, 니블)."""
    row=Y//16; blk=first+row*per_row+X//32
    tx=(X%32)//8; ty=(Y%16)//8
    t=blk*8+ty*4+tx
    o=t*32+(Y%8)*4+(X%8)//2
    return o,X&1
def render(raw,per_row,first=0):
    from PIL import Image
    nblk=(len(raw)//256-first); rows=(nblk+per_row-1)//per_row
    im=Image.new('L',(per_row*32,rows*16),255)
    for Y in range(rows*16):
        for X in range(per_row*32):
            o,h=bar_px(raw,per_row,X,Y,first)
            if o<len(raw): im.putpixel((X,Y),255-((raw[o]>>(4*h))&15)*16)
    return im
