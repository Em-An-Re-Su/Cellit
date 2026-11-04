import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import math
import random

# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="BioSphere 3D | 생명과학 탐구실",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 15% 10%, #142b42 0%, transparent 35%),
        linear-gradient(135deg, #07111e 0%, #0b1725 55%, #101d2d 100%);
    color: #e8f0fa;
}

section[data-testid="stSidebar"] {
    background: #0a1522;
    border-right: 1px solid #26384b;
}

h1, h2, h3 {
    color: #f0f6ff;
}

p, li, label {
    color: #c6d4e3;
}

div[data-testid="stMetric"] {
    background: #142438;
    border: 1px solid #2b4057;
    padding: 15px;
    border-radius: 13px;
}

div.stButton > button {
    border-radius: 10px;
    border: 1px solid #36516c;
    background: #172b40;
    color: #e8f3ff;
    font-weight: 600;
    min-height: 42px;
}

div.stButton > button:hover {
    border-color: #54c9df;
    color: white;
    background: #203c55;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

.bio-card {
    background: linear-gradient(145deg, #14263a, #101e2e);
    border: 1px solid #2a4057;
    padding: 18px;
    border-radius: 15px;
    margin: 8px 0;
}

.small-label {
    color: #70cde0;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 1px;
}

.stage {
    background: #13283c;
    border: 1px solid #34516a;
    padding: 10px 15px;
    border-radius: 10px;
    color: #bfeaff;
    display: inline-block;
    margin-bottom: 12px;
}

hr {
    border-color: #263b50;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# 세션 상태
# =========================================================

DEFAULTS = {
    "stage": "body",
    "selected_organ": "심장",
    "selected_cell": "심근세포",
    "cutaway": True,
    "dna_sequence": "ATGCGTACGTTAGCGATCGT",
    "drug": "카페인",
    "drug_effect": False,
    "show_drug_view": False,
    "removed_organs": [],
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# 데이터
# =========================================================

ORGAN_DATA = {
    "뇌": {
        "name": "뇌",
        "type": "신경계",
        "color": "#e9a6c9",
        "function": "감각 정보 처리, 운동 조절, 기억, 학습, 감정 및 항상성 조절",
        "cells": ["신경세포", "성상세포", "희소돌기아교세포"],
        "cell_main": "신경세포",
        "problem": "뇌 기능이 손상되면 운동, 감각, 기억, 언어 등 다양한 기능에 문제가 생길 수 있습니다.",
        "detail": "대뇌, 소뇌, 뇌줄기 등으로 구분되며 각 영역은 서로 협력하여 신체 기능을 조절합니다."
    },
    "심장": {
        "name": "심장",
        "type": "순환계",
        "color": "#e85d75",
        "function": "수축과 이완을 반복하여 혈액을 온몸으로 순환시킵니다.",
        "cells": ["심근세포", "내피세포", "섬유아세포"],
        "cell_main": "심근세포",
        "problem": "심장의 펌프 기능이 저하되면 신체 조직에 충분한 산소와 영양분이 공급되지 않을 수 있습니다.",
        "detail": "심장은 네 개의 방으로 구성되며, 판막은 혈액이 역류하지 않도록 돕습니다."
    },
    "폐": {
        "name": "폐",
        "type": "호흡계",
        "color": "#7dc6e8",
        "function": "산소를 혈액으로 전달하고 이산화탄소를 몸 밖으로 내보냅니다.",
        "cells": ["폐포세포", "섬모상피세포", "대식세포"],
        "cell_main": "폐포세포",
        "problem": "가스 교환 기능이 저하되면 혈액의 산소 공급과 이산화탄소 배출에 문제가 생길 수 있습니다.",
        "detail": "폐포는 작은 공기주머니로, 표면적이 넓어 효율적인 기체 교환이 가능합니다."
    },
    "간": {
        "name": "간",
        "type": "소화·대사계",
        "color": "#c68b54",
        "function": "영양소 대사, 해독, 담즙 생성, 혈당 조절 및 여러 단백질 합성",
        "cells": ["간세포", "쿠퍼세포", "담관세포"],
        "cell_main": "간세포",
        "problem": "간 기능이 저하되면 대사와 해독, 혈액 응고에 관련된 기능에 문제가 생길 수 있습니다.",
        "detail": "간은 다양한 대사 반응이 일어나는 기관이며 재생 능력이 비교적 뛰어납니다."
    },
    "위": {
        "name": "위",
        "type": "소화계",
        "color": "#e7a36f",
        "function": "음식물을 저장하고 위액과 섞어 소화 과정을 진행합니다.",
        "cells": ["위벽세포", "주세포", "점액세포"],
        "cell_main": "위벽세포",
        "problem": "위의 점막 방어 기능이 약해지거나 소화 기능에 문제가 생길 수 있습니다.",
        "detail": "위벽에서는 위산과 소화 효소, 점액 등이 분비됩니다."
    },
    "신장": {
        "name": "신장",
        "type": "비뇨계",
        "color": "#a77ed1",
        "function": "혈액을 여과하고 노폐물과 수분, 전해질 균형을 조절합니다.",
        "cells": ["족세포", "세뇨관 상피세포", "사구체 내피세포"],
        "cell_main": "세뇨관 상피세포",
        "problem": "여과 기능이 저하되면 체내 노폐물과 수분 및 전해질 균형에 문제가 생길 수 있습니다.",
        "detail": "신장의 기능적 기본 단위는 네프론이며 사구체와 세뇨관으로 이루어집니다."
    },
    "소장": {
        "name": "소장",
        "type": "소화계",
        "color": "#e5c26b",
        "function": "소화된 영양소 대부분을 흡수합니다.",
        "cells": ["흡수상피세포", "배상세포", "장내분비세포"],
        "cell_main": "흡수상피세포",
        "problem": "영양소 흡수가 원활하지 않으면 영양 상태와 에너지 공급에 영향을 줄 수 있습니다.",
        "detail": "융모와 미세융모는 흡수 표면적을 넓혀 영양소 흡수를 돕습니다."
    },
    "췌장": {
        "name": "췌장",
        "type": "소화·내분비계",
        "color": "#e3b17d",
        "function": "소화 효소를 분비하고 인슐린과 글루카곤으로 혈당을 조절합니다.",
        "cells": ["췌장 선방세포", "베타세포", "알파세포"],
        "cell_main": "베타세포",
        "problem": "인슐린 분비나 작용에 문제가 생기면 혈당 조절에 어려움이 생길 수 있습니다.",
        "detail": "췌장의 랑게르한스섬에는 혈당 조절에 관여하는 여러 내분비세포가 있습니다."
    }
}


# =========================================================
# 3D 모델 생성 함수
# =========================================================

def ellipsoid_mesh(center, radii, color, name="", opacity=1.0,
                   resolution=24, showlegend=False):
    """타원체 형태의 3D 표면 생성"""
    cx, cy, cz = center
    rx, ry, rz = radii

    u = np.linspace(0, 2 * np.pi, resolution)
    v = np.linspace(0, np.pi, resolution)

    x = cx + rx * np.outer(np.cos(u), np.sin(v))
    y = cy + ry * np.outer(np.sin(u), np.sin(v))
    z = cz + rz * np.outer(np.ones_like(u), np.cos(v))

    return go.Surface(
        x=x,
        y=y,
        z=z,
        colorscale=[[0, color], [1, color]],
        showscale=False,
        opacity=opacity,
        name=name,
        hovertemplate=f"{name}<extra></extra>"
    )



def tube_mesh(start, end, radius, color, name="", resolution=18):
    """두 지점 사이를 잇는 원통형 구조"""
    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)

    direction = end - start
    length = np.linalg.norm(direction)

    if length == 0:
        return []

    direction = direction / length

    helper = np.array([0, 0, 1], dtype=float)
    if abs(np.dot(direction, helper)) > 0.9:
        helper = np.array([0, 1, 0], dtype=float)

    u = np.cross(direction, helper)
    u = u / np.linalg.norm(u)
    v = np.cross(direction, u)

    theta = np.linspace(0, 2 * np.pi, resolution)
    t = np.linspace(0, length, 12)

    X, Y, Z = [], [], []

    for ti in t:
        ring = start + direction * ti
        points = [
            ring + radius * (u * np.cos(a) + v * np.sin(a))
            for a in theta
        ]
        X.append([p[0] for p in points])
        Y.append([p[1] for p in points])
        Z.append([p[2] for p in points])

    return [go.Surface(
        x=np.array(X), y=np.array(Y), z=np.array(Z),
        colorscale=[[0, color], [1, color]],
        showscale=False,
        opacity=0.95,
        name=name,
        hovertemplate=f"{name}<extra></extra>"
    )]


def add_body_mesh(fig, cutaway=True):
    """인체의 외형: 머리, 목, 몸통, 팔, 다리"""

    # 머리
    fig.add_trace(ellipsoid_mesh(
        (0, 0, 7.7), (0.48, 0.42, 0.62),
        "#d6a58d", "머리", 1
    ))

    # 목
    fig.add_trace(ellipsoid_mesh(
        (0, 0, 6.95), (0.22, 0.22, 0.32),
        "#c9937d", "목", 1
    ))

    # 몸통
    if cutaway:
        # 앞쪽을 일부 개방한 몸통 표면
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi, 40)

        X = 0.92 * np.outer(np.cos(u), np.sin(v))
        Y = 0.48 * np.outer(np.sin(u), np.sin(v))
        Z = 5.45 + 1.35 * np.outer(np.ones_like(u), np.cos(v))

        # 앞면(y < 0)을 제거해 내부 장기가 보이게 함
        Y = np.where(Y < -0.03, np.nan, Y)

        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale=[[0, "#b77f6b"], [1, "#d5a28c"]],
            showscale=False,
            opacity=0.24,
            name="절개된 몸통",
            hoverinfo="skip"
        ))
    else:
        fig.add_trace(ellipsoid_mesh(
            (0, 0, 5.45), (0.92, 0.48, 1.35),
            "#c9937d", "몸통", 0.85
        ))

    # 어깨
    for x in [-0.9, 0.9]:
        fig.add_trace(ellipsoid_mesh(
            (x, 0, 6.35), (0.35, 0.32, 0.38),
            "#c9937d", "어깨", 0.95
        ))

    # 팔
    for side in [-1, 1]:
        x = side
        fig.add_trace(ellipsoid_mesh(
            (side * 1.08, 0, 5.65), (0.22, 0.25, 0.82),
            "#c9937d", "위팔", 0.95
        ))
        fig.add_trace(ellipsoid_mesh(
            (side * 1.18, 0, 4.55), (0.17, 0.19, 0.72),
            "#c9937d", "아래팔", 0.95
        ))
        fig.add_trace(ellipsoid_mesh(
            (side * 1.18, -0.02, 3.78), (0.18, 0.12, 0.28),
            "#d6a58d", "손", 0.95
        ))

    # 골반
    fig.add_trace(ellipsoid_mesh(
        (0, 0, 3.95), (0.72, 0.42, 0.48),
        "#c9937d", "골반", 0.8
    ))

    # 다리
    for side in [-1, 1]:
        fig.add_trace(ellipsoid_mesh(
            (side * 0.38, 0, 2.65), (0.29, 0.32, 1.05),
            "#c9937d", "허벅지", 0.95
        ))
        fig.add_trace(ellipsoid_mesh(
            (side * 0.38, 0, 1.35), (0.22, 0.24, 0.95),
            "#c9937d", "종아리", 0.95
        ))
        fig.add_trace(ellipsoid_mesh(
            (side * 0.38, -0.10, 0.35), (0.25, 0.38, 0.25),
            "#d6a58d", "발", 0.95
        ))


ORGAN_POSITIONS = {
    "뇌": (0, -0.08, 7.75),
    "심장": (0.0, -0.32, 5.65),
    "폐": (0, -0.22, 5.65),
    "간": (-0.38, -0.30, 4.85),
    "위": (0.35, -0.30, 4.85),
    "신장": (0.55, 0.10, 4.55),
    "소장": (0, -0.24, 4.05),
    "췌장": (0.1, -0.28, 4.72)
}


def add_organ(fig, organ, opacity=1.0, highlight=False):
    """장기별 서로 다른 형태의 3D 표현"""
    pos = ORGAN_POSITIONS[organ]
    color = ORGAN_DATA[organ]["color"]
    edge = "#ffffff" if highlight else color

    if organ == "뇌":
        fig.add_trace(ellipsoid_mesh(pos, (0.39, 0.34, 0.42),
                                     color, "뇌", opacity, 30))
        # 뇌 표면 주름을 단순화한 곡선
        for i in range(5):
            x = np.linspace(-0.25, 0.25, 30)
            y = np.full_like(x, pos[1] - 0.32)
            z = pos[2] + 0.12 * np.sin(x * 18 + i) + (i - 2) * 0.10
            fig.add_trace(go.Scatter3d(
                x=x, y=y, z=z, mode="lines",
                line=dict(color="#f6c4dc", width=3),
                showlegend=False, hoverinfo="skip"
            ))

    elif organ == "심장":
        # 심장 형태를 여러 연결된 근육 덩어리로 구성
        fig.add_trace(ellipsoid_mesh(
            (pos[0] - 0.12, pos[1], pos[2] + 0.10),
            (0.22, 0.22, 0.34), color, "심장", opacity, 28
        ))
        fig.add_trace(ellipsoid_mesh(
            (pos[0] + 0.13, pos[1], pos[2] + 0.12),
            (0.22, 0.22, 0.30), color, "심장", opacity, 28
        ))
        fig.add_trace(ellipsoid_mesh(
            (pos[0], pos[1], pos[2] - 0.17),
            (0.24, 0.20, 0.28), "#c9445d", "심첨부", opacity, 28
        ))
        fig.add_traces(tube_mesh(
            (pos[0] - 0.10, pos[1], pos[2] + 0.30),
            (pos[0] - 0.10, pos[1], pos[2] + 0.62),
            0.07, "#b64c58", "대동맥"
        ))

    elif organ == "폐":
        for side in [-1, 1]:
            fig.add_trace(ellipsoid_mesh(
                (side * 0.31, pos[1], pos[2]),
                (0.28, 0.22, 0.55),
                color, "폐", opacity, 28
            ))
        fig.add_traces(tube_mesh(
            (0, pos[1], pos[2] + 0.52),
            (0, pos[1], pos[2] + 0.05),
            0.07, "#7cc9e7", "기관"
        ))

    elif organ == "간":
        fig.add_trace(ellipsoid_mesh(
            pos, (0.58, 0.30, 0.28), color, "간", opacity, 32
        ))
        fig.add_trace(ellipsoid_mesh(
            (pos[0] + 0.40, pos[1] - 0.02, pos[2] - 0.03),
            (0.20, 0.25, 0.23), "#a66c42", "간의 오른쪽 부분", opacity
        ))

    elif organ == "위":
        fig.add_trace(ellipsoid_mesh(
            pos, (0.27, 0.25, 0.43), color, "위", opacity, 28
        ))
        fig.add_trace(ellipsoid_mesh(
            (pos[0] + 0.10, pos[1], pos[2] - 0.20),
            (0.30, 0.22, 0.18), color, "위 아랫부분", opacity
        ))

    elif organ == "신장":
        for side in [-1, 1]:
            fig.add_trace(ellipsoid_mesh(
                (side * 0.53, pos[1], pos[2]),
                (0.18, 0.20, 0.34), color, "신장", opacity, 28
            ))

    elif organ == "소장":
        # 소장 굴곡을 여러 개의 관 형태로 표현
        for i in range(5):
            z = pos[2] + (i - 2) * 0.10
            x = np.linspace(-0.38, 0.38, 40)
            y = pos[1] + 0.10 * np.sin(x * 15 + i)
            zz = z + 0.08 * np.cos(x * 15 + i)
            fig.add_trace(go.Scatter3d(
                x=x, y=y, z=zz,
                mode="lines",
                line=dict(color=color, width=8),
                showlegend=False,
                hovertemplate="소장<extra></extra>"
            ))

    elif organ == "췌장":
        x = np.linspace(-0.40, 0.40, 35)
        y = np.full_like(x, pos[1])
        z = pos[2] + 0.06 * np.sin(x * 8)
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z, mode="lines",
            line=dict(color=color, width=13),
            name="췌장"
        ))


def scene_layout(fig, title="", camera=None, height=650):
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color="#e9f5ff")),
        height=height,
        margin=dict(l=0, r=0, t=45, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False, range=[-1.8, 1.8]),
            yaxis=dict(visible=False, range=[-1.2, 1.2]),
            zaxis=dict(visible=False, range=[0, 8.7]),
            aspectmode="manual",
            aspectratio=dict(x=0.65, y=0.48, z=1.5),
            camera=camera or dict(eye=dict(x=1.8, y=-2.8, z=1.0))
        ),
        showlegend=False
    )
    return fig


def body_scene(cutaway=True, selected=None):
    fig = go.Figure()
    add_body_mesh(fig, cutaway)

    for organ in ORGAN_DATA:
        if organ in st.session_state.removed_organs:
            continue
        add_organ(
            fig,
            organ,
            opacity=1.0 if selected == organ else 0.90,
            highlight=(selected == organ)
        )

    return scene_layout(fig, "HUMAN ANATOMY · 3D MODEL")


# =========================================================
# 세포 3D 모델
# =========================================================

CELL_DATA = {
    "심근세포": {
        "desc": "심근세포는 심장 근육을 구성하며, 규칙적인 수축을 통해 혈액을 이동시킵니다.",
        "features": ["가로무늬 구조", "풍부한 미토콘드리아", "사이원반을 통한 세포 연결"],
        "color": "#e85d75"
    },
    "신경세포": {
        "desc": "신경세포는 전기적·화학적 신호를 전달하여 정보를 처리합니다.",
        "features": ["세포체", "수상돌기", "축삭"],
        "color": "#e9c66d"
    },
    "폐포세포": {
        "desc": "폐포세포는 폐포의 벽을 구성하며 기체 교환에 중요한 역할을 합니다.",
        "features": ["얇은 세포층", "넓은 교환 표면", "폐포 구조 유지"],
        "color": "#7dc6e8"
    },
    "간세포": {
        "desc": "간세포는 대사, 저장, 단백질 합성, 해독 등 다양한 기능을 담당합니다.",
        "features": ["풍부한 소포체", "글리코겐 저장", "다양한 효소"],
        "color": "#c68b54"
    },
    "위벽세포": {
        "desc": "위벽세포는 위산과 내인자를 분비하는 세포입니다.",
        "features": ["미토콘드리아가 풍부함", "위산 분비", "위 점막의 일부"],
        "color": "#e7a36f"
    },
    "세뇨관 상피세포": {
        "desc": "세뇨관 상피세포는 여과된 물질 중 필요한 물질을 재흡수하고 분비합니다.",
        "features": ["막 수송 단백질", "미토콘드리아", "재흡수 기능"],
        "color": "#a77ed1"
    },
    "흡수상피세포": {
        "desc": "소장 흡수상피세포는 영양소를 흡수하며 미세융모를 가지고 있습니다.",
        "features": ["미세융모", "세포막 수송", "영양소 흡수"],
        "color": "#e5c26b"
    },
    "베타세포": {
        "desc": "췌장 베타세포는 혈당이 높아졌을 때 인슐린을 분비합니다.",
        "features": ["인슐린 합성", "분비 과립", "혈당 감지"],
        "color": "#e3b17d"
    },
    "성상세포": {
        "desc": "성상세포는 신경세포 주변 환경을 유지하고 신경계 기능을 지원합니다.",
        "features": ["별 모양 돌기", "신경세포 지원", "혈액뇌장벽 유지에 관여"],
        "color": "#d9b4e6"
    },
    "희소돌기아교세포": {
        "desc": "희소돌기아교세포는 중추신경계 축삭을 둘러싸는 수초 형성에 관여합니다.",
        "features": ["수초 형성", "축삭 보호", "신경 신호 전달 지원"],
        "color": "#b9a2e8"
    },
    "내피세포": {
        "desc": "내피세포는 혈관 안쪽 표면을 덮으며 물질 교환과 혈관 기능에 관여합니다.",
        "features": ["혈관 내벽", "물질 이동 조절", "혈관 기능 유지"],
        "color": "#86c6c8"
    },
    "섬모상피세포": {
        "desc": "섬모상피세포는 섬모의 움직임으로 기도 내 점액과 입자를 이동시키는 데 기여합니다.",
        "features": ["섬모", "점액 이동", "기도 방어"],
        "color": "#7dc6e8"
    },
    "대식세포": {
        "desc": "대식세포는 이물질과 세포 잔해 등을 포식하는 면역세포입니다.",
        "features": ["포식 작용", "면역 신호 전달", "항원 제시"],
        "color": "#9fc98c"
    },
    "쿠퍼세포": {
        "desc": "쿠퍼세포는 간의 굴모세혈관에 존재하는 대식세포입니다.",
        "features": ["포식 작용", "면역 감시", "간 내 이물질 제거"],
        "color": "#c68b54"
    },
    "담관세포": {
        "desc": "담관세포는 담관을 구성하며 담즙의 이동과 조성 조절에 관여합니다.",
        "features": ["담관 구성", "담즙 이동", "상피세포"],
        "color": "#d2a36b"
    },
    "족세포": {
        "desc": "족세포는 신장 사구체의 여과 장벽을 구성하는 중요한 세포입니다.",
        "features": ["발돌기", "여과 틈새", "사구체 여과"],
        "color": "#a77ed1"
    },
    "사구체 내피세포": {
        "desc": "사구체 내피세포는 혈액이 여과되는 모세혈관의 안쪽을 구성합니다.",
        "features": ["모세혈관 내벽", "여과 기능", "구멍이 있는 구조"],
        "color": "#a77ed1"
    },
    "주세포": {
        "desc": "주세포는 위에서 펩시노겐을 분비하며 소화 과정에 관여합니다.",
        "features": ["펩시노겐 분비", "단백질 소화 지원", "분비 과립"],
        "color": "#e7a36f"
    },
    "점액세포": {
        "desc": "점액세포는 점액을 분비하여 위 점막을 보호합니다.",
        "features": ["점액 분비", "점막 보호", "상피 표면 유지"],
        "color": "#e7a36f"
    },
    "췌장 선방세포": {
        "desc": "췌장 선방세포는 소화 효소를 포함하는 분비물을 만듭니다.",
        "features": ["소화 효소 합성", "분비 과립", "단백질 합성"],
        "color": "#e3b17d"
    },
    "알파세포": {
        "desc": "췌장 알파세포는 혈당이 낮아졌을 때 글루카곤을 분비합니다.",
        "features": ["글루카곤 합성", "분비 과립", "혈당 조절"],
        "color": "#e3b17d"
    },
}


def cell_scene(cell_name):
    info = CELL_DATA.get(cell_name, CELL_DATA["심근세포"])
    color = info["color"]

    fig = go.Figure()

    # 세포막
    fig.add_trace(ellipsoid_mesh(
        (0, 0, 0), (2.1, 1.6, 1.4),
        color, "세포막", 0.24, 36
    ))

    # 핵
    fig.add_trace(ellipsoid_mesh(
        (-0.2, 0, 0.1), (0.66, 0.58, 0.65),
        "#8f79dc", "세포핵", 0.95, 30
    ))

    # 핵소체
    fig.add_trace(ellipsoid_mesh(
        (-0.12, -0.35, 0.25), (0.20, 0.18, 0.20),
        "#d7b8ff", "핵소체", 1
    ))

    # 미토콘드리아
    for x, y, z, angle in [
        (0.85, 0.45, 0.25, 0),
        (-0.95, -0.45, -0.30, 1),
        (0.85, -0.55, -0.45, 2),
        (-0.95, 0.55, 0.55, 1)
    ]:
        fig.add_trace(ellipsoid_mesh(
            (x, y, z), (0.42, 0.20, 0.18),
            "#e9a85d", "미토콘드리아", 0.95, 20
        ))

    # 소포체 - 굴곡진 선
    for i in range(5):
        t = np.linspace(-1, 1, 60)
        x = -0.2 + 0.75 * t
        y = 0.58 + i * 0.10 + 0.12 * np.sin(t * 7 + i)
        z = 0.1 + 0.12 * np.cos(t * 8 + i)

        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode="lines",
            line=dict(color="#6ec6bd", width=5),
            showlegend=False,
            hovertemplate="소포체<extra></extra>"
        ))

    # 골지체
    for i in range(4):
        t = np.linspace(-0.4, 0.4, 35)
        x = 0.1 + t
        y = -0.9 - i * 0.09
        z = -0.2 + 0.12 * np.sin(t * 5)
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode="lines",
            line=dict(color="#e5bd6a", width=6),
            showlegend=False,
            hovertemplate="골지체<extra></extra>"
        ))

    # 리보솜
    rng = np.random.default_rng(4)
    for _ in range(35):
        x, y, z = rng.uniform(-1.5, 1.5), rng.uniform(-1.1, 1.1), rng.uniform(-1, 1)
        fig.add_trace(go.Scatter3d(
            x=[x], y=[y], z=[z],
            mode="markers",
            marker=dict(size=2.5, color="#f0d78b"),
            showlegend=False,
            hovertemplate="리보솜<extra></extra>"
        ))

    fig.update_layout(
        title=f"{cell_name} · 3D CELL MODEL",
        height=620,
        margin=dict(l=0, r=0, t=45, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False, range=[-2.5, 2.5]),
            yaxis=dict(visible=False, range=[-2, 2]),
            zaxis=dict(visible=False, range=[-1.8, 1.8]),
            aspectmode="data",
            camera=dict(eye=dict(x=1.7, y=-2.3, z=1.1))
        ),
        showlegend=False
    )
    return fig


# =========================================================
# DNA 3D 모델
# =========================================================

def dna_scene(sequence):
    sequence = sequence.upper()
    if not sequence:
        sequence = "ATGC"

    fig = go.Figure()

    colors = {
        "A": "#58c9a7",
        "T": "#e9a85d",
        "G": "#7e9fe8",
        "C": "#d78ac8"
    }

    n = len(sequence)
    t = np.linspace(0, 4 * np.pi, n * 8)

    x1 = np.cos(t)
    y1 = np.sin(t)
    z1 = np.linspace(0, 8, len(t))

    x2 = -np.cos(t)
    y2 = -np.sin(t)
    z2 = z1

    fig.add_trace(go.Scatter3d(
        x=x1, y=y1, z=z1,
        mode="lines",
        line=dict(color="#60d5c2", width=8),
        name="DNA 가닥 1"
    ))

    fig.add_trace(go.Scatter3d(
        x=x2, y=y2, z=z2,
        mode="lines",
        line=dict(color="#b08be7", width=8),
        name="DNA 가닥 2"
    ))

    # 염기쌍 연결
    for i in range(n):
        ti = (i / max(n - 1, 1)) * 4 * np.pi
        zi = (i / max(n - 1, 1)) * 8

        fig.add_trace(go.Scatter3d(
            x=[math.cos(ti), -math.cos(ti)],
            y=[math.sin(ti), -math.sin(ti)],
            z=[zi, zi],
            mode="lines",
            line=dict(color="#e7dca7", width=3),
            showlegend=False,
            hovertemplate=f"염기쌍 {i+1}<extra></extra>"
        ))

        base = sequence[i]
        fig.add_trace(go.Scatter3d(
            x=[math.cos(ti)],
            y=[math.sin(ti)],
            z=[zi],
            mode="markers+text",
            marker=dict(size=5, color=colors.get(base, "#ffffff")),
            text=[base],
            textposition="top center",
            textfont=dict(color="white", size=10),
            showlegend=False,
            hovertemplate=f"위치 {i+1}: {base}<extra></extra>"
        ))

    fig.update_layout(
        title="DNA DOUBLE HELIX · 3D",
        height=620,
        margin=dict(l=0, r=0, t=45, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(eye=dict(x=1.8, y=-2.4, z=0.8))
        ),
        showlegend=False
    )
    return fig


# =========================================================
# 약물 시뮬레이션 데이터
# =========================================================

DRUG_DATA = {
    "카페인": {
        "category": "중추신경계 자극 관련 물질",
        "mechanism": "아데노신 수용체 작용을 방해하여 졸음과 피로감에 영향을 줄 수 있습니다.",
        "effects": ["각성 상태 변화", "심박수 변화 가능성", "수면에 영향"],
        "vision": "각성 변화",
        "warning": "개인에 따라 반응이 다르며 수면과 심혈관계에 영향을 줄 수 있습니다."
    },
    "니코틴": {
        "category": "신경계 작용 물질",
        "mechanism": "니코틴성 아세틸콜린 수용체에 작용하여 신경전달에 영향을 줍니다.",
        "effects": ["신경전달 변화", "심박수와 혈압 변화 가능성", "의존성 위험"],
        "vision": "감각 민감도 변화",
        "warning": "의존성이 생길 수 있으며 청소년의 뇌 발달에 특히 해로울 수 있습니다."
    },
    "알코올": {
        "category": "중추신경계 억제 물질",
        "mechanism": "여러 신경전달 체계에 영향을 주어 판단과 운동 조절 능력을 저하시킬 수 있습니다.",
        "effects": ["판단력 저하", "균형감각 변화", "반응 속도 저하"],
        "vision": "초점·균형감각 변화",
        "warning": "판단과 운동 능력을 떨어뜨리며 성장기에는 특히 위험할 수 있습니다."
    },
    "진정제 계열": {
        "category": "중추신경계 억제 관련 약물",
        "mechanism": "일부 약물은 GABA 신호 전달을 강화하여 신경계 활동을 낮춥니다.",
        "effects": ["졸림", "반응 속도 저하", "기억과 집중력 변화"],
        "vision": "반응 지연",
        "warning": "의료진의 관리 없이 사용하면 위험할 수 있습니다."
    },
    "오피오이드 계열": {
        "category": "통증 조절 관련 약물",
        "mechanism": "오피오이드 수용체에 작용하여 통증 신호 전달을 변화시킵니다.",
        "effects": ["통증 인식 변화", "졸림", "호흡 억제 위험"],
        "vision": "주의·각성 저하",
        "warning": "호흡 기능을 심각하게 억제할 수 있는 위험이 있어 의료적 관리가 필요합니다."
    },
    "항히스타민제": {
        "category": "알레르기 증상 완화 약물",
        "mechanism": "히스타민 수용체를 차단하여 알레르기 반응을 완화합니다.",
        "effects": ["알레르기 증상 완화", "일부 종류에서 졸림", "주의력 변화 가능성"],
        "vision": "졸림·주의력 변화",
        "warning": "종류에 따라 졸림 등 부작용이 나타날 수 있습니다."
    },
    "항우울제": {
        "category": "정신건강 치료 약물",
        "mechanism": "세로토닌 등 신경전달물질 체계에 영향을 주는 여러 종류의 약물이 있습니다.",
        "effects": ["신경전달 조절", "기분 증상 개선에 도움", "개인별 부작용 차이"],
        "vision": "직접적인 시야 효과로 단순화할 수 없음",
        "warning": "효과와 부작용은 약물 종류와 개인에 따라 다르며 의료진의 처방과 관리가 필요합니다."
    },
    "기관지확장제": {
        "category": "호흡기 치료 약물",
        "mechanism": "기도 평활근을 이완시켜 공기가 이동하는 통로를 넓히는 데 도움을 줍니다.",
        "effects": ["기도 확장", "호흡 흐름 개선", "일부 종류에서 심박수 변화"],
        "vision": "직접적인 시야 효과는 일반화하기 어려움",
        "warning": "약물 종류에 따라 작용과 주의사항이 다릅니다."
    },
    "인슐린": {
        "category": "호르몬 치료제",
        "mechanism": "세포의 포도당 흡수를 돕고 혈당을 낮추는 호르몬입니다.",
        "effects": ["혈당 조절", "포도당 이용 변화", "저혈당 위험"],
        "vision": "시야 변화가 아니라 혈당 상태 변화 중심",
        "warning": "혈당 조절에 중요한 약물이며 사용은 의료진의 지시에 따라야 합니다."
    },
    "항생제": {
        "category": "감염 치료 약물",
        "mechanism": "세균의 생존이나 증식에 필요한 과정을 방해하는 약물군입니다.",
        "effects": ["세균 감염 치료", "약물별 표적 차이", "내성 문제"],
        "vision": "일반적인 1인칭 시야 변화 없음",
        "warning": "바이러스 감염에는 효과가 없으며 불필요한 사용은 항생제 내성을 높일 수 있습니다."
    },
    "항염증제": {
        "category": "염증·통증 조절 약물",
        "mechanism": "종류에 따라 염증 반응에 관여하는 물질의 생성을 억제합니다.",
        "effects": ["염증 반응 변화", "통증 완화", "약물별 부작용"],
        "vision": "일반적인 1인칭 시야 변화 없음",
        "warning": "약물 종류에 따라 위장관·신장 등에 영향을 줄 수 있습니다."
    },
    "마취제": {
        "category": "의료용 마취 약물",
        "mechanism": "신경 신호 전달을 억제하거나 의식 상태를 조절하는 데 사용됩니다.",
        "effects": ["감각 전달 변화", "의식 상태 변화 가능성", "의료적 감시 필요"],
        "vision": "감각 입력 감소를 추상적으로 표현",
        "warning": "전문적인 의료 환경에서 감시하며 사용하는 약물입니다."
    }
}


# =========================================================
# 1인칭 시야 시뮬레이션
# =========================================================

def first_person_scene(drug_name, intensity=0.65):
    """
    실제 약물 경험을 재현하는 것이 아니라,
    신경계 기능 변화 개념을 추상적인 시각 효과로 보여준다.
    """

    info = DRUG_DATA[drug_name]
    vision = info["vision"]

    fig = go.Figure()

    # 가상의 시야 중심
    theta = np.linspace(0, 2 * np.pi, 100)
    x = np.cos(theta)
    y = np.sin(theta)

    # 기본 시야 테두리
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode="lines",
        line=dict(color="#9ddff2", width=3),
        showlegend=False,
        hoverinfo="skip"
    ))

    rng = np.random.default_rng(10)

    if vision == "초점·균형감각 변화":
        # 초점이 여러 겹으로 보이는 추상 효과
        for r in [0.22, 0.42, 0.62, 0.82]:
            fig.add_shape(
                type="circle",
                x0=-r, y0=-r, x1=r, y1=r,
                line=dict(color="rgba(230,190,120,0.5)", width=2)
            )
        for angle in np.linspace(0, 2*np.pi, 8):
            fig.add_trace(go.Scatter(
                x=[0, 0.8*np.cos(angle)],
                y=[0, 0.8*np.sin(angle)],
                mode="lines",
                line=dict(color="rgba(230,190,120,0.35)", width=2),
                showlegend=False,
                hoverinfo="skip"
            ))

    elif vision == "반응 지연":
        # 입력과 반응 사이의 시간 지연을 나타내는 동심원
        for r in [0.2, 0.4, 0.6, 0.8]:
            fig.add_shape(
                type="circle",
                x0=-r, y0=-r, x1=r, y1=r,
                line=dict(color="rgba(150,170,220,0.5)", width=2)
            )

    elif vision == "각성 변화":
        # 각성 정도 변화 개념을 나타내는 빛의 점
        for i in range(45):
            a = rng.uniform(0, 2*np.pi)
            r = rng.uniform(0.15, 0.9)
            fig.add_trace(go.Scatter(
                x=[r*np.cos(a)], y=[r*np.sin(a)],
                mode="markers",
                marker=dict(
                    size=rng.uniform(3, 8),
                    color="#f3d78d",
                    opacity=0.7
                ),
                showlegend=False,
                hoverinfo="skip"
            ))

    elif vision == "감각 민감도 변화":
        for i in range(12):
            a = i * np.pi / 6
            fig.add_trace(go.Scatter(
                x=[0, 0.85*np.cos(a)],
                y=[0, 0.85*np.sin(a)],
                mode="lines",
                line=dict(color="rgba(120,210,220,0.45)", width=2),
                showlegend=False,
                hoverinfo="skip"
            ))

    else:
        # 직접적인 시야 효과가 없는 경우도 구분하여 표시
        fig.add_trace(go.Scatter(
            x=[0], y=[0],
            mode="markers+text",
            marker=dict(size=20, color="#9ddff2"),
            text=["시각 효과를 단정할 수 없음"],
            textposition="bottom center",
            textfont=dict(color="white", size=12),
            showlegend=False
        ))

    fig.update_layout(
        height=460,
        margin=dict(l=5, r=5, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#091522",
        xaxis=dict(
            range=[-1.1, 1.1],
            visible=False,
            scaleanchor="y"
        ),
        yaxis=dict(
            range=[-1.1, 1.1],
            visible=False
        ),
        showlegend=False
    )

    return fig


# =========================================================
# DNA 염기서열 분석
# =========================================================

def analyze_sequence(sequence):
    sequence = sequence.upper()
    valid = all(base in "ATGC" for base in sequence)

    if not valid:
        return None

    counts = {
        "A": sequence.count("A"),
        "T": sequence.count("T"),
        "G": sequence.count("G"),
        "C": sequence.count("C")
    }

    total = len(sequence)
    if total == 0:
        return None

    gc = (counts["G"] + counts["C"]) / total * 100

    return counts, gc


# =========================================================
# 상단 제목
# =========================================================

st.markdown("""
<div style="padding: 8px 0 18px 0;">
    <div class="small-label">INTERACTIVE LIFE SCIENCE LABORATORY</div>
    <h1 style="font-size:2.5rem; margin-bottom:0;">BioSphere 3D</h1>
    <p style="font-size:1.05rem; color:#9fb4c8;">
        인체에서 세포와 DNA까지 이어지는 생명과학 탐구 시뮬레이터
    </p>
</div>
""", unsafe_allow_html=True)


# =========================================================
# 사이드바
# =========================================================

with st.sidebar:
    st.markdown("## 🧬 탐구 메뉴")
    st.caption("하나의 생명체를 단계적으로 확대합니다.")

    stage_label = {
        "body": "① 인체 · 장기",
        "organ": "② 장기 확대",
        "cell": "③ 세포 확대",
        "dna": "④ 핵 · DNA",
        "drug": "⑤ 약물 반응"
    }

    for key, label in stage_label.items():
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.stage = key
            if key == "organ" and not st.session_state.selected_organ:
                st.session_state.selected_organ = "심장"

    st.divider()

    st.markdown("### 탐구 단계")
    steps = ["인체", "장기", "세포", "핵", "DNA"]
    current = {
        "body": 0, "organ": 1, "cell": 2, "dna": 4, "drug": 0
    }[st.session_state.stage]

    for i, step in enumerate(steps):
        prefix = "●" if i <= current else "○"
        st.write(f"{prefix} {step}")

    st.divider()
    st.caption("모든 3D 장면은 마우스 드래그로 회전하고 휠로 확대할 수 있습니다.")


# =========================================================
# ① 인체 및 장기 탐색
# =========================================================

if st.session_state.stage == "body":

    st.markdown('<div class="stage">STAGE 01 · HUMAN BODY</div>', unsafe_allow_html=True)
    st.header("인체를 절개하여 내부 장기를 관찰하기")

    left, right = st.columns([1.65, 1])

    with left:
        st.session_state.cutaway = st.toggle(
            "메스로 몸통 앞면을 절개해 내부 보기",
            value=st.session_state.cutaway
        )

        st.plotly_chart(
            body_scene(
                cutaway=st.session_state.cutaway,
                selected=st.session_state.selected_organ
            ),
            use_container_width=True,
            config={"displayModeBar": True}
        )

        st.caption(
            "모형은 주요 장기의 상대적 위치를 학습하기 위한 단순화된 3D 표현입니다. "
            "실제 인체의 크기·형태·위치는 개인과 해부학적 조건에 따라 다릅니다."
        )

    with right:
        st.markdown("### 내부 장기 선택")
        st.write("확인하고 싶은 장기를 선택하세요.")

        organ_names = list(ORGAN_DATA.keys())

        for start in range(0, len(organ_names), 2):
            cols = st.columns(2)
            for j, organ in enumerate(organ_names[start:start+2]):
                with cols[j]:
                    if st.button(
                        f"🫀 {organ}",
                        key=f"select_{organ}",
                        use_container_width=True
                    ):
                        st.session_state.selected_organ = organ
                        st.session_state.stage = "organ"
                        st.rerun()

        st.divider()

        st.markdown("### 장기 기능 제거 실험")
        st.write("특정 장기가 정상적으로 기능하지 못할 때의 영향을 개념적으로 살펴봅니다.")

        removed = st.multiselect(
            "기능을 비활성화할 장기",
            options=organ_names,
            default=st.session_state.removed_organs
        )

        st.session_state.removed_organs = removed

        if removed:
            st.warning("선택한 장기의 기능이 비활성화된 가상 상황입니다.")
            for organ in removed:
                st.markdown(f"**{organ}**")
                st.write(ORGAN_DATA[organ]["problem"])
        else:
            st.success("모든 장기가 기능하는 기본 상태입니다.")


# =========================================================
# ② 장기 확대
# =========================================================

elif st.session_state.stage == "organ":

    organ = st.session_state.selected_organ
    data = ORGAN_DATA[organ]

    st.markdown('<div class="stage">STAGE 02 · ORGAN EXPLORATION</div>', unsafe_allow_html=True)
    st.header(f"{organ} 탐구")

    c1, c2 = st.columns([1.5, 1])

    with c1:
        fig = go.Figure()
        add_organ(fig, organ, 1.0, True)

        # 주변 구조를 함께 표현
        if organ == "심장":
            add_organ(fig, "폐", 0.20)
        elif organ == "폐":
            add_organ(fig, "심장", 0.20)
        elif organ in ["위", "간", "췌장"]:
            add_organ(fig, "소장", 0.20)

        fig.update_layout(
            title=f"{organ} · ORGAN MODEL",
            height=600,
            margin=dict(l=0, r=0, t=45, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            scene=dict(
                bgcolor="rgba(0,0,0,0)",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                aspectmode="data",
                camera=dict(eye=dict(x=1.6, y=-2.2, z=1.0))
            ),
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown(f"### {organ}")
        st.markdown(f"**기관계:** {data['type']}")
        st.markdown("#### 주요 기능")
        st.write(data["function"])

        st.markdown("#### 구조적 특징")
        st.write(data["detail"])

        st.markdown("#### 기능 저하 시 나타날 수 있는 영향")
        st.info(data["problem"])

        st.markdown("#### 이 장기를 구성하는 대표 세포")
        for cell in data["cells"]:
            st.write(f"• {cell}")

        st.divider()

        if st.button("🔬 이 장기를 구성하는 세포로 확대", use_container_width=True):
            st.session_state.selected_cell = data["cell_main"]
            st.session_state.stage = "cell"
            st.rerun()

        if st.button("← 인체 전체로 돌아가기", use_container_width=True):
            st.session_state.stage = "body"
            st.rerun()


# =========================================================
# ③ 세포 확대
# =========================================================

elif st.session_state.stage == "cell":

    organ = st.session_state.selected_organ
    data = ORGAN_DATA[organ]

    st.markdown('<div class="stage">STAGE 03 · CELL EXPLORATION</div>', unsafe_allow_html=True)
    st.header(f"{organ} → 세포 단계")

    st.markdown(
        f"현재 탐색 중인 장기: **{organ}**  "
        f" / 대표 세포: **{data['cell_main']}**"
    )

    selected_cell = st.selectbox(
        "관찰할 세포 선택",
        options=data["cells"],
        index=data["cells"].index(st.session_state.selected_cell)
        if st.session_state.selected_cell in data["cells"] else 0
    )
    st.session_state.selected_cell = selected_cell

    left, right = st.columns([1.5, 1])

    with left:
        st.plotly_chart(
            cell_scene(selected_cell),
            use_container_width=True,
            config={"displayModeBar": True}
        )

    with right:
        cell_info = CELL_DATA.get(
            selected_cell,
            {
                "desc": "이 세포는 해당 장기의 기능을 수행하는 데 관여합니다.",
                "features": ["세포막", "세포질", "핵"],
                "color": "#9cc9dd"
            }
        )

        st.markdown(f"### {selected_cell}")
        st.write(cell_info["desc"])

        st.markdown("#### 세포의 특징")
        for feature in cell_info["features"]:
            st.write(f"• {feature}")

        st.divider()
        st.markdown("#### 세포 내부 구조")

        organelles = {
            "핵": "DNA를 포함하며 유전자 발현과 세포 활동 조절에 관여합니다.",
            "미토콘드리아": "세포 호흡을 통해 ATP를 생산하는 데 중요한 역할을 합니다.",
            "소포체": "단백질과 지질의 합성 및 이동에 관여합니다.",
            "골지체": "단백질과 지질을 가공하고 분류하여 운반합니다.",
            "리보솜": "mRNA 정보를 바탕으로 단백질을 합성합니다."
        }

        for name, desc in organelles.items():
            with st.expander(name):
                st.write(desc)

        if st.button("🧬 세포핵을 확대해 DNA 관찰하기", use_container_width=True):
            st.session_state.stage = "dna"
            st.rerun()

        if st.button("← 장기 단계로 돌아가기", use_container_width=True):
            st.session_state.stage = "organ"
            st.rerun()


# =========================================================
# ④ 핵과 DNA
# =========================================================

elif st.session_state.stage == "dna":

    st.markdown('<div class="stage">STAGE 04 · NUCLEUS & DNA</div>', unsafe_allow_html=True)
    st.header("세포핵 속 DNA 탐구")

    st.write(
        f"탐색 경로: 인체 → {st.session_state.selected_organ} → "
        f"{st.session_state.selected_cell} → 세포핵 → DNA"
    )

    left, right = st.columns([1.4, 1])

    with left:
        st.plotly_chart(
            dna_scene(st.session_state.dna_sequence),
            use_container_width=True,
            config={"displayModeBar": True}
        )

    with right:
        st.markdown("### DNA 염기서열")

        sequence = st.text_area(
            "염기서열 입력 (A, T, G, C)",
            value=st.session_state.dna_sequence,
            height=120,
            help="교육용으로 짧은 염기서열을 입력할 수 있습니다."
        ).upper().replace(" ", "").replace("\n", "")

        if all(base in "ATGC" for base in sequence) and len(sequence) > 0:
            st.session_state.dna_sequence = sequence
            result = analyze_sequence(sequence)

            counts, gc = result

            m1, m2 = st.columns(2)
            m1.metric("염기 수", len(sequence))
            m2.metric("GC 비율", f"{gc:.1f}%")

            st.markdown("#### 염기별 구성")
            chart = px.bar(
                x=list(counts.keys()),
                y=list(counts.values()),
                labels={"x": "염기", "y": "개수"},
                color=list(counts.keys()),
                color_discrete_map={
                    "A": "#58c9a7",
                    "T": "#e9a85d",
                    "G": "#7e9fe8",
                    "C": "#d78ac8"
                }
            )
            chart.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#dce9f5",
                showlegend=False,
                height=250
            )
            st.plotly_chart(chart, use_container_width=True)

        else:
            st.error("염기서열에는 A, T, G, C만 입력할 수 있습니다.")

        st.divider()

        st.markdown("#### 염기서열 변경 실험")

        if st.button("염기 하나를 임의로 바꾸기", use_container_width=True):
            seq = list(st.session_state.dna_sequence)
            if seq:
                idx = random.randrange(len(seq))
                current = seq[idx]
                choices = [b for b in "ATGC" if b != current]
                seq[idx] = random.choice(choices)
                st.session_state.dna_sequence = "".join(seq)
                st.rerun()

        if st.button("기본 염기서열로 초기화", use_container_width=True):
            st.session_state.dna_sequence = "ATGCGTACGTTAGCGATCGT"
            st.rerun()

        st.warning(
            "이 기능은 염기서열의 구성과 변화를 시각화하는 교육용 실험입니다. "
            "실제 형질은 유전자 발현, 여러 유전자 사이의 상호작용, 환경 등 다양한 요인에 의해 결정됩니다. "
            "이 모형은 실제 개인의 형질이나 질병을 예측하지 않습니다."
        )

    if st.button("← 세포 단계로 돌아가기"):
        st.session_state.stage = "cell"
        st.rerun()


# =========================================================
# ⑤ 약물 반응 및 가상 1인칭 시야
# =========================================================

elif st.session_state.stage == "drug":

    st.markdown('<div class="stage">STAGE 05 · PHYSIOLOGICAL RESPONSE</div>', unsafe_allow_html=True)
    st.header("약물과 신경계 반응 시뮬레이션")

    st.info(
        "이 화면은 약물이 신경계와 신체 기능에 미칠 수 있는 영향을 이해하기 위한 "
        "추상적 교육 모형입니다. 실제 약물 투여나 사용을 재현하지 않습니다."
    )

    drug_name = st.selectbox(
        "관찰할 약물 또는 약물 계열",
        list(DRUG_DATA.keys()),
        index=list(DRUG_DATA.keys()).index(st.session_state.drug)
        if st.session_state.drug in DRUG_DATA else 0
    )
    st.session_state.drug = drug_name

    info = DRUG_DATA[drug_name]

    st.markdown(f"### {drug_name}")
    st.markdown(f"**분류:** {info['category']}")

    a, b = st.columns([1, 1])

    with a:
        st.markdown("#### 작용 원리")
        st.write(info["mechanism"])

        st.markdown("#### 관찰 가능한 생리적 영향")
        for effect in info["effects"]:
            st.write(f"• {effect}")

        st.markdown("#### 주의할 점")
        st.warning(info["warning"])

    with b:
        st.markdown("#### 가상 시야 시뮬레이션")
        st.write(
            "선택한 물질과 관련된 신경계 기능 변화를 추상적인 화면 효과로 표현합니다. "
            "실제 경험이나 개인별 반응을 그대로 재현하는 것은 아닙니다."
        )

        if st.button("가상 1인칭 시야 보기", use_container_width=True):
            st.session_state.show_drug_view = True
            st.rerun()

        if st.session_state.show_drug_view:
            st.plotly_chart(
                first_person_scene(drug_name),
                use_container_width=True,
                config={"displayModeBar": False}
            )

            st.caption(
                f"시각화 주제: {info['vision']} · "
                "실제 시야 변화의 의학적 예측이나 체험 재현이 아닙니다."
            )

            if st.button("시야 시뮬레이션 닫기"):
                st.session_state.show_drug_view = False
                st.rerun()

    st.divider()

    st.markdown("### 약물 작용을 이해하는 핵심 개념")

    concepts = [
        ("수용체", "세포막이나 세포 내부에서 특정 신호 물질을 인식하는 단백질입니다."),
        ("신경전달물질", "신경세포 사이에서 신호를 전달하는 화학적 물질입니다."),
        ("항상성", "생명체가 내부 환경을 일정한 범위로 유지하려는 조절 작용입니다."),
        ("부작용", "약물이 의도한 치료 효과 외에 일으킬 수 있는 바람직하지 않은 반응입니다.")
    ]

    cols = st.columns(4)
    for i, (title, desc) in enumerate(concepts):
        with cols[i]:
            st.markdown(f"""
            <div class="bio-card">
                <div class="small-label">{title}</div>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.caption(
        "약물의 효과와 부작용은 물질의 종류, 개인의 건강 상태, 다른 약물과의 상호작용 등에 따라 달라집니다. "
        "이 앱은 복용·투여 방법이나 용량을 제시하지 않습니다."
    )


# =========================================================
# 하단 공통 안내
# =========================================================

st.divider()

st.markdown("""
<div style="text-align:center; padding:15px 0; color:#7892a9;">
    <b>BioSphere 3D</b> · Interactive Biology Learning Environment
    <br>
    <small>교육용 시각화 모델이며 실제 해부학·진단·치료 시뮬레이터가 아닙니다.</small>
</div>
""", unsafe_allow_html=True)
