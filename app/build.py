import re,base64,os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
s=open('src.html').read()
s=s.replace('<script src="sim.js"></script>','<script>\n'+open('sim.js').read()+'\n</script>')
s=re.sub(r'url\((fonts/[^)]+)\)',lambda m:'url(data:font/woff2;base64,'+base64.b64encode(open(m.group(1),'rb').read()).decode()+')',s)
s=re.sub(r'src="(img/[^"]+)"',lambda m:'src="data:image/png;base64,'+base64.b64encode(open(m.group(1),'rb').read()).decode()+'"',s)
open('index.html','w').write(s); print('index.html built',len(s),'bytes')
