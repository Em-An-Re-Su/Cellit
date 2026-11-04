import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import math
import random

# =========================================================
# 0. 기본 설정
# =========================================================

st.set_page_config(
    page_title="BioSphere 3D",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: Pretendard, sans-serif;
}
.stApp {
    background: linear-gradient(145deg, #081421, #101e30 65%, #0b1928);
    color: #eaf3fc;
}
section[data-testid="stSidebar"] {
    background: #091522;
    border-right: 1px solid #263d52;
}
h1, h2, h3 { color: #edf6ff; }
p, li, label { color: #c6d6e6; }
div[data-testid="stMetric"] {
    background: #14273b;
    border: 1px solid #2d455d;
    padding: 14px;
    border-radius: 13px;
}
div.stButton > button {
    border-radius: 10px;
    background: #172d43;
    color: #eaf5ff;
    border: 1px solid #38536e;
    min-height: 42px;
    font-weight: 600;
}
div.stButton > button:hover {
    background: #23445f;
    border-color: #64c9df;
}
.bio-panel {
    background: linear-gradient(145deg, #152a40, #102033);
    border: 1px solid #304a63;
    border-radius: 14px;
    padding: 17px;
    margin-bottom: 10px;
}
.eyebrow {
    color: #6ed0dc;
    font-size: 0.82rem;
    letter-spacing: 1.5px;
    font-weight: 700;
}
.stage-pill {
    display: inline-block;
    background: #18364c;
    border: 1px solid #3a647d;
    border-radius: 8px;
    padding: 7px 12px;
    color: #a8e8f2;
    font-size: 0.85rem;
    font-weight: 700;
}
hr { border-color: #2a4055; }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 1. 세션 상태
# =========================================================

DEFAULTS = {
    "stage": "body",
    "organ": "심장",
    "cell": "심근세포",
    "organelle": "핵",
    "cut_open": False,
    "removed": [],
    "dna_sequence": "ATGCGTACGTTAGCGATCGT",
    "eye_allele_1": "B",
    "eye_allele_2": "b",
    "hair_allele_1": "D",
    "hair_allele_2": "d",
    "drug": "펜타닐(의료용 오피오이드)",
    "drug_view": False,
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# =========================================================
# 2. 장기 정보
# =========================================================

ORGANS = {
    "뇌": {
        "system": "신경계",
        "color": "#d9a6c9",
        "function": "감각 정보를 처리하고 운동, 기억, 학습, 감정 및 항상성을 조절합니다.",
        "structure": "대뇌, 소뇌, 뇌줄기 등으로 구성됩니다. 각 영역은 서로 연결되어 정보를 처리합니다.",
        "cells": ["신경세포", "성상세포", "희소돌기아교세포"],
        "main_cell": "신경세포",
        "problem": "뇌 기능이 크게 저하되면 의식, 운동, 감각, 언어, 기억 등 여러 기능에 영향을 줄 수 있습니다.",
        "effects": {
            "순환": "뇌로 공급되는 산소와 영양분이 부족해지면 신경세포 기능이 저하될 수 있습니다.",
            "신경": "신경 신호 처리와 신체 조절 기능에 문제가 발생할 수 있습니다."
        }
    },
    "심장": {
        "system": "순환계",
        "color": "#e45e75",
        "function": "심근의 수축과 이완으로 혈액을 폐와 온몸으로 이동시킵니다.",
        "structure": "두 개의 심방과 두 개의 심실, 판막 및 심장근육으로 구성됩니다.",
        "cells": ["심근세포", "내피세포", "섬유아세포"],
        "main_cell": "심근세포",
        "problem": "심장의 펌프 기능이 크게 떨어지면 여러 조직으로 가는 혈류와 산소 공급이 감소합니다.",
        "effects": {
            "순환": "혈압과 혈류 유지가 어려워지고 여러 장기의 산소 공급이 감소할 수 있습니다.",
            "뇌": "뇌 혈류가 감소하면 어지러움이나 의식 저하 등이 발생할 수 있습니다.",
            "신장": "신장으로 가는 혈류가 감소하면 여과 기능에 영향을 줄 수 있습니다."
        }
    },
    "폐": {
        "system": "호흡계",
        "color": "#79c5e5",
        "function": "폐포에서 산소와 이산화탄소를 교환합니다.",
        "structure": "기관지와 세기관지가 나뉘며 끝부분에 작은 폐포가 모여 있습니다.",
        "cells": ["폐포세포", "섬모상피세포", "대식세포"],
        "main_cell": "폐포세포",
        "problem": "가스 교환이 저하되면 혈액의 산소 공급과 이산화탄소 배출에 문제가 생길 수 있습니다.",
        "effects": {
            "호흡": "산소 교환이 감소하고 이산화탄소 배출이 어려워질 수 있습니다.",
            "뇌": "산소 부족은 뇌 기능과 의식 수준에 영향을 줄 수 있습니다.",
            "심장": "산소 공급 저하는 심장 기능에도 부담을 줄 수 있습니다."
        }
    },
    "간": {
        "system": "소화·대사계",
        "color": "#bd8755",
        "function": "영양소 대사, 담즙 생성, 혈당 조절, 혈장 단백질 합성 및 약물 대사에 관여합니다.",
        "structure": "간세포가 소엽 구조를 이루며 혈액과 담즙이 서로 다른 방향으로 흐릅니다.",
        "cells": ["간세포", "쿠퍼세포", "담관세포"],
        "main_cell": "간세포",
        "problem": "대사, 해독, 단백질 합성 및 담즙 생성 기능이 저하될 수 있습니다.",
        "effects": {
            "대사": "영양소 처리와 혈당 조절이 어려워질 수 있습니다.",
            "혈액": "혈액 응고에 관여하는 단백질 합성이 감소할 수 있습니다."
        }
    },
    "위": {
        "system": "소화계",
        "color": "#e6a16d",
        "function": "음식물을 저장하고 위액과 섞어 소화 과정을 진행합니다.",
        "structure": "점막, 점막하층, 근육층, 장막 등으로 구성됩니다.",
        "cells": ["위벽세포", "주세포", "점액세포"],
        "main_cell": "위벽세포",
        "problem": "소화 과정과 음식물 저장 및 이동에 영향을 줄 수 있습니다.",
        "effects": {
            "소화": "음식물의 소화와 다음 소화기관으로의 이동에 영향을 줄 수 있습니다."
        }
    },
    "신장": {
        "system": "비뇨계",
        "color": "#a88bd2",
        "function": "혈액을 여과하고 수분, 전해질, 산·염기 균형을 조절합니다.",
        "structure": "네프론은 사구체와 세뇨관으로 이루어져 있으며 혈액 여과와 재흡수에 관여합니다.",
        "cells": ["족세포", "세뇨관 상피세포", "사구체 내피세포"],
        "main_cell": "세뇨관 상피세포",
        "problem": "노폐물 배출과 체액·전해질 균형 유지에 문제가 생길 수 있습니다.",
        "effects": {
            "배설": "노폐물과 수분을 조절하는 능력이 감소할 수 있습니다.",
            "순환": "체액량과 혈압 조절에 영향을 줄 수 있습니다."
        }
    },
    "소장": {
        "system": "소화계",
        "color": "#e6c46d",
        "function": "소화된 영양소 대부분을 흡수합니다.",
        "structure": "융모와 미세융모가 표면적을 넓혀 영양소 흡수를 돕습니다.",
        "cells": ["흡수상피세포", "배상세포", "장내분비세포"],
        "main_cell": "흡수상피세포",
        "problem": "영양소 흡수가 감소하면 영양 상태와 에너지 공급에 영향을 줄 수 있습니다.",
        "effects": {
            "소화": "영양소 흡수와 수분 흡수에 문제가 생길 수 있습니다."
        }
    },
    "췌장": {
        "system": "소화·내분비계",
        "color": "#dfb17d",
        "function": "소화 효소를 분비하고 인슐린과 글루카곤으로 혈당을 조절합니다.",
        "structure": "외분비 조직과 랑게르한스섬으로 이루어집니다.",
        "cells": ["췌장 선방세포", "베타세포", "알파세포"],
        "main_cell": "베타세포",
        "problem": "소화 효소 분비와 혈당 조절 기능에 영향을 줄 수 있습니다.",
        "effects": {
            "대사": "인슐린과 글루카곤의 조절이 어려워져 혈당 균형에 문제가 생길 수 있습니다."
        }
    }
}


# =========================================================
# 3. 3D 메시 생성 함수
# =========================================================

def surface_ellipsoid(center, radii, color, name, opacity=1.0,
                      deform=None, resolution=42):
    """
    타원체를 기본으로 하되 deform 함수로 표면을 변형할 수 있는 메시.
    Plotly Surface에서 지원하지 않는 속성은 사용하지 않는다.
    """
    cx, cy, cz = center
    rx, ry, rz = radii

    u = np.linspace(0, 2*np.pi, resolution)
    v = np.linspace(0, np.pi, resolution)

    U, V = np.meshgrid(u, v)

    X = rx * np.cos(U) * np.sin(V)
    Y = ry * np.sin(U) * np.sin(V)
    Z = rz * np.cos(V)

    if deform is not None:
        X, Y, Z = deform(X, Y, Z, U, V)

    return go.Surface(
        x=X + cx,
        y=Y + cy,
        z=Z + cz,
        surfacecolor=np.zeros_like(X),
        colorscale=[[0, color], [1, color]],
        showscale=False,
        opacity=opacity,
        name=name,
        hovertemplate=f"{name}<extra></extra>"
    )


def add_tube(fig, points, radius, color, name, resolution=12):
    """곡선 경로를 따라가는 튜브 메시."""
    points = np.asarray(points, dtype=float)
    if len(points) < 2:
        return

    theta = np.linspace(0, 2*np.pi, resolution)
    X, Y, Z = [], [], []

    for i, p in enumerate(points):
        if i == 0:
            tangent = points[1] - points[0]
        elif i == len(points)-1:
            tangent = points[-1] - points[-2]
        else:
            tangent = points[i+1] - points[i-1]

        tangent = tangent / (np.linalg.norm(tangent) + 1e-9)
        helper = np.array([0.0, 0.0, 1.0])

        if abs(np.dot(tangent, helper)) > 0.9:
            helper = np.array([0.0, 1.0, 0.0])

        normal = np.cross(tangent, helper)
        normal /= np.linalg.norm(normal) + 1e-9
        binormal = np.cross(tangent, normal)

        ring = [
            p + radius * (
                normal*np.cos(a) + binormal*np.sin(a)
            )
            for a in theta
        ]

        X.append([q[0] for q in ring])
        Y.append([q[1] for q in ring])
        Z.append([q[2] for q in ring])

    fig.add_trace(go.Surface(
        x=np.array(X),
        y=np.array(Y),
        z=np.array(Z),
        colorscale=[[0, color], [1, color]],
        showscale=False,
        opacity=0.98,
        name=name,
        hovertemplate=f"{name}<extra></extra>"
    ))


def organ_shape(fig, name, opacity=1.0):
    """장기별 형태를 구분해 메시를 생성한다."""

    color = ORGANS[name]["color"]

    if name == "뇌":
        # 대뇌 반구와 소뇌, 뇌줄기를 별도 메시로 표현
        for side in [-1, 1]:
            def brain_fold(X, Y, Z, U, V):
                fold = 1 + 0.035*np.sin(8*U)*np.sin(7*V)
                return X*fold, Y*fold, Z*fold

            fig.add_trace(surface_ellipsoid(
                (side*0.18, 0, 7.75),
                (0.34, 0.37, 0.40),
                color, "대뇌 반구", opacity,
                deform=brain_fold
            ))

        fig.add_trace(surface_ellipsoid(
            (0, 0.12, 7.38), (0.24, 0.28, 0.19),
            "#c18db9", "소뇌", opacity
        ))
        add_tube(
            fig,
            [(0, 0.03, 7.45), (0, 0.04, 7.20), (0, 0.04, 6.95)],
            0.09, "#d49abf", "뇌줄기"
        )

    elif name == "심장":
        # 심장 덩어리 + 심첨부 + 대혈관
        def heart_deform(X, Y, Z, U, V):
            width = 1 - 0.18*np.cos(V)
            return X*width, Y, Z

        fig.add_trace(surface_ellipsoid(
            (0, -0.27, 5.60), (0.36, 0.25, 0.48),
            color, "심장", opacity, deform=heart_deform
        ))
        add_tube(fig, [
            (-0.10, -0.27, 5.95),
            (-0.10, -0.27, 6.18),
            (-0.04, -0.27, 6.32)
        ], 0.075, "#cf5367", "대동맥")
        add_tube(fig, [
            (0.13, -0.26, 5.92),
            (0.22, -0.26, 6.12),
            (0.30, -0.26, 6.23)
        ], 0.065, "#7aaed2", "폐동맥")

    elif name == "폐":
        for side in [-1, 1]:
            def lung_deform(X, Y, Z, U, V):
                # 폐의 아래쪽이 넓고 위쪽이 좁아지는 형태
                factor = 0.82 + 0.20*np.sin(V)
                return X*factor, Y, Z

            fig.add_trace(surface_ellipsoid(
                (side*0.38, -0.20, 5.60),
                (0.31, 0.23, 0.66),
                color, "폐", opacity, deform=lung_deform
            ))

        add_tube(fig, [
            (0, -0.18, 6.32),
            (0, -0.18, 6.02),
            (0, -0.18, 5.85)
        ], 0.07, "#82c9e4", "기관")

    elif name == "간":
        def liver_deform(X, Y, Z, U, V):
            X = X * (1 + 0.16*np.sin(U))
            Z = Z * (1 + 0.08*np.cos(U))
            return X, Y, Z

        fig.add_trace(surface_ellipsoid(
            (-0.32, -0.27, 4.91),
            (0.63, 0.30, 0.31),
            color, "간", opacity, deform=liver_deform
        ))

    elif name == "위":
        def stomach_deform(X, Y, Z, U, V):
            X = X * (1 + 0.20*np.sin(V))
            Z = Z + 0.09*np.sin(U*2)*np.sin(V)
            return X, Y, Z

        fig.add_trace(surface_ellipsoid(
            (0.34, -0.27, 4.82),
            (0.30, 0.25, 0.47),
            color, "위", opacity, deform=stomach_deform
        ))

    elif name == "신장":
        for side in [-1, 1]:
            def kidney_deform(X, Y, Z, U, V):
                X = X * (1 - 0.20*np.exp(-((Z/0.35)**2)))
                return X, Y, Z

            fig.add_trace(surface_ellipsoid(
                (side*0.57, 0.05, 4.65),
                (0.19, 0.19, 0.35),
                color, "신장", opacity, deform=kidney_deform
            ))

    elif name == "소장":
        # 굴곡이 있는 장관을 튜브로 표현
        for j in range(5):
            pts = []
            for t in np.linspace(-1, 1, 65):
                x = 0.43*t
                y = -0.27 + 0.10*np.sin(t*13 + j*0.8)
                z = 4.12 + (j-2)*0.105 + 0.07*np.cos(t*12 + j)
                pts.append((x, y, z))
            add_tube(fig, pts, 0.035, color, "소장")

    elif name == "췌장":
        pts = []
        for t in np.linspace(-1, 1, 60):
            pts.append((
                0.50*t,
                -0.29,
                4.75 + 0.08*np.sin(t*3)
            ))
        add_tube(fig, pts, 0.09, color, "췌장")


# =========================================================
# 4. 인체 모델
# =========================================================

def body_mesh(fig, open_body=True):
    # 머리와 얼굴
    fig.add_trace(surface_ellipsoid(
        (0, 0, 7.77), (0.43, 0.39, 0.58),
        "#c99780", "머리", 0.98
    ))

    # 목
    fig.add_trace(surface_ellipsoid(
        (0, 0, 7.05), (0.19, 0.20, 0.28),
        "#bd8b76", "목", 0.95
    ))

    # 몸통을 표면 곡면으로 구성
    def torso_shape(X, Y, Z, U, V):
        # 어깨 쪽은 넓고 허리 쪽은 좁아지는 형태
        width = 0.82 + 0.17*np.cos(V) + 0.10*np.sin(V*2)
        X = X*width
        return X, Y, Z

    if open_body:
        # 앞면 일부를 잘라 내부를 볼 수 있도록 표면의 일부를 제거
        u = np.linspace(0, 2*np.pi, 64)
        v = np.linspace(0, np.pi, 48)
        U, V = np.meshgrid(u, v)

        X = 0.82*np.cos(U)*np.sin(V)
        Y = 0.42*np.sin(U)*np.sin(V)
        Z = 5.48 + 1.30*np.cos(V)

        # 앞쪽 절개면을 열어 둠
        mask = (Y < -0.03) & (np.abs(X) < 0.67)
        X = np.where(mask, np.nan, X)
        Y = np.where(mask, np.nan, Y)

        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale=[[0, "#bd8b76"], [1, "#d6a38d"]],
            showscale=False,
            opacity=0.32,
            name="절개된 몸통",
            hoverinfo="skip"
        ))
    else:
        fig.add_trace(surface_ellipsoid(
            (0, 0, 5.48), (0.82, 0.42, 1.30),
            "#c99780", "몸통", 0.90,
            deform=torso_shape
        ))

    # 어깨와 팔
    for side in [-1, 1]:
        fig.add_trace(surface_ellipsoid(
            (side*0.86, 0, 6.27), (0.32, 0.30, 0.34),
            "#c99780", "어깨", 0.95
        ))

        add_tube(fig, [
            (side*0.88, 0, 6.18),
            (side*1.03, 0, 5.72),
            (side*1.10, 0, 5.25)
        ], 0.16, "#c99780", "위팔")

        add_tube(fig, [
            (side*1.10, 0, 5.25),
            (side*1.17, 0, 4.78),
            (side*1.19, 0, 4.30)
        ], 0.125, "#c99780", "아래팔")

        fig.add_trace(surface_ellipsoid(
            (side*1.19, -0.02, 4.13),
            (0.15, 0.10, 0.22),
            "#c99780", "손", 0.95
        ))

    # 골반
    fig.add_trace(surface_ellipsoid(
        (0, 0, 4.10), (0.62, 0.38, 0.40),
        "#bd8b76", "골반", 0.90
    ))

    # 다리
    for side in [-1, 1]:
        add_tube(fig, [
            (side*0.32, 0, 3.98),
            (side*0.36, 0, 3.25),
            (side*0.37, 0, 2.65)
        ], 0.21, "#c99780", "허벅지")

        add_tube(fig, [
            (side*0.37, 0, 2.65),
            (side*0.37, 0, 1.80),
            (side*0.37, 0, 0.65)
        ], 0.15, "#c99780", "종아리")

        fig.add_trace(surface_ellipsoid(
            (side*0.37, -0.08, 0.38),
            (0.19, 0.31, 0.16),
            "#c99780", "발", 0.95
        ))


ORGAN_POINTS = {
    "뇌": (0, -0.40, 7.78),
    "심장": (0, -0.48, 5.60),
    "폐": (0, -0.47, 5.63),
    "간": (-0.34, -0.48, 4.91),
    "위": (0.34, -0.48, 4.82),
    "신장": (0.57, -0.05, 4.65),
    "소장": (0, -0.47, 4.12),
    "췌장": (0, -0.50, 4.75)
}


def body_scene():
    fig = go.Figure()
    body_mesh(fig, st.session_state.cut_open)

    for organ in ORGANS:
        if organ in st.session_state.removed:
            continue
        organ_shape(fig, organ, 0.95)

    # 장기 선택용 포인트. 3D 선택 기능을 지원하는 환경에서는 포인트를 선택할 수 있다.
    names = []
    xs, ys, zs = [], [], []
    for name, pos in ORGAN_POINTS.items():
        if name not in st.session_state.removed:
            names.append(name)
            xs.append(pos[0])
            ys.append(pos[1])
            zs.append(pos[2])

    fig.add_trace(go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode="markers+text",
        text=names,
        customdata=names,
        textposition="top center",
        textfont=dict(color="#f5fbff", size=11),
        marker=dict(
            size=7,
            color="#ffffff",
            opacity=0.78,
            line=dict(color="#16374d", width=2)
        ),
        name="장기 선택",
        hovertemplate="%{customdata} 선택<extra></extra>"
    ))

    fig.update_layout(
        title="HUMAN ANATOMY · INTERACTIVE 3D",
        height=720,
        margin=dict(l=0, r=0, t=45, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False, range=[-1.7, 1.7]),
            yaxis=dict(visible=False, range=[-0.9, 0.9]),
            zaxis=dict(visible=False, range=[0, 8.6]),
            aspectmode="manual",
            aspectratio=dict(x=0.72, y=0.42, z=1.55),
            camera=dict(eye=dict(x=1.7, y=-2.8, z=0.9))
        ),
        showlegend=False
    )
    return fig


# =========================================================
# 5. 장기 기능 저하 모델
# =========================================================

BASE_FUNCTIONS = {
    "산소 공급": 100,
    "혈액 순환": 100,
    "영양소 흡수": 100,
    "노폐물 배출": 100,
    "혈당 조절": 100,
    "신경계 조절": 100
}

ORGAN_IMPACTS = {
    "뇌": {"신경계 조절": 12},
    "심장": {"혈액 순환": 10, "산소 공급": 25},
    "폐": {"산소 공급": 10},
    "간": {"노폐물 배출": 20, "혈당 조절": 20},
    "위": {"영양소 흡수": 25},
    "신장": {"노폐물 배출": 15, "혈액 순환": 15},
    "소장": {"영양소 흡수": 10},
    "췌장": {"혈당 조절": 12}
}


def calculate_function_levels(removed):
    values = BASE_FUNCTIONS.copy()

    for organ in removed:
        for key, amount in ORGAN_IMPACTS.get(organ, {}).items():
            values[key] = max(0, values[key] - amount)

    return values


def removal_explanation(removed):
    if not removed:
        return [
            "현재 모든 장기가 정상적으로 기능하는 기본 상태입니다."
        ]

    explanations = []
    for organ in removed:
        explanations.append(f"**{organ} 기능 저하:** {ORGANS[organ]['problem']}")

    if "심장" in removed:
        explanations.append("혈액 순환이 저하되면 여러 장기에 산소와 영양분 공급이 줄어들 수 있습니다.")
    if "폐" in removed:
        explanations.append("산소 교환이 저하되면 뇌와 심장 등 산소를 많이 사용하는 조직이 영향을 받을 수 있습니다.")
    if "신장" in removed:
        explanations.append("수분과 전해질 균형 및 노폐물 배출이 어려워질 수 있습니다.")
    if "췌장" in removed:
        explanations.append("인슐린·글루카곤 분비 조절에 문제가 생기면 혈당 항상성이 흔들릴 수 있습니다.")

    return explanations


# =========================================================
# 6. 세포 및 소기관 데이터
# =========================================================

CELL_INFO = {
    "심근세포": {
        "description": "심근세포는 심장 근육을 구성하며, 수축과 이완을 통해 혈액을 이동시킵니다.",
        "features": ["가로무늬 구조", "풍부한 미토콘드리아", "사이원반을 통한 세포 연결"],
        "color": "#e45e75"
    },
    "신경세포": {
        "description": "신경세포는 전기적·화학적 신호를 전달하여 정보를 처리합니다.",
        "features": ["세포체", "수상돌기", "축삭", "시냅스"],
        "color": "#d9bd70"
    },
    "성상세포": {
        "description": "성상세포는 신경세포 주변 환경을 유지하고 신경계 기능을 지원합니다.",
        "features": ["별 모양 돌기", "신경세포 지원", "혈액뇌장벽 유지에 관여"],
        "color": "#d9a6c9"
    },
    "희소돌기아교세포": {
        "description": "중추신경계 축삭을 둘러싸는 수초 형성에 관여합니다.",
        "features": ["수초 형성", "축삭 보호", "신경 신호 전달 지원"],
        "color": "#b9a2e8"
    },
    "내피세포": {
        "description": "혈관 안쪽 표면을 덮으며 물질 교환과 혈관 기능에 관여합니다.",
        "features": ["혈관 내벽", "물질 이동 조절", "혈관 기능 유지"],
        "color": "#86c6c8"
    },
    "폐포세포": {
        "description": "폐포 벽을 구성하며 산소와 이산화탄소의 교환에 관여합니다.",
        "features": ["얇은 세포층", "넓은 교환 표면", "폐포 구조 유지"],
        "color": "#79c5e5"
    },
    "섬모상피세포": {
        "description": "섬모의 움직임으로 기도 내 점액과 입자를 이동시키는 데 기여합니다.",
        "features": ["섬모", "점액 이동", "기도 방어"],
        "color": "#79c5e5"
    },
    "대식세포": {
        "description": "이물질과 세포 잔해 등을 포식하는 면역세포입니다.",
        "features": ["포식 작용", "면역 신호 전달", "항원 제시"],
        "color": "#9fc98c"
    },
    "간세포": {
        "description": "대사, 저장, 단백질 합성 및 여러 물질의 처리에 관여합니다.",
        "features": ["풍부한 소포체", "글리코겐 저장", "다양한 효소"],
        "color": "#bd8755"
    },
    "쿠퍼세포": {
        "description": "간의 굴모세혈관에 존재하는 대식세포입니다.",
        "features": ["포식 작용", "면역 감시", "간 내 이물질 제거"],
        "color": "#bd8755"
    },
    "담관세포": {
        "description": "담관을 구성하며 담즙의 이동과 조절에 관여합니다.",
        "features": ["담관 구성", "담즙 이동", "상피세포"],
        "color": "#bd8755"
    },
    "위벽세포": {
        "description": "위산과 내인자를 분비하는 세포입니다.",
        "features": ["위산 분비", "미토콘드리아 풍부", "소화 과정 지원"],
        "color": "#e6a16d"
    },
    "주세포": {
        "description": "위에서 펩시노겐을 분비하며 단백질 소화 과정에 관여합니다.",
        "features": ["펩시노겐 분비", "분비 과립", "단백질 소화 지원"],
        "color": "#e6a16d"
    },
    "점액세포": {
        "description": "점액을 분비하여 위 점막을 보호합니다.",
        "features": ["점액 분비", "점막 보호", "상피 표면 유지"],
        "color": "#e6a16d"
    },
    "족세포": {
        "description": "신장 사구체의 여과 장벽을 구성하는 중요한 세포입니다.",
        "features": ["발돌기", "여과 틈새", "사구체 여과"],
        "color": "#a88bd2"
    },
    "세뇨관 상피세포": {
        "description": "세뇨관에서 물질의 재흡수와 분비를 수행합니다.",
        "features": ["막 수송 단백질", "미토콘드리아", "재흡수 기능"],
        "color": "#a88bd2"
    },
    "사구체 내피세포": {
        "description": "사구체 모세혈관의 안쪽을 구성하며 여과에 관여합니다.",
        "features": ["모세혈관 내벽", "여과 기능", "창문형 구조"],
        "color": "#a88bd2"
    },
    "흡수상피세포": {
        "description": "소장 내 영양소를 흡수하며 표면에 미세융모를 가지고 있습니다.",
        "features": ["미세융모", "세포막 수송", "영양소 흡수"],
        "color": "#e6c46d"
    },
    "베타세포": {
        "description": "혈당이 높아졌을 때 인슐린을 분비하는 췌장 세포입니다.",
        "features": ["인슐린 합성", "분비 과립", "혈당 감지"],
        "color": "#dfb17d"
    },
    "알파세포": {
        "description": "혈당이 낮아졌을 때 글루카곤을 분비하는 췌장 세포입니다.",
        "features": ["글루카곤 합성", "분비 과립", "혈당 조절"],
        "color": "#dfb17d"
    },
    "췌장 선방세포": {
        "description": "소화 효소를 포함하는 분비물을 만들어 소화 과정에 기여합니다.",
        "features": ["소화 효소 합성", "분비 과립", "단백질 합성"],
        "color": "#dfb17d"
    }
}

ORGANELLES = {
    "세포막": {
        "description": "세포의 경계를 형성하고 물질의 출입과 세포 간 신호 전달을 조절합니다.",
        "color": "#65c7d7"
    },
    "핵": {
        "description": "DNA를 보관하며 유전자 발현과 세포 활동 조절에 중요한 역할을 합니다.",
        "color": "#a88be8"
    },
    "핵소체": {
        "description": "리보솜을 구성하는 rRNA의 합성과 리보솜 소단위체 형성에 관여합니다.",
        "color": "#d9b8ff"
    },
    "미토콘드리아": {
        "description": "세포 호흡을 통해 ATP를 생산하는 데 중요한 역할을 합니다.",
        "color": "#e5a35d"
    },
    "거친면 소포체": {
        "description": "리보솜이 붙어 있으며 분비 단백질과 막 단백질의 합성에 관여합니다.",
        "color": "#65bcb2"
    },
    "매끈면 소포체": {
        "description": "지질 합성과 물질 대사, 일부 세포에서 칼슘 저장에 관여합니다.",
        "color": "#6daea5"
    },
    "골지체": {
        "description": "단백질과 지질을 가공하고 분류하여 목적지로 운반합니다.",
        "color": "#e2bd69"
    },
    "리보솜": {
        "description": "mRNA 정보를 바탕으로 아미노산을 연결해 단백질을 합성합니다.",
        "color": "#e8d58e"
    },
    "리소좀": {
        "description": "세포 내 불필요한 물질과 일부 세포 구성 요소를 분해합니다.",
        "color": "#9acb8a"
    },
    "세포골격": {
        "description": "세포의 형태를 유지하고 세포 내부 구조의 이동과 배열에 관여합니다.",
        "color": "#8eabc8"
    }
}


# =========================================================
# 7. 세포 3D 모델
# =========================================================

def cell_scene(cell_name, selected_organelle):
    info = CELL_INFO[cell_name]
    fig = go.Figure()

    # 세포막
    fig.add_trace(surface_ellipsoid(
        (0, 0, 0), (2.1, 1.55, 1.25),
        info["color"], "세포막", 0.22, resolution=48
    ))

    # 세포질은 배경에 가까운 반투명 구조
    fig.add_trace(surface_ellipsoid(
        (0, 0, 0), (1.94, 1.42, 1.12),
        "#75a9bd", "세포질", 0.07, resolution=36
    ))

    # 핵
    fig.add_trace(surface_ellipsoid(
        (-0.25, 0.02, 0.05), (0.63, 0.55, 0.57),
        ORGANELLES["핵"]["color"], "핵", 0.96
    ))

    # 핵소체
    fig.add_trace(surface_ellipsoid(
        (-0.12, -0.30, 0.24), (0.20, 0.17, 0.18),
        ORGANELLES["핵소체"]["color"], "핵소체", 1
    ))

    # 미토콘드리아: 여러 개의 곡선형 기관
    for i, (x, y, z) in enumerate([
        (0.88, 0.45, 0.22),
        (-0.95, -0.48, -0.30),
        (0.92, -0.55, -0.42),
        (-0.92, 0.55, 0.50)
    ]):
        def mito_fold(X, Y, Z, U, V):
            Z = Z + 0.045*np.sin(U*5)*np.sin(V*4)
            return X, Y, Z

        fig.add_trace(surface_ellipsoid(
            (x, y, z), (0.38, 0.17, 0.15),
            ORGANELLES["미토콘드리아"]["color"],
            "미토콘드리아", 0.98,
            deform=mito_fold, resolution=26
        ))

    # 소포체: 핵 주변을 감싸는 접힌 막
    for j in range(5):
        t = np.linspace(-1, 1, 80)
        x = -0.15 + 0.72*t
        y = 0.57 + j*0.095 + 0.11*np.sin(t*7 + j)
        z = 0.13 + 0.11*np.cos(t*8 + j)

        fig.add_trace(go.Scatter3d(
            x=x,
            y=np.full_like(x, y),
            z=z,
            mode="lines",
            line=dict(color=ORGANELLES["거친면 소포체"]["color"], width=5),
            name="소포체",
            hovertemplate="소포체<extra></extra>"
        ))

    # 골지체: 납작한 주머니가 층층이 쌓인 형태
    for j in range(5):
        t = np.linspace(-0.48, 0.48, 70)
        x = 0.25 + t
        y = np.full_like(t, -0.87 - j*0.045)
        z = -0.24 + 0.11*np.sin(t*4) + j*0.065

        fig.add_trace(go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode="lines",
            line=dict(color=ORGANELLES["골지체"]["color"], width=7),
            name="골지체",
            hovertemplate="골지체<extra></extra>"
        ))

    # 리보솜 점
    rng = np.random.default_rng(12)
    for _ in range(48):
        x = rng.uniform(-1.45, 1.45)
        y = rng.uniform(-1.05, 1.05)
        z = rng.uniform(-0.90, 0.90)

        fig.add_trace(go.Scatter3d(
            x=[x], y=[y], z=[z],
            mode="markers",
            marker=dict(size=2.8, color=ORGANELLES["리보솜"]["color"]),
            name="리보솜",
            hovertemplate="리보솜<extra></extra>"
        ))

    # 리소좀
    for x, y, z in [(1.25, 0.2, 0.2), (-1.15, -0.2, 0.35)]:
        fig.add_trace(surface_ellipsoid(
            (x, y, z), (0.13, 0.13, 0.13),
            ORGANELLES["리소좀"]["color"], "리소좀", 0.95
        ))

    # 선택된 소기관을 표시하는 강조 메시
    if selected_organelle == "미토콘드리아":
        fig.add_trace(surface_ellipsoid(
            (0.88, 0.45, 0.22), (0.43, 0.22, 0.20),
            "#fff2bd", "선택한 미토콘드리아", 0.28
        ))

    fig.update_layout(
        title=f"{cell_name} · CELL STRUCTURE",
        height=650,
        margin=dict(l=0, r=0, t=45, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False, range=[-2.4, 2.4]),
            yaxis=dict(visible=False, range=[-1.9, 1.9]),
            zaxis=dict(visible=False, range=[-1.6, 1.6]),
            aspectmode="data",
            camera=dict(eye=dict(x=1.8, y=-2.4, z=1.2))
        ),
        showlegend=False
    )
    return fig


# =========================================================
# 8. DNA 모델
# =========================================================

def dna_scene(sequence):
    sequence = sequence.upper()
    if not sequence:
        sequence = "ATGC"

    fig = go.Figure()

    colors = {
        "A": "#55c9a5",
        "T": "#e8a45e",
        "G": "#7d9ee7",
        "C": "#d78ac8"
    }

    t = np.linspace(0, 4*np.pi, max(80, len(sequence)*8))
    z = np.linspace(0, 8, len(t))

    fig.add_trace(go.Scatter3d(
        x=np.cos(t), y=np.sin(t), z=z,
        mode="lines",
        line=dict(color="#62d5c2", width=9),
        name="DNA 가닥 1"
    ))

    fig.add_trace(go.Scatter3d(
        x=-np.cos(t), y=-np.sin(t), z=z,
        mode="lines",
        line=dict(color="#b08be7", width=9),
        name="DNA 가닥 2"
    ))

    for i, base in enumerate(sequence):
        frac = i / max(len(sequence)-1, 1)
        ti = frac*4*np.pi
        zi = frac*8

        fig.add_trace(go.Scatter3d(
            x=[np.cos(ti), -np.cos(ti)],
            y=[np.sin(ti), -np.sin(ti)],
            z=[zi, zi],
            mode="lines",
            line=dict(color="#d6dce6", width=3),
            showlegend=False,
            hovertemplate=f"염기쌍 {i+1}<extra></extra>"
        ))

        fig.add_trace(go.Scatter3d(
            x=[np.cos(ti)],
            y=[np.sin(ti)],
            z=[zi],
            mode="markers+text",
            marker=dict(size=5, color=colors.get(base, "#ffffff")),
            text=[base],
            textposition="top center",
            textfont=dict(color="white", size=10),
            showlegend=False,
            hovertemplate=f"{i+1}번째 염기: {base}<extra></extra>"
        ))

    fig.update_layout(
        title="DNA DOUBLE HELIX",
        height=620,
        margin=dict(l=0, r=0, t=45, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(eye=dict(x=1.7, y=-2.2, z=0.8))
        ),
        showlegend=False
    )
    return fig


# =========================================================
# 9. 가상 유전 형질 실험
# =========================================================

TRAIT_INFO = {
    "eye": {
        "name": "눈동자 색",
        "dominant": "갈색 계열",
        "recessive": "밝은 색 계열",
        "alleles": ["B", "b"],
        "note": "실제 눈동자 색은 여러 유전자와 유전자 조절의 영향을 받습니다. 아래는 단순화한 멘델 유전 모형입니다."
    },
    "hair": {
        "name": "머리카락 색",
        "dominant": "짙은 색 계열",
        "recessive": "밝은 색 계열",
        "alleles": ["D", "d"],
        "note": "실제 머리카락 색 역시 여러 유전자와 색소 생성 과정의 영향을 받습니다."
    }
}


def genotype_result(a, b):
    if a.isupper() or b.isupper():
        return "우성 대립유전자가 포함된 모형"
    return "열성 대립유전자 조합 모형"


def punnett(a1, a2, b1, b2):
    return [
        [a1+b1, a1+b2],
        [a2+b1, a2+b2]
    ]


def trait_phenotype():
    eye = "갈색 계열" if (
        st.session_state.eye_allele_1 == "B"
        or st.session_state.eye_allele_2 == "B"
    ) else "밝은 색 계열"

    hair = "짙은 색 계열" if (
        st.session_state.hair_allele_1 == "D"
        or st.session_state.hair_allele_2 == "D"
    ) else "밝은 색 계열"

    return eye, hair


def avatar_scene():
    eye, hair = trait_phenotype()

    hair_color = "#4a3027" if hair == "짙은 색 계열" else "#d8b77c"
    eye_color = "#70452c" if eye == "갈색 계열" else "#82b7c7"

    fig = go.Figure()

    # 얼굴 형태
    fig.add_trace(surface_ellipsoid(
        (0, 0, 0), (0.78, 0.68, 1.02),
        "#d9ad94", "가상 인체 얼굴", 1.0, resolution=50
    ))

    # 머리카락 상단
    def hair_cap(X, Y, Z, U, V):
        return X*1.03, Y*1.03, Z*1.03

    fig.add_trace(surface_ellipsoid(
        (0, 0.01, 0.58), (0.81, 0.70, 0.54),
        hair_color, "머리카락", 0.98,
        deform=hair_cap, resolution=38
    ))

    # 눈
    for side in [-1, 1]:
        fig.add_trace(surface_ellipsoid(
            (side*0.29, -0.61, 0.15),
            (0.12, 0.07, 0.08),
            "#f5f3ed", "눈 흰자", 1
        ))
        fig.add_trace(surface_ellipsoid(
            (side*0.29, -0.68, 0.15),
            (0.055, 0.035, 0.055),
            eye_color, "홍채", 1
        ))
        fig.add_trace(surface_ellipsoid(
            (side*0.29, -0.71, 0.15),
            (0.025, 0.02, 0.03),
            "#17191e", "동공", 1
        ))

    # 코와 입
    fig.add_trace(surface_ellipsoid(
        (0, -0.68, -0.10), (0.10, 0.10, 0.22),
        "#c8947d", "코", 1
    ))

    fig.add_trace(go.Scatter3d(
        x=np.linspace(-0.16, 0.16, 30),
        y=np.full(30, -0.67),
        z=-0.42 + 0.025*np.sin(np.linspace(-np.pi, np.pi, 30)),
        mode="lines",
        line=dict(color="#985c5b", width=5),
        showlegend=False,
        hoverinfo="skip"
    ))

    fig.update_layout(
        title="VIRTUAL TRAIT AVATAR",
        height=550,
        margin=dict(l=0, r=0, t=45, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(eye=dict(x=1.4, y=-2.7, z=0.65))
        ),
        showlegend=False
    )
    return fig


# =========================================================
# 10. 약물 교육 데이터
# =========================================================

DRUGS = {
    "펜타닐(의료용 오피오이드)": {
        "group": "오피오이드계 진통제",
        "target": "오피오이드 수용체",
        "mechanism": "통증 신호 전달에 관여하는 오피오이드 수용체에 작용합니다.",
        "effects": ["통증 신호 전달 변화", "졸림 및 의식 저하 가능성", "호흡 억제 위험"],
        "risk": "호흡을 조절하는 뇌 기능을 억제할 수 있어 과량 노출은 생명을 위협하는 응급상황으로 이어질 수 있습니다.",
        "vision": "주의력 저하와 시각 처리 반응 저하를 추상적으로 표현합니다.",
        "level": "호흡 억제 위험"
    },
    "모르핀(의료용 오피오이드)": {
        "group": "오피오이드계 진통제",
        "target": "오피오이드 수용체",
        "mechanism": "중추신경계의 통증 신호 처리에 영향을 줍니다.",
        "effects": ["통증 완화", "졸림", "호흡 억제 위험"],
        "risk": "의료진의 감시가 필요한 약물이며 호흡 억제와 의존성 위험이 있습니다.",
        "vision": "각성도와 반응 속도 저하를 개념적으로 표현합니다.",
        "level": "호흡 억제 위험"
    },
    "진정·수면제 계열": {
        "group": "중추신경계 억제 관련 약물",
        "target": "GABA 등 신경전달 체계",
        "mechanism": "일부 약물은 억제성 신경전달을 강화해 중추신경계 활동을 낮춥니다.",
        "effects": ["졸림", "반응 속도 저하", "기억과 집중력 변화"],
        "risk": "다른 중추신경계 억제 물질과 함께 작용하면 위험이 커질 수 있습니다.",
        "vision": "초점 유지와 반응 속도 저하를 비미화적으로 표현합니다.",
        "level": "각성 저하"
    },
    "각성제 계열": {
        "group": "중추신경계 자극 관련 물질",
        "target": "도파민·노르에피네프린 신호 체계 등",
        "mechanism": "신경전달물질의 신호에 영향을 주어 각성 상태와 심혈관계 반응을 변화시킬 수 있습니다.",
        "effects": ["각성 변화", "심박수 증가 가능성", "불안 및 수면 장애 가능성"],
        "risk": "심혈관계 부담과 정신·신경계 부작용이 발생할 수 있습니다.",
        "vision": "주의 집중과 감각 처리의 변화를 중립적인 정보 화면으로 표현합니다.",
        "level": "심혈관계 부담"
    },
    "환각제 계열": {
        "group": "지각·인지에 영향을 주는 물질군",
        "target": "세로토닌 수용체 등",
        "mechanism": "감각 정보 처리와 지각에 관여하는 신경전달 체계에 영향을 줄 수 있습니다.",
        "effects": ["지각 변화 가능성", "판단력 변화", "불안 및 혼란 가능성"],
        "risk": "지각과 판단이 불안정해져 사고 위험이 커질 수 있습니다.",
        "vision": "환각을 재미있거나 매력적으로 재현하지 않고, 지각 정보의 신뢰도가 낮아지는 위험을 설명합니다.",
        "level": "지각·판단 변화"
    },
    "알코올": {
        "group": "중추신경계 억제 물질",
        "target": "여러 신경전달 체계",
        "mechanism": "억제성·흥분성 신경전달 체계에 영향을 주어 뇌 기능을 변화시킵니다.",
        "effects": ["판단력 저하", "균형감각 변화", "반응 속도 저하"],
        "risk": "운동 조절과 판단력이 떨어지며 다른 억제 물질과 함께 작용하면 위험이 커집니다.",
        "vision": "시각 초점과 반응 속도 저하를 단순화해 표현합니다.",
        "level": "운동·판단 저하"
    },
    "니코틴": {
        "group": "신경계 작용 물질",
        "target": "니코틴성 아세틸콜린 수용체",
        "mechanism": "신경전달에 관여하는 수용체에 작용합니다.",
        "effects": ["신경전달 변화", "심박수 변화", "의존성 위험"],
        "risk": "의존성이 생길 수 있으며 청소년의 뇌 발달에 특히 해로울 수 있습니다.",
        "vision": "시각 변화보다는 신경계와 심혈관계의 작용을 설명합니다.",
        "level": "의존성 위험"
    },
    "항히스타민제": {
        "group": "알레르기 치료제",
        "target": "히스타민 수용체",
        "mechanism": "히스타민 수용체를 차단하여 알레르기 증상을 완화합니다.",
        "effects": ["알레르기 증상 완화", "일부 종류에서 졸림", "주의력 변화 가능성"],
        "risk": "종류에 따라 졸림이나 주의력 저하가 나타날 수 있습니다.",
        "vision": "일부 약물에서 나타날 수 있는 졸림과 반응 저하를 표현합니다.",
        "level": "졸림 가능성"
    },
    "항우울제": {
        "group": "정신건강 치료제",
        "target": "세로토닌 등 신경전달 체계",
        "mechanism": "종류에 따라 신경전달물질의 작용과 신호 전달에 영향을 줍니다.",
        "effects": ["정신건강 증상 치료에 도움", "개인별 반응 차이", "부작용 가능성"],
        "risk": "효과와 부작용은 약물 종류와 개인에 따라 다르므로 의료진의 관리가 필요합니다.",
        "vision": "일반적인 시야 효과로 단순화할 수 없으며 치료 목적과 작용 원리를 설명합니다.",
        "level": "개인별 반응 차이"
    },
    "기관지확장제": {
        "group": "호흡기 치료제",
        "target": "기도 평활근 관련 수용체",
        "mechanism": "기도 평활근을 이완시켜 공기가 이동하는 통로를 넓히는 데 도움을 줍니다.",
        "effects": ["기도 확장", "호흡 흐름 개선", "일부 종류에서 심박수 변화"],
        "risk": "약물 종류에 따라 심박수 변화 등 부작용이 있을 수 있습니다.",
        "vision": "직접적인 시야 효과보다는 호흡 기능의 변화를 설명합니다.",
        "level": "호흡 기능 변화"
    },
    "인슐린": {
        "group": "호르몬 치료제",
        "target": "인슐린 수용체",
        "mechanism": "세포의 포도당 이용과 혈당 조절에 관여합니다.",
        "effects": ["혈당 조절", "포도당 이용 변화", "저혈당 위험"],
        "risk": "혈당이 지나치게 낮아지는 경우 의식과 신경계 기능에 문제가 생길 수 있습니다.",
        "vision": "혈당 변화에 따른 신경계 기능 저하 가능성을 교육적으로 설명합니다.",
        "level": "혈당 균형"
    },
    "항생제": {
        "group": "세균 감염 치료제",
        "target": "세균의 생존·증식 과정",
        "mechanism": "세균의 세포벽 합성이나 단백질 합성 등 특정 과정을 방해합니다.",
        "effects": ["세균 감염 치료", "약물별 표적 차이", "내성 문제"],
        "risk": "바이러스 감염에는 효과가 없으며 불필요한 사용은 항생제 내성을 높일 수 있습니다.",
        "vision": "일반적인 시각 변화는 없습니다. 세균 세포의 표적 작용을 설명합니다.",
        "level": "세균 표적 작용"
    },
    "항염증제": {
        "group": "염증·통증 조절 약물",
        "target": "염증 매개 물질 생성 경로",
        "mechanism": "종류에 따라 염증 반응에 관여하는 물질의 생성을 억제합니다.",
        "effects": ["염증 반응 변화", "통증 완화", "약물별 부작용"],
        "risk": "종류에 따라 위장관이나 신장 등에 영향을 줄 수 있습니다.",
        "vision": "일반적인 시각 변화보다는 염증 반응의 변화를 설명합니다.",
        "level": "염증 반응 조절"
    },
    "국소마취제": {
        "group": "의료용 마취제",
        "target": "전압 개폐성 나트륨 통로",
        "mechanism": "신경세포의 활동전위 발생과 전도에 영향을 주어 특정 부위의 감각 전달을 차단합니다.",
        "effects": ["특정 부위 감각 전달 감소", "통증 신호 전달 차단"],
        "risk": "사용 부위와 약물에 따라 의료적 주의가 필요합니다.",
        "vision": "시야 변화가 아니라 특정 부위 감각 신호 전달의 변화를 설명합니다.",
        "level": "감각 전달 차단"
    }
}


# =========================================================
# 11. 비미화적 1인칭 시야 모형
# =========================================================

def first_person_view(drug_name):
    info = DRUGS[drug_name]
    fig = go.Figure()

    # 시야 테두리
    theta = np.linspace(0, 2*np.pi, 160)
    fig.add_trace(go.Scatter(
        x=np.cos(theta), y=np.sin(theta),
        mode="lines",
        line=dict(color="#8bd7e8", width=3),
        showlegend=False,
        hoverinfo="skip"
    ))

    # 중심 응시점
    fig.add_trace(go.Scatter(
        x=[0], y=[0],
        mode="markers",
        marker=dict(size=9, color="#e9f6ff"),
        showlegend=False,
        hoverinfo="skip"
    ))

    if "호흡 억제" in info["level"] or "각성 저하" in info["level"]:
        # 시야의 흐림/주의 저하를 나타내는 중립적 동심원
        for r in [0.25, 0.45, 0.65, 0.85]:
            fig.add_shape(
                type="circle",
                x0=-r, y0=-r, x1=r, y1=r,
                line=dict(color="rgba(160,180,195,0.38)", width=2)
            )

        fig.add_annotation(
            x=0, y=-0.75,
            text="주의력·반응 저하 가능성",
            showarrow=False,
            font=dict(color="#d7e4ee", size=12)
        )

    elif "심혈관계" in info["level"]:
        for r in [0.35, 0.55, 0.75]:
            fig.add_shape(
                type="circle",
                x0=-r, y0=-r, x1=r, y1=r,
                line=dict(color="rgba(220,160,145,0.38)", width=2)
            )
        fig.add_annotation(
            x=0, y=-0.75,
            text="심박·각성 변화 가능성",
            showarrow=False,
            font=dict(color="#d7e4ee", size=12)
        )

    else:
        # 직접적인 시야 변화가 일반화되지 않는 경우
        fig.add_annotation(
            x=0, y=0.25,
            text="일반적인 시야 변화로<br>표현하기 어려움",
            showarrow=False,
            font=dict(color="#d7e4ee", size=14)
        )
        fig.add_annotation(
            x=0, y=-0.45,
            text="약물의 실제 작용 부위와 생리적 변화를 확인하세요.",
            showarrow=False,
            font=dict(color="#9fb8cb", size=10)
        )

    fig.update_layout(
        title="FIRST-PERSON VISUAL FUNCTION MODEL",
        height=470,
        margin=dict(l=10, r=10, t=45, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#071321",
        xaxis=dict(visible=False, range=[-1.08, 1.08], scaleanchor="y"),
        yaxis=dict(visible=False, range=[-1.08, 1.08]),
        showlegend=False
    )
    return fig


# =========================================================
# 12. DNA 염기서열 도구
# =========================================================

def sequence_stats(sequence):
    sequence = sequence.upper()
    if not sequence or any(x not in "ATGC" for x in sequence):
        return None

    counts = {b: sequence.count(b) for b in "ATGC"}
    gc = (counts["G"] + counts["C"]) / len(sequence) * 100
    return counts, gc


def mutate_one(sequence):
    seq = list(sequence)
    if not seq:
        return sequence

    idx = random.randrange(len(seq))
    old = seq[idx]
    seq[idx] = random.choice([x for x in "ATGC" if x != old])
    return "".join(seq)


# =========================================================
# 13. 공통 제목 및 탐색 메뉴
# =========================================================

st.markdown("""
<div style="padding: 10px 0 20px 0;">
    <div class="eyebrow">INTERACTIVE LIFE SCIENCE LABORATORY</div>
    <h1 style="font-size:2.55rem; margin:0;">BioSphere 3D</h1>
    <p style="color:#9fb6c9; margin-top:5px;">
        인체에서 장기, 세포, 소기관, DNA까지 이어지는 생명과학 탐구
    </p>
</div>
""", unsafe_allow_html=True)

STAGES = {
    "body": "① 인체·장기 탐색",
    "organ": "② 장기 확대",
    "cell": "③ 세포와 소기관",
    "dna": "④ 핵과 DNA",
    "traits": "⑤ 유전 형질 실험",
    "drug": "⑥ 약물의 생리적 작용"
}

with st.sidebar:
    st.markdown("## 🧬 탐구실")
    st.caption("하나의 인체를 단계적으로 확대합니다.")

    for key, label in STAGES.items():
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.stage = key
            st.rerun()

    st.divider()
    st.markdown("### 현재 탐색 경로")

    route = [
        "인체",
        st.session_state.organ,
        st.session_state.cell,
        "세포핵",
        "DNA"
    ]

    for i, item in enumerate(route):
        st.write(f"{'●' if i == 0 else '↳'} {item}")

    st.divider()
    st.caption("3D 장면은 마우스 드래그로 회전하고 휠로 확대할 수 있습니다.")


# =========================================================
# 14. 인체 탐색 화면
# =========================================================

if st.session_state.stage == "body":

    st.markdown('<span class="stage-pill">STAGE 01 · HUMAN ANATOMY</span>', unsafe_allow_html=True)
    st.header("인체를 관찰하고 장기를 선택하세요.")

    col_model, col_control = st.columns([1.65, 1])

    with col_model:
        st.session_state.cut_open = st.toggle(
            "메스 절개 모드",
            value=st.session_state.cut_open
        )

        if st.session_state.cut_open:
            st.success("몸통 앞면이 열린 상태입니다. 내부 장기를 관찰할 수 있습니다.")
        else:
            st.info("절개 모드를 켜면 몸통 내부 구조가 드러납니다.")

        fig = body_scene()
        selected_event = st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": True},
            on_select="rerun",
            selection_mode="points",
            key="body_3d_select"
        )

        # Plotly 선택 이벤트가 전달되는 환경에서는 선택한 장기로 이동
        try:
            points = selected_event.selection.points
            if points:
                selected_name = points[0].get("customdata")
                if selected_name in ORGANS:
                    st.session_state.organ = selected_name
                    st.session_state.stage = "organ"
                    st.rerun()
        except Exception:
            pass

        st.caption(
            "장기 위치의 선택 점을 선택하거나 오른쪽 장기 목록에서 장기를 선택하세요. "
            "이 모형은 교육용 3D 해부 구조입니다."
        )

    with col_control:
        st.markdown("### 장기 선택")
        st.write("확대하고 싶은 장기를 선택하세요.")

        for organ in ORGANS:
            if organ in st.session_state.removed:
                continue

            if st.button(
                f"◉ {organ} · {ORGANS[organ]['system']}",
                key=f"choose_{organ}",
                use_container_width=True
            ):
                st.session_state.organ = organ
                st.session_state.stage = "organ"
                st.rerun()

        st.divider()
        st.markdown("### 메스 절개 및 적출 실험")

        st.write(
            "메스 절개 모드를 켠 뒤 장기를 선택하고, 적출 실험을 진행할 수 있습니다."
        )

        if st.session_state.organ not in st.session_state.removed:
            if st.button(
                f"선택 장기 적출 실험: {st.session_state.organ}",
                use_container_width=True
            ):
                st.session_state.removed.append(st.session_state.organ)
                st.rerun()

        if st.session_state.removed:
            st.warning("현재 기능이 제거된 것으로 설정된 장기")
            for item in st.session_state.removed:
                st.write(f"• {item}")

            if st.button("모든 장기 기능 복원"):
                st.session_state.removed = []
                st.rerun()

    st.divider()
    st.subheader("장기 기능 변화")

    levels = calculate_function_levels(st.session_state.removed)

    metric_cols = st.columns(3)
    for i, (name, value) in enumerate(levels.items()):
        with metric_cols[i % 3]:
            st.metric(name, f"{value}%")

    chart = px.bar(
        x=list(levels.keys()),
        y=list(levels.values()),
        labels={"x": "생리 기능", "y": "상대적 기능 지표"},
        range_y=[0, 100],
        color=list(levels.values()),
        color_continuous_scale=["#d95f68", "#e6c36b", "#54c5a5"]
    )
    chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#dce9f5",
        coloraxis_showscale=False,
        height=330
    )
    st.plotly_chart(chart, use_container_width=True)

    st.markdown("### 장기 기능 변화에 대한 설명")
    for explanation in removal_explanation(st.session_state.removed):
        st.markdown(f"- {explanation}")

    st.caption(
        "기능 지표는 장기 기능 저하의 개념을 설명하기 위한 가상 점수입니다. "
        "실제 인체의 생존 가능성이나 임상 수치를 계산하는 모델은 아닙니다."
    )


# =========================================================
# 15. 장기 확대 화면
# =========================================================

elif st.session_state.stage == "organ":

    organ = st.session_state.organ
    data = ORGANS[organ]

    st.markdown('<span class="stage-pill">STAGE 02 · ORGAN EXPLORATION</span>', unsafe_allow_html=True)
    st.header(f"{organ} 확대 관찰")

    col_model, col_info = st.columns([1.45, 1])

    with col_model:
        fig = go.Figure()
        organ_shape(fig, organ)

        fig.update_layout(
            title=f"{organ.upper()} · 3D ORGAN MODEL",
            height=650,
            margin=dict(l=0, r=0, t=45, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            scene=dict(
                bgcolor="rgba(0,0,0,0)",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                aspectmode="data",
                camera=dict(eye=dict(x=1.6, y=-2.1, z=1.0))
            ),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_info:
        st.markdown(f"### {organ}")
        st.markdown(f"**기관계:** {data['system']}")

        st.markdown("#### 주요 기능")
        st.write(data["function"])

        st.markdown("#### 구조적 특징")
        st.write(data["structure"])

        st.markdown("#### 기능 저하 시")
        st.warning(data["problem"])

        st.markdown("#### 대표 구성 세포")
        for cell in data["cells"]:
            st.write(f"• {cell}")

        if organ in st.session_state.removed:
            st.error("이 장기는 현재 적출 실험 상태입니다.")
        else:
            if st.button("메스로 이 장기 적출하기", use_container_width=True):
                st.session_state.removed.append(organ)
                st.session_state.stage = "body"
                st.rerun()

        if st.button("🔬 이 장기의 세포로 확대", use_container_width=True):
            st.session_state.cell = data["main_cell"]
            st.session_state.stage = "cell"
            st.rerun()

        if st.button("← 인체 전체로 돌아가기", use_container_width=True):
            st.session_state.stage = "body"
            st.rerun()


# =========================================================
# 16. 세포 및 소기관 탐색
# =========================================================

elif st.session_state.stage == "cell":

    organ = st.session_state.organ
    data = ORGANS[organ]

    st.markdown('<span class="stage-pill">STAGE 03 · CELL & ORGANELLES</span>', unsafe_allow_html=True)
    st.header(f"{organ}을 구성하는 세포")

    if st.session_state.cell not in data["cells"]:
        st.session_state.cell = data["main_cell"]

    cell = st.selectbox(
        "관찰할 세포",
        data["cells"],
        index=data["cells"].index(st.session_state.cell)
    )
    st.session_state.cell = cell

    cell_info = CELL_INFO[cell]

    col_model, col_info = st.columns([1.45, 1])

    with col_model:
        st.plotly_chart(
            cell_scene(cell, st.session_state.organelle),
            use_container_width=True,
            config={"displayModeBar": True}
        )

    with col_info:
        st.markdown(f"### {cell}")
        st.write(cell_info["description"])

        st.markdown("#### 세포의 주요 특징")
        for feature in cell_info["features"]:
            st.write(f"• {feature}")

        st.divider()
        st.markdown("### 소기관 선택")

        organelle_names = list(ORGANELLES.keys())
        selected_organelle = st.selectbox(
            "3D로 관찰할 소기관",
            organelle_names,
            index=organelle_names.index(st.session_state.organelle)
        )
        st.session_state.organelle = selected_organelle

        st.markdown(f"#### {selected_organelle}")
        st.write(ORGANELLES[selected_organelle]["description"])

        if selected_organelle == "핵":
            if st.button("🧬 핵 내부의 DNA 확대", use_container_width=True):
                st.session_state.stage = "dna"
                st.rerun()

        if st.button("← 장기 단계로 돌아가기", use_container_width=True):
            st.session_state.stage = "organ"
            st.rerun()

    st.divider()
    st.markdown("### 세포 소기관 기능 비교")

    organelle_df = pd.DataFrame([
        {"소기관": k, "주요 기능": v["description"]}
        for k, v in ORGANELLES.items()
    ])
    st.dataframe(organelle_df, use_container_width=True, hide_index=True)


# =========================================================
# 17. DNA 탐구 화면
# =========================================================

elif st.session_state.stage == "dna":

    st.markdown('<span class="stage-pill">STAGE 04 · DNA EXPLORATION</span>', unsafe_allow_html=True)
    st.header("세포핵 속 DNA 구조와 염기서열")

    st.write(
        f"탐색 경로: 인체 → {st.session_state.organ} → "
        f"{st.session_state.cell} → 핵 → DNA"
    )

    col_model, col_tools = st.columns([1.35, 1])

    with col_model:
        st.plotly_chart(
            dna_scene(st.session_state.dna_sequence),
            use_container_width=True,
            config={"displayModeBar": True}
        )

    with col_tools:
        st.markdown("### 염기서열 탐구")

        sequence = st.text_area(
            "DNA 염기서열",
            value=st.session_state.dna_sequence,
            height=100,
            help="A, T, G, C로 구성된 짧은 예시 서열입니다."
        ).upper().replace(" ", "").replace("\n", "")

        if sequence and all(x in "ATGC" for x in sequence):
            st.session_state.dna_sequence = sequence
            stats = sequence_stats(sequence)
            counts, gc = stats

            a, b = st.columns(2)
            a.metric("염기 개수", len(sequence))
            b.metric("GC 비율", f"{gc:.1f}%")

            chart = px.bar(
                x=list(counts.keys()),
                y=list(counts.values()),
                labels={"x": "염기", "y": "개수"},
                color=list(counts.keys()),
                color_discrete_map={
                    "A": "#55c9a5",
                    "T": "#e8a45e",
                    "G": "#7d9ee7",
                    "C": "#d78ac8"
                }
            )
            chart.update_layout(
                height=250,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#dce9f5",
                showlegend=False
            )
            st.plotly_chart(chart, use_container_width=True)

        else:
            st.error("염기서열에는 A, T, G, C만 입력할 수 있습니다.")

        st.markdown("### 간편 염기 변경")

        if st.button("염기 하나 무작위 변경"):
            st.session_state.dna_sequence = mutate_one(st.session_state.dna_sequence)
            st.rerun()

        if st.button("기본 염기서열 복원"):
            st.session_state.dna_sequence = "ATGCGTACGTTAGCGATCGT"
            st.rerun()

        st.info(
            "염기서열의 변화는 단백질 합성과 유전자 발현에 영향을 줄 수 있습니다. "
            "다만 모든 염기 변화가 형질 변화로 이어지는 것은 아닙니다."
        )

    st.divider()
    st.markdown("### DNA에서 형질까지")

    flow_cols = st.columns(4)
    flow = [
        ("DNA 염기서열", "유전 정보의 저장"),
        ("전사", "DNA 정보를 RNA로 전달"),
        ("번역", "RNA 정보를 바탕으로 단백질 합성"),
        ("형질", "단백질과 세포 기능 등이 표현형에 기여")
    ]

    for i, (title, desc) in enumerate(flow):
        with flow_cols[i]:
            st.markdown(f"""
            <div class="bio-panel">
                <div class="eyebrow">STEP {i+1}</div>
                <b>{title}</b>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.warning(
        "이 화면의 염기서열은 교육용 예시입니다. "
        "임의의 짧은 서열을 바꾸는 것만으로 실제 사람의 눈동자나 머리카락 색이 바뀌는 것은 아닙니다. "
        "형질 실험은 다음 메뉴의 단순화된 유전 모형에서 별도로 진행합니다."
    )

    if st.button("유전 형질 실험으로 이동"):
        st.session_state.stage = "traits"
        st.rerun()


# =========================================================
# 18. 유전 형질 실험
# =========================================================

elif st.session_state.stage == "traits":

    st.markdown('<span class="stage-pill">STAGE 05 · GENETIC TRAIT LAB</span>', unsafe_allow_html=True)
    st.header("대립유전자 조합과 가상 형질 변화")

    st.info(
        "이 실험은 멘델 유전의 기본 원리를 보여주기 위한 단순화된 가상 모형입니다. "
        "실제 눈동자와 머리카락 색은 여러 유전자와 환경의 영향을 받습니다."
    )

    col_controls, col_avatar = st.columns([1, 1.2])

    with col_controls:
        st.markdown("### 눈동자 색 모형")

        e1 = st.selectbox(
            "첫 번째 대립유전자",
            ["B", "b"],
            index=["B", "b"].index(st.session_state.eye_allele_1),
            key="eye1"
        )
        e2 = st.selectbox(
            "두 번째 대립유전자",
            ["B", "b"],
            index=["B", "b"].index(st.session_state.eye_allele_2),
            key="eye2"
        )

        st.session_state.eye_allele_1 = e1
        st.session_state.eye_allele_2 = e2

        st.markdown("### 머리카락 색 모형")

        h1 = st.selectbox(
            "첫 번째 대립유전자 ",
            ["D", "d"],
            index=["D", "d"].index(st.session_state.hair_allele_1),
            key="hair1"
        )
        h2 = st.selectbox(
            "두 번째 대립유전자 ",
            ["D", "d"],
            index=["D", "d"].index(st.session_state.hair_allele_2),
            key="hair2"
        )

        st.session_state.hair_allele_1 = h1
        st.session_state.hair_allele_2 = h2

        eye, hair = trait_phenotype()

        st.divider()
        st.markdown("### 현재 가상 형질")
        st.metric("눈동자 색 모형", eye)
        st.metric("머리카락 색 모형", hair)

    with col_avatar:
        st.plotly_chart(
            avatar_scene(),
            use_container_width=True,
            config={"displayModeBar": True}
        )

    st.divider()
    st.markdown("### 유전 조합표")

    p1, p2 = st.columns(2)

    with p1:
        st.markdown("#### 눈동자 색 대립유전자")
        eye_table = punnett("B", "b", e1, e2)
        eye_df = pd.DataFrame(
            eye_table,
            index=["B", "b"],
            columns=[e1, e2]
        )
        st.table(eye_df)

    with p2:
        st.markdown("#### 머리카락 색 대립유전자")
        hair_table = punnett("D", "d", h1, h2)
        hair_df = pd.DataFrame(
            hair_table,
            index=["D", "d"],
            columns=[h1, h2]
        )
        st.table(hair_df)

    st.markdown("### 유전 원리 이해하기")
    st.write(
        "각 부모는 자녀에게 대립유전자 하나씩을 전달합니다. "
        "두 대립유전자의 조합에 따라 단순화된 모형에서 우성 또는 열성 표현형을 구분할 수 있습니다."
    )

    st.caption(
        "이 가상 얼굴은 유전학 개념을 시각적으로 설명하기 위한 캐릭터입니다. "
        "실제 사람의 외모를 예측하거나 유전자 편집 결과를 재현하는 도구가 아닙니다."
    )


# =========================================================
# 19. 약물의 생리적 작용
# =========================================================

elif st.session_state.stage == "drug":

    st.markdown('<span class="stage-pill">STAGE 06 · PHARMACOLOGY</span>', unsafe_allow_html=True)
    st.header("약물이 인체와 신경계에 미치는 영향")

    st.info(
        "약물의 작용을 학습하기 위한 의학 교육 화면입니다. "
        "실제 투여 방법이나 용량을 안내하지 않으며, 약물의 효과를 미화하거나 체험하도록 재현하지 않습니다."
    )

    drug = st.selectbox(
        "관찰할 약물 또는 약물 계열",
        list(DRUGS.keys()),
        index=list(DRUGS.keys()).index(st.session_state.drug)
        if st.session_state.drug in DRUGS else 0
    )
    st.session_state.drug = drug

    info = DRUGS[drug]

    st.markdown(f"## {drug}")
    st.markdown(f"**분류:** {info['group']}")

    col_info, col_view = st.columns([1, 1])

    with col_info:
        st.markdown("### 작용 원리")
        st.write(info["mechanism"])

        st.markdown("### 주요 작용 부위")
        st.write(info["target"])

        st.markdown("### 생리적 영향")
        for effect in info["effects"]:
            st.write(f"• {effect}")

        st.markdown("### 주의할 점")
        st.warning(info["risk"])

    with col_view:
        st.markdown("### 가상 1인칭 시야")

        st.write(
            "실제 환각이나 약물 경험을 재현하는 것이 아니라, "
            "주의력·반응 속도·시각 처리의 저하 가능성을 중립적인 시각 자료로 설명합니다."
        )

        if st.button("가상 시야 모델 보기", use_container_width=True):
            st.session_state.drug_view = True
            st.rerun()

        if st.session_state.drug_view:
            st.plotly_chart(
                first_person_view(drug),
                use_container_width=True,
                config={"displayModeBar": False}
            )

            st.caption(info["vision"])

            if st.button("시야 모델 닫기"):
                st.session_state.drug_view = False
                st.rerun()

    st.divider()
    st.markdown("### 약물 작용과 인체의 관계")

    drug_path = [
        ("약물의 표적", info["target"]),
        ("세포 반응", "수용체 또는 세포 내 신호 전달 변화"),
        ("기관 반응", "신경계·호흡계·심혈관계 등 기관 기능 변화"),
        ("전신 반응", "여러 기관의 상호작용에 따른 생리적 변화")
    ]

    cols = st.columns(4)
    for i, (title, desc) in enumerate(drug_path):
        with cols[i]:
            st.markdown(f"""
            <div class="bio-panel">
                <div class="eyebrow">LEVEL {i+1}</div>
                <b>{title}</b>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    if "호흡 억제" in info["risk"] or "호흡" in info["risk"]:
        st.error(
            "중요: 오피오이드 등 일부 물질은 호흡을 심각하게 억제할 수 있습니다. "
            "의식이 떨어지거나 호흡이 비정상적인 사람을 발견하면 즉시 119에 연락해야 합니다."
        )

    st.caption(
        "약물 반응은 약물 종류, 개인의 건강 상태, 다른 약물과의 상호작용 등에 따라 다릅니다. "
        "이 모형은 임상적 예측이나 실제 복용·투여를 위한 도구가 아닙니다."
    )


# =========================================================
# 20. 하단
# =========================================================

st.divider()

st.markdown("""
<div style="text-align:center; padding:18px 0; color:#7892a9;">
    <b>BioSphere 3D</b> · Interactive Biology Learning Environment
    <br>
    <small>
    Educational visualization only · Not a diagnostic or treatment simulator
    </small>
</div>
""", unsafe_allow_html=True)
