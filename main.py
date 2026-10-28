import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="교과 SURVIVOR",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@400;600;800;900&display=swap');
.stApp { background: radial-gradient(circle at top, #1e293b, #080b14 70%); color: #f8fafc; }
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.block-container { max-width: 1200px; padding-top: 1.2rem; padding-bottom: 1rem; }
h1 { font-family: 'Black Han Sans', sans-serif; color: #fbbf24; letter-spacing: .03em; }
div[data-testid="stMarkdownContainer"] p { color: #cbd5e1; }
</style>
""", unsafe_allow_html=True)

st.title("🎮 교과 SURVIVOR")
st.caption("몬스터를 피하고 경험치를 모아 성장하라. 레벨업할 때마다 교과 스킬을 선택할 수 있어!")

st.markdown("""
**조작법:** `WASD` 또는 `방향키` 이동 · `SPACE` 대시 · `P` 일시정지  
**게임 목표:** 최대한 오래 살아남고 몬스터를 처치해 레벨을 올려 봐.
""")

game_html = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<style>
*{box-sizing:border-box} html,body{margin:0;padding:0;background:#080b14;color:#f8fafc;font-family:Arial,'Noto Sans KR',sans-serif}
#wrap{position:relative;width:100%;max-width:1100px;margin:auto}
canvas{display:block;width:100%;height:auto;border:1px solid #334155;border-radius:16px;background:#0b1220;outline:none}
#hud{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 8px}
.pill{background:#151e30;border:1px solid #29364d;border-radius:999px;padding:7px 12px;font-size:13px;font-weight:bold}
#bar{height:10px;background:#263248;border-radius:20px;overflow:hidden;margin-bottom:8px}
#xpbar{height:100%;width:0;background:linear-gradient(90deg,#22d3ee,#818cf8);transition:width .12s}
#overlay{position:absolute;inset:42px 0 0;background:#050814e8;border-radius:16px;display:flex;align-items:center;justify-content:center;padding:18px;z-index:5}
.hidden{display:none!important}
.panel{width:min(660px,100%);background:linear-gradient(145deg,#182238,#0d1322);border:1px solid #475569;border-radius:22px;padding:22px;box-shadow:0 20px 80px #0009;text-align:center}
.panel h2{margin:0 0 8px;font-size:28px;color:#fbbf24}.panel p{color:#cbd5e1;margin:6px 0 15px}
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.choice{border:1px solid #475569;border-radius:15px;background:#202c42;color:white;padding:14px 10px;min-height:135px;text-align:left;cursor:pointer;font-size:14px}
.choice:hover{border-color:#fbbf24;transform:translateY(-2px);background:#293851}
.choice strong{display:block;font-size:17px;margin:5px 0;color:#fde68a}.choice small{color:#cbd5e1;line-height:1.4}
.action{border:0;border-radius:12px;padding:11px 18px;background:linear-gradient(135deg,#fbbf24,#f97316);color:#111827;font-weight:900;cursor:pointer;margin:5px}
@media(max-width:650px){.cards{grid-template-columns:1fr}.choice{min-height:0}.panel{padding:16px}.panel h2{font-size:23px}}
</style>
</head>
<body>
<div id="wrap">
 <div id="hud">
  <div class="pill">❤️ 체력 <span id="hp">100</span></div>
  <div class="pill">⭐ 레벨 <span id="lv">1</span></div>
  <div class="pill">☠ 처치 <span id="kills">0</span></div>
  <div class="pill">⏱ 생존 <span id="time">0</span>초</div>
  <div class="pill">📚 스킬 <span id="skillcount">0</span></div>
 </div>
 <div id="bar"><div id="xpbar"></div></div>
 <canvas id="game" width="1000" height="600" tabindex="0"></canvas>
 <div id="overlay">
  <div class="panel" id="startpanel">
   <h2>교과 SURVIVOR</h2>
   <p>교과 지식을 무기로 몬스터 무리에서 살아남아라!</p>
   <p>WASD / 방향키 이동 · SPACE 대시 · P 일시정지</p>
   <button class="action" id="startbtn">게임 시작</button>
  </div>
  <div class="panel hidden" id="levelpanel">
   <h2>📖 레벨 업!</h2><p>배울 교과 스킬 하나를 선택해.</p>
   <div class="cards" id="choices"></div>
  </div>
  <div class="panel hidden" id="pausepanel">
   <h2>⏸ 일시정지</h2><p>P 키를 누르면 계속할 수 있어.</p><button class="action" id="resume">계속하기</button>
  </div>
  <div class="panel hidden" id="gameoverpanel">
   <h2>💀 게임 오버</h2><p id="summary"></p><button class="action" id="restart">다시 도전</button>
  </div>
 </div>
</div>
<script>
(()=>{
const canvas=document.getElementById('game'),ctx=canvas.getContext('2d');
const $=id=>document.getElementById(id);
const W=canvas.width,H=canvas.height;
const skills=[
 {name:'국어 · 어휘력',desc:'문장의 힘으로 공격 범위가 넓어진다.',emoji:'📚',apply:g=>g.range+=35},
 {name:'수학 · 계산력',desc:'공격 피해가 30% 증가한다.',emoji:'➗',apply:g=>g.damage*=1.3},
 {name:'영어 · 스피킹',desc:'이동 속도가 빨라진다.',emoji:'🔤',apply:g=>g.speed+=0.55},
 {name:'과학 · 실험',desc:'자동 공격 속도가 빨라진다.',emoji:'🧪',apply:g=>g.cooldown=Math.max(0.25,g.cooldown*0.78)},
 {name:'사회 · 협동',desc:'최대 체력과 현재 체력을 회복한다.',emoji:'🌍',apply:g=>{g.maxHp+=20;g.hp=Math.min(g.maxHp,g.hp+35)}},
 {name:'체육 · 순발력',desc:'대시 재사용 대기시간이 감소한다.',emoji:'🏃',apply:g=>g.dashCooldown=Math.max(1.2,g.dashCooldown*0.75)},
 {name:'정보 · 알고리즘',desc:'추가 투사체를 발사한다.',emoji:'💻',apply:g=>g.projectiles=Math.min(5,g.projectiles+1)},
 {name:'미술 · 조준',desc:'투사체 크기와 공격 범위가 증가한다.',emoji:'🎨',apply:g=>{g.shotSize+=2;g.range+=15}},
 {name:'음악 · 리듬',desc:'경험치 획득량이 증가한다.',emoji:'🎵',apply:g=>g.xpBonus+=0.25}
];
let keys={},state='start',last=0,elapsed=0,spawnTimer=0,shotTimer=0,levelPending=0;
let player,monsters,orbs,shots,particles,kills,level,xp,xpNeed,skillCount;
function fresh(){
 player={x:W/2,y:H/2,r:15,hp:100,maxHp:100,speed:3.2,damage:1,range:175,cooldown:0.8,shotSize:5,projectiles:1,xpBonus:1,dashCooldown:3,dashLeft:0,invuln:0};
 monsters=[];orbs=[];shots=[];particles=[];kills=0;level=1;xp=0;xpNeed=5;skillCount=0;elapsed=0;spawnTimer=0;shotTimer=0;levelPending=0;updateHud();
}
function showPanel(id){['startpanel','levelpanel','pausepanel','gameoverpanel'].forEach(x=>$(x).classList.toggle('hidden',x!==id));$('overlay').classList.remove('hidden')}
function hideOverlay(){$('overlay').classList.add('hidden')}
function updateHud(){$('hp').textContent=Math.max(0,Math.ceil(player?.hp||0));$('lv').textContent=level;$('kills').textContent=kills;$('time').textContent=Math.floor(elapsed);$('skillcount').textContent=skillCount;$('xpbar').style.width=(Math.min(1,xp/xpNeed)*100)+'%'}
function rand(a,b){return a+Math.random()*(b-a)}
function spawnMonster(){
 let side=Math.floor(Math.random()*4),x=side===0?-20:side===1?W+20:rand(0,W),y=side===2?-20:side===3?H+20:rand(0,H);
 let t=elapsed, r=rand(11,18)+Math.min(7,t/45);
 monsters.push({x,y,r,hp:1+Math.floor(t/35),speed:rand(.65,1.15)+Math.min(.65,t/150),color:['#fb7185','#a78bfa','#f97316','#34d399'][Math.floor(Math.random()*4)],hit:0});
}
function distance(a,b){return Math.hypot(a.x-b.x,a.y-b.y)}
function nearest(){
 let target=null,d=Infinity;
 for(let m of monsters){let dd=distance(player,m);if(dd<d&&dd<player.range+80){d=dd;target=m}}
 return target;
}
function fire(){
 let target=nearest();if(!target)return;
 let base=Math.atan2(target.y-player.y,target.x-player.x);
 for(let i=0;i<player.projectiles;i++){
  let spread=(i-(player.projectiles-1)/2)*0.16,ang=base+spread;
  shots.push({x:player.x,y:player.y,vx:Math.cos(ang)*6.2,vy:Math.sin(ang)*6.2,r:player.shotSize,damage:player.damage,life:70});
 }
}
function gainXp(amount){
 xp+=amount*player.xpBonus;
 while(xp>=xpNeed){xp-=xpNeed;level++;xpNeed=Math.floor(xpNeed*1.35+2);levelPending++}
 if(levelPending>0&&state==='play')levelUp();
}
function levelUp(){
 state='level';showPanel('levelpanel');
 const pool=[...skills].sort(()=>Math.random()-.5).slice(0,3);
 $('choices').innerHTML='';
 pool.forEach(sk=>{
  let b=document.createElement('button');b.className='choice';
  b.innerHTML=`<div style="font-size:26px">${sk.emoji}</div><strong>${sk.name}</strong><small>${sk.desc}</small>`;
  b.onclick=()=>{sk.apply(player);skillCount++;levelPending--;updateHud();if(levelPending>0){levelUp()}else{state='play';hideOverlay();last=performance.now();canvas.focus()}};
  $('choices').appendChild(b);
 });
}
function endGame(){state='over';$('summary').textContent=`${Math.floor(elapsed)}초 생존 · 몬스터 ${kills}마리 처치 · 레벨 ${level} 달성`;showPanel('gameoverpanel')}
function dash(){if(state==='play'&&player.dashLeft<=0){player.dashLeft=0.18;player.invuln=0.35;player._dashCD=player.dashCooldown}}
function update(dt){
 elapsed+=dt;player.invuln=Math.max(0,player.invuln-dt);player.dashLeft=Math.max(0,player.dashLeft-dt);player._dashCD=Math.max(0,(player._dashCD||0)-dt);
 let dx=(keys.ArrowRight||keys.d?1:0)-(keys.ArrowLeft||keys.a?1:0),dy=(keys.ArrowDown||keys.s?1:0)-(keys.ArrowUp||keys.w?1:0);
 if(dx||dy){let len=Math.hypot(dx,dy);dx/=len;dy/=len;let speed=player.speed*(player.dashLeft>0?3.5:1);player.x+=dx*speed*dt*60;player.y+=dy*speed*dt*60}
 player.x=Math.max(player.r,Math.min(W-player.r,player.x));player.y=Math.max(player.r,Math.min(H-player.r,player.y));
 spawnTimer+=dt;let interval=Math.max(.22,1.15-elapsed/160);while(spawnTimer>=interval){spawnTimer-=interval;spawnMonster();if(elapsed>35&&Math.random()<.35)spawnMonster()}
 shotTimer+=dt;if(shotTimer>=player.cooldown){shotTimer=0;fire()}
 for(let m of monsters){let a=Math.atan2(player.y-m.y,player.x-m.x);m.x+=Math.cos(a)*m.speed*dt*60;m.y+=Math.sin(a)*m.speed*dt*60;
  if(distance(player,m)<player.r+m.r&&player.invuln<=0){player.hp-=12;player.invuln=.7;if(player.hp<=0){endGame();return}}
 }
 for(let s of shots){s.x+=s.vx;s.y+=s.vy;s.life--;for(let m of monsters){if(m.hp>0&&Math.hypot(s.x-m.x,s.y-m.y)<s.r+m.r){m.hp-=s.damage;s.life=0;for(let j=0;j<4;j++)particles.push({x:m.x,y:m.y,vx:rand(-2,2),vy:rand(-2,2),life:16});if(m.hp<=0){kills++;orbs.push({x:m.x,y:m.y,r:6});}}}}
 shots=shots.filter(s=>s.life>0&&s.x>-30&&s.x<W+30&&s.y>-30&&s.y<H+30);
 monsters=monsters.filter(m=>m.hp>0);
 for(let o of orbs){let d=distance(player,o);if(d<100){o.x+=(player.x-o.x)*.08;o.y+=(player.y-o.y)*.08}if(d<player.r+o.r){o.got=true;gainXp(1)}}
 orbs=orbs.filter(o=>!o.got);
 for(let p of particles){p.x+=p.vx;p.y+=p.vy;p.life--}particles=particles.filter(p=>p.life>0);
 updateHud();
}
function draw(){
 ctx.clearRect(0,0,W,H);
 ctx.fillStyle='#0b1220';ctx.fillRect(0,0,W,H);
 ctx.strokeStyle='#17243a';ctx.lineWidth=1;
 for(let x=0;x<W;x+=40){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke()}
 for(let y=0;y<H;y+=40){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke()}
 // soft arena glow
 let grad=ctx.createRadialGradient(player.x,player.y,20,player.x,player.y,300);grad.addColorStop(0,'#1d4ed81a');grad.addColorStop(1,'#00000000');ctx.fillStyle=grad;ctx.fillRect(0,0,W,H);
 for(let o of orbs){ctx.beginPath();ctx.fillStyle='#22d3ee';ctx.shadowBlur=12;ctx.shadowColor='#22d3ee';ctx.arc(o.x,o.y,o.r,0,Math.PI*2);ctx.fill();ctx.shadowBlur=0}
 for(let s of shots){ctx.beginPath();ctx.fillStyle='#fde68a';ctx.shadowBlur=10;ctx.shadowColor='#fbbf24';ctx.arc(s.x,s.y,s.r,0,Math.PI*2);ctx.fill();ctx.shadowBlur=0}
 for(let m of monsters){ctx.beginPath();ctx.fillStyle=m.color;ctx.shadowBlur=14;ctx.shadowColor=m.color;ctx.arc(m.x,m.y,m.r,0,Math.PI*2);ctx.fill();ctx.shadowBlur=0;ctx.fillStyle='#111827';ctx.beginPath();ctx.arc(m.x-m.r*.25,m.y-2,2,0,Math.PI*2);ctx.arc(m.x+m.r*.25,m.y-2,2,0,Math.PI*2);ctx.fill()}
 for(let p of particles){ctx.globalAlpha=Math.max(0,p.life/16);ctx.fillStyle='#fda4af';ctx.fillRect(p.x,p.y,3,3)}ctx.globalAlpha=1;
 // player shield flicker
 ctx.beginPath();ctx.fillStyle=player.invuln>0?'#bfdbfe':'#60a5fa';ctx.shadowBlur=20;ctx.shadowColor='#60a5fa';ctx.arc(player.x,player.y,player.r,0,Math.PI*2);ctx.fill();ctx.shadowBlur=0;
 ctx.strokeStyle='#dbeafe';ctx.lineWidth=3;ctx.stroke();
 ctx.fillStyle='#e2e8f0';ctx.font='bold 13px Arial';ctx.textAlign='center';ctx.fillText('YOU',player.x,player.y-23);
 ctx.textAlign='left';ctx.fillStyle='#94a3b8';ctx.font='12px Arial';ctx.fillText('교과 스킬로 살아남기',14,H-14);
}
function loop(now){
 let dt=Math.min(.035,(now-last)/1000||0);last=now;
 if(state==='play')update(dt);
 draw();
 requestAnimationFrame(loop);
}
$('startbtn').onclick=()=>{fresh();state='play';hideOverlay();last=performance.now();canvas.focus()};
$('restart').onclick=()=>{fresh();state='play';hideOverlay();last=performance.now();canvas.focus()};
$('resume').onclick=()=>{state='play';hideOverlay();last=performance.now();canvas.focus()};
document.addEventListener('keydown',e=>{
 let k=e.key.length===1?e.key.toLowerCase():e.key;
 if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' '].includes(e.key))e.preventDefault();
 keys[k]=true;
 if((k==='p'||k==='Escape')&&state==='play'){state='pause';showPanel('pausepanel')}
 else if((k==='p'||k==='Escape')&&state==='pause'){state='play';hideOverlay();last=performance.now()}
 if(k===' '){if(state==='play'&&(player._dashCD||0)<=0){dash();player._dashCD=player.dashCooldown}}
});
document.addEventListener('keyup',e=>{let k=e.key.length===1?e.key.toLowerCase():e.key;keys[k]=false});
fresh();requestAnimationFrame(t=>{last=t;loop(t)});
})();
</script>
</body>
</html>
"""

components.html(game_html, height=720, scrolling=False)

st.info("레벨업 선택창에서 교과 스킬을 선택하면 게임이 다시 진행돼. 게임 화면을 한 번 클릭한 뒤 키보드로 조작해.")
