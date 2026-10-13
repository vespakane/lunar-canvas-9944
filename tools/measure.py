import sys
from PIL import Image
S=3.0
def pt(v): return round(v/S,1)
def runs(flags):
    out=[];start=None
    for i,f in enumerate(flags):
        if f and start is None: start=i
        if not f and start is not None: out.append((start,i-1)); start=None
    if start is not None: out.append((start,len(flags)-1))
    return out
def analyze(path, x0=None, x1=None, y0=0, y1=None):
    im=Image.open(path).convert('RGB'); W,H=im.size
    px=im.load()
    x0 = x0 if x0 is not None else 0
    x1 = x1 if x1 is not None else W
    y1 = y1 if y1 is not None else H
    print("==",path.split('/')[-1], "cols",x0,x1,"->pt",pt(x0),pt(x1))
    # row classification: background colour at col x0+? ; text rows contain dark pixels
    dark=[]; 
    for y in range(y0,y1):
        d=False
        for x in range(x0,x1):
            r,g,b=px[x,y]
            if r+g+b<450: d=True;break
        dark.append(d)
    for a,b in runs(dark):
        a+=y0;b+=y0
        if b-a>=3: print(f"  text/ink rows {a}-{b}  pt {pt(a)}-{pt(b)}  h={pt(b-a+1)} center={pt((a+b)/2)}")
def bg_runs(path, x, y0=0, y1=None, tol=6):
    im=Image.open(path).convert('RGB'); W,H=im.size; px=im.load()
    y1=y1 or H
    print("== bg column x=",x,"pt",pt(x), path.split('/')[-1])
    cur=None; start=y0
    for y in range(y0,y1):
        c=px[x,y]
        if cur is None: cur=c; start=y; continue
        if max(abs(c[i]-cur[i]) for i in range(3))>tol:
            if y-start>=4: print(f"  {start}-{y-1} pt {pt(start)}-{pt(y-1)} color #{cur[0]:02x}{cur[1]:02x}{cur[2]:02x}")
            cur=c; start=y
    print(f"  {start}-{y1-1} pt {pt(start)}-{pt(y1-1)} color #{cur[0]:02x}{cur[1]:02x}{cur[2]:02x}")
def col_runs(path, y, x0=0, x1=None, tol=6):
    im=Image.open(path).convert('RGB'); W,H=im.size; px=im.load()
    x1=x1 or W
    print("== bg row y=",y,"pt",pt(y), path.split('/')[-1])
    cur=None; start=x0
    for x in range(x0,x1):
        c=px[x,y]
        if cur is None: cur=c; start=x; continue
        if max(abs(c[i]-cur[i]) for i in range(3))>tol:
            if x-start>=3: print(f"  {start}-{x-1} pt {pt(start)}-{pt(x-1)} color #{cur[0]:02x}{cur[1]:02x}{cur[2]:02x}")
            cur=c; start=x
    print(f"  {start}-{x1-1} pt {pt(start)}-{pt(x1-1)} color #{cur[0]:02x}{cur[1]:02x}{cur[2]:02x}")
def ink_cols(path, y0, y1, x0=0, x1=None, thr=450):
    im=Image.open(path).convert('RGB'); W,H=im.size; px=im.load()
    x1=x1 or W
    flags=[]
    for x in range(x0,x1):
        d=False
        for y in range(y0,y1):
            r,g,b=px[x,y]
            if r+g+b<thr: d=True;break
        flags.append(d)
    print("== ink cols rows",y0,y1, path.split('/')[-1])
    for a,b in runs(flags):
        a+=x0;b+=x0
        if b-a>=2: print(f"  x {a}-{b} pt {pt(a)}-{pt(b)} w={pt(b-a+1)}")
def color(path,x,y):
    im=Image.open(path).convert('RGB'); c=im.getpixel((x,y)); print(path.split('/')[-1],x,y,'#%02x%02x%02x'%c)
if __name__=='__main__':
    cmd=sys.argv[1]; p=sys.argv[2]; args=[int(a) for a in sys.argv[3:]]
    globals()[cmd](p,*args)
