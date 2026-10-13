const S=require(require('path').resolve(process.argv[2]));
const seeds=[12345,7,99,2026];
for(const seed of seeds){
  const start=new Date(2025,7,20); // 420 days before ~13 Oct 2026
  const r=S.simulate({seed,start,days:420});
  const months={};
  for(const k of r.keys){const m=k.slice(0,7);months[m]=months[m]||{rev:0,orders:0,vis:0,n:0,so:0};const v=r.days[k];months[m].rev+=v.income;months[m].orders+=v.orders;months[m].vis+=v.visitors;months[m].n++;if(v.stockout)months[m].so++;}
  console.log('\nSEED',seed);
  for(const m of Object.keys(months)){const x=months[m];console.log(m,'rev £'+Math.round(x.rev).toLocaleString().padStart(8),'orders',String(x.orders).padStart(5),'visitors',String(x.vis).padStart(6),'days',x.n,'stockoutDays',x.so)}
  const last=r.days[r.keys[r.keys.length-1]];console.log('last day',JSON.stringify(last));
  console.log('events',r.events.length);for(const e of r.events.slice(-12))console.log(' ',e.d,e.t);
}
