from PIL import Image
import os
OUT='app/img'
def bbox(im, region, bg_thr=235):
    x0,y0,x1,y1=region; px=im.load()
    xs=[];ys=[]
    for y in range(y0,y1):
        for x in range(x0,x1):
            r,g,b=px[x,y]
            if min(r,g,b)<bg_thr or max(abs(r-g),abs(g-b))>12:
                xs.append(x);ys.append(y)
    return (min(xs),min(ys),max(xs)+1,max(ys)+1)
def alpha_from_bg(im, box, bg, mode='mono'):
    """mode mono: dark icon on light bg -> black with alpha. mode color: unmix over bg (assume bg white-ish)."""
    crop=im.crop(box).convert('RGB'); w,h=crop.size
    out=Image.new('RGBA',(w,h)); src=crop.load(); dst=out.load()
    for y in range(h):
        for x in range(w):
            r,g,b=src[x,y]
            if mode=='mono':
                lum=(r+g+b)/3; a=max(0.0,min(1.0,1-lum/bg))
                dst[x,y]=(20,20,20,int(round(a*255)))
            else:
                m=min(r,g,b); a=1-m/bg
                if a<=0.01: dst[x,y]=(0,0,0,0); continue
                a=min(1.0,a)
                c=[int(max(0,min(255,(v-(1-a)*bg)/a))) for v in (r,g,b)]
                dst[x,y]=(c[0],c[1],c[2],int(round(a*255)))
    return out
def save(name, img, box):
    img.save(f'{OUT}/{name}.png')
    print(f"{name}: box px {box} -> pt x={box[0]/3:.2f} y={box[1]/3:.2f} w={(box[2]-box[0])/3:.2f} h={(box[3]-box[1])/3:.2f}")
h1=Image.open('IMG_0418.PNG').convert('RGB')
h2=Image.open('IMG_0419.PNG').convert('RGB')
d1=Image.open('IMG_0421.PNG').convert('RGB')
d2=Image.open('IMG_0422.PNG').convert('RGB')
d7=Image.open('IMG_0425.PNG').convert('RGB')
sh=Image.open('IMG_0428.PNG').convert('RGB')
mono=[ # name, image, region, bg
 ('gift',h1,(800,195,880,300),245),('help',h1,(1095,195,1175,300),245),('bell',h1,(935,215,1005,300),245),
 ('ic-overview',h1,(70,418,122,474),255),('ic-growth',h1,(72,785,122,842),255),('ic-ads',h1,(70,1475,122,1528),255),
 ('ic-accel',h1,(70,1648,122,1700),255),('ic-tasks',h1,(70,1820,122,1872),255),('ic-content',h1,(70,2200,122,2252),255),
 ('tab-home',h1,(120,2355,200,2440),255),('tab-products',h1,(345,2355,415,2440),255),('tab-orders',h1,(570,2355,640,2440),255),
 ('tab-chat',h1,(785,2355,865,2440),255),('tab-more',h1,(1005,2355,1090,2440),255),
 ('ic-campaigns',h2,(70,1375,122,1430),255),('ic-promos',h2,(70,1545,122,1605),255),('ic-discount',h2,(205,1680,275,1770),245),
 ('ic-flash',h2,(570,1680,640,1770),245),('ic-voucher',h2,(925,1680,1005,1770),245),('ic-opps',h2,(70,2020,122,2080),255),('ic-ratings',h2,(70,2195,122,2255),255),
 ('chev-right',h1,(1095,420,1130,470),255),('chev-back',d1,(60,205,105,300),248),('chev-down',d1,(250,390,285,440),248),
 ('chev-grey',d1,(1095,1750,1130,1800),255),('tri-up',d7,(80,870,112,892),255),('close-x',sh,(1105,1240,1160,1300),255),
 ('chev-viewall',d2,(1095,1310,1130,1350),255),
]
for name,im,region,bg in mono:
    box=bbox(im,region, bg_thr=bg-10); save(name, alpha_from_bg(im,box,bg,'mono'), box)
color=[('ic-ticket',h1,(120,1140,172,1188),247),('live',d1,(165,1945,245,2015),255),('videos',d1,(435,1945,505,2015),255),
 ('productcard',d1,(700,1945,770,2015),255),('market',d1,(965,1945,1040,2015),255),('video-illu',d1,(70,1725,170,1805),255),
 ('ai-btn',d1,(1020,2040,1206,2230),255),('badge',h1,(985,195,1045,245),245)]
for name,im,region,bg in color:
    box=bbox(im,region,bg_thr=bg-10); save(name, alpha_from_bg(im,box,bg,'color'), box)
# raw crops
box=(36,875,1169,1203); d2.crop(box).save(f'{OUT}/focus-card.png'); print('focus-card', box, [v/3 for v in box])
# colour sampling: darkest pixel in regions
def darkest(im,region,label):
    x0,y0,x1,y1=region; px=im.load(); best=(999,None)
    for y in range(y0,y1):
        for x in range(x0,x1):
            c=px[x,y]; s=sum(c)
            if s<best[0]: best=(s,c)
    print(label,'#%02x%02x%02x'%best[1])
darkest(h1,(75,497,780,532),'home updated grey')
darkest(h1,(174,639,300,665),'home label grey')
darkest(h1,(123,933,460,962),'expires grey')
darkest(h1,(503,1148,730,1180),'claimed grey')
darkest(h1,(189,1148,480,1180),'voucher blue')
darkest(h1,(320,2455,445,2490),'tab label grey')
darkest(h1,(120,2455,200,2490),'tab label active')
darkest(h1,(466,238,780,277),'title black')
darkest(d1,(507,268,700,295),'gmt grey')
darkest(d1,(74,720,200,755),'gmv label grey')
darkest(d1,(73,865,280,895),'yesterday grey')
darkest(d1,(76,555,360,600),'key metrics black')
darkest(d1,(60,1540,300,1580),'video diagnosis grey')
darkest(d1,(60,2300,420,2340),'focus grey')
darkest(d1,(60,2400,900,2440),'focus body grey')
darkest(d1,(92,385,240,435),'pill text')
darkest(d1,(250,390,285,440),'pill chevron')
darkest(d1,(60,758,200,770),'dotted underline')
darkest(d7,(118,870,150,895),'dash grey after triangle')
darkest(sh,(151,1400,280,1445),'sheet btn text')
darkest(sh,(1,1375,120,1470),'sheet btn border')
darkest(sh,(140,1850,720,1890),'wheel grey text')
darkest(sh,(140,1830,400,1850),'wheel grey text2')
darkest(sh,(1,1180,1206,1200),'sheet top row')
darkest(h1,(1000,1620,1100,1660),'badge red')
darkest(d1,(540,2440,1000,2470),'no data grey')
