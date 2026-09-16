import streamlit as st
import streamlit.components.v1 as components
import html
import math

st.set_page_config(
    page_title="거지 탈출 RPG",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# 게임 데이터
# -----------------------------
STAGES = [
    {"name": "시골 탈출", "target": 1_000_000, "bg": "rural", "emoji": "🌾", "desc": "시골을 벗어나 새로운 삶을 시작하자!"},
    {"name": "길거리 탈출", "target": 5_000_000, "bg": "street", "emoji": "🚶", "desc": "길거리에서 돈을 모아 다음 지역으로!"},
    {"name": "반지하 탈출", "target": 50_000_000, "bg": "basement", "emoji": "🏠", "desc": "반지하를 탈출할 만큼 돈을 모으자!"},
    {"name": "1층 탈출", "target": 250_000_000, "bg": "house", "emoji": "🏡", "desc": "더 나은 집을 향해 한 단계 더!"},
    {"name": "지방도시 탈출", "target": 1_250_000_000, "bg": "city", "emoji": "🏢", "desc": "마지막 목표! 지방도시를 벗어나자!"},
]

UPGRADES = [
    ("click_power", "💪 손재주 강화", "클릭당 수입 +1,000원", 1000),
    ("double_click", "⚡ 빠른 손", "클릭 1회가 2회 클릭으로 적용", 1000),
    ("bonus", "🍀 행운 주머니", "클릭 보너스 +1,000원", 1000),
]

# -----------------------------
# 세션 초기화
# -----------------------------
defaults = {
    "money": 0,
    "stage": 0,
    "click_power": 0,
    "double_click": 0,
    "bonus": 0,
    "floating_id": 0,
    "last_gain": 0,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -----------------------------
# 유틸
# -----------------------------
def won(n: int) -> str:
    return f"{n:,}원"

def upgrade_cost(level: int) -> int:
    # 1,000 -> 1,500 -> 2,250 ...
    return math.ceil(1000 * (1.5 ** level))

def click_gain() -> int:
    return 1000 * (1 + st.session_state.click_power + st.session_state.bonus)

def perform_click():
    multiplier = 1 + st.session_state.double_click
    gain = click_gain() * multiplier
    st.session_state.money += gain
    st.session_state.last_gain = gain
    st.session_state.floating_id += 1

    # 현재 스테이지 목표를 넘으면 다음 스테이지로 이동
    while (
        st.session_state.stage < len(STAGES) - 1
        and st.session_state.money >= STAGES[st.session_state.stage]["target"]
    ):
        st.session_state.stage += 1

def buy_upgrade(key: str):
    level = st.session_state[key]
    cost = upgrade_cost(level)
    if st.session_state.money >= cost:
        st.session_state.money -= cost
        st.session_state[key] += 1
        st.rerun()

def reset_game():
    for key, value in defaults.items():
        st.session_state[key] = value
    st.rerun()

# -----------------------------
# CSS — DARK FANTASY / RPG UI
# -----------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@400;700;900&display=swap');
.stApp {{ background: radial-gradient(circle at 50% -10%, #29344d 0%, #101522 42%, #070a10 100%); color:#f5f7fb; font-family:'Noto Sans KR',sans-serif; }}
.stApp::before {{ content:""; position:fixed; inset:0; pointer-events:none; opacity:.22; background-image:linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px); background-size:32px 32px; }}
.block-container {{ max-width:1250px; padding-top:1.3rem; }}
.game-title {{ text-align:center; font-family:'Black Han Sans',sans-serif; font-size:3.25rem; letter-spacing:-2px; color:#fff; text-shadow:0 4px 0 #000,0 0 30px rgba(255,180,50,.2); margin-bottom:.15rem; }}
.subtitle {{ text-align:center; color:#8e9bb0; font-size:.9rem; margin-bottom:1.25rem; }}
.card {{ background:linear-gradient(145deg,rgba(25,31,44,.97),rgba(10,14,22,.98)); border:1px solid #30394b; border-radius:20px; padding:19px; margin-bottom:15px; box-shadow:0 18px 45px rgba(0,0,0,.45),inset 0 1px rgba(255,255,255,.04); }}
.stage-pill {{ display:inline-block; padding:5px 12px; border-radius:99px; background:#e9a42d; color:#171108; font-weight:900; font-size:.72rem; letter-spacing:1px; }}
.stage-name {{ text-align:center; color:#fff; font-size:1.45rem; font-weight:900; margin-top:8px; }}
.target {{ text-align:center; color:#8793a7; font-size:.82rem; font-weight:700; }}
.desc {{ text-align:center; color:#b9c1cf; font-size:.88rem; line-height:1.55; margin-top:12px; }}
.money-label {{ text-align:center; color:#707c90; font-size:.7rem; font-weight:900; letter-spacing:2px; }}
.money {{ text-align:center; color:#ffd36a; font-size:2.65rem; font-weight:950; letter-spacing:-1px; text-shadow:0 0 25px rgba(255,193,70,.18); margin:2px 0 10px; }}
.bar-wrap {{ height:16px; background:#070a0f; border:1px solid #394255; border-radius:99px; overflow:hidden; box-shadow:inset 0 3px 8px #000; }}
.bar {{ width:{progress*100:.2f}%; height:100%; background:linear-gradient(90deg,#ffc44d,#ff8b16); box-shadow:0 0 18px rgba(255,155,35,.6); }}
.character-zone {{ border:1px solid #30394a; border-radius:18px; background:radial-gradient(circle,#222b3e 0%,#0b0f18 70%); padding:20px 5px 14px; margin-bottom:13px; }}
.character {{ font-size:8rem; text-align:center; line-height:1; filter:drop-shadow(0 14px 8px #000); }}
.click-info {{ text-align:center; color:#ffd166; font-weight:900; margin-bottom:12px; }}
.shop-header {{ text-align:center; color:#fff; font-size:1.45rem; font-weight:950; }}
.shop-sub {{ text-align:center; color:#7e899d; font-size:.76rem; margin-bottom:15px; }}
.upgrade-title {{ color:#f4f6fa; font-size:1rem; font-weight:900; margin-top:5px; }}
.small {{ color:#8a95a8; font-size:.78rem; margin-bottom:5px; }}
div.stButton > button {{ min-height:3rem; border-radius:12px; background:#171d29; color:#e9edf4; border:1px solid #364054; font-weight:900; transition:.12s; box-shadow:0 5px 15px rgba(0,0,0,.25); }}
div.stButton > button:hover {{ background:#222a3a; border-color:#e7a83b; color:#fff; transform:translateY(-1px); }}
div.stButton > button[kind="primary"] {{ min-height:4.25rem; background:linear-gradient(135deg,#ffd36b,#ed8a0b); color:#1b1207; border:1px solid #ffe08e; font-size:1.35rem; font-weight:950; box-shadow:0 7px 0 #875006,0 15px 30px rgba(239,139,12,.25); }}
div.stButton > button[kind="primary"]:hover {{ background:linear-gradient(135deg,#ffe08a,#ff9e1b); box-shadow:0 7px 0 #875006,0 18px 35px rgba(239,139,12,.35); }}
div.stButton > button[kind="primary"]:active {{ transform:translateY(5px); box-shadow:0 2px 0 #875006; }}
.map-title {{ color:#fff; font-size:1.25rem; font-weight:950; margin-bottom:13px; }}
.stage-node {{ text-align:center; padding:11px 3px; min-height:120px; background:#101620; border:1px solid #2b3445; border-radius:14px; }}
.stage-node.active {{ border-color:#e8a536; box-shadow:0 0 22px rgba(232,165,54,.14); }}
.stage-node .emoji {{ font-size:1.8rem; }} .stage-node .num {{ color:#e8aa3c; font-size:.68rem; font-weight:950; }} .stage-node .name {{ color:#edf0f6; font-weight:900; font-size:.84rem; }} .stage-node .goal {{ color:#758197; font-size:.65rem; }} .stage-node .status {{ color:#9ca7b8; font-size:.68rem; font-weight:900; margin-top:6px; }}
div[data-testid="stExpander"] {{ background:#0f141e; border:1px solid #283143; border-radius:14px; }}
.stAlert {{ background:#141b27 !important; color:#fff !important; border:1px solid #3a4558 !important; }}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 화면
# -----------------------------
st.markdown('<div class="game-title">💰 거지 탈출 RPG</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">클릭해서 돈을 벌고, 업그레이드해서 5개의 탈출 스테이지를 돌파하세요!</div>',
    unsafe_allow_html=True,
)

left, center, right = st.columns([1, 1.6, 1])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="stage-pill">STAGE {st.session_state.stage + 1} / 5</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stage-name">{stage["emoji"]} {stage["name"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="target">목표: {won(stage["target"])}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<p style="text-align:center;">{html.escape(stage["desc"])}</p>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="stage-name">📊 현재 진행도</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="money">{won(st.session_state.money)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="bar-wrap"><div class="bar"></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="target">{progress*100:.1f}% / 다음 목표 {won(stage["target"])}</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

with center:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="character-zone"><div class="character">🧎‍♂️</div></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="click-info">1회 클릭 수입: +{won(click_gain())}</div>',
        unsafe_allow_html=True,
    )

    if st.button("💰 돈 구걸하기!", type="primary", use_container_width=True):
        perform_click()
        st.rerun()

    # 페이드아웃 + 간단 효과음
    if st.session_state.last_gain:
        fid = st.session_state.floating_id
        gain = st.session_state.last_gain
        components.html(
            f"""
            <div id="fx{fid}" style="
                text-align:center;
                font-size:28px;
                font-weight:900;
                color:#ff8a00;
                animation: fadeUp 0.9s ease-out forwards;">
                +{gain:,}원
            </div>
            <style>
            @keyframes fadeUp {{
                0% {{opacity:1; transform:translateY(10px) scale(1);}}
                70% {{opacity:.75; transform:translateY(-15px) scale(1.08);}}
                100% {{opacity:0; transform:translateY(-38px) scale(.9);}}
            }}
            </style>
            <script>
            try {{
                const Ctx = window.AudioContext || window.webkitAudioContext;
                if (Ctx) {{
                    const ctx = new Ctx();
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = "sine";
                    osc.frequency.setValueAtTime(520, ctx.currentTime);
                    osc.frequency.exponentialRampToValueAtTime(760, ctx.currentTime + 0.08);
                    gain.gain.setValueAtTime(0.08, ctx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.12);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start();
                    osc.stop(ctx.currentTime + 0.12);
                }}
            }} catch(e) {{}}
            </script>
            """,
            height=60,
        )
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="shop-header">🛒 아이템 상점</div><div class="shop-sub">돈을 투자해서 더 빠르게 탈출하세요.</div>', unsafe_allow_html=True)
    st.caption("모든 업그레이드는 1,000원부터 시작하며 구매할 때마다 가격이 50% 증가합니다.")

    for key, name, description, _ in UPGRADES:
        level = st.session_state[key]
        cost = upgrade_cost(level)
        st.markdown(f'<div class="upgrade-title">{name} Lv.{level}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="small">{description}</div>', unsafe_allow_html=True)
        if st.button(
            f"구매 — {won(cost)}",
            key=f"buy_{key}",
            disabled=st.session_state.money < cost,
            use_container_width=True,
        ):
            buy_upgrade(key)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# 하단 정보 / 스테이지 목록
# -----------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="map-title">🗺️ 5단계 탈출 지도</div>', unsafe_allow_html=True)

cols = st.columns(5)
for i, s in enumerate(STAGES):
    with cols[i]:
        status = "✅ 클리어" if i < st.session_state.stage else ("🔥 진행 중" if i == st.session_state.stage else "🔒 잠김")
        st.markdown(
            f"""
            <div class="stage-node {"active" if i == st.session_state.stage else ""}">
                <div class="emoji">{s["emoji"]}</div>
                <div class="num">STAGE {i+1}</div>
                <div class="name">{s["name"]}</div>
                <div class="goal">{won(s["target"])}</div>
                <div class="status">{status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.stage == 4 and st.session_state.money >= STAGES[4]["target"]:
    st.success("🎉 모든 스테이지를 클리어했습니다! 축하합니다!")
    if st.button("🔄 처음부터 다시 하기", use_container_width=True):
        reset_game()

with st.expander("⚙️ 게임 설정"):
    st.write("현재 버전은 Streamlit 세션에 게임 상태를 저장합니다.")
    if st.button("🗑️ 게임 데이터 초기화", use_container_width=True):
        reset_game()
