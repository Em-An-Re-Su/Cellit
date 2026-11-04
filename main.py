
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import math

# Optional component enables actual 3D point-click interaction.
try:
    from streamlit_plotly_events import plotly_events
    HAS_3D_CLICK = True
except Exception:
    HAS_3D_CLICK = False

st.set_page_config(page_title="BIOVERSE 3D | 생명과학 탐험", page_icon="🧬", layout="wide")

# --------------------------- DESIGN ---------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:Pretendard,sans-serif}
.stApp{background:radial-gradient(circle at 18% 0%,#18324a 0%,#0a1725 43%,#07111d 100%);color:#edf5ff}
section[data-testid="stSidebar"]{background:#0b1928;border-right:1px solid #294158}
.block-container{max-width:1540px;padding-top:1.2rem}
.hero{padding:22px 26px;border:1px solid #31516b;border-radius:18px;background:linear-gradient(120deg,rgba(22,52,78,.96),rgba(10,25,42,.92));margin-bottom:16px}
.hero h1{font-size:2.15rem;margin:0;color:#f3f8ff}
.hero p{color:#b0c5d9;margin:.4rem 0 0}
.panel{background:rgba(17,36,55,.9);border:1px solid #2c4962;padding:16px 18px;border-radius:14px;margin-bottom:12px}
.eyebrow{color:#6ee0ce;font-size:.74rem;font-weight:800;letter-spacing:1.8px}
.small{font-size:.88rem;color:#a9bfd3}
.stButton>button{border-radius:10px;border:1px solid #41617d;background:#17354f;color:#edf6ff;min-height:2.55rem}
.stButton>button:hover{border-color:#69d8c8;background:#214b65;color:white}
div[data-testid="stMetric"]{background:#142b40;border:1px solid #31506a;padding:12px;border-radius:12px}
</style>
""", unsafe_allow_html=True)

# --------------------------- DATA ---------------------------
ORGANS = {
    "뇌": dict(pos=(0,-.02,7.05), color="#c58bda", system="신경계",
        role="감각 정보를 통합하고 운동·기억·언어·감정·항상성을 조절합니다.",
        cells=["뉴런","성상세포","희소돌기아교세포"],
        problem="손상 부위에 따라 운동·감각·언어·기억 기능이 달라질 수 있습니다.",
        detail="대뇌·소뇌·뇌줄기 등 여러 영역이 연결되어 정보를 처리합니다."),
    "심장": dict(pos=(0,-.27,5.15), color="#dc5368", system="순환계",
        role="수축과 이완을 반복해 혈액을 폐와 온몸으로 보냅니다.",
        cells=["심근세포","심장박동조율세포","혈관내피세포"],
        problem="혈액 순환이 크게 저하되면 뇌와 다른 장기에 산소·영양분 공급이 부족해질 수 있습니다.",
        detail="심방·심실·판막·전도계가 협력하며 심근세포의 동기화된 수축이 펌프 기능을 만듭니다."),
    "폐": dict(pos=(0,-.18,5.35), color="#70b8dc", system="호흡계",
        role="폐포에서 산소와 이산화탄소를 교환합니다.",
        cells=["폐포 1형 세포","폐포 2형 세포","섬모상피세포"],
        problem="가스 교환이 저하되면 혈액의 산소 공급과 이산화탄소 배출에 문제가 생깁니다.",
        detail="폐포 1형 세포는 얇은 교환 표면을 만들고, 2형 세포는 표면활성제를 분비합니다."),
    "간": dict(pos=(.34,-.20,4.55), color="#bd8053", system="소화·대사계",
        role="영양소 대사, 담즙 생성, 여러 혈장 단백질 합성 및 물질 변환을 담당합니다.",
        cells=["간세포","쿠퍼세포","간성상세포"],
        problem="대사·담즙 생성·단백질 합성 등 여러 기능에 영향을 줄 수 있습니다.",
        detail="간세포가 대사와 합성의 중심이며 쿠퍼세포는 면역 방어에 관여합니다."),
    "위": dict(pos=(-.12,-.20,4.43), color="#d88e7b", system="소화계",
        role="음식물을 저장하고 위산·소화 효소와 섞어 소화를 시작합니다.",
        cells=["위표면점액세포","벽세포","주세포"],
        problem="소화와 점막 방어에 문제가 생겨 통증이나 소화 장애가 나타날 수 있습니다.",
        detail="벽세포는 염산, 주세포는 펩시노겐, 점액세포는 보호 점액을 분비합니다."),
    "신장": dict(pos=(.50,.02,3.96), color="#b97883", system="비뇨계",
        role="혈액을 여과하고 노폐물 배출과 수분·전해질 균형을 조절합니다.",
        cells=["족세포","세뇨관 상피세포","사구체 내피세포"],
        problem="노폐물 배출과 체액·전해질 균형에 문제가 생길 수 있습니다.",
        detail="네프론의 사구체와 세뇨관이 여과·재흡수·분비를 수행합니다."),
    "소장": dict(pos=(0,-.25,3.90), color="#d6b66b", system="소화계",
        role="소화된 영양소 대부분을 흡수합니다.",
        cells=["흡수상피세포","배상세포","장내분비세포"],
        problem="영양소 흡수가 저하되어 영양 상태와 에너지 공급에 영향을 줄 수 있습니다.",
        detail="융모와 미세융모가 흡수 표면적을 크게 늘립니다."),
    "췌장": dict(pos=(.10,-.25,4.72), color="#d9a878", system="소화·내분비계",
        role="소화 효소를 분비하고 인슐린·글루카곤으로 혈당 조절에 관여합니다.",
        cells=["췌장 선방세포","베타세포","알파세포"],
        problem="소화 효소 분비나 혈당 조절에 문제가 생길 수 있습니다.",
        detail="외분비 선방세포와 내분비 랑게르한스섬이 서로 다른 기능을 담당합니다.")
}

CELL_INFO = {
    "뉴런":("신경 신호를 받아들이고 다른 세포로 전달하는 세포입니다.","세포체·수상돌기·축삭·시냅스"),
    "성상세포":("신경세포 주변 환경과 혈액-뇌 장벽 유지에 기여합니다.","별 모양 돌기·이온 조절·대사 지원"),
    "희소돌기아교세포":("중추신경계 축삭에 수초를 형성해 신호 전달을 돕습니다.","수초·축삭 절연·여러 돌기"),
    "심근세포":("심장 근육을 이루며 동기화된 수축으로 혈액을 이동시킵니다.","근절·개재판·풍부한 미토콘드리아"),
    "심장박동조율세포":("전기 신호를 만들어 심장 박동 리듬을 조절합니다.","이온 통로·자발적 탈분극·전기적 연결"),
    "혈관내피세포":("혈관 안쪽을 덮어 물질 교환과 혈관 반응을 조절합니다.","얇은 세포층·세포간 연결"),
    "폐포 1형 세포":("얇은 폐포 표면을 형성해 기체 확산을 돕습니다.","매우 얇은 세포질·넓은 표면"),
    "폐포 2형 세포":("표면활성제를 분비해 폐포의 표면 장력을 낮춥니다.","분비 과립·층판소체"),
    "섬모상피세포":("섬모 운동으로 기도 점액과 입자를 이동시킵니다.","섬모·미세소관"),
    "간세포":("대사·합성·저장·물질 변환을 담당합니다.","소포체·미토콘드리아·글리코겐"),
    "쿠퍼세포":("간의 혈액 속 이물질과 노화 세포 처리에 관여합니다.","포식 작용·리소좀"),
    "간성상세포":("비타민 A 저장 및 간 조직 구조 유지에 관여합니다.","지질 방울·세포외기질"),
    "위표면점액세포":("점액과 중탄산염으로 위 점막을 보호합니다.","점액 분비 과립"),
    "벽세포":("위산과 내인성 인자를 분비합니다.","분비 세관·풍부한 미토콘드리아"),
    "주세포":("단백질 소화 효소의 전구체인 펩시노겐을 분비합니다.","조면소포체·분비 과립"),
    "족세포":("사구체 모세혈관을 감싸 여과 장벽을 형성합니다.","발돌기·여과 틈새"),
    "세뇨관 상피세포":("물·이온·영양소의 재흡수와 분비를 수행합니다.","미세융모·미토콘드리아"),
    "사구체 내피세포":("혈액이 여과되는 모세혈관의 안쪽을 구성합니다.","창문형 구멍·기저막"),
    "흡수상피세포":("소화된 영양소를 흡수하는 소장 상피세포입니다.","미세융모·막 수송 단백질"),
    "배상세포":("점액을 분비해 장 표면을 보호합니다.","점액 분비 과립"),
    "장내분비세포":("장 내 환경을 감지하고 호르몬 신호를 분비합니다.","분비 과립·화학적 감지"),
    "췌장 선방세포":("소화 효소가 포함된 분비물을 만듭니다.","조면소포체·분비 과립"),
    "베타세포":("혈당이 높아졌을 때 인슐린을 분비합니다.","분비 과립·포도당 감지"),
    "알파세포":("혈당이 낮아졌을 때 글루카곤을 분비합니다.","분비 과립·호르몬 신호")
}

ORGAN_EFFECTS = {
    "뇌": {"영향":["운동·감각 정보 처리","기억·언어 기능","자율신경 조절"],"지표":{"신경 정보 전달":28,"운동 조절":35,"인지 기능":32}},
    "심장": {"영향":["혈액 순환 저하","조직 산소 공급 감소","다른 장기 기능 부담"],"지표":{"순환 기능":18,"조직 산소 공급":30,"활동 지속 능력":25}},
    "폐": {"영향":["산소 교환 저하","이산화탄소 배출 저하","호흡 부담 증가"],"지표":{"산소 교환":22,"이산화탄소 배출":35,"호흡 여유":25}},
    "간": {"영향":["영양소 대사 변화","담즙 생성 저하","혈장 단백질 합성 저하"],"지표":{"대사 기능":35,"담즙 생성":25,"단백질 합성":40}},
    "위": {"영향":["음식물 소화 과정 변화","위산·효소 분비 저하","소화 불편 가능"],"지표":{"위 내 소화":35,"단백질 소화 시작":30,"점막 방어":55}},
    "신장": {"영향":["노폐물 배출 저하","수분·전해질 조절 변화","산염기 균형 부담"],"지표":{"여과 기능":20,"전해질 조절":35,"노폐물 배출":22}},
    "소장": {"영향":["영양소 흡수 저하","수분 흡수 변화","영양 상태 영향"],"지표":{"영양소 흡수":25,"수분 흡수":45,"에너지 공급":35}},
    "췌장": {"영향":["소화 효소 분비 변화","혈당 조절 이상","대사 균형 부담"],"지표":{"소화 효소 분비":35,"혈당 조절":25,"대사 균형":40}}
}

ORGANELLES = {
    "핵":("DNA를 보관하고 유전자 발현을 조절하는 정보 관리 중심입니다.","핵막·핵공·염색질·핵소체"),
    "미토콘드리아":("세포 호흡과 ATP 생성에 중요한 역할을 합니다.","외막·내막·크리스타·기질"),
    "조면소포체":("리보솜이 붙어 분비 단백질과 막 단백질의 합성·가공에 관여합니다.","막 주머니·부착 리보솜"),
    "활면소포체":("지질 합성, 해독, 칼슘 저장 등 세포 종류별 기능을 수행합니다.","관 모양 막 구조"),
    "골지체":("단백질과 지질을 가공·분류·포장해 목적지로 보냅니다.","납작한 시스터나 층·운반 소포"),
    "리보솜":("mRNA 정보를 읽어 아미노산을 연결해 단백질을 합성합니다.","큰 소단위체·작은 소단위체"),
    "리소좀":("분해 효소를 이용해 세포 안의 물질을 분해·재활용합니다.","막으로 둘러싸인 산성 소기관")
}

DRUGS = {
    "아세트아미노펜 계열":("진통·해열 치료","통증과 발열 조절에 관여하는 약물입니다.","증상 완화가 목적이며 간 건강 등 개인 상태와 제품별 주의사항이 중요합니다.",{"각성":90,"호흡 기능":100,"통증 신호":55}),
    "항히스타민제":("알레르기 치료","히스타민 수용체 작용을 차단해 알레르기 증상을 완화합니다.","일부 종류는 졸림·주의력 저하를 일으킬 수 있습니다.",{"각성":65,"호흡 기능":100,"알레르기 신호":35}),
    "기관지확장제":("호흡기 치료","기도 평활근을 이완시켜 공기 흐름을 개선하는 데 도움을 줍니다.","종류에 따라 심박 변화나 떨림 등이 나타날 수 있습니다.",{"각성":90,"호흡 기능":90,"기도 저항":35}),
    "항생제":("세균 감염 치료","세균의 세포벽·단백질 합성 등 생존 과정에 작용하는 약물군입니다.","바이러스에는 효과가 없으며 불필요한 사용은 내성 문제를 키웁니다.",{"각성":100,"호흡 기능":100,"세균 증식 지표":25}),
    "국소마취제":("의료용 감각 전달 조절","신경세포의 전압 개폐성 나트륨 통로를 억제해 특정 부위의 신호 전달을 줄입니다.","전문적인 의료 환경에서 사용과 감시가 필요합니다.",{"각성":100,"호흡 기능":100,"해당 부위 감각 신호":20}),
    "항염증제":("염증·통증 조절","종류에 따라 염증 매개 물질의 생성 또는 작용을 억제합니다.","위장관·신장 등에 미치는 영향은 약물과 개인 상태에 따라 다릅니다.",{"각성":100,"호흡 기능":100,"염증 신호":40}),
    "항우울제 계열":("정신건강 치료","세로토닌 등 신경전달 체계에 작용하는 여러 치료 약물군이 있습니다.","효과와 부작용은 종류와 개인에 따라 다르며 의료진의 관리가 필요합니다.",{"각성":85,"호흡 기능":100,"신경전달 조절":65}),
    "수면·진정 관련 처방약":("의료용 수면·진정 치료","중추신경계 활동을 낮추는 등 약물별로 서로 다른 기전이 있습니다.","졸림과 반응 저하가 나타날 수 있고 다른 진정 물질과 함께 작용하면 위험할 수 있습니다.",{"각성":35,"호흡 기능":78,"반응 속도":40}),
    "오피오이드 진통제(펜타닐 포함)":("중증 통증의 의료적 조절","오피오이드 수용체에 작용해 통증 신호 전달을 변화시키는 강력한 진통제 계열입니다.","호흡 억제와 의식 저하 등 생명을 위협할 수 있는 위험이 있어 엄격한 의료적 감시가 필요합니다.",{"각성":28,"호흡 기능":30,"통증 신호":25}),
    "항응고제":("혈전 예방·치료","혈액 응고 과정의 특정 단계를 억제해 혈전 형성을 줄이는 약물군입니다.","출혈 위험과 상호작용을 고려한 의료진의 관리가 필요합니다.",{"각성":100,"호흡 기능":100,"응고 과정 지표":35}),
    "인슐린":("당뇨병 치료 호르몬","세포의 포도당 이용을 돕고 혈당을 낮추는 호르몬입니다.","혈당 관리와 저혈당 위험을 고려한 의료적 관리가 중요합니다.",{"각성":90,"호흡 기능":100,"혈당 조절 지표":75})
}

# --------------------------- 3D GEOMETRY ---------------------------
def mesh_surface(x,y,z,color,name,opacity=1.0):
    return go.Surface(
        x=x,y=y,z=z,
        surfacecolor=np.zeros_like(x),
        colorscale=[[0,color],[1,color]],
        showscale=False,opacity=opacity,name=name,
        hovertemplate=f"{name}<extra></extra>",
        lighting=dict(ambient=.52,diffuse=.82,specular=.28,roughness=.52)
    )

def loft(center_path,rx_values,ry_values,color,name,opacity=1.0,ntheta=32):
    """서로 다른 단면을 부드럽게 연결한 유기적 형태."""
    path=np.asarray(center_path,float)
    theta=np.linspace(0,2*np.pi,ntheta)
    X=[];Y=[];Z=[]
    for (cx,cy,cz),rx,ry in zip(path,rx_values,ry_values):
        X.append(cx+rx*np.cos(theta))
        Y.append(cy+ry*np.sin(theta))
        Z.append(np.full_like(theta,cz))
    return mesh_surface(np.asarray(X),np.asarray(Y),np.asarray(Z),color,name,opacity)

def blob(center,radii,color,name,opacity=1.0,detail=40,lobes=0):
    u=np.linspace(0,2*np.pi,detail)
    v=np.linspace(0,np.pi,detail)
    U,V=np.meshgrid(u,v)
    mod=1.0
    if lobes:
        mod += .045*np.sin(lobes*U)*np.sin(4*V)+.025*np.cos(3*U+V)
    x=center[0]+radii[0]*mod*np.cos(U)*np.sin(V)
    y=center[1]+radii[1]*mod*np.sin(U)*np.sin(V)
    z=center[2]+radii[2]*mod*np.cos(V)
    return mesh_surface(x,y,z,color,name,opacity)

def tube(points,radius,color,name,n=14):
    """곡선을 따라 이어지는 3D 관 형태."""
    p=np.asarray(points,float)
    if len(p)<2: return []
    verts=[]; faces=[]
    for i,pt in enumerate(p):
        tangent=p[min(i+1,len(p)-1)]-p[max(i-1,0)]
        tangent=tangent/(np.linalg.norm(tangent)+1e-9)
        helper=np.array([0,0,1.]) if abs(tangent[2])<.9 else np.array([0,1.,0])
        a=np.cross(tangent,helper)
        a/=np.linalg.norm(a)+1e-9
        b=np.cross(tangent,a)
        for ang in np.linspace(0,2*np.pi,n,endpoint=False):
            verts.append(pt+radius*(a*np.cos(ang)+b*np.sin(ang)))
    for i in range(len(p)-1):
        for j in range(n):
            a=i*n+j; b=i*n+(j+1)%n
            c=(i+1)*n+(j+1)%n; d=(i+1)*n+j
            faces.extend([(a,b,d),(b,c,d)])
    v=np.asarray(verts); f=np.asarray(faces)
    return [go.Mesh3d(x=v[:,0],y=v[:,1],z=v[:,2],
        i=f[:,0],j=f[:,1],k=f[:,2],color=color,opacity=.98,
        name=name,hovertemplate=f"{name}<extra></extra>")]

def add_body(fig,cut=False,trait=None):
    skin="#c9947e"
    # 몸통은 높이에 따라 폭이 달라지는 단면 구조
    z=np.array([3.9,4.15,4.55,5.0,5.45,5.9,6.2])
    cx=np.zeros_like(z); cy=np.zeros_like(z)
    rx=[.40,.56,.68,.73,.70,.65,.42]
    ry=[.28,.34,.37,.36,.34,.31,.25]
    fig.add_trace(loft(list(zip(cx,cy,z)),rx,ry,skin,"몸통",.23 if cut else .97,48))
    fig.add_trace(loft([(0,0,6.12),(0,0,6.30),(0,0,6.52)],
        [.20,.18,.19],[.19,.18,.18],skin,"목",.98))
    fig.add_trace(blob((0,-.015,6.88),(.36,.32,.48),skin,"머리",1,42,2))
    fig.add_trace(blob((0,-.29,6.78),(.19,.11,.14),"#d5a08b","코",1,22))
    for x in [-.145,.145]:
        fig.add_trace(blob((x,-.29,6.98),(.085,.045,.065),"#f1e6d8","눈 흰자",1,18))
    iris=trait.get("iris_color","#5b4636") if trait else "#5b4636"
    hair=trait.get("hair_color","#38251e") if trait else "#38251e"
    for x in [-.145,.145]:
        fig.add_trace(blob((x,-.335,6.98),(.038,.022,.040),iris,"홍채",1,18))
        fig.add_trace(blob((x,-.35,6.98),(.016,.012,.024),"#171717","동공",1,14))
    uu=np.linspace(0,2*np.pi,42)
    vv=np.linspace(0,np.pi/2,18)
    U,V=np.meshgrid(uu,vv)
    hx=.375*np.cos(U)*np.sin(V)
    hy=.34*np.sin(U)*np.sin(V)-.015
    hz=7.02+.30*np.cos(V)
    fig.add_trace(mesh_surface(hx,hy,hz,hair,"머리카락",1))
    # 팔과 다리는 서로 다른 굵기의 관형 구조
    for s in [-1,1]:
        fig.add_traces(tube([(s*.62,0,5.85),(s*.83,0,5.50),(s*.98,0,5.05)],.16,skin,"위팔"))
        fig.add_traces(tube([(s*.98,0,5.05),(s*1.08,-.01,4.62),(s*1.12,-.04,4.12)],.115,skin,"아래팔"))
        fig.add_trace(blob((s*1.12,-.06,3.95),(.13,.09,.22),skin,"손",1,20))
        fig.add_traces(tube([(s*.32,0,3.95),(s*.36,0,3.25),(s*.37,0,2.55)],.205,skin,"허벅지"))
        fig.add_traces(tube([(s*.37,0,2.55),(s*.37,0,1.85),(s*.37,-.01,1.10)],.145,skin,"종아리"))
        fig.add_trace(blob((s*.37,-.10,.82),(.17,.30,.12),skin,"발",1,22))
    if cut:
        fig.add_trace(go.Scatter3d(
            x=[-.62,-.58,-.52,-.52,.52,.58,.62],
            y=[-.36]*7,
            z=[6.05,5.75,5.35,4.35,4.35,5.75,6.05],
            mode="lines",line=dict(color="#f0c1a9",width=6),
            name="절개 경계",hoverinfo="skip"))

def add_organ(fig,name,opacity=1.0):
    d=ORGANS[name]
    x,y,z=d["pos"]
    c=d["color"]
    if name=="뇌":
        fig.add_trace(blob((x,y,z),(.39,.33,.37),c,"대뇌 반구",opacity,48,8))
        for j in range(8):
            xx=np.linspace(-.27,.27,50)
            yy=y-.29+0.035*np.sin(xx*18+j*.7)
            zz=z+(j-3.5)*.075+.035*np.cos(xx*15+j)
            fig.add_trace(go.Scatter3d(x=xx,y=yy,z=zz,mode="lines",
                line=dict(color="#efc4eb",width=2),showlegend=False,hoverinfo="skip"))
        fig.add_trace(blob((0,.20,6.82),(.22,.20,.17),"#a97ac4","소뇌",opacity,28,5))
    elif name=="심장":
        fig.add_trace(blob((-.13,y,z+.08),(.23,.21,.34),"#e56a78","좌심실 영역",opacity,36,2))
        fig.add_trace(blob((.14,y,z+.10),(.22,.20,.30),"#cf465d","우심실 영역",opacity,36,2))
        fig.add_trace(blob((0,y,z+.34),(.28,.20,.18),"#ed8790","심방 영역",opacity,30,2))
        fig.add_traces(tube([(0,y,z+.35),(0,y,z+.60),(.05,y,z+.73)],.065,"#bd5264","대동맥"))
        fig.add_traces(tube([(-.12,y,z+.32),(-.20,y,z+.55),(-.28,y,z+.65)],.045,"#759acb","폐동맥"))
    elif name=="폐":
        for s in [-1,1]:
            fig.add_trace(blob((s*.32,y,z),(.27,.20,.55),
                "#8bc8e4" if s<0 else "#6fb3d6","폐엽",opacity,42,4))
            for j in range(2):
                zz=z-.2+j*.27
                xx=np.linspace(s*.18,s*.48,25)
                fig.add_trace(go.Scatter3d(x=xx,y=np.full_like(xx,y-.18),
                    z=zz+.06*np.sin(np.linspace(0,np.pi,25)),mode="lines",
                    line=dict(color="#d5edf5",width=2),showlegend=False,hoverinfo="skip"))
        fig.add_traces(tube([(0,y,z+.65),(0,y,z+.32),(0,y,z+.10)],.07,"#e6c5b4","기관"))
        for s in [-1,1]:
            fig.add_traces(tube([(0,y,z+.18),(s*.18,y,z+.02),(s*.28,y,z-.10)],.035,"#e6c5b4","기관지"))
    elif name=="간":
        fig.add_trace(blob((x,y,z),(.53,.29,.27),c,"간 우엽",opacity,46,3))
        fig.add_trace(blob((x-.39,y-.015,z+.02),(.25,.23,.20),"#d39769","간 좌엽",opacity,36,2))
        fig.add_traces(tube([(x-.10,y-.25,z-.08),(x+.12,y-.27,z-.12)],.025,"#e5c17b","간문맥"))
    elif name=="위":
        pts=[(x-.18,y,z+.34),(x-.28,y,z+.17),(x-.25,y,z-.02),
             (x-.08,y,z-.20),(x+.12,y,z-.23),(x+.23,y,z-.10)]
        fig.add_traces(tube(pts,.16,c,"위의 곡선형 몸통",18))
        fig.add_trace(blob((x-.18,y,z+.29),(.15,.15,.18),"#e5a38e","위 분문부",opacity,24))
    elif name=="신장":
        for s in [-1,1]:
            u=np.linspace(0,2*np.pi,48)
            v=np.linspace(0,np.pi,36)
            U,V=np.meshgrid(u,v)
            mod=1-.22*np.exp(-((U-np.pi/2)/.45)**2)*np.sin(V)
            xx=s*.48+.19*mod*np.cos(U)*np.sin(V)
            yy=y+.15*np.sin(U)*np.sin(V)
            zz=z+.31*np.cos(V)
            fig.add_trace(mesh_surface(xx,yy,zz,c,"신장",opacity))
            fig.add_trace(blob((s*.48-s*.07,y-.17,z),(.09,.09,.12),"#e4c28d","신장문",opacity,18))
    elif name=="소장":
        for j in range(6):
            xx=np.linspace(-.30,.30,65)
            yy=y+.11*np.sin(xx*19+j*1.15)
            zz=z+(j-2.5)*.085+.045*np.cos(xx*17+j)
            fig.add_trace(go.Scatter3d(x=xx,y=yy,z=zz,mode="lines",
                line=dict(color=c,width=7),showlegend=False,hoverinfo="skip"))
    elif name=="췌장":
        xx=np.linspace(-.43,.43,70)
        yy=y+.04*np.sin(xx*5)
        zz=z+.045*np.sin(xx*9)
        fig.add_trace(go.Scatter3d(x=xx,y=yy,z=zz,mode="lines",
            line=dict(color=c,width=12),name="췌장"))
        for j in range(5):
            fig.add_trace(blob((-.28+j*.14,y-.02,z+.06*np.sin(j)),
                (.055,.06,.07),"#f0c79d","췌장 소엽",opacity,14))

def body_scene(cut=False,selected=None,removed=None,trait=None,click_targets=False):
    fig=go.Figure()
    add_body(fig,cut,trait)
    if cut:
        for name in ORGANS:
            if name==removed:
                continue
            add_organ(fig,name,1.0 if name==selected else .9)
        if removed:
            rx,ry,rz=ORGANS[removed]["pos"]
            fig.add_trace(go.Scatter3d(
                x=[rx],y=[ry-.34],z=[rz],mode="markers+text",
                marker=dict(size=15,color="#ff6578",symbol="x",
                            line=dict(width=3,color="#ffe0e0")),
                text=[f"{removed} 기능 비활성"],textposition="top center",
                textfont=dict(color="#ff9aa7",size=11),
                showlegend=False,hoverinfo="skip"))
            for other in ORGANS:
                if other!=removed:
                    ox,oy,oz=ORGANS[other]["pos"]
                    fig.add_trace(go.Scatter3d(
                        x=[rx,ox],y=[ry-.25,oy-.25],z=[rz,oz],
                        mode="lines",
                        line=dict(color="rgba(245,115,130,.42)",width=3,dash="dot"),
                        showlegend=False,hoverinfo="skip"))
        if click_targets:
            names=[n for n in ORGANS if n!=removed]
            fig.add_trace(go.Scatter3d(
                x=[ORGANS[n]["pos"][0] for n in names],
                y=[ORGANS[n]["pos"][1]-.38 for n in names],
                z=[ORGANS[n]["pos"][2] for n in names],
                mode="markers+text",
                marker=dict(size=10,color="#fff2bc",opacity=.92,
                            line=dict(color="#253c50",width=2)),
                text=names,textposition="top center",
                customdata=names,name="장기 선택",
                hovertemplate="%{customdata}<extra>클릭하여 확대</extra>"))
    fig.update_layout(
        title="인체 해부 모형 · 3D 탐색",height=720,
        margin=dict(l=0,r=0,t=45,b=0),
        paper_bgcolor="rgba(0,0,0,0)",font=dict(color="#dceafa"),
        scene=dict(bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False,range=[-1.5,1.5]),
            yaxis=dict(visible=False,range=[-1,1]),
            zaxis=dict(visible=False,range=[0,7.8]),
            aspectmode="manual",aspectratio=dict(x=.72,y=.48,z=1.55),
            camera=dict(eye=dict(x=1.8,y=-2.6,z=1.1))),
        showlegend=False)
    return fig

def cell_scene(cell_name):
    fig=go.Figure()
    fig.add_trace(blob((0,0,0),(1.35,1.0,.85),"#64b8b0","세포막",.20,44,5))
    fig.add_trace(blob((-.18,.02,.04),(.43,.39,.39),"#9576c8","핵",.98,34,2))
    fig.add_trace(blob((-.08,-.29,.12),(.14,.12,.13),"#e5c16f","핵소체",1,22))
    for p in [(.62,.32,.22),(-.72,.30,-.20),(.50,-.48,-.30)]:
        fig.add_trace(blob(p,(.29,.15,.15),"#d77c49","미토콘드리아 외막",1,26,2))
        for k in range(3):
            t=np.linspace(-.18,.18,24)
            yy=p[1]+.04*np.sin(t*28+k)
            zz=np.full_like(t,p[2]+(k-1)*.045)
            fig.add_trace(go.Scatter3d(x=p[0]+t,y=yy,z=zz,mode="lines",
                line=dict(color="#ffe0a1",width=3),showlegend=False,hoverinfo="skip"))
    # 소포체
    for k in range(5):
        t=np.linspace(-.42,.42,45)
        x=-.35+t
        y=np.full_like(t,.55+k*.045)+.05*np.sin(t*9+k)
        z=np.full_like(t,.26+(k-2)*.07)
        fig.add_trace(go.Scatter3d(x=x,y=y,z=z,mode="lines",
            line=dict(color="#62c7db",width=5),showlegend=False,hoverinfo="skip"))
    # 골지체
    for k in range(5):
        t=np.linspace(-.34,.34,40)
        x=.10+t
        y=np.full_like(t,-.72-k*.035)+.05*np.sin(t*7+k)
        z=np.full_like(t,-.28+(k-2)*.06)
        fig.add_trace(go.Scatter3d(x=x,y=y,z=z,mode="lines",
            line=dict(color="#e5b968",width=6),showlegend=False,hoverinfo="skip"))
    rng=np.random.default_rng(13)
    pts=rng.normal(0,.62,(70,3))
    mask=np.sum((pts/np.array([1.2,.9,.75]))**2,axis=1)<1
    pts=pts[mask]
    fig.add_trace(go.Scatter3d(x=pts[:,0],y=pts[:,1],z=pts[:,2],
        mode="markers",marker=dict(size=2.8,color="#f0e5b8"),name="리보솜"))
    fig.update_layout(
        title=f"{cell_name} · 세포 내부 구조",height=650,
        margin=dict(l=0,r=0,t=45,b=0),paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),yaxis=dict(visible=False),zaxis=dict(visible=False),
            aspectmode="data",camera=dict(eye=dict(x=1.6,y=-2.2,z=1.2))),
        showlegend=False)
    return fig

def organelle_scene(name):
    fig=go.Figure()
    if name=="핵":
        fig.add_trace(blob((0,0,0),(.85,.72,.66),"#9676c7","핵막",.45,40,2))
        fig.add_trace(blob((.05,-.05,.04),(.23,.22,.22),"#e5bd68","핵소체",1,28))
        for a in np.linspace(0,2*np.pi,18,endpoint=False):
            fig.add_trace(blob((.82*np.cos(a),.70*np.sin(a),.04),
                (.045,.045,.045),"#d8c6f4","핵공",1,12))
        rng=np.random.default_rng(3)
        pts=rng.normal(0,.32,(90,3))
        fig.add_trace(go.Scatter3d(x=pts[:,0],y=pts[:,1],z=pts[:,2],
            mode="markers",marker=dict(size=2,color="#d9a6d4"),name="염색질"))
    elif name=="미토콘드리아":
        fig.add_trace(blob((0,0,0),(1.05,.53,.43),"#d77d48","외막",1,44,2))
        for k in range(7):
            t=np.linspace(-.82,.82,60)
            x=t
            y=.22*np.sin(12*t+k*.6)
            z=np.full_like(t,(k-3)*.045)
            fig.add_trace(go.Scatter3d(x=x,y=y,z=z,mode="lines",
                line=dict(color="#ffe0a1",width=5),showlegend=False,hoverinfo="skip"))
    elif name in ["조면소포체","활면소포체"]:
        for k in range(9):
            t=np.linspace(-.9,.9,70)
            x=t
            y=(k-4)*.15+.08*np.sin(t*7+k)
            z=.10*np.cos(t*5+k)
            fig.add_trace(go.Scatter3d(x=x,y=y,z=z,mode="lines",
                line=dict(color="#62c7db",width=7),showlegend=False,hoverinfo="skip"))
            if name=="조면소포체":
                idx=np.arange(3,67,7)
                fig.add_trace(go.Scatter3d(x=x[idx],y=y[idx],z=z[idx]+.035,
                    mode="markers",marker=dict(size=3,color="#f2d17b"),
                    showlegend=False,hoverinfo="skip"))
    elif name=="골지체":
        for k in range(7):
            t=np.linspace(-.8,.8,60)
            x=t
            y=np.full_like(t,(k-3)*.13)+.07*np.sin(t*4)
            z=np.full_like(t,(k-3)*.07)
            fig.add_trace(go.Scatter3d(x=x,y=y,z=z,mode="lines",
                line=dict(color="#e6b965",width=9),showlegend=False,hoverinfo="skip"))
        for x,y,z in [(-.9,.1,.2),(.9,-.1,-.2),(.7,.4,.15)]:
            fig.add_trace(blob((x,y,z),(.10,.10,.10),"#e5a7a3","운반 소포",1,18))
    elif name=="리보솜":
        fig.add_trace(blob((-.20,0,0),(.48,.38,.30),"#72b5a5","큰 소단위체",1,30,2))
        fig.add_trace(blob((.30,0,-.12),(.36,.30,.23),"#e4c477","작은 소단위체",1,28,2))
        fig.add_trace(go.Scatter3d(x=[-.9,.9],y=[0,0],z=[.25,.25],
            mode="markers",marker=dict(size=5,color="#c58cdb"),name="mRNA 진행 방향"))
    else:
        fig.add_trace(blob((0,0,0),(.55,.48,.45),"#8b9fc5","리소좀 막",.8,32,2))
        for i in range(25):
            a=i*2.4
            fig.add_trace(blob((.35*np.cos(a),.30*np.sin(a),.22*np.sin(a*1.7)),
                (.055,.055,.055),"#e8cf88","분해 효소 입자",1,12))
    fig.update_layout(
        title=f"{name} · 소기관 3D 확대",height=610,
        margin=dict(l=0,r=0,t=45,b=0),paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),yaxis=dict(visible=False),zaxis=dict(visible=False),
            aspectmode="data",camera=dict(eye=dict(x=1.7,y=-2.2,z=1.15))),
        showlegend=False)
    return fig

def dna_scene(seq,changed=None):
    fig=go.Figure()
    n=len(seq)
    t=np.linspace(0,4*np.pi,max(80,n*10))
    z=np.linspace(-2.5,2.5,len(t))
    x1=.65*np.cos(t); y1=.65*np.sin(t)
    x2=-x1; y2=-y1
    fig.add_trace(go.Scatter3d(x=x1,y=y1,z=z,mode="lines",
        line=dict(color="#57c8d9",width=9),name="DNA 가닥 1"))
    fig.add_trace(go.Scatter3d(x=x2,y=y2,z=z,mode="lines",
        line=dict(color="#d78ac8",width=9),name="DNA 가닥 2"))
    colors={"A":"#56c9a5","T":"#e9a85d","G":"#789ce5","C":"#d78ac8"}
    for i,b in enumerate(seq):
        q=int(i/(max(n-1,1))*(len(t)-1))
        c="#ff6578" if i==changed else colors[b]
        fig.add_trace(go.Scatter3d(
            x=[x1[q],x2[q]],y=[y1[q],y2[q]],z=[z[q],z[q]],
            mode="lines+markers",line=dict(color=c,width=4),
            marker=dict(size=3,color=c),showlegend=False,
            hovertemplate=f"{i+1}번 염기쌍: {b}<extra></extra>"))
    fig.update_layout(
        title="DNA 이중 나선 · 염기서열 시각화",height=610,
        margin=dict(l=0,r=0,t=45,b=0),paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),yaxis=dict(visible=False),zaxis=dict(visible=False),
            aspectmode="data",camera=dict(eye=dict(x=1.7,y=-2.4,z=.8))),
        showlegend=False)
    return fig

def effect_chart(organ):
    vals=ORGAN_EFFECTS[organ]["지표"]
    fig=go.Figure(go.Bar(
        x=list(vals.values()),y=list(vals.keys()),orientation="h",
        marker=dict(color="#d87582")))
    fig.update_layout(
        title="장기 기능 저하의 개념적 영향 지수",
        xaxis=dict(range=[0,100],title="가상 기능 지수 (0–100)"),
        yaxis=dict(autorange="reversed"),height=300,
        margin=dict(l=10,r=10,t=45,b=35),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dceafa"))
    return fig

# --------------------------- SESSION STATE ---------------------------
defaults={
    "stage":"body","cut":False,"organ":"심장","cell":"심근세포",
    "organelle":"핵","removed":None,"sequence":"ATGCGTAC",
    "changed_idx":None,"hair_color":"#38251e","iris_color":"#5b4636",
    "hair_label":"짙은 갈색","iris_label":"갈색",
    "drug":"항히스타민제","drug_stage":"투여 전 기준 상태",
    "drug_run":False,"genotype":"AA"
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k]=v

def go(stage):
    st.session_state.stage=stage
    st.rerun()

def trait_state():
    return {
        "hair_color":st.session_state.hair_color,
        "iris_color":st.session_state.iris_color
    }

# --------------------------- HEADER / NAV ---------------------------
st.markdown(
    '<div class="hero"><div class="eyebrow">BIOVERSE · INTERACTIVE LIFE SCIENCE</div>'
    '<h1>생명의 구조를 따라가는 3D 탐험</h1>'
    '<p>인체 → 장기 → 세포 → 소기관 → 핵 → DNA · 하나의 생명체를 단계적으로 확대합니다.</p></div>',
    unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🧭 탐험 메뉴")
    for label,key in [
        ("인체와 메스 절개","body"),
        ("장기 상세·적출 실험","organ"),
        ("세포 확대","cell"),
        ("세포 소기관","organelle"),
        ("DNA·유전 형질","dna"),
        ("약물의 생리 작용","drug")
    ]:
        if st.button(label,use_container_width=True,
                     type="primary" if st.session_state.stage==key else "secondary"):
            go(key)
    st.divider()
    st.caption("3D 장면은 드래그로 회전하고 휠로 확대할 수 있습니다.")
    if st.button("처음 인체 화면으로",use_container_width=True):
        st.session_state.cut=False
        st.session_state.removed=None
        go("body")

# --------------------------- BODY / SCALPEL ---------------------------
if st.session_state.stage=="body":
    left,right=st.columns([1.55,1])
    with left:
        st.markdown("### 01 · 인체 3D 모형")
        if st.session_state.cut and HAS_3D_CLICK:
            events=plotly_events(
                body_scene(True,trait=trait_state(),click_targets=True),
                click_event=True,hover_event=False,select_event=False,
                key="body_click_large")
            if events:
                idx=events[0].get("pointNumber",events[0].get("pointIndex",-1))
                names=[n for n in ORGANS if n!=st.session_state.removed]
                if isinstance(idx,int) and 0<=idx<len(names):
                    st.session_state.organ=names[idx]
                    go("organ")
        else:
            st.plotly_chart(
                body_scene(st.session_state.cut,trait=trait_state()),
                use_container_width=True,config={"displayModeBar":True})
        st.caption("해부학적 형태를 참고해 절차적으로 만든 교육용 모형입니다. 실제 해부학 모델·진단용 모델은 아닙니다.")
    with right:
        st.markdown("### 메스 절개 탐색")
        st.write("절개 관찰 모드를 켜면 몸통 전면의 관찰창이 열리고 내부 장기가 드러납니다. 실제 수술 장면이 아닌 해부 구조 학습용 시각화입니다.")
        if not st.session_state.cut:
            if st.button("🩺 메스로 절개하여 내부 보기",use_container_width=True,type="primary"):
                st.session_state.cut=True
                st.rerun()
        else:
            st.success("절개 관찰 모드가 활성화되었습니다.")
            if st.button("절개창 닫기",use_container_width=True):
                st.session_state.cut=False
                st.rerun()
            st.markdown("**내부 장기를 직접 클릭해 확대하세요.**")
            if not HAS_3D_CLICK:
                st.warning("현재 클릭 컴포넌트가 설치되지 않았습니다. 아래 장기 버튼으로 같은 탐색을 진행할 수 있습니다.")
                for name in ORGANS:
                    if st.button(f"{name} 확대 →",key=f"body_{name}",use_container_width=True):
                        st.session_state.organ=name
                        go("organ")
        st.divider()
        st.markdown("**현재 가상 형질**")
        st.write(f"머리카락: {st.session_state.hair_label} · 홍채: {st.session_state.iris_label}")
        if st.session_state.removed:
            st.warning(f"현재 가상 적출 상태: {st.session_state.removed}")
            if st.button("장기 복원",use_container_width=True):
                st.session_state.removed=None
                st.rerun()

# --------------------------- ORGAN / REMOVAL ---------------------------
elif st.session_state.stage=="organ":
    name=st.session_state.organ
    d=ORGANS[name]
    left,right=st.columns([1.45,1])
    with left:
        st.markdown(f"### 02 · {name} 3D 확대")
        fig=go.Figure()
        add_organ(fig,name,1)
        fig.update_layout(
            title=f"{name} · 3D 장기 구조",height=620,
            margin=dict(l=0,r=0,t=45,b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            scene=dict(bgcolor="rgba(0,0,0,0)",
                xaxis=dict(visible=False),yaxis=dict(visible=False),zaxis=dict(visible=False),
                aspectmode="data",camera=dict(eye=dict(x=1.6,y=-2.3,z=1.1))),
            showlegend=False)
        st.plotly_chart(fig,use_container_width=True)
    with right:
        st.markdown(f"### {name} · {d['system']}")
        st.write(d["role"])
        st.markdown("**구조적 특징**")
        st.write(d["detail"])
        st.markdown("**대표 구성 세포**")
        st.write(" · ".join(d["cells"]))
        if st.button(f"🔬 {name}를 구성하는 세포로 확대",use_container_width=True,type="primary"):
            st.session_state.cell=d["cells"][0]
            go("cell")
        st.divider()
        st.markdown("### 메스 적출 실험")
        st.write("교육용 가상 적출을 실행하면 장기 모형에서 해당 장기가 사라지고, 그 장기의 기능 저하가 다른 신체 기능에 미치는 영향을 지표와 설명으로 확인합니다.")
        if st.session_state.removed==name:
            st.error(f"{name} 기능이 비활성화된 가상 상태입니다.")
            if st.button("이 장기 복원",use_container_width=True):
                st.session_state.removed=None
                st.rerun()
        else:
            if st.button(f"메스로 {name} 가상 적출",use_container_width=True):
                st.session_state.removed=name
                st.rerun()
    if st.session_state.removed==name:
        st.markdown("### 적출 이후의 인체 변화")
        st.plotly_chart(
            body_scene(True,selected=None,removed=name,trait=trait_state()),
            use_container_width=True,config={"displayModeBar":True})
        st.markdown("### 적출 이후의 기능 변화")
        a,b=st.columns([1,1.2])
        with a:
            for item in ORGAN_EFFECTS[name]["영향"]:
                st.markdown(f"- **{item}**")
            st.warning(d["problem"])
        with b:
            st.plotly_chart(effect_chart(name),use_container_width=True)
        st.caption("그래프의 수치는 실제 환자 예후나 임상 측정값이 아닌, 장기 기능의 중요성을 설명하기 위한 가상 지수입니다.")
    st.divider()
    if st.button("← 인체 전체로 돌아가기"):
        go("body")

# --------------------------- CELL ---------------------------
elif st.session_state.stage=="cell":
    d=ORGANS[st.session_state.organ]
    left,right=st.columns([1.4,1])
    with left:
        st.markdown(f"### 03 · {st.session_state.organ} 조직에서 세포로")
        st.plotly_chart(
            cell_scene(st.session_state.cell),
            use_container_width=True,config={"displayModeBar":True})
    with right:
        st.markdown(f"### {st.session_state.organ}의 구성 세포")
        cell=st.selectbox(
            "관찰할 세포 유형",d["cells"],
            index=d["cells"].index(st.session_state.cell),
            key="cell_picker")
        st.session_state.cell=cell
        desc,features=CELL_INFO[cell]
        st.markdown(
            f'<div class="panel"><div class="eyebrow">CELL PROFILE</div>'
            f'<h3>{cell}</h3><p>{desc}</p><b>구조적 특징</b>'
            f'<p class="small">{features}</p></div>',
            unsafe_allow_html=True)
        st.markdown("**3D 모형에서 확인할 구조**")
        st.write("세포막 · 핵 · 핵소체 · 미토콘드리아와 크리스타 · 소포체 · 골지체 · 리보솜")
        if st.button("세포 소기관 하나씩 확대하기 →",use_container_width=True,type="primary"):
            st.session_state.organelle="핵"
            go("organelle")
        if st.button("← 장기 단계로 돌아가기"):
            go("organ")
    st.caption("세포 3D는 대표적인 진핵세포의 구조를 바탕으로 한 모형입니다. 실제 세포마다 소기관의 수·크기·배치는 다릅니다.")

# --------------------------- ORGANELLE ---------------------------
elif st.session_state.stage=="organelle":
    left,right=st.columns([1.4,1])
    with left:
        st.markdown("### 04 · 세포 소기관 확대")
        st.plotly_chart(
            organelle_scene(st.session_state.organelle),
            use_container_width=True,config={"displayModeBar":True})
    with right:
        names=list(ORGANELLES)
        org=st.selectbox(
            "확대할 소기관",names,
            index=names.index(st.session_state.organelle),
            key="organelle_picker")
        st.session_state.organelle=org
        desc,features=ORGANELLES[org]
        st.markdown(
            f'<div class="panel"><div class="eyebrow">ORGANELLE PROFILE</div>'
            f'<h3>{org}</h3><p>{desc}</p><b>모형의 주요 구조</b>'
            f'<p class="small">{features}</p></div>',
            unsafe_allow_html=True)
        if org=="핵":
            if st.button("핵 속 DNA 이중나선으로 확대 →",use_container_width=True,type="primary"):
                go("dna")
        else:
            st.info("선택한 소기관의 구조와 기능을 확인했습니다. DNA 탐구는 핵을 통해 이어집니다.")
            if st.button("핵으로 이동 →",use_container_width=True):
                st.session_state.organelle="핵"
                st.rerun()
        if st.button("← 세포 전체로 돌아가기"):
            go("cell")

# --------------------------- DNA / TRAITS ---------------------------
elif st.session_state.stage=="dna":
    left,right=st.columns([1.35,1])
    with left:
        st.markdown("### 05 · 핵 내부의 DNA 이중나선")
        st.plotly_chart(
            dna_scene(st.session_state.sequence,st.session_state.changed_idx),
            use_container_width=True,config={"displayModeBar":True})
        st.caption("A–T, G–C 상보적 염기쌍을 단순화한 3D 표현입니다.")
    with right:
        st.markdown("### 직접 입력하지 않고 바꾸는 염기서열")
        presets={
            "기본 예시":"ATGCGTAC",
            "염기 하나가 바뀐 예시":"ATGAGTAC",
            "GC가 많은 예시":"GCGCCGTA",
            "AT가 많은 예시":"ATATATTA"
        }
        preset=st.selectbox("예시 서열 불러오기",list(presets))
        if st.button("선택한 예시 적용",use_container_width=True):
            st.session_state.sequence=presets[preset]
            st.session_state.changed_idx=None
            base_color={
                "A":("갈색","#5b4636"),
                "T":("파란색","#4d8fbd"),
                "G":("초록색","#5d956b"),
                "C":("회색","#8799a5")
            }
            st.session_state.iris_label,st.session_state.iris_color=base_color[st.session_state.sequence[0]]
            st.rerun()
        seq=st.session_state.sequence
        st.code("5′ — "+"  ".join(seq)+" — 3′",language="text")
        idx=st.select_slider(
            "바꿀 염기 위치",options=list(range(1,len(seq)+1)),
            value=1,format_func=lambda i:f"{i}번 ({seq[i-1]})")
        base=st.radio(
            "새 염기 선택",[b for b in "ATGC" if b!=seq[idx-1]],
            horizontal=True)
        if st.button("선택한 염기 바꾸기",use_container_width=True,type="primary"):
            chars=list(seq)
            chars[idx-1]=base
            st.session_state.sequence="".join(chars)
            st.session_state.changed_idx=idx-1
            if idx==1:
                base_color={
                    "A":("갈색","#5b4636"),
                    "T":("파란색","#4d8fbd"),
                    "G":("초록색","#5d956b"),
                    "C":("회색","#8799a5")
                }
                st.session_state.iris_label,st.session_state.iris_color=base_color[base]
            st.rerun()
        counts={b:seq.count(b) for b in "ATGC"}
        st.markdown("**염기 구성 그래프**")
        chart=px.bar(
            x=list(counts),y=list(counts.values()),
            labels={"x":"염기","y":"개수"},
            color=list(counts),
            color_discrete_map={
                "A":"#56c9a5","T":"#e9a85d",
                "G":"#789ce5","C":"#d78ac8"})
        chart.update_layout(
            height=230,margin=dict(l=5,r=5,t=5,b=5),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#dceafa",showlegend=False)
        st.plotly_chart(chart,use_container_width=True)
    st.divider()
    st.markdown("### 유전자와 가상 형질 연결 실험")
    st.info("아래 눈동자·머리카락 색은 유전 원리를 설명하기 위한 가상 단일 유전자 모형입니다. 실제 사람의 눈·머리카락 색은 여러 유전자와 발달·환경 요인이 관여하므로 이 앱의 서열과 실제 형질을 일대일로 연결할 수 없습니다.")
    c1,c2,c3=st.columns(3)
    with c1:
        hair=st.selectbox(
            "가상 머리카락 색",
            ["짙은 갈색","검정","금발","붉은 갈색"],
            index=["짙은 갈색","검정","금발","붉은 갈색"].index(st.session_state.hair_label))
    with c2:
        iris=st.selectbox(
            "가상 홍채 색",
            ["갈색","파란색","초록색","회색"],
            index=["갈색","파란색","초록색","회색"].index(st.session_state.iris_label))
    with c3:
        genotype=st.selectbox(
            "가상 대립유전자 조합",["AA","Aa","aa"],
            index=["AA","Aa","aa"].index(st.session_state.genotype),
            help="단일 유전자 우성·열성 원리를 설명하는 가상 예시입니다.")
    if st.button("가상 형질을 인체 3D 모형에 적용",use_container_width=True):
        hairmap={
            "짙은 갈색":"#38251e","검정":"#171719",
            "금발":"#d5b16a","붉은 갈색":"#9c513b"}
        st.session_state.hair_label=hair
        st.session_state.hair_color=hairmap[hair]
        st.session_state.genotype=genotype
        if genotype in ("AA","Aa"):
            st.session_state.iris_label="갈색"
            st.session_state.iris_color="#5b4636"
        else:
            st.session_state.iris_label="파란색"
            st.session_state.iris_color="#4d8fbd"
        st.success("가상 형질이 인체 3D 모형에 적용되었습니다.")
    st.markdown("**가상 유전도: Aa × Aa**")
    st.table({
        "부모 생식세포":["A","a"],
        "A":["AA","Aa"],
        "a":["Aa","aa"]
    })
    st.caption("이 표는 멘델의 단일 유전자 분리 원리를 설명하는 예시입니다. 실제 눈동자·머리카락 색의 유전도를 뜻하지 않습니다.")
    inheritance=px.bar(
        x=["우성 표현형","열성 표현형"],y=[75,25],
        labels={"x":"가상 표현형","y":"자손 비율(%)"},
        text=["75%","25%"],
        color=["우성 표현형","열성 표현형"],
        color_discrete_map={"우성 표현형":"#6dcbb8","열성 표현형":"#8d9fda"})
    inheritance.update_layout(
        height=230,margin=dict(l=5,r=5,t=5,b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#dceafa",showlegend=False,yaxis=dict(range=[0,100]))
    st.plotly_chart(inheritance,use_container_width=True)
    st.caption("첫 염기는 앱 내부의 가상 색소 표지에만 연결됩니다: A=갈색, T=파란색, G=초록색, C=회색. 실제 유전자 변이의 효과를 뜻하지 않습니다.")
    st.markdown(
        f"현재 가상 유전자형: **{st.session_state.genotype}** · "
        f"단순 모형의 표현형: **{'갈색 홍채' if st.session_state.genotype in ('AA','Aa') else '파란 홍채'}**")
    st.markdown(f"**현재 인체 모형:** 머리카락 {st.session_state.hair_label} · 홍채 {st.session_state.iris_label}")
    if st.button("변경된 형질을 인체 3D에서 확인 →",use_container_width=True):
        go("body")

# --------------------------- PHARMACOLOGY ---------------------------
elif st.session_state.stage=="drug":
    st.markdown("### 약물의 생리적 작용 · 의료 교육 모드")
    st.warning("이 기능은 약리학 학습용입니다. 실제 투여 방법·용량·주사 위치를 안내하지 않으며, 약물의 취한 느낌이나 환각을 오락적으로 재현하지 않습니다. 특히 펜타닐 등 오피오이드는 호흡 억제와 의식 저하로 생명을 위협할 수 있어 엄격한 의료적 감시가 필요합니다.")
    left,right=st.columns([1,1.25])
    with left:
        drug=st.selectbox(
            "학습할 치료 약물·약물 계열",list(DRUGS),
            index=list(DRUGS).index(st.session_state.drug))
        st.session_state.drug=drug
        purpose,mechanism,caution,metrics=DRUGS[drug]
        st.markdown(
            f'<div class="panel"><div class="eyebrow">PHARMACOLOGY PROFILE</div>'
            f'<h3>{drug}</h3><p><b>의학적 목적:</b> {purpose}</p>'
            f'<p>{mechanism}</p><p class="small"><b>주의:</b> {caution}</p></div>',
            unsafe_allow_html=True)
        st.markdown("**약물 작용의 개념적 단계**")
        stage=st.select_slider(
            "시뮬레이션 단계",
            options=["투여 전 기준 상태","혈액·체액 내 이동 개념","표적 수용체·조직 작용","생리적 반응 관찰"],
            value=st.session_state.drug_stage)
        st.session_state.drug_stage=stage
        if st.button("의료 모니터 시뮬레이션 실행",use_container_width=True,type="primary"):
            st.session_state.drug_run=True
    with right:
        if st.session_state.drug_run:
            st.markdown("#### 환자 관찰 패널 · 개념적 1인칭 시야")
            alert=metrics.get("각성",100)
            resp=metrics.get("호흡 기능",100)
            if stage=="투여 전 기준 상태":
                alert=100
                resp=100
            elif stage=="혈액·체액 내 이동 개념":
                alert=min(100,alert+18)
                resp=min(100,resp+8)
            elif stage=="표적 수용체·조직 작용":
                alert=metrics.get("각성",100)
                resp=metrics.get("호흡 기능",100)
            fig=go.Figure()
            theta=np.linspace(0,2*np.pi,120)
            radius=.92
            fig.add_trace(go.Scatter(
                x=radius*np.cos(theta),y=radius*np.sin(theta),
                mode="lines",line=dict(color="#8ac6d9",width=3),
                showlegend=False,hoverinfo="skip"))
            clarity=max(.22,min(1.0,alert/100))
            for r in [.22,.43,.64]:
                fig.add_shape(
                    type="circle",x0=-r,y0=-r,x1=r,y1=r,
                    line=dict(color=f"rgba(130,190,210,{.18+clarity*.25})",width=2))
            fig.add_trace(go.Scatter(
                x=[0],y=[0],mode="markers",
                marker=dict(size=12,color="#f0d79b",opacity=clarity),
                showlegend=False))
            fig.update_layout(
                height=360,margin=dict(l=5,r=5,t=5,b=5),
                paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="#0a1826",
                xaxis=dict(visible=False,range=[-1.05,1.05],scaleanchor="y"),
                yaxis=dict(visible=False,range=[-1.05,1.05]))
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
            m1,m2=st.columns(2)
            m1.metric("각성·주의 지표",f"{alert}/100")
            m2.metric("호흡 기능 지표",f"{resp}/100")
            st.caption("시야 패널은 주의·각성 상태를 상징하는 교육용 도식이며 실제 환자의 시야나 약물 경험을 재현하지 않습니다.")
            bars=go.Figure(go.Bar(
                x=[alert,resp],y=["각성·주의","호흡 기능"],
                orientation="h",marker_color=["#76b8d2","#69cdb8"]))
            bars.update_layout(
                height=190,xaxis=dict(range=[0,100],title="가상 지표"),
                yaxis=dict(autorange="reversed"),
                margin=dict(l=5,r=5,t=5,b=5),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",font_color="#dceafa")
            st.plotly_chart(bars,use_container_width=True)
            if drug.startswith("오피오이드"):
                st.error("오피오이드 계열은 호흡 억제 위험이 핵심적인 안전 문제입니다. 색채 효과나 쾌감이 아니라 호흡·의식 상태의 면밀한 관찰이 중요한 이유를 학습하세요.")
        else:
            st.plotly_chart(
                body_scene(True,trait=trait_state()),
                use_container_width=True)
            st.info("왼쪽에서 약물 계열과 개념적 단계를 선택한 뒤 의료 모니터 시뮬레이션을 실행하세요.")
    st.markdown("#### 약물 작용을 이해하는 핵심 개념")
    cc=st.columns(4)
    concepts=[
        ("수용체","세포가 특정 신호를 인식하는 단백질"),
        ("약동학","약물이 체내에서 흡수·분포·대사·배설되는 과정"),
        ("약력학","약물이 표적에 작용해 생리 반응을 일으키는 과정"),
        ("항상성","내부 환경을 일정 범위로 유지하는 조절 작용")
    ]
    for col,(title,desc) in zip(cc,concepts):
        with col:
            st.markdown(
                f'<div class="panel"><div class="eyebrow">{title}</div>'
                f'<p>{desc}</p></div>',
                unsafe_allow_html=True)

st.divider()
st.markdown(
    "<div style='text-align:center;color:#829bb1;font-size:.8rem'>"
    "BIOVERSE 3D · 교육 및 탐구 목적 · 실제 진단·치료·유전형질 예측 도구가 아닙니다."
    "</div>",
    unsafe_allow_html=True)
