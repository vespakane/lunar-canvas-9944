import sys
from PIL import Image
def rows(path,x0,x1,y0,y1,thr=450):
    im=Image.open(path).convert('RGB');px=im.load();out=[];start=None
    for y in range(y0,y1):
        d=any(sum(px[x,y])<thr for x in range(x0,x1))
        if d and start is None:start=y
        if not d and start is not None:
            if y-start>=3: out.append((start,y-1))
            start=None
    return out
ref,ren,x0,x1,y0,y1=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6])
a=rows(ref,x0,x1,y0,y1);b=rows(ren,x0,x1,y0,y1)
print(f"{'REF rows (pt)':34s} | RENDER rows (pt)")
for i in range(max(len(a),len(b))):
    ra=a[i] if i<len(a) else None; rb=b[i] if i<len(b) else None
    fa=f"{ra[0]/3:6.1f}-{ra[1]/3:6.1f} c={(ra[0]+ra[1])/6:6.1f}" if ra else ' '*27
    fb=f"{rb[0]/3:6.1f}-{rb[1]/3:6.1f} c={(rb[0]+rb[1])/6:6.1f}" if rb else ''
    d=f"  Δc={(rb[0]+rb[1])/6-(ra[0]+ra[1])/6:+.1f}" if ra and rb else ''
    print(f"{fa:34s} | {fb}{d}")
