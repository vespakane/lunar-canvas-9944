import subprocess, sys, os
from PIL import Image, ImageChops
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SP=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out'); os.makedirs(SP,exist_ok=True)
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
def render(name, hash_):
    out=f'{SP}/r_{name}.png'
    url=f'file://{ROOT}/app/index.html?test=1#{hash_}'
    subprocess.run([CHROME,'--headless=new','--disable-gpu','--no-sandbox','--hide-scrollbars','--force-device-scale-factor=3','--window-size=402,874','--virtual-time-budget=6000',f'--screenshot={out}',url],capture_output=True)
    return out
def compare(name, ref, hash_, strip_top=0):
    out=render(name,hash_)
    a=Image.open(f'{ROOT}/{ref}').convert('RGB'); b=Image.open(out).convert('RGB')
    if a.size!=b.size: print('size mismatch',a.size,b.size); b=b.resize(a.size)
    # mask status bar region (top 59pt) in ref: copy from render so diff ignores it
    a2=a.copy(); a2.paste(b.crop((0,0,1206,177)),(0,0))
    d=ImageChops.difference(a2,b).convert('L').point(lambda v:255 if v>40 else 0)
    bbox=d.getbbox(); px=sum(1 for v in d.getdata() if v)
    print(f'{name}: differing px {px} ({px/(1206*2622)*100:.2f}%) bbox {bbox}')
    W=1206//2; H=2622//2
    sheet=Image.new('RGB',(W*3+20,H),(255,0,255))
    sheet.paste(a.resize((W,H)),(0,0)); sheet.paste(b.resize((W,H)),(W+10,0))
    dd=Image.merge('RGB',(d,ImageChops.invert(d).point(lambda v:v//2+128),ImageChops.invert(d).point(lambda v:v//2+128))).resize((W,H))
    sheet.paste(dd,(2*W+20,0)); sheet.save(f'{SP}/cmp_{name}.png')
    return out
if __name__=='__main__':
    for arg in sys.argv[1:]:
        name,ref,h=arg.split('|'); compare(name,ref,h)
