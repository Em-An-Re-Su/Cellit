import streamlit as st
import plotly.graph_objects as go
import numpy as np
import math

st.set_page_config(page_title="BIOVERSE | 3D 생명과학 탐험", page_icon="🧬", layout="wide")

# ------------------------------------------------------------
# BIOVERSE: 교육용 3D 생명과학 탐험
# 모든 형상은 앱 안에서 절차적으로 생성되며 외부 3D 파일이 필요하지 않습니다.
# ------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family: Pretendard, sans-serif;}
.stApp {background: radial-gradient(circle at 15% 0%, #14243a 0%, #091321 42%, #07101c 100%); color:#edf4ff;}
section[data-testid="stSidebar"] {background:#0c1929; border-right:1px solid #20354d;}
.block-container {padding-top:1.3rem; max-width:1500px;}
.hero {padding:22px 26px; border:1px solid #29435e; border-radius:18px;
background:linear-gradient(120deg,rgba(20,47,72,.92),rgba(10,25,42,.9)); margin-bottom:18px;}
.hero h1 {font-size:2.1rem; margin:0; letter-spacing:-1px; color:#f2f7ff;}
.hero p {color:#a9c0d8; margin:.35rem 0 0 0;}
.eyebrow {color:#63d7c5; font-size:.75rem; font-weight:800; letter-spacing:2px;}
.panel {background:rgba(17,34,53,.82); border:1px solid #294158; padding:16px 18px; border-radius:14px; margin-bottom:12px;}
.panel h3 {margin-top:0; color:#e8f4ff;}
.small {font-size:.88rem;color:#a9bfd4;}
.metric {font-size:1.5rem;font-weight:800;color:#70e0ce;}
.stButton>button {border-radius:10px; border:1px solid #41617d; background:#17334d; color:#eaf5ff; min-height:2.65rem;}
.stButton>button:hover {border-color:#66d8c8; color:white; background:#214863;}
div[data-testid="stAlert"] {border-radius:12px;}
</style>
""", unsafe_allow_html=True)

# ---------- 데이터 ----------
ORGANS = {
    "심장": {"pos":(0.00,-0.20,5.15),"scale":(.38,.30,.48),"color":"#d94b63",
            "role":"온몸으로 혈액을 보내는 펌프입니다. 심장 근육의 수축과 이완이 혈액 순환을 유지합니다.",
            "cells":["심근세포","심장박동조율세포","혈관내피세포"],
            "problem":"기능이 크게 저하되면 혈액 공급이 부족해져 여러 장기의 기능이 함께 떨어질 수 있습니다.",
            "detail":"심근세포는 서로 연결되어 동기화된 수축을 합니다. 심장박동조율세포는 전기 신호를 만들어 박동 리듬을 조절합니다."},
    "폐": {"pos":(0.00,-0.12,5.35),"scale":(.78,.32,.72),"color":"#65a9d8",
            "role":"폐포에서 산소와 이산화탄소를 교환합니다. 산소는 혈액으로, 이산화탄소는 바깥 공기로 이동합니다.",
            "cells":["폐포 1형 세포","폐포 2형 세포","섬모상피세포"],
            "problem":"가스 교환이 원활하지 않으면 혈액의 산소 공급과 이산화탄소 배출에 문제가 생길 수 있습니다.",
            "detail":"폐포 1형 세포는 얇은 기체 교환 표면을 만들고, 2형 세포는 표면활성제를 분비해 폐포가 쉽게 허탈되지 않도록 돕습니다."},
    "간": {"pos":(0.32,-0.12,4.55),"scale":(.60,.34,.34),"color":"#b8794d",
            "role":"영양소 대사, 해독에 관여하는 물질의 처리, 담즙 생성, 혈장 단백질 합성 등을 담당합니다.",
            "cells":["간세포","쿠퍼세포","간성상세포"],
            "problem":"간 기능이 떨어지면 대사·해독·단백질 합성 등 여러 기능에 영향을 줄 수 있습니다.",
            "detail":"간세포는 대사와 합성의 중심입니다. 쿠퍼세포는 간의 면역 방어에 관여하는 대식세포입니다."},
    "위": {"pos":(-.05,-.17,4.42),"scale":(.42,.30,.40),"color":"#d88b78",
            "role":"음식물을 일시적으로 저장하고 위산과 소화 효소를 이용해 소화를 시작합니다.",
            "cells":["위표면점액세포","벽세포","주세포"],
            "problem":"위 점막 방어와 소화 기능에 문제가 생기면 통증이나 소화 장애가 나타날 수 있습니다.",
            "detail":"벽세포는 염산을 분비하고, 주세포는 펩시노겐을 분비합니다. 점액세포는 점액으로 위벽을 보호합니다."},
    "신장": {"pos":(.48,.02,3.95),"scale":(.32,.27,.48),"color":"#bd6871",
            "role":"혈액을 여과해 노폐물을 배출하고 수분·전해질·산염기 균형을 조절합니다.",
            "cells":["족세포","세뇨관 상피세포","사구체 내피세포"],
            "problem":"여과와 재흡수 기능이 저하되면 체액·전해질 균형과 노폐물 배출에 문제가 생길 수 있습니다.",
            "detail":"족세포는 사구체 여과 장벽을 구성하고, 세뇨관 상피세포는 필요한 물질을 재흡수하거나 분비합니다."},
    "뇌": {"pos":(0,-.02,7.12),"scale":(.43,.36,.42),"color":"#c28bd8",
            "role":"감각 정보를 통합하고 운동·기억·언어·감정 등 다양한 신경 기능을 조절합니다.",
            "cells":["뉴런","성상세포","희소돌기아교세포"],
            "problem":"손상 부위에 따라 운동, 감각, 언어, 기억 등 서로 다른 기능에 변화가 생길 수 있습니다.",
            "detail":"뉴런은 전기·화학 신호를 전달합니다. 성상세포는 신경세포의 환경을 유지하고 희소돌기아교세포는 축삭의 수초 형성에 관여합니다."}
}
CELL_INFO = {
    "심근세포":("심장 근육을 이루며 규칙적으로 수축하는 세포","근절, 풍부한 미토콘드리아, 개재판"),
    "심장박동조율세포":("자발적으로 전기 신호를 만들어 심장 박동의 리듬을 조절","이온 통로, 세포막, 전기적 연결"),
    "혈관내피세포":("혈관 안쪽 표면을 덮어 물질 교환과 혈관 반응을 조절","얇은 세포층, 세포간 연결"),
    "폐포 1형 세포":("폐포 표면을 얇게 덮어 기체 확산을 돕는 세포","매우 얇은 세포질, 넓은 표면"),
    "폐포 2형 세포":("표면활성제를 분비해 폐포의 표면 장력을 낮추는 세포","분비 과립, 층판소체"),
    "섬모상피세포":("기도의 점액과 이물질을 섬모 운동으로 이동시키는 세포","섬모, 미세소관"),
    "간세포":("대사·합성·저장·물질 변환을 담당하는 간의 주요 세포","풍부한 소포체, 미토콘드리아, 글리코겐"),
    "쿠퍼세포":("간의 혈액 속 이물질과 노화 세포 등을 처리하는 면역세포","식세포 작용, 리소좀"),
    "간성상세포":("비타민 A 저장 및 간 조직의 구조 유지에 관여","지질 방울, 세포외기질"),
    "위표면점액세포":("점액과 중탄산염으로 위 점막을 보호","점액 분비 과립"),
    "벽세포":("위산과 내인성 인자를 분비하는 세포","분비 세관, 미토콘드리아"),
    "주세포":("단백질 소화 효소의 전구체인 펩시노겐을 분비","조면소포체, 분비 과립"),
    "족세포":("사구체 모세혈관을 감싸 여과 장벽을 형성","발돌기, 여과 틈새"),
    "세뇨관 상피세포":("물과 이온, 영양소의 재흡수 및 분비를 수행","미세융모, 미토콘드리아"),
    "사구체 내피세포":("혈액이 여과되는 모세혈관의 안쪽을 구성","창문형 구멍, 기저막"),
    "뉴런":("전기 신호를 받아들이고 다른 세포로 전달하는 신경세포","수상돌기, 세포체, 축삭, 시냅스"),
    "성상세포":("신경세포 주변 환경과 혈액-뇌 장벽 유지에 기여","별 모양 돌기, 글리코겐 저장"),
    "희소돌기아교세포":("중추신경계 축삭에 수초를 형성해 신호 전달을 빠르게 함","수초, 여러 축삭 돌기")
}
DRUGS = {
    "진통·해열제(일반적 작용)":("통증과 발열을 완화하는 약물 계열","통증·발열 신호 경로에 관여하는 물질의 생성을 낮추는 방식 등이 있습니다.","증상 완화, 위장 불편 등 약물별 차이가 있음","통증 신호가 줄어드는 과정을 신경 경로의 밝기 변화로 표시"),
    "항히스타민제":("알레르기 증상을 완화하는 약물 계열","히스타민 수용체의 작용을 차단해 재채기·가려움 등의 반응을 줄입니다.","일부 약물에서 졸림, 입마름 등이 나타날 수 있음","졸림 가능성을 흐릿한 주변 시야와 낮아진 주의력 지표로 상징화"),
    "기관지확장제":("일부 호흡기 질환에서 기도 확장을 돕는 약물 계열","기도 평활근의 긴장을 낮춰 공기 흐름을 개선하는 방식 등이 있습니다.","심박 변화나 떨림 등 약물별 부작용 가능","기도 단면이 넓어지고 공기 흐름 입자가 원활해지는 3D 장면"),
    "항생제":("세균 감염을 치료하는 데 사용하는 약물 계열","세균의 세포벽 합성이나 단백질 합성 등 세균의 생존 과정에 작용합니다.","알레르기 반응, 설사 등 약물별 부작용 가능. 바이러스에는 효과가 없음","세균 모형의 증식 표시가 감소하는 교육용 장면"),
    "국소마취제":("특정 부위의 감각 전달을 일시적으로 차단하는 약물 계열","신경세포의 전압 개폐성 나트륨 통로를 억제해 신호 전달을 줄입니다.","감각 변화. 실제 사용은 의료진의 판단과 감독이 필요","특정 신경 경로의 신호 입자가 일시적으로 줄어드는 장면"),
    "항염증제":("염증 반응을 조절하는 약물 계열","약물 종류에 따라 염증 매개 물질의 생성 또는 작용을 억제합니다.","위장관·신장 등 영향은 약물과 개인 상태에 따라 다름","염증 부위의 신호 입자와 붉은 발광이 감소하는 장면"),
    "수면·진정 관련 처방약":("의료진이 특정 상황에서 처방하는 중추신경계 작용 약물 계열","중추신경계의 활동을 낮추는 방식 등 약물별 작용 기전이 다릅니다.","졸림과 반응 저하 가능. 다른 진정 물질과의 병용은 위험할 수 있음","시야의 선명도와 반응 지표가 낮아지는 추상적 시뮬레이션")
}

# ---------- 3D 도형 도구 ----------
def ellipsoid(center, radii, color, name="", opacity=1.0, resolution=22, showscale=False):
    u = np.linspace(0, 2*np.pi, resolution)
    v = np.linspace(0, np.pi, resolution)
    x = center[0] + radii[0]*np.outer(np.cos(u), np.sin(v))
    y = center[1] + radii[1]*np.outer(np.sin(u), np.sin(v))
    z = center[2] + radii[2]*np.outer(np.ones_like(u), np.cos(v))
    return go.Surface(x=x, y=y, z=z, colorscale=[[0,color],[1,color]], showscale=showscale,
                      opacity=opacity, name=name, hovertemplate=f"{name}<extra></extra>",
                      lighting=dict(ambient=.48,diffuse=.78,specular=.35,roughness=.45),
                      lightposition=dict(x=100,y=150,z=200))

def line3d(points, color, width=5, name=""):
    p=np.array(points)
    return go.Scatter3d(x=p[:,0],y=p[:,1],z=p[:,2],mode="lines",line=dict(color=color,width=width),name=name,hoverinfo="skip")

def scene_layout(title, camera=None, height=650):
    return dict(title=dict(text=title,font=dict(color="#eaf4ff",size=18)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dceafa"), height=height, margin=dict(l=0,r=0,t=45,b=0),
        scene=dict(xaxis=dict(visible=False,range=[-1.8,1.8]),
                   yaxis=dict(visible=False,range=[-1.2,1.2]),
                   zaxis=dict(visible=False,range=[0,8.1]),
                   aspectmode="manual",aspectratio=dict(x=1,y=.55,z=1.8),
                   camera=camera or dict(eye=dict(x=2.0,y=2.5,z=1.25))),
        legend=dict(bgcolor="rgba(8,20,34,.5)",font=dict(color="#dceafa")))

def body_scene(revealed=False, removed=None, trait="기본 형질"):
    fig=go.Figure()
    # 몸통, 머리, 목, 골반, 팔다리: 인체 비율을 참고한 절차적 3D 마네킹
    skin="#c98f78"
    fig.add_trace(ellipsoid((0,0,5.05),(.78,.38,1.18),skin,"몸통",.94))
    fig.add_trace(ellipsoid((0,0,6.78),(.39,.34,.49),skin,"머리",.98))
    fig.add_trace(ellipsoid((0,0,6.30),(.19,.20,.25),skin,"목",.98))
    fig.add_trace(ellipsoid((0,0,3.75),(.57,.34,.48),"#b77d6c","골반",.98))
    # 팔과 다리
    for x in [-.88,.88]:
        fig.add_trace(ellipsoid((x*.92,0,5.08),(.22,.24,.77),skin,"상완",.98))
        fig.add_trace(ellipsoid((x*1.04,0,4.15),(.17,.19,.72),skin,"전완",.98))
        fig.add_trace(ellipsoid((x*.48,0,2.65),(.25,.27,1.02),skin,"허벅지",.98))
        fig.add_trace(ellipsoid((x*.48,0,1.30),(.19,.21,.85),skin,"종아리",.98))
        fig.add_trace(ellipsoid((x*.48,-.12,.48),(.24,.38,.19),skin,"발",.98))
    # 절개 시 전면 피부를 투명하게 하고 장기 배치
    if revealed:
        # 몸통 전면에 반투명한 절개창 프레임
        fig.add_trace(ellipsoid((0,-.405,5.03),(.70,.025,1.08),"#6c9db0","절개 관찰창",.13))
        for name,d in ORGANS.items():
            if name == removed: continue
            pos=d["pos"]; scale=d["scale"]
            fig.add_trace(ellipsoid(pos,scale,d["color"],name,.98,26))
            fig.add_trace(go.Scatter3d(x=[pos[0]],y=[pos[1]-.05],z=[pos[2]],mode="markers+text",
                marker=dict(size=3,color="#fff1d6"),text=[name],textposition="top center",
                textfont=dict(size=10,color="#ffffff"),name=name+" 라벨",showlegend=False))
    # 형질 변화는 안전한 가상 표현형으로만 표시
    if trait=="가상 키 성장 형질":
        fig.add_trace(ellipsoid((0,0,7.25),(.39,.34,.49),skin,"형질 변화 표시",.95))
        fig.add_trace(go.Scatter3d(x=[0],y=[-.45],z=[7.85],mode="text",text=["성장 형질 변화(가상)"],textfont=dict(color="#7ce6d2",size=11),showlegend=False))
    elif trait=="가상 홍채 색 변화":
        fig.add_trace(go.Scatter3d(x=[-.14,.14],y=[-.32,-.32],z=[6.83,6.83],mode="markers",marker=dict(size=7,color="#63b6d9"),name="홍채 색 변화"))
    fig.update_layout(**scene_layout("인체 해부 모형 · 3D"))
    return fig

def cell_scene(cell_name):
    fig=go.Figure()
    fig.add_trace(ellipsoid((0,0,0), (1.12,.92,.86), "#5ba7a0","세포막",.24,30))
    fig.add_trace(ellipsoid((-.12,0,.05),(.38,.34,.34),"#9b79c8","핵",.96,24))
    # 핵소체
    fig.add_trace(ellipsoid((-.02,-.22,.10),(.12,.12,.12),"#e7c56f","핵소체",1))
    # 미토콘드리아
    for p in [(.55,.22,.22),(-.58,.28,-.18),(.42,-.48,-.25)]:
        fig.add_trace(ellipsoid(p,(.25,.12,.13),"#e58b52","미토콘드리아",1))
    # 소포체 / 골지체
    for k in range(4):
        x=-.55+k*.12
        fig.add_trace(line3d([(x,-.25,.25),(x+.12,-.35,.32),(x+.25,-.28,.36)],"#68c7df",4,"소포체"))
    for k in range(3):
        z=-.35+k*.10
        fig.add_trace(line3d([(-.15,-.48,z),(.12,-.52,z+.03),(.32,-.42,z)],"#f0bd69",5,"골지체"))
    # 리보솜 점
    rng=np.random.default_rng(9)
    pts=rng.normal(0,.52,(55,3))
    fig.add_trace(go.Scatter3d(x=pts[:,0],y=pts[:,1],z=pts[:,2],mode="markers",
        marker=dict(size=2.5,color="#e9e7c4"),name="리보솜"))
    fig.update_layout(**scene_layout(f"{cell_name} · 세포 3D 확대",height=620))
    return fig

def organelle_scene(organelle):
    fig=go.Figure()
    if organelle=="핵":
        fig.add_trace(ellipsoid((0,0,0),(.8,.72,.7),"#9672c6","핵막",.45,28))
        fig.add_trace(ellipsoid((.1,0,.05),(.27,.25,.25),"#e2b65e","핵소체",1))
        # 핵공
        for a in np.linspace(0,2*np.pi,14,endpoint=False):
            fig.add_trace(ellipsoid((.8*np.cos(a),.72*np.sin(a),.05),(.07,.07,.07),"#e5d8ff","핵공",1,12))
    elif organelle=="미토콘드리아":
        fig.add_trace(ellipsoid((0,0,0),(.95,.48,.42),"#df8550","외막",1,30))
        t=np.linspace(-.8,.8,80)
        y=.20*np.sin(15*t)
        fig.add_trace(line3d(list(zip(t,y,np.zeros_like(t))),"#ffe0a0",5,"내막 주름(크리스타)"))
        fig.add_trace(line3d(list(zip(t,-y*.7,np.zeros_like(t))),"#ffe0a0",4,"내막 주름"))
    else:
        for j in range(5):
            x=-.7+j*.28
            fig.add_trace(line3d([(x,-.3,-.1),(x+.15,-.1,.12),(x+.25,.12,.18)],"#64c6dc",7,"막 구조"))
        for i in range(20):
            a=i*2.4
            fig.add_trace(ellipsoid((.65*np.cos(a),.45*np.sin(a),.15*np.sin(a*1.7)),(.045,.045,.045),"#f2d17b","리보솜",1,8))
    fig.update_layout(**scene_layout(f"{organelle} · 소기관 3D",height=570))
    return fig

def dna_scene(sequence, changed_idx=None):
    fig=go.Figure()
    n=180
    t=np.linspace(0,8*np.pi,n)
    z=np.linspace(-2.4,2.4,n)
    x1=.62*np.cos(t); y1=.62*np.sin(t)
    x2=.62*np.cos(t+np.pi); y2=.62*np.sin(t+np.pi)
    fig.add_trace(go.Scatter3d(x=x1,y=y1,z=z,mode="lines",line=dict(color="#55c6d9",width=8),name="DNA 가닥 1"))
    fig.add_trace(go.Scatter3d(x=x2,y=y2,z=z,mode="lines",line=dict(color="#d88acb",width=8),name="DNA 가닥 2"))
    for i in range(0,n,8):
        c="#f2d17b" if changed_idx is None or i//8 != changed_idx else "#ff626f"
        fig.add_trace(line3d([(x1[i],y1[i],z[i]),(x2[i],y2[i],z[i])],c,3,"염기쌍"))
    fig.update_layout(**scene_layout("DNA 이중 나선 · 3D 확대",height=600))
    return fig

# ---------- 상태 ----------
defaults={"stage":"body","organ":"심장","cell":"심근세포","organelle":"핵","removed":None,
          "trait":"기본 형질","sequence":"ATGCCGTA","changed_idx":None,"drug":None,"drug_applied":False}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k]=v

def go(stage):
    st.session_state.stage=stage
    st.rerun()

# ---------- 상단 ----------
st.markdown('<div class="hero"><div class="eyebrow">BIOVERSE · INTERACTIVE LIFE SCIENCE</div><h1>생명의 구조를 따라가는 3D 탐험</h1><p>인체 → 장기 → 세포 → 소기관 → DNA. 하나의 생명체를 단계적으로 확대하며 탐구합니다.</p></div>',unsafe_allow_html=True)
st.markdown("**탐험 경로**　① 인체　›　② 장기　›　③ 세포　›　④ 소기관　›　⑤ DNA")
st.progress({"body":0.0,"organ":.2,"cell":.4,"organelle":.6,"dna":.8,"drug":1.0}[st.session_state.stage])

with st.sidebar:
    st.markdown("## 🧭 탐험 메뉴")
    menu={"인체 탐색":"body","장기 분석":"organ","세포 확대":"cell","세포 소기관":"organelle","DNA와 형질":"dna","약물 반응 실험":"drug"}
    for label,key in menu.items():
        if st.button(label, use_container_width=True, type="primary" if st.session_state.stage==key else "secondary"):
            go(key)
    st.divider()
    st.caption("교육용 3D 모형 · 실제 인체의 크기와 구조를 단순화한 표현입니다.")
    if st.button("처음 인체 화면으로",use_container_width=True):
        st.session_state.removed=None
        go("body")

# ---------- 인체 ----------
if st.session_state.stage=="body":
    left,right=st.columns([1.55,1])
    with left:
        st.plotly_chart(body_scene(False,trait=st.session_state.trait),use_container_width=True,config={"displayModeBar":True})
    with right:
        st.markdown("### 인체 탐색")
        st.markdown('<div class="panel"><div class="eyebrow">ANATOMY MODE</div><h3>피부 아래의 구조를 확인해 보세요</h3><p class="small">절개 관찰 모드를 켜면 흉부와 복부의 주요 장기가 드러납니다. 장기를 선택하면 기능과 세포 단계로 이어집니다.</p></div>',unsafe_allow_html=True)
        if st.button("🩺 메스 절개 · 내부 장기 보기",use_container_width=True):
            go("organ")
        st.markdown("**현재 가상 형질**")
        st.write(st.session_state.trait)
        st.caption("DNA 탐구 단계에서 교육용 가상 형질을 바꿀 수 있습니다. 실제 유전자 편집 결과를 예측하는 기능은 아닙니다.")
        st.info("왼쪽 3D 모형은 마우스로 회전·확대할 수 있습니다.")

# ---------- 장기 ----------
elif st.session_state.stage=="organ":
    left,right=st.columns([1.55,1])
    with left:
        st.plotly_chart(body_scene(True,st.session_state.removed,st.session_state.trait),use_container_width=True,config={"displayModeBar":True})
        st.caption("장기를 제거한 모습은 기능 저하를 설명하기 위한 가상 시각화이며 실제 수술 장면이 아닙니다.")
    with right:
        st.markdown("### 장기 선택")
        organ=st.selectbox("탐구할 장기",list(ORGANS.keys()),index=list(ORGANS).index(st.session_state.organ))
        st.session_state.organ=organ
        d=ORGANS[organ]
        st.markdown(f'<div class="panel"><div class="eyebrow">ORGAN PROFILE</div><h3>{organ}</h3><p>{d["role"]}</p><hr><b>기능 저하 시 예상되는 영향</b><p class="small">{d["problem"]}</p></div>',unsafe_allow_html=True)
        a,b=st.columns(2)
        with a:
            if st.button("장기 가상 제거",use_container_width=True):
                st.session_state.removed=organ
                st.rerun()
        with b:
            if st.button("장기 복원",use_container_width=True):
                st.session_state.removed=None
                st.rerun()
        if st.session_state.removed==organ:
            st.warning(f"{organ}이(가) 없는 가상 모형입니다. {d['problem']}")
        st.markdown("**이 장기를 이루는 대표 세포**")
        st.write(" · ".join(d["cells"]))
        if st.button(f"{organ}의 세포로 확대 →",use_container_width=True):
            st.session_state.cell=d["cells"][0]
            go("cell")

# ---------- 세포 ----------
elif st.session_state.stage=="cell":
    d=ORGANS[st.session_state.organ]
    left,right=st.columns([1.45,1])
    with left:
        st.plotly_chart(cell_scene(st.session_state.cell),use_container_width=True,config={"displayModeBar":True})
    with right:
        st.markdown(f"### {st.session_state.organ}의 세포")
        cell=st.selectbox("세포 유형 선택",d["cells"],index=d["cells"].index(st.session_state.cell))
        st.session_state.cell=cell
        desc,features=CELL_INFO[cell]
        st.markdown(f'<div class="panel"><div class="eyebrow">CELL PROFILE</div><h3>{cell}</h3><p>{desc}</p><b>구조적 특징</b><p class="small">{features}</p></div>',unsafe_allow_html=True)
        st.markdown("**세포 내부 구성**")
        st.write("세포막 · 세포질 · 핵 · 미토콘드리아 · 소포체 · 골지체 · 리보솜")
        st.caption("실제 세포의 소기관 수와 배치는 세포 종류에 따라 달라집니다.")
        if st.button("세포의 핵을 확대 →",use_container_width=True):
            st.session_state.organelle="핵"
            go("organelle")

# ---------- 소기관 ----------
elif st.session_state.stage=="organelle":
    left,right=st.columns([1.4,1])
    with left:
        st.plotly_chart(organelle_scene(st.session_state.organelle),use_container_width=True,config={"displayModeBar":True})
    with right:
        st.markdown("### 세포 소기관 탐구")
        org=st.selectbox("확대할 소기관",["핵","미토콘드리아","소포체·리보솜"],index=["핵","미토콘드리아","소포체·리보솜"].index(st.session_state.organelle))
        st.session_state.organelle=org
        info={
            "핵":"DNA를 보관하고 유전자 발현을 조절하는 세포의 정보 관리 중심입니다. 핵막과 핵공이 핵과 세포질 사이의 물질 이동을 조절합니다.",
            "미토콘드리아":"세포 호흡을 통해 ATP를 만드는 데 중요한 역할을 합니다. 내막의 주름인 크리스타에는 에너지 전환 과정에 관여하는 단백질 복합체가 있습니다.",
            "소포체·리보솜":"리보솜은 단백질을 합성합니다. 조면소포체는 분비·막 단백질의 합성 및 가공에, 활면소포체는 지질 합성 등 여러 기능에 관여합니다."
        }
        st.markdown(f'<div class="panel"><div class="eyebrow">ORGANELLE PROFILE</div><h3>{org}</h3><p>{info[org]}</p></div>',unsafe_allow_html=True)
        if org=="핵":
            if st.button("핵 내부 DNA로 확대 →",use_container_width=True): go("dna")
        else:
            st.info("이 소기관의 구조를 확인한 뒤, 핵을 선택하면 DNA 탐구로 이어집니다.")
            if st.button("핵으로 이동 →",use_container_width=True):
                st.session_state.organelle="핵"; st.rerun()

# ---------- DNA ----------
elif st.session_state.stage=="dna":
    left,right=st.columns([1.35,1])
    with left:
        st.plotly_chart(dna_scene(st.session_state.sequence,st.session_state.changed_idx),use_container_width=True,config={"displayModeBar":True})
    with right:
        st.markdown("### DNA 염기서열 탐구")
        st.markdown('<div class="panel"><div class="eyebrow">DNA SEQUENCE LAB</div><h3>염기서열을 관찰하고 가상 변화를 적용해 보세요</h3><p class="small">아래 편집은 교육용 가상 모델입니다. 실제 유전자 편집 방법이나 생물학적 결과를 재현하지 않습니다.</p></div>',unsafe_allow_html=True)
        seq=st.session_state.sequence
        st.code("5′ — "+"  ".join(seq)+" — 3′",language="text")
        idx=st.selectbox("변경할 염기 위치",list(range(1,len(seq)+1)),format_func=lambda x:f"{x}번째 염기 ({seq[x-1]})")
        base=st.selectbox("새 염기",["A","T","G","C"])
        if st.button("가상 염기서열 변경",use_container_width=True):
            chars=list(seq); chars[idx-1]=base
            st.session_state.sequence="".join(chars)
            st.session_state.changed_idx=idx-1
            st.success("가상 서열이 변경되었습니다.")
            st.rerun()
        st.markdown("**가상 표현형 연결**")
        trait=st.selectbox("인체 모형에 적용할 교육용 형질",["기본 형질","가상 키 성장 형질","가상 홍채 색 변화"],index=["기본 형질","가상 키 성장 형질","가상 홍채 색 변화"].index(st.session_state.trait))
        if st.button("인체 모형에 형질 반영",use_container_width=True):
            st.session_state.trait=trait
            st.success("인체 모형의 가상 표현형을 업데이트했습니다.")
        if st.button("인체 모형으로 돌아가기",use_container_width=True): go("body")
        st.caption("실제 형질은 여러 유전자와 환경의 상호작용으로 결정되는 경우가 많습니다. 이 화면은 유전자-형질 관계를 설명하기 위한 단순화된 예시입니다.")

# ---------- 약물 ----------
elif st.session_state.stage=="drug":
    st.markdown("### 약물 작용과 인체 반응 시뮬레이션")
    st.warning("안전 안내: 이 공간은 약리학 학습용 가상 모델입니다. 실제 약물의 투여량·투여 방법을 안내하지 않으며, 오락 목적의 약물 사용이나 위험한 약물 체험을 재현하지 않습니다. 약물은 의료진·약사의 안내에 따라 사용해야 합니다.")
    left,right=st.columns([1,1.25])
    with left:
        drug=st.selectbox("학습할 약물 계열",list(DRUGS.keys()))
        st.session_state.drug=drug
        name,mechanism,effect,visual=DRUGS[drug]
        st.markdown(f'<div class="panel"><div class="eyebrow">PHARMACOLOGY</div><h3>{name}</h3><p>{mechanism}</p><b>알아둘 점</b><p class="small">{effect}</p></div>',unsafe_allow_html=True)
        if st.button("가상 반응 장면 실행",use_container_width=True):
            st.session_state.drug_applied=True
    with right:
        if st.session_state.drug_applied:
            # 3D 시야 장면: 환자의 시각·감각 변화를 상징하는 추상적 시각화
            fig=go.Figure()
            if drug=="기관지확장제":
                for r in [.35,.55,.78]:
                    fig.add_trace(go.Scatter3d(x=r*np.cos(np.linspace(0,2*np.pi,80)),y=r*np.sin(np.linspace(0,2*np.pi,80)),z=np.zeros(80),mode="lines",line=dict(color="#66d8bd",width=5),name="기도 단면"))
                for i in range(24):
                    a=i*2.4
                    fig.add_trace(ellipsoid((.9*np.cos(a),.9*np.sin(a),.1*np.sin(a*2)),(.035,.035,.035),"#9ee9d7","공기 흐름",1,8))
            elif drug=="항생제":
                rng=np.random.default_rng(4)
                for i in range(12):
                    p=rng.uniform(-.8,.8,3)
                    fig.add_trace(ellipsoid(tuple(p),(.10,.07,.07),"#d8797f","세균 모형",.85,10))
                fig.add_trace(ellipsoid((0,0,0),(.18,.18,.18),"#7bd7bd","면역 반응 중심",.8))
            else:
                # 추상적인 시야 구체와 광선. 실제 환각/취한 상태를 재현하지 않음.
                fig.add_trace(ellipsoid((0,0,0),(1.05,1.05,.12),"#4c7894","시야 기준면",.20,28))
                for a in np.linspace(0,2*np.pi,16,endpoint=False):
                    x,y=np.cos(a),np.sin(a)
                    fig.add_trace(line3d([(0,0,.05),(.85*x,.85*y,.05)],"#7ac8d7",3,"감각 신호"))
                clarity=.58 if drug in ["항히스타민제","수면·진정 관련 처방약"] else .9
                fig.add_trace(go.Scatter3d(x=[0],y=[0],z=[.12],mode="markers",marker=dict(size=18,color="#e7d9a3",opacity=clarity),name="시야 중심"))
            fig.update_layout(**scene_layout("가상 환자 시점 · 감각/생리 반응 시각화",height=520))
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":True})
            st.markdown(f'<div class="panel"><b>관찰 포인트</b><p>{visual}</p><p class="small">이 장면은 작용 원리를 상징적으로 표현한 것으로 실제 환자의 시야나 개인별 반응을 예측하지 않습니다.</p></div>',unsafe_allow_html=True)
        else:
            st.plotly_chart(body_scene(True,trait=st.session_state.trait),use_container_width=True,config={"displayModeBar":True})
            st.info("왼쪽에서 약물 계열을 선택하고 가상 반응 장면을 실행해 보세요.")
    st.caption("약물 반응은 개인의 건강 상태, 다른 약물, 연령 등 다양한 요인에 따라 달라집니다. 본 시뮬레이터는 진단·처방 도구가 아닙니다.")

st.divider()
st.markdown("<div style='text-align:center;color:#7791aa;font-size:.8rem'>BIOVERSE · 3D LIFE SCIENCE EXPLORER · 교육 및 탐구 목적</div>",unsafe_allow_html=True)
