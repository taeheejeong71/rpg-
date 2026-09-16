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
# CSS
# -----------------------------
stage = STAGES[st.session_state.stage]
progress_target = stage["target"]
progress = min(st.session_state.money / progress_target, 1.0)

bg_css = {
    "rural": "linear-gradient(135deg,#b8d88a 0%,#e8d59a 45%,#8fbd73 100%)",
    "street": "linear-gradient(135deg,#8f8f8f 0%,#d4d4d4 48%,#696969 100%)",
    "basement": "linear-gradient(135deg,#302c3a 0%,#554c59 50%,#241f2a 100%)",
    "house": "linear-gradient(135deg,#d8c2a4 0%,#f0e0c5 50%,#bda27f 100%)",
    "city": "linear-gradient(135deg,#607d9c 0%,#b8c9d8 48%,#52677b 100%)",
}[stage["bg"]]

st.markdown(
    f"""
<style>
    .stApp {{
        background: {bg_css};
        color: #222;
    }}
    .block-container {{
        max-width: 1150px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }}
    .game-title {{
        text-align:center;
        font-size: 2.7rem;
        font-weight: 900;
        color:#fff;
        text-shadow: 3px 3px 0 #3d3026;
        margin-bottom: .2rem;
    }}
    .subtitle {{
        text-align:center;
        color:#fff;
        font-weight:700;
        text-shadow:1px 1px 2px #333;
        margin-bottom:1rem;
    }}
    .card {{
        background: rgba(255,255,255,.92);
        border: 3px solid rgba(75,55,35,.35);
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 7px 0 rgba(50,35,20,.22);
        margin-bottom: 14px;
    }}
    .money {{
        text-align:center;
        font-size:2.4rem;
        font-weight:900;
        color:#8a4b00;
        margin:4px 0;
    }}
    .stage-name {{
        text-align:center;
        font-size:1.5rem;
        font-weight:900;
    }}
    .target {{
        text-align:center;
        color:#555;
        font-weight:700;
    }}
    .bar-wrap {{
        background:#ddd;
        border-radius:999px;
        height:25px;
        overflow:hidden;
        border:2px solid #777;
    }}
    .bar {{
        width:{progress*100:.2f}%;
        height:100%;
        background:linear-gradient(90deg,#ffd54a,#ff9d00);
        transition:width .3s ease;
    }}
    .character {{
        font-size:8rem;
        text-align:center;
        line-height:1;
        filter: drop-shadow(0 8px 3px rgba(0,0,0,.25));
    }}
    .click-info {{
        text-align:center;
        font-weight:900;
        font-size:1.15rem;
        color:#7a3e00;
    }}
    .upgrade-title {{
        font-size:1.35rem;
        font-weight:900;
        margin-bottom:5px;
    }}
    .small {{
        color:#666;
        font-size:.9rem;
    }}
    div.stButton > button {{
        border-radius:14px;
        border:2px solid #704b25;
        font-weight:900;
        min-height:3rem;
    }}
    div.stButton > button[kind="primary"] {{
        background:linear-gradient(#ffd86a,#f5a800);
        color:#4b2a00;
        font-size:1.35rem;
        box-shadow:0 5px 0 #9b6500;
    }}
    div.stButton > button[kind="primary"]:active {{
        transform:translateY(4px);
        box-shadow:0 1px 0 #9b6500;
    }}
    .stage-pill {{
        display:inline-block;
        padding:6px 12px;
        border-radius:999px;
        background:#4d3929;
        color:white;
        font-weight:900;
    }}
</style>
""",
    unsafe_allow_html=True,
)

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
    st.markdown('<div class="character">🧎‍♂️</div>', unsafe_allow_html=True)
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
    st.markdown('<div class="stage-name">🛒 상점</div>', unsafe_allow_html=True)
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
st.markdown("### 🗺️ 5단계 탈출 지도")

cols = st.columns(5)
for i, s in enumerate(STAGES):
    with cols[i]:
        status = "✅ 클리어" if i < st.session_state.stage else ("🔥 진행 중" if i == st.session_state.stage else "🔒 잠김")
        st.markdown(
            f"""
            <div style="text-align:center;">
                <div style="font-size:2rem;">{s["emoji"]}</div>
                <b>STAGE {i+1}</b><br>
                {s["name"]}<br>
                <span style="font-size:.8rem;color:#666;">{won(s["target"])}</span><br>
                <b>{status}</b>
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
