/* Seller simulation engine. Deterministic for a given seed.
   Works in the browser (window.SellerSim) and in node (module.exports). */
(function(root){
'use strict';
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return ((t^t>>>14)>>>0)/4294967296}}
function pad(n){return (n<10?'0':'')+n}
function ymd(d){return d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate())}
function addDays(d,n){var x=new Date(d);x.setDate(x.getDate()+n);return x}
function dm(d){return pad(d.getDate())+'/'+pad(d.getMonth()+1)}
function clamp(v,a,b){return Math.max(a,Math.min(b,v))}

var WEEKDAY=[1.10,0.94,0.96,0.99,1.01,1.06,1.14]; // Sun..Sat
function season(d){ // demand multiplier by calendar
  var m=d.getMonth(),day=d.getDate();
  var base=[0.82,0.88,0.95,0.97,1.0,0.98,0.96,0.97,1.02,1.08,1.28,1.32][m];
  if(m===10&&day>=24&&day<=30)base*=1.55;      // Black Friday week
  if(m===11&&day>=20)base*=0.75;                 // post-cutoff slump
  if(m===0&&day<=3)base*=0.6;
  return base;
}
var DEMAND_SHOCKS=['Ad account flagged for review','Main creator campaign ended','Algorithm change hit video reach','Competitor undercut price','Checkout bug in the shop app'];
var VIRALS=['Creator video went viral','Featured in a marketplace campaign','Flash sale picked up by the algorithm','Trending sound used our product'];
var PRODUCTION=['Factory QC rejected 40% of the batch','Supplier moved to a new production line','Raw material shortage at the factory'];

function simulate(opts){
  opts=opts||{};
  var seed=opts.seed|0||12345, start=opts.start, days=opts.days||420;
  var minMonthly=opts.minMonthly||50000, maxMonthly=opts.maxMonthly||200000;
  var rnd=mulberry32(seed);
  var gauss=function(){var u=1-rnd(),v=rnd();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v)};
  var ri=function(a,b){return a+Math.floor(rnd()*(b-a+1))};
  var rf=function(a,b){return a+rnd()*(b-a)};

  // --- state ---
  var capital=64000, ad=420, organic=4300, aov=9.4, unitCost=2.1, cpc=0.21, conv=0.034; var CREDIT=30000;
  var inventory=22000, onOrder=[]; var lastPO=-99; var trailingDemand=[]; // {arrive:index, units, note}
  var demandMul=1, demandUntil=-1, viralMul=1, viralUntil=-1;
  var events=[], out={}, list=[];
  var trailing=[]; // last 28 days revenue
  var skus=10, lowStockCount=1, unshipped=0, stockoutDays=0;
  // growth target: scale so monthly revenue grows from ~minMonthly*1.1 to ~maxMonthly*0.85 over the year
  var startMonthly=minMonthly*1.3, endMonthly=maxMonthly*0.78;
  var dailyGrowth=Math.pow(endMonthly/startMonthly,1/(days-60))-1; // compounding of organic base

  function avgDemandSafe(){return trailingDemand.length?trailingDemand.reduce(function(a,b){return a+b},0)/trailingDemand.length:2000}
  for(var i=0;i<days;i++){
    var d=addDays(start,i), key=ymd(d);
    // --- inbound stock ---
    for(var k=onOrder.length-1;k>=0;k--){ if(onOrder[k].arrive<=i){ inventory+=onOrder[k].units; capital-=onOrder[k].balance; events.push({d:key,t:'Stock arrived: '+onOrder[k].units.toLocaleString()+' units'+onOrder[k].note}); onOrder.splice(k,1);} }
    // --- shocks ---
    if(i>demandUntil&&rnd()<1/95){ demandMul=rf(0.42,0.68); demandUntil=i+ri(6,21); var reason=DEMAND_SHOCKS[ri(0,DEMAND_SHOCKS.length-1)]; events.push({d:key,t:reason+' — sales down '+Math.round((1-demandMul)*100)+'% for '+(demandUntil-i)+' days',kind:'drop'}); }
    if(i>demandUntil)demandMul+= (1-demandMul)*0.35; // recover
    if(i>viralUntil&&rnd()<1/70){ viralMul=rf(1.7,3.1); viralUntil=i+ri(2,5); events.push({d:key,t:VIRALS[ri(0,VIRALS.length-1)]+' — traffic ×'+viralMul.toFixed(1),kind:'spike'}); }
    if(i>viralUntil)viralMul+= (1-viralMul)*0.5;
    // --- demand ---
    organic*=1+dailyGrowth+gauss()*0.004;
    var adVisitors=ad/cpc;
    var visitors=Math.round((organic+adVisitors)*WEEKDAY[d.getDay()]*season(d)*demandMul*viralMul*(1+gauss()*0.07));
    var cr=conv*(1+gauss()*0.08)*(viralMul>1.2?0.85:1);
    var demandOrders=Math.round(visitors*cr);
    var unitsPerOrder=1.6;
    var demandUnits=Math.round(demandOrders*unitsPerOrder);
    // --- supply constraint ---
    var fill=inventory>=demandUnits?1:(demandUnits?inventory/demandUnits:1);
    if(fill<1&&inventory===0&&!(out[ymd(addDays(d,-1))]&&out[ymd(addDays(d,-1))].stockout)) events.push({d:key,t:'Stockout — best sellers sold out, orders capped',kind:'stockout'});
    var units=Math.min(demandUnits,inventory);
    stockoutDays=fill<0.5?stockoutDays+1:0;
    if(stockoutDays===4&&capital+CREDIT>8000){var eq=Math.round(Math.max(20,avgDemandSafe()/aov*unitsPerOrder)*14);var ec=eq*unitCost*1.35;if(ec>(capital+CREDIT)*0.8){eq=Math.floor((capital+CREDIT)*0.8/(unitCost*1.35));ec=eq*unitCost*1.35;}if(eq>0){onOrder.push({arrive:i+ri(6,10),units:eq,note:' (air freight)',balance:0});capital-=ec;events.push({d:key,t:'Emergency air-freight order: '+eq.toLocaleString()+' units at +35% cost',kind:'po'});}}
    var orders=Math.round(demandOrders*fill);
    var buyers=Math.round(orders*rf(0.93,0.985));
    inventory-=units;
    var revenue=Math.round(orders*aov*(1+gauss()*0.03)*100)/100;
    // --- finance ---
    var cogs=units*unitCost, fees=revenue*0.09, profit=revenue-cogs-fees-ad;
    capital+=profit;
    trailing.push(revenue); if(trailing.length>28)trailing.shift();
    trailingDemand.push(demandOrders*aov); if(trailingDemand.length>28)trailingDemand.shift();
    var avgRev=trailing.reduce(function(a,b){return a+b},0)/trailing.length;
    var avgDemand=trailingDemand.reduce(function(a,b){return a+b},0)/trailingDemand.length;
    // reinvest: ad budget follows 11-14% of demand revenue, paused during stockouts, capped by cash
    var adTarget=avgDemand*rf(0.11,0.14)*(fill<0.4?0.25:1); ad+= (adTarget-ad)*0.08; ad=clamp(ad,150,Math.max(150,(capital+CREDIT)*0.03));
    cpc*=1+gauss()*0.004+0.0002; aov=clamp(aov*(1+gauss()*0.002+0.0002),7.5,14.5); conv=clamp(conv*(1+gauss()*0.003),0.026,0.052);
    // --- purchasing with lead times ---
    var dailyUnits=Math.max(20,avgDemand/aov*unitsPerOrder*(1+dailyGrowth*30));
    var cover=(inventory+onOrder.reduce(function(a,o){return a+o.units},0))/dailyUnits;
    if(cover<42&&i-lastPO>=5){ lastPO=i;
      var lead=ri(16,34), note='', long=rnd()<0.22;
      if(long){lead=ri(45,78);note=' (long lead)';}
      var qty=Math.round(dailyUnits*ri(28,45));
      var cost=qty*unitCost, deposit=cost*0.3;
      if(deposit>(capital+CREDIT)*0.6){qty=Math.max(0,Math.floor((capital+CREDIT)*0.6/(unitCost*0.3)));cost=qty*unitCost;deposit=cost*0.3;note+=' (cash limited)';}
      if(qty>0){
        var ev={d:key,t:'PO placed: '+qty.toLocaleString()+' units, lead time '+lead+' days'+(long?' — supplier long lead':''),kind:long?'lead':'po'};
        if(rnd()<0.16){var p=PRODUCTION[ri(0,PRODUCTION.length-1)];var cut=rnd()<0.5;if(cut){qty=Math.round(qty*0.6);note+=' (short batch)';}else{lead+=ri(10,22);note+=' (delayed)';}ev.t+=' — '+p;ev.kind='production';}
        onOrder.push({arrive:i+lead,units:qty,note:note,balance:qty*unitCost*0.7});capital-=deposit;events.push(ev);
      }
    }
    lowStockCount=clamp(Math.round((1-clamp(cover/30,0,1))*skus*0.6+(fill<1?3:0)),0,skus);
    unshipped=Math.round(orders*rf(0.25,0.45)+(out[ymd(addDays(d,-1))]?out[ymd(addDays(d,-1))].orders*rf(0.03,0.12):0));
    var rec={income:revenue,orders:orders,buyers:buyers,visitors:visitors,sold:units,ad:Math.round(ad),capital:Math.round(capital),inventory:inventory,stockout:fill<1,lowStock:lowStockCount,ship:unshipped,
      liveShare:clamp(0.16+gauss()*0.03,0.05,0.3),videoShare:clamp(0.46+gauss()*0.04,0.3,0.6),impressions:Math.round(visitors*rf(6.5,9.5)),videoViews:Math.round(visitors*rf(14,26))};
    out[key]=rec; list.push(key);
  }
  return {days:out,keys:list,events:events,seed:seed};
}
/* intraday progression: fraction of the day's total reached at a given hour (shopping peaks evening) */
function intraday(hour,minute){
  var h=hour+minute/60; var w=[0.6,0.4,0.3,0.25,0.25,0.35,0.6,0.9,1.1,1.2,1.25,1.3,1.35,1.3,1.25,1.3,1.4,1.55,1.75,1.9,1.85,1.6,1.2,0.85];
  var total=w.reduce(function(a,b){return a+b},0),acc=0;
  for(var i=0;i<24;i++){ if(h>=i+1)acc+=w[i]; else if(h>i){acc+=w[i]*(h-i);break} else break; }
  return acc/total;
}
var api={simulate:simulate,intraday:intraday,ymd:ymd,addDays:addDays};
if(typeof module!=='undefined'&&module.exports)module.exports=api; else root.SellerSim=api;
})(typeof window!=='undefined'?window:this);
