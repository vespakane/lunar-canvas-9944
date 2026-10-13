import sys
from PIL import Image
def cols(path,y0,y1,x0,x1,thr):
    im=Image.open(path).convert('RGB');px=im.load();out=[];start=None
    for x in range(x0,x1):
        d=any(sum(px[x,y])<thr for y in range(y0,y1))
        if d and start is None:start=x
        if not d and start is not None:
            if x-start>=2: out.append((start,x-1))
            start=None
    return out
ref,ren,y0,y1=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]); thr=int(sys.argv[5]) if len(sys.argv)>5 else 450
a=cols(ref,y0,y1,0,1206,thr);b=cols(ren,y0,y1,0,1206,thr)
def merge(r,gap=12):  # merge glyph runs into words
    out=[]
    for s,e in r:
        if out and s-out[-1][1]<=gap: out[-1]=(out[-1][0],e)
        else: out.append((s,e))
    return out
a=merge(a);b=merge(b)
print(f"rows {y0/3:.0f}-{y1/3:.0f}pt: {'REF words x (pt)':30s} | RENDER")
for i in range(max(len(a),len(b))):
    ra=a[i] if i<len(a) else None; rb=b[i] if i<len(b) else None
    fa=f"{ra[0]/3:6.1f}-{ra[1]/3:6.1f} w={(ra[1]-ra[0]+1)/3:5.1f}" if ra else ' '*22
    fb=f"{rb[0]/3:6.1f}-{rb[1]/3:6.1f} w={(rb[1]-rb[0]+1)/3:5.1f}" if rb else ''
    d=f"  Δx={(rb[0]-ra[0])/3:+.1f} Δw={((rb[1]-rb[0])-(ra[1]-ra[0]))/3:+.1f}" if ra and rb else ''
    print(f"  {fa:30s} | {fb}{d}")
