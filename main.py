import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="교과 SURVIVOR", page_icon="🎮", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.stApp { background:#111; color:#eee; }
.block-container { max-width:1100px; padding-top:1rem; padding-bottom:.5rem; }
h1 { color:#f2f2f2 !important; font-family:monospace; }
p, div { font-family:monospace; }
</style>
""", unsafe_allow_html=True)

st.title("교과 SURVIVOR")
st.write("이동: WASD / 방향키 · 대시: SPACE · 특수 스킬: Q / E / R / F · 일시정지: P")
st.caption("클래식한 아레나 생존 게임. 경험치를 모아 교과 스킬을 선택하고, 아래 스킬 칸에서 쿨타임을 확인해!")

game_html = r"""
<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<style>
*{box-sizing:border-box}body{margin:0;background:#111;color:#eee;font-family:monospace}
#wrap{max-width:1000px;margin:auto}
#top{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 7px}
.stat{background:#222;border:1px solid #555;padding:6px 10px;font-size:13px}
canvas{display:block;width:100%;height:auto;background:#171717;border:2px solid #aaa;image-rendering:pixelated}
#xpbg{height:8px;background:#333;margin-bottom:7px;border:1px solid #666}#xp{height:100%;width:0;background:#ddd}
#skills{display:grid;grid-template-columns:repeat(5,1fr);gap:6px;margin-top:7px}
.skill{background:#202020;border:1px solid #666;min-height:62px;padding:7px;position:relative;font-size:12px}
.skill b{font-size:14px;display:block;margin-bottom:3px}.skill .key{float:right;color:#fff;border:1px solid #aaa;padding:1px 5px}
.cool{height:4px;background:#444;margin-top:6px}.cool span{height:100%;display:block;background:#bbb;width:0}
#overlay{position:absolute;inset:0;background:#000d;display:flex;align-items:center;justify-content:center;padding:14px;z-index:5}
.hidden{display:none!important}.panel{width:min(640px,100%);background:#171717;border:2px solid #ddd;padding:20px;text-align:center}
.panel h2{margin:0 0 8px;font-size:26px}.panel p{line-height:1.5;color:#ddd}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.choice{background:#242424;border:1px solid #aaa;color:#fff;text-align:left;padding:12px;min-height:115px;cursor:pointer;font-family:monospace}
.choice:hover{background:#444}.choice strong{display:block;font-size:15px;margin:7px 0}.choice small{line-height:1.4;color:#ddd}
button.action{background:#eee;color:#111;border:1px solid white;padding:10px 18px;font-family:monospace;font-weight:bold;cursor:pointer}
#gamearea{position:relative}
@media(max-width:600px){.cards{grid-template-columns:1fr}.choice{min-height:0}#skills{grid-template-columns:repeat(2,1fr)}}
</style></head><body><div id="wrap">
<div id="top">
 <div class="stat">HP: <span id="hp">100</span></div><div class="stat">LV: <span id="lv">1</span></div>
 <div class="stat">KILLS: <span id="kills">0</span></div><div class="stat">TIME: <span id="time">0</span>s</div>
 <div class="stat">SUBJECT SKILLS: <span id="skillnum">0</span></div>
</div>
<div id="xpbg"><div id="xp"></div></div>
<div id="gamearea">
 <canvas id="game" width="960" height="540" tabindex="0"></canvas>
 <div id="overlay"><div class="panel" id="startpanel"><h2>교과 SURVIVOR</h2>
 <p>클래식 아레나 생존 게임<br>몬스터를 피하고 자동 공격으로 경험치를 모아라.<br><br>이동 WASD/방향키 · 대시 SPACE · 특수 스킬 Q/E/R/F</p>
 <button class="action" id="start">START GAME</button></div>
 <div class="panel hidden" id="levelpanel"><h2>LEVEL UP!</h2><p>교과 스킬 하나를 선택하세요.</p><div class="cards" id="choices"></div></div>
 <div class="panel hidden" id="pausepanel"><h2>PAUSED</h2><p>P 키를 누르면 계속합니다.</p><button class="action" id="resume">CONTINUE</button></div>
 <div class="panel hidden" id="overpanel"><h2>GAME OVER</h2><p id="result"></p><button class="action" id="again">RESTART</button></div>
 </div>
</div>
<div id="skills"></div>
</div>
<script>
(()=>{
const c=document.getElementById('game'),ctx=c.getContext('2d'),$=id=>document.getElementById(id),W=c.width,H=c.height;
let state='start',keys={},last=0,elapsed=0,spawnT=0,shotT=0,level=1,xp=0,xpNeed=5,pending=0,kills=0,skillNum=0,player,mobs=[],orbs=[],shots=[],effects=[],abilities=[],ownedSkills={},powerMultiplier=1;
const skillPool=[
 {subject:'국어',name:'속독',desc:'자동 공격 간격 감소',type:'passive',apply:p=>p.rate=Math.max(.18,p.rate*.84)},
 {subject:'국어',name:'문장 방패',desc:'최대 체력 +20, 체력 회복',type:'passive',apply:p=>{p.max+=20;p.hp=Math.min(p.max,p.hp+20)}},
 {subject:'국어',name:'낱말 폭탄',desc:'Q: 주변 적에게 피해',type:'active',key:'Q',cd:7,run:()=>blast(105,3,'#eee')},
 {subject:'수학',name:'곱셈 타격',desc:'투사체 피해 증가',type:'passive',apply:p=>p.damage+=1},
 {subject:'수학',name:'도형 관통',desc:'투사체 +1개',type:'passive',apply:p=>p.bullets=Math.min(5,p.bullets+1)},
 {subject:'수학',name:'피타고라스 파동',desc:'E: 원형 파동으로 피해',type:'active',key:'E',cd:9,run:()=>blast(160,4,'#ddd')},
 {subject:'영어',name:'빠른 회화',desc:'이동 속도 증가',type:'passive',apply:p=>p.speed+=.45},
 {subject:'영어',name:'퀵 리딩',desc:'R: 짧은 시간 무적 대시',type:'active',key:'R',cd:8,run:()=>{player.invuln=1.1;player.dash=0.3;effects.push({type:'ring',x:player.x,y:player.y,r:18,max:100,color:'#fff',life:20})}},
 {subject:'영어',name:'단어 폭격',desc:'자동 공격 사거리 증가',type:'passive',apply:p=>p.range+=45},
 {subject:'과학',name:'화학 반응',desc:'공격 속도 증가',type:'passive',apply:p=>p.rate=Math.max(.18,p.rate*.78)},
 {subject:'과학',name:'중력 실험',desc:'F: 주변 적을 밀어내고 피해',type:'active',key:'F',cd:10,run:()=>blast(180,2,'#aaa',true)},
 {subject:'과학',name:'에너지 보존',desc:'받는 피해 감소',type:'passive',apply:p=>p.armor=Math.min(.6,p.armor+.12)},
 {subject:'사회',name:'협력 네트워크',desc:'체력 회복 +25',type:'passive',apply:p=>p.hp=Math.min(p.max,p.hp+25)},
 {subject:'사회',name:'군중 심리',desc:'몬스터 생성 속도 감소',type:'passive',apply:p=>p.crowd=Math.min(1.5,p.crowd+.12)},
 {subject:'사회',name:'긴급 지원',desc:'Q: 체력 35 회복',type:'active',key:'Q',cd:12,run:()=>{player.hp=Math.min(player.max,player.hp+35);flash('#fff')}},
 {subject:'체육',name:'순발력',desc:'이동 속도 증가',type:'passive',apply:p=>p.speed+=.35},
 {subject:'체육',name:'스프린트',desc:'R: 빠르게 돌진하며 무적',type:'active',key:'R',cd:6,run:()=>{player.invuln=1;player.dash=.55;flash('#fff')}},
 {subject:'체육',name:'지구력',desc:'최대 체력 +30',type:'passive',apply:p=>{p.max+=30;p.hp+=30}},
 {subject:'정보',name:'알고리즘 최적화',desc:'투사체 속도와 피해 증가',type:'passive',apply:p=>{p.shotSpeed+=1;p.damage+=.5}},
 {subject:'정보',name:'버그 스캐너',desc:'E: 화면의 모든 적에게 피해',type:'active',key:'E',cd:13,run:()=>blast(1000,2,'#fff')},
 {subject:'정보',name:'멀티스레드',desc:'자동 공격 투사체 +1',type:'passive',apply:p=>p.bullets=Math.min(5,p.bullets+1)},
 {subject:'미술',name:'원근법',desc:'공격 사거리 증가',type:'passive',apply:p=>p.range+=55},
 {subject:'미술',name:'색채 폭발',desc:'F: 넓은 범위 공격',type:'active',key:'F',cd:11,run:()=>blast(210,3,'#ddd')},
 {subject:'미술',name:'정밀 묘사',desc:'투사체 크기 증가',type:'passive',apply:p=>p.shotSize+=2},
 {subject:'음악',name:'박자 감각',desc:'경험치 획득량 증가',type:'passive',apply:p=>p.xpBonus+=.3},
 {subject:'음악',name:'크레셴도',desc:'E: 짧은 시간 공격 속도 증가',type:'active',key:'E',cd:12,run:()=>{player.rapid=4;flash('#ddd')}},
 {subject:'음악',name:'불협화음',desc:'주변 적을 잠시 느리게',type:'active',key:'Q',cd:10,run:()=>{mobs.forEach(m=>m.slow=3);blast(140,1,'#aaa')}},
 {subject:'국어',name:'속담 반격',desc:'맞으면 주변에 반격 피해',type:'passive',apply:p=>p.counter=(p.counter||0)+1},
 {subject:'국어',name:'핵심 요약',desc:'경험치 획득 범위 증가',type:'passive',apply:p=>p.magnet=(p.magnet||75)+25},
 {subject:'국어',name:'맞춤법 교정',desc:'자동 공격 피해 증가',type:'passive',apply:p=>p.damage+=.7},
 {subject:'수학',name:'소수점 난사',desc:'투사체가 더 빠르게 날아감',type:'passive',apply:p=>p.shotSpeed+=1.2},
 {subject:'수학',name:'분수 분열',desc:'적중 시 작은 추가 탄환 발사',type:'passive',apply:p=>p.split=(p.split||0)+1},
 {subject:'수학',name:'확률 계산',desc:'일정 확률로 피해 3배',type:'passive',apply:p=>p.crit=(p.crit||0)+.12},
 {subject:'영어',name:'표현 확장',desc:'공격 사거리 크게 증가',type:'passive',apply:p=>p.range+=70},
 {subject:'영어',name:'번역 오류',desc:'Q: 적들을 잠시 느리게 하고 피해',type:'active',key:'Q',cd:9,run:()=>{mobs.forEach(m=>m.slow=4);blast(170,2,'#eee')}},
 {subject:'영어',name:'발음 충격파',desc:'E: 직선 방향으로 강한 충격파',type:'active',key:'E',cd:8,run:()=>blast(125,5,'#fff')},
 {subject:'과학',name:'전기 유도',desc:'자동 공격이 추가 적에게 튐',type:'passive',apply:p=>p.chain=(p.chain||0)+1},
 {subject:'과학',name:'광합성 회복',desc:'시간이 지나면 체력 회복',type:'passive',apply:p=>p.regen=(p.regen||0)+.25},
 {subject:'과학',name:'빙점 실험',desc:'R: 주변 적을 얼리고 피해',type:'active',key:'R',cd:12,run:()=>{mobs.forEach(m=>m.slow=5);blast(190,3,'#fff')}},
 {subject:'사회',name:'경제적 선택',desc:'몬스터 처치 경험치 추가 획득',type:'passive',apply:p=>p.xpBonus+=.2},
 {subject:'사회',name:'법과 질서',desc:'몬스터 접촉 피해 감소',type:'passive',apply:p=>p.armor=Math.min(.7,p.armor+.08)},
 {subject:'사회',name:'역사적 전환점',desc:'F: 강력한 광역 공격',type:'active',key:'F',cd:14,run:()=>blast(240,5,'#ddd')},
 {subject:'체육',name:'유연성',desc:'대시 쿨타임 감소',type:'passive',apply:p=>{let a=abilities.find(x=>x.key==='SPACE');if(a)a.cd=Math.max(1.2,a.cd*.8)}},
 {subject:'체육',name:'파워 슛',desc:'자동 공격 피해와 크기 증가',type:'passive',apply:p=>{p.damage+=1;p.shotSize+=1}},
 {subject:'체육',name:'태클',desc:'SPACE: 돌진 중 주변 적에게 피해',type:'active',key:'R',cd:7,run:()=>{player.dash=.65;player.invuln=.65;blast(95,3,'#fff')}},
 {subject:'정보',name:'방화벽',desc:'피격 후 잠깐 더 긴 무적',type:'passive',apply:p=>p.invulnBonus=(p.invulnBonus||0)+.12},
 {subject:'정보',name:'데이터 복제',desc:'경험치 획득량 증가',type:'passive',apply:p=>p.xpBonus+=.25},
 {subject:'정보',name:'강제 종료',desc:'F: 화면의 적을 모두 강하게 타격',type:'active',key:'F',cd:16,run:()=>blast(1000,4,'#fff')},
 {subject:'미술',name:'모자이크',desc:'투사체 개수 +1',type:'passive',apply:p=>p.bullets=Math.min(7,p.bullets+1)},
 {subject:'미술',name:'조각상',desc:'최대 체력과 방어력 증가',type:'passive',apply:p=>{p.max+=15;p.hp+=15;p.armor=Math.min(.7,p.armor+.04)}},
 {subject:'미술',name:'선과 면',desc:'Q: 플레이어 주위 네 방향 공격',type:'active',key:'Q',cd:8,run:()=>{blast(115,4,'#fff');shots.push({x:player.x-30,y:player.y,vx:-7,vy:0,r:6,life:25,damage:3},{x:player.x+30,y:player.y,vx:7,vy:0,r:6,life:25,damage:3})}},
 {subject:'음악',name:'리듬 콤보',desc:'공격 속도와 투사체 속도 증가',type:'passive',apply:p=>{p.rate=Math.max(.16,p.rate*.9);p.shotSpeed+=.5}},
 {subject:'음악',name:'저음 진동',desc:'주변 적을 밀어내고 피해',type:'active',key:'R',cd:10,run:()=>blast(155,3,'#ddd',true)},
 {subject:'음악',name:'앙코르',desc:'처치 시 낮은 확률로 체력 회복',type:'passive',apply:p=>p.healOnKill=(p.healOnKill||0)+.12}

];
const abilityDefs=[
 {key:'Q',name:'Q 스킬',desc:'Q 스킬을 선택하면 사용 가능',cd:0,left:0,run:null},
 {key:'E',name:'E 스킬',desc:'E 스킬을 선택하면 사용 가능',cd:0,left:0,run:null},
 {key:'R',name:'R 스킬',desc:'R 스킬을 선택하면 사용 가능',cd:0,left:0,run:null},
 {key:'F',name:'F 스킬',desc:'F 스킬을 선택하면 사용 가능',cd:0,left:0,run:null},
 {key:'SPACE',name:'대시',desc:'짧은 무적 대시',cd:3,left:0,run:()=>{player.dash=.2;player.invuln=.25}}
];
function reset(){ownedSkills={};powerMultiplier=1;player={x:W/2,y:H/2,r:11,hp:100,max:100,speed:2.8,damage:1,range:150,rate:.72,shotSize:4,shotSpeed:5.5,bullets:1,xpBonus:1,armor:0,magnet:75,counter:0,regen:0,crit:0,split:0,chain:0,healOnKill:0,invulnBonus:0,invuln:0,dash:0,rapid:0,crowd:1};mobs=[];orbs=[];shots=[];effects=[];abilities=abilityDefs.map(a=>({...a,left:0,run:a.key==='SPACE'?a.run:null}));level=1;xp=0;xpNeed=5;pending=0;kills=0;skillNum=0;elapsed=0;spawnT=0;shotT=0;state='play';renderSkills();hud();hide();last=performance.now()}
function show(id){['startpanel','levelpanel','pausepanel','overpanel'].forEach(x=>$(x).classList.toggle('hidden',x!==id));$('overlay').classList.remove('hidden')}
function hide(){$('overlay').classList.add('hidden')}
function hud(){$('hp').textContent=Math.max(0,Math.ceil(player.hp));$('lv').textContent=level;$('kills').textContent=kills;$('time').textContent=Math.floor(elapsed);$('skillnum').textContent=skillNum;$('xp').style.width=Math.min(100,xp/xpNeed*100)+'%';renderSkills()}
function renderSkills(){
 if(!player)return;
 const box=$('skills');box.innerHTML='';
 abilities.forEach(a=>{
  const el=document.createElement('div');el.className='skill';
  const available=a.run!==null,remaining=Math.max(0,a.left||0),cd=a.cd||0;
  el.innerHTML=`<span class="key">${a.key}</span><b>${a.name}${a.skillName&&ownedSkills[a.skillName]?' LV'+ownedSkills[a.skillName].level:''}</b><div>${available?a.desc:(a.key==='SPACE'?'짧은 대시':'레벨업으로 해금')}</div><div class="cool"><span style="width:${cd?Math.max(0,remaining/cd*100):0}%"></span></div><div style="margin-top:3px;color:#ccc">${available?(remaining>0?remaining.toFixed(1)+'s':'READY'):'LOCKED'}</div>`;
  box.appendChild(el);
 });
}
function flash(color){effects.push({type:'flash',color,life:8})}
function blast(range,damage,color,push=false){
 effects.push({type:'ring',x:player.x,y:player.y,r:10,max:range,color,life:18});
 for(const m of mobs){let d=Math.hypot(m.x-player.x,m.y-player.y);if(d<range){m.hp-=damage*powerMultiplier;if(push){let a=Math.atan2(m.y-player.y,m.x-player.x);m.x+=Math.cos(a)*65;m.y+=Math.sin(a)*65}if(m.hp<=0)kill(m)}}
 mobs=mobs.filter(m=>m.hp>0);
}
function activate(key){
 const a=abilities.find(x=>x.key===key);if(!a||!a.run||a.left>0||state!=='play')return;
 a.run();a.left=a.cd||1;renderSkills();
}
function offerLevel(){
 state='level';show('levelpanel');const choices=$('choices');choices.innerHTML='';
 const candidates=[];
 // Unowned skills are new acquisitions; owned skills return as explicit upgrades.
 for(const sk of skillPool){
   const owned=ownedSkills[sk.name];
   if(!owned)candidates.push({sk,upgrade:false});
   else if(owned.level<8)candidates.push({sk,upgrade:true});
 }
 candidates.sort(()=>Math.random()-.5);
 const pool=candidates.slice(0,3);
 pool.forEach(({sk,upgrade})=>{
  const current=ownedSkills[sk.name];
  const nextLevel=upgrade?current.level+1:1;
  const b=document.createElement('button');b.className='choice';
  b.innerHTML=`<div>${sk.subject} · ${sk.type==='active'?'액티브':'패시브'}</div><strong>${sk.name} ${upgrade?'LV '+nextLevel:'NEW'}</strong><small>${sk.desc}<br>${upgrade?'선택하면 기존 스킬이 강화됩니다.':'새 스킬을 획득합니다.'}</small>`;
  b.onclick=()=>{
    if(upgrade){
      current.level=nextLevel;
      if(sk.type==='passive'){sk.apply(player)}
      else {
        const a=abilities.find(x=>x.key===sk.key);
        if(a&&a.skillName===sk.name){a.cd=Math.max(2.5,a.baseCd*Math.pow(.9,current.level-1));}
        powerMultiplier=1+Object.values(ownedSkills).filter(x=>x.type==='active').reduce((sum,x)=>sum+Math.max(0,x.level-1)*.12,0);
      }
    }else{
      ownedSkills[sk.name]={level:1,type:sk.type,subject:sk.subject};
      if(sk.type==='passive')sk.apply(player);
      else{
        let a=abilities.find(x=>x.key===sk.key);
        a.name=sk.name;a.desc=sk.desc;a.cd=sk.cd;a.baseCd=sk.cd;a.left=0;a.run=sk.run;a.skillName=sk.name;
      }
    }
    skillNum=Object.keys(ownedSkills).length;
    pending--;hud();
    if(pending>0)offerLevel();else{state='play';hide();last=performance.now();c.focus()}
  };
  choices.appendChild(b);
 });
 if(pool.length===0){const b=document.createElement('button');b.className='choice';b.innerHTML='<strong>기본 능력 강화</strong><small>공격 피해가 증가합니다.</small>';b.onclick=()=>{player.damage+=1;pending--;if(pending>0)offerLevel();else{state='play';hide();last=performance.now()}};choices.appendChild(b)}
}
function addXp(n){xp+=n*player.xpBonus;while(xp>=xpNeed){xp-=xpNeed;level++;xpNeed=Math.floor(xpNeed*1.34+2);pending++}if(pending>0&&state==='play')offerLevel()}
function spawn(){let side=Math.floor(Math.random()*4),x=side===0?-15:side===1?W+15:Math.random()*W,y=side===2?-15:side===3?H+15:Math.random()*H,t=elapsed;mobs.push({x,y,r:9+Math.min(6,t/70),hp:1+Math.floor(t/38),speed:.65+Math.random()*.45+Math.min(.7,t/180),slow:0})}
function nearest(){let best=null,d=Infinity;for(const m of mobs){let dd=Math.hypot(m.x-player.x,m.y-player.y);if(dd<d&&dd<player.range){best=m;d=dd}}return best}
function fire(){
 let m=nearest();if(!m)return;
 let base=Math.atan2(m.y-player.y,m.x-player.x);
 const critical=player.crit&&Math.random()<Math.min(.8,player.crit);
 const damage=player.damage*(critical?3:1);
 for(let i=0;i<player.bullets;i++){
  let a=base+(i-(player.bullets-1)/2)*.18;
  shots.push({x:player.x,y:player.y,vx:Math.cos(a)*player.shotSpeed,vy:Math.sin(a)*player.shotSpeed,r:player.shotSize,life:70,damage});
  if(player.split&&Math.random()<.18){
   shots.push({x:player.x,y:player.y,vx:Math.cos(a+.5)*player.shotSpeed*.8,vy:Math.sin(a+.5)*player.shotSpeed*.8,r:Math.max(2,player.shotSize-1),life:45,damage:damage*.5});
  }
 }
 if(player.chain){
  const extra=mobs.filter(x=>x!==m&&!x.dead).sort((a,b)=>Math.hypot(a.x-player.x,a.y-player.y)-Math.hypot(b.x-player.x,b.y-player.y)).slice(0,player.chain);
  extra.forEach(x=>shots.push({x:player.x,y:player.y,vx:(x.x-player.x)/Math.max(1,Math.hypot(x.x-player.x,x.y-player.y))*player.shotSpeed,vy:(x.y-player.y)/Math.max(1,Math.hypot(x.x-player.x,x.y-player.y))*player.shotSpeed,r:player.shotSize,life:70,damage:damage*.65}));
 }
}
function kill(m){if(m.dead)return;m.dead=true;kills++;if(player.healOnKill&&Math.random()<Math.min(.8,player.healOnKill))player.hp=Math.min(player.max,player.hp+3);orbs.push({x:m.x,y:m.y,r:4})}
function end(){state='over';$('result').textContent=`생존 ${Math.floor(elapsed)}초 · 처치 ${kills}마리 · 레벨 ${level}`;show('overpanel')}
function update(dt){
 elapsed+=dt;if(player.regen)player.hp=Math.min(player.max,player.hp+player.regen*dt);player.invuln=Math.max(0,player.invuln-dt);player.dash=Math.max(0,player.dash-dt);player.rapid=Math.max(0,player.rapid-dt);
 for(const a of abilities)a.left=Math.max(0,(a.left||0)-dt);
 let dx=((keys.ArrowRight||keys.d)?1:0)-((keys.ArrowLeft||keys.a)?1:0),dy=((keys.ArrowDown||keys.s)?1:0)-((keys.ArrowUp||keys.w)?1:0);
 if(dx||dy){let l=Math.hypot(dx,dy);dx/=l;dy/=l;let sp=player.speed*(player.dash>0?3.6:1);player.x+=dx*sp*dt*60;player.y+=dy*sp*dt*60}
 player.x=Math.max(player.r,Math.min(W-player.r,player.x));player.y=Math.max(player.r,Math.min(H-player.r,player.y));
 spawnT+=dt;let interval=Math.max(.22,(1.12-elapsed/170)*player.crowd);while(spawnT>=interval){spawnT-=interval;spawn();if(elapsed>30&&Math.random()<.35)spawn()}
 shotT+=dt;if(shotT>=(player.rapid>0?player.rate*.35:player.rate)){shotT=0;fire()}
 for(const m of mobs){let a=Math.atan2(player.y-m.y,player.x-m.x),slow=m.slow>0?.35:1;m.slow=Math.max(0,m.slow-dt);m.x+=Math.cos(a)*m.speed*slow*dt*60;m.y+=Math.sin(a)*m.speed*slow*dt*60;if(Math.hypot(m.x-player.x,m.y-player.y)<m.r+player.r&&player.invuln<=0){if(player.counter){m.hp-=player.counter; if(m.hp<=0)kill(m)} player.hp-=10*(1-player.armor);player.invuln=.65+(player.invulnBonus||0);if(player.hp<=0){end();return}}}
 for(const s of shots){s.x+=s.vx;s.y+=s.vy;s.life--;for(const m of mobs){if(!m.dead&&Math.hypot(s.x-m.x,s.y-m.y)<s.r+m.r){m.hp-=s.damage;s.life=0;if(m.hp<=0)kill(m)}}}
 shots=shots.filter(s=>s.life>0&&s.x>-20&&s.x<W+20&&s.y>-20&&s.y<H+20);mobs=mobs.filter(m=>!m.dead&&m.hp>0);
 for(const o of orbs){if(Math.hypot(o.x-player.x,o.y-player.y)<(player.magnet||75)){o.x+=(player.x-o.x)*.1;o.y+=(player.y-o.y)*.1}if(Math.hypot(o.x-player.x,o.y-player.y)<player.r+o.r){o.got=true;addXp(1)}}
 orbs=orbs.filter(o=>!o.got);
 for(const e of effects)e.life--;effects=effects.filter(e=>e.life>0);
 hud();
}
function draw(){
 ctx.fillStyle='#171717';ctx.fillRect(0,0,W,H);
 ctx.strokeStyle='#252525';ctx.lineWidth=1;
 for(let x=0;x<W;x+=32){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke()}
 for(let y=0;y<H;y+=32){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke()}
 for(const o of orbs){ctx.fillStyle='#ddd';ctx.fillRect(o.x-3,o.y-3,6,6)}
 for(const s of shots){ctx.fillStyle='#fff';ctx.fillRect(s.x-s.r,s.y-s.r,s.r*2,s.r*2)}
 for(const m of mobs){ctx.fillStyle='#bdbdbd';ctx.fillRect(m.x-m.r,m.y-m.r,m.r*2,m.r*2);ctx.fillStyle='#222';ctx.fillRect(m.x-4,m.y-2,2,2);ctx.fillRect(m.x+2,m.y-2,2,2)}
 for(const e of effects){if(e.type==='ring'){ctx.strokeStyle=e.color;ctx.lineWidth=3;ctx.beginPath();ctx.arc(e.x,e.y,e.max*(1-e.life/18),0,Math.PI*2);ctx.stroke()}else if(e.type==='flash'){ctx.fillStyle=e.color;ctx.globalAlpha=e.life/20;ctx.fillRect(0,0,W,H);ctx.globalAlpha=1}}
 ctx.fillStyle=player.invuln>0?'#fff':'#ddd';ctx.fillRect(player.x-player.r,player.y-player.r,player.r*2,player.r*2);ctx.strokeStyle='#111';ctx.strokeRect(player.x-player.r,player.y-player.r,player.r*2,player.r*2);
}
function loop(now){let dt=Math.min(.04,(now-last)/1000||0);last=now;if(state==='play')update(dt);draw();requestAnimationFrame(loop)}
$('start').onclick=()=>{reset();c.focus()};$('again').onclick=()=>{reset();c.focus()};$('resume').onclick=()=>{state='play';hide();last=performance.now();c.focus()};
document.addEventListener('keydown',e=>{let k=e.key.length===1?e.key.toLowerCase():e.key;if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' '].includes(e.key))e.preventDefault();keys[k]=true;if((k==='p'||k==='Escape')&&state==='play'){state='pause';show('pausepanel')}else if((k==='p'||k==='Escape')&&state==='pause'){state='play';hide();last=performance.now()}if(k===' '&&state==='play')activate('SPACE');if(['q','e','r','f'].includes(k))activate(k.toUpperCase())});
document.addEventListener('keyup',e=>{let k=e.key.length===1?e.key.toLowerCase():e.key;keys[k]=false});
reset();state='start';show('startpanel');requestAnimationFrame(t=>{last=t;loop(t)});
})();
</script></body></html>
"""

components.html(game_html, height=730, scrolling=False)
st.caption("레벨업 선택지에는 같은 과목의 서로 다른 스킬이 포함돼. Q/E/R/F 스킬은 레벨업에서 획득한 뒤 해당 키로 발동하며, 아래쪽 칸에서 쿨타임을 확인할 수 있어.")
