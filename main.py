
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import math
import time

# ============================================================
# 1. 기본 설정
# ============================================================

st.set_page_config(
    page_title="BIOLOGY 3D LAB",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: #0b1020;
    color: #e5e7eb;
}
section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #263247;
}
.block-container {
    padding-top: 1.5rem;
    max-width: 1600px;
}
h1, h2, h3 {
    color: #f8fafc !important;
}
div[data-testid="stMetric"] {
    background: #151f33;
    border: 1px solid #263750;
    padding: 15px;
    border-radius: 12px;
}
div.stButton > button {
    border-radius: 9px;
    border: 1px solid #334155;
    background: #17243a;
    color: #e5e7eb;
    min-height: 42px;
}
div.stButton > button:hover {
    border-color: #38bdf8;
    color: #38bdf8;
}
.bio-panel {
    background: #151f33;
    border: 1px solid #293950;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 12px;
}
.small-muted {
    color: #94a3b8;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 2. 상태 관리
# ============================================================

DEFAULTS = {
    "stage": "body",
    "selected_organ": "brain",
    "selected_cell": "neuron",
    "selected_organelle": "nucleus",
    "selected_gene": "OCA2",
    "incision": False,
    "removed_organs": [],
    "edited_traits": {},
    "drug_selected": "진통제",
    "drug_effect": False,
    "drug_visual": "정상",
    "gene_edits": {},
    "experiment_history": [],
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def reset_experiment():
    for key, value in DEFAULTS.items():
        st.session_state[key] = value


# ============================================================
# 3. 생명과학 데이터
# ============================================================

ORGANS = {
    "brain": {
        "name": "뇌",
        "position": (0, -0.10, 5.25),
        "color": "#e6a5a5",
        "function": "감각 정보 처리, 운동 조절, 기억, 학습, 감정 및 항상성 조절",
        "cells": ["뉴런", "성상교세포", "희소돌기아교세포", "미세아교세포"],
        "cell_type": "neuron",
        "removed": "신경계의 통합 기능이 심각하게 손상되어 의식, 운동, 감각 및 생명 유지 기능에 큰 문제가 발생합니다.",
        "system": "신경계",
        "importance": 100
    },
    "heart": {
        "name": "심장",
        "position": (0.16, -0.15, 3.65),
        "color": "#d94b5b",
        "function": "수축과 이완을 반복하여 혈액을 온몸으로 순환시키는 펌프 역할",
        "cells": ["심근세포", "내피세포", "섬유아세포"],
        "cell_type": "cardiac",
        "removed": "혈액 순환이 유지되지 못해 산소와 영양분 공급 및 노폐물 운반에 심각한 장애가 생깁니다.",
        "system": "순환계",
        "importance": 100
    },
    "left_lung": {
        "name": "왼쪽 폐",
        "position": (-0.38, -0.10, 3.65),
        "color": "#e99a9a",
        "function": "폐포에서 산소와 이산화탄소를 교환합니다.",
        "cells": ["제1형 폐포세포", "제2형 폐포세포", "섬모상피세포"],
        "cell_type": "alveolar",
        "removed": "가스 교환 능력이 감소하여 혈액의 산소 공급과 이산화탄소 배출에 문제가 생깁니다.",
        "system": "호흡계",
        "importance": 55
    },
    "right_lung": {
        "name": "오른쪽 폐",
        "position": (0.48, -0.10, 3.65),
        "color": "#e99a9a",
        "function": "폐포에서 산소와 이산화탄소를 교환합니다.",
        "cells": ["제1형 폐포세포", "제2형 폐포세포", "섬모상피세포"],
        "cell_type": "alveolar",
        "removed": "가스 교환 능력이 감소합니다. 남은 폐의 보상 능력과 건강 상태에 따라 영향이 달라집니다.",
        "system": "호흡계",
        "importance": 55
    },
    "liver": {
        "name": "간",
        "position": (0.28, -0.12, 3.05),
        "color": "#9d654d",
        "function": "영양소 대사, 해독, 담즙 생성, 혈장 단백질 합성 및 글리코젠 저장",
        "cells": ["간세포", "쿠퍼세포", "간성상세포", "내피세포"],
        "cell_type": "hepatocyte",
        "removed": "대사와 해독, 단백질 합성, 담즙 생성 등 다양한 기능이 상실됩니다.",
        "system": "소화·대사계",
        "importance": 100
    },
    "stomach": {
        "name": "위",
        "position": (-0.12, -0.12, 2.90),
        "color": "#d88b86",
        "function": "음식물을 저장하고 위액과 섞어 소화 과정을 진행합니다.",
        "cells": ["위벽세포", "주세포", "점액분비세포"],
        "cell_type": "epithelial",
        "removed": "음식물 저장과 초기 소화 기능에 변화가 생기며 영양 섭취 방식에도 영향을 줍니다.",
        "system": "소화계",
        "importance": 45
    },
    "kidney": {
        "name": "신장",
        "position": (0.52, -0.03, 2.85),
        "color": "#a94f59",
        "function": "혈액을 여과하고 노폐물을 배출하며 수분과 전해질 균형을 조절합니다.",
        "cells": ["족세포", "세뇨관 상피세포", "사구체 내피세포"],
        "cell_type": "podocyte",
        "removed": "체액과 전해질 조절, 노폐물 배설 기능에 문제가 생깁니다.",
        "system": "비뇨계",
        "importance": 90
    },
    "intestine": {
        "name": "소장",
        "position": (0.03, -0.15, 2.38),
        "color": "#d8a16e",
        "function": "소화된 영양소 대부분을 흡수합니다.",
        "cells": ["장상피세포", "배상세포", "장내분비세포"],
        "cell_type": "epithelial",
        "removed": "영양소와 수분 흡수에 문제가 발생합니다.",
        "system": "소화계",
        "importance": 75
    },
    "pancreas": {
        "name": "췌장",
        "position": (0.0, -0.05, 2.75),
        "color": "#e0b27c",
        "function": "소화 효소와 혈당 조절 호르몬을 분비합니다.",
        "cells": ["췌장 선방세포", "베타세포", "알파세포"],
        "cell_type": "beta",
        "removed": "소화 효소 분비와 혈당 조절에 문제가 생깁니다.",
        "system": "소화·내분비계",
        "importance": 80
    },
}

CELLS = {
    "neuron": {
        "name": "뉴런(신경세포)",
        "function": "전기적 신호와 화학적 신호를 이용하여 정보를 전달합니다.",
        "features": "세포체, 가지돌기, 축삭, 축삭 말단으로 구성됩니다.",
        "role": "신경계의 정보 전달"
    },
    "cardiac": {
        "name": "심근세포",
        "function": "규칙적인 수축과 이완으로 혈액을 이동시킵니다.",
        "features": "줄무늬가 있고 가지를 치며 사이원반으로 연결됩니다.",
        "role": "심장의 수축"
    },
    "alveolar": {
        "name": "폐포세포",
        "function": "폐포의 얇은 벽을 구성하여 기체 교환에 관여합니다.",
        "features": "제1형은 얇은 교환 표면을 만들고 제2형은 계면활성제를 분비합니다.",
        "role": "산소와 이산화탄소 교환"
    },
    "hepatocyte": {
        "name": "간세포",
        "function": "영양소 대사와 해독, 단백질 합성 등을 담당합니다.",
        "features": "풍부한 소포체와 미토콘드리아, 글리코젠 저장 과립을 가집니다.",
        "role": "대사와 해독"
    },
    "podocyte": {
        "name": "족세포",
        "function": "신장의 사구체 여과 장벽을 구성합니다.",
        "features": "발돌기가 모세혈관을 감싸며 여과 틈새를 형성합니다.",
        "role": "혈액 여과"
    },
    "epithelial": {
        "name": "상피세포",
        "function": "표면을 덮고 물질 흡수와 분비, 보호 기능을 담당합니다.",
        "features": "세포들이 서로 밀착하여 층을 형성합니다.",
        "role": "보호와 물질 이동"
    },
    "beta": {
        "name": "췌장 베타세포",
        "function": "혈당이 높아지면 인슐린을 분비합니다.",
        "features": "분비 과립과 발달한 소포체, 골지체를 가집니다.",
        "role": "혈당 조절"
    }
}

ORGANELLES = {
    "nucleus": {
        "name": "핵",
        "function": "DNA를 보관하며 유전자 발현을 조절합니다.",
        "detail": "이중막인 핵막으로 둘러싸여 있고 핵공을 통해 물질이 이동합니다.",
        "color": "#9b8cf2"
    },
    "mitochondria": {
        "name": "미토콘드리아",
        "function": "세포 호흡을 통해 ATP를 생산합니다.",
        "detail": "내막이 주름진 크리스타 구조를 가지며 자체 DNA도 보유합니다.",
        "color": "#e99c56"
    },
    "ribosome": {
        "name": "리보솜",
        "function": "mRNA의 정보를 바탕으로 단백질을 합성합니다.",
        "detail": "큰 소단위체와 작은 소단위체로 이루어집니다.",
        "color": "#e4d36b"
    },
    "rough_er": {
        "name": "거친면 소포체",
        "function": "분비 단백질과 막 단백질의 합성 및 가공에 관여합니다.",
        "detail": "표면에 리보솜이 붙어 있는 막성 구조입니다.",
        "color": "#58b7c8"
    },
    "smooth_er": {
        "name": "활면 소포체",
        "function": "지질 합성, 칼슘 저장, 해독 등에 관여합니다.",
        "detail": "표면에 리보솜이 붙어 있지 않은 막성 구조입니다.",
        "color": "#60b6a1"
    },
    "golgi": {
        "name": "골지체",
        "function": "단백질과 지질을 변형하고 분류하여 운반합니다.",
        "detail": "납작한 막 주머니가 여러 층 쌓인 형태입니다.",
        "color": "#d68ac4"
    },
    "lysosome": {
        "name": "리소좀",
        "function": "세포 내 불필요한 물질과 노폐물을 분해합니다.",
        "detail": "분해 효소를 포함하는 막성 소기관입니다.",
        "color": "#d97979"
    },
    "membrane": {
        "name": "세포막",
        "function": "세포 내부와 외부를 구분하고 물질 출입을 조절합니다.",
        "detail": "인지질 이중층과 다양한 막 단백질로 이루어집니다.",
        "color": "#6da8e9"
    }
}


# ============================================================
# 4. 3D 메시 생성 도구
# ============================================================

def mesh_surface(x, y, z, color, name, opacity=1.0,
                 showlegend=False, hovertext=None):

    x = np.asarray(x).flatten()
    y = np.asarray(y).flatten()
    z = np.asarray(z).flatten()

    if len(x) < 3:
        return None

    # 정규 격자 표면 삼각형 구성
    if np.asarray(x).size == 0:
        return None

    rows, cols = np.asarray(z).shape if np.asarray(z).ndim == 2 else (0, 0)

    if rows < 2 or cols < 2:
        return None

    indices_i, indices_j, indices_k = [], [], []

    for r in range(rows - 1):
        for c in range(cols - 1):
            a = r * cols + c
            b = a + 1
            d = (r + 1) * cols + c
            e = d + 1

            indices_i.extend([a, a])
            indices_j.extend([b, e])
            indices_k.extend([e, d])

    return go.Mesh3d(
        x=x, y=y, z=z,
        i=indices_i, j=indices_j, k=indices_k,
        color=color,
        opacity=opacity,
        name=name,
        showscale=False,
        showlegend=showlegend,
        hovertext=hovertext,
        hoverinfo="text" if hovertext else "name",
        flatshading=False,
        lighting=dict(
            ambient=0.48,
            diffuse=0.78,
            specular=0.45,
            roughness=0.55,
            fresnel=0.15
        ),
        lightposition=dict(x=100, y=-100, z=150)
    )


def ellipsoid(cx, cy, cz, rx, ry, rz,
              color, name, opacity=1.0,
              resolution=30):

    u = np.linspace(0, 2*np.pi, resolution)
    v = np.linspace(0, np.pi, resolution)

    U, V = np.meshgrid(u, v)

    X = cx + rx * np.sin(V) * np.cos(U)
    Y = cy + ry * np.sin(V) * np.sin(U)
    Z = cz + rz * np.cos(V)

    return mesh_surface(X, Y, Z, color, name, opacity)


def tube_between(start, end, radius, color, name,
                 sides=20, segments=24, taper=0.0):

    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)

    direction = end - start
    length = np.linalg.norm(direction)

    if length == 0:
        return None

    direction = direction / length

    reference = np.array([0., 0., 1.])
    if abs(np.dot(direction, reference)) > 0.9:
        reference = np.array([0., 1., 0.])

    axis1 = np.cross(direction, reference)
    axis1 /= np.linalg.norm(axis1)
    axis2 = np.cross(direction, axis1)

    t = np.linspace(0, 1, segments)
    theta = np.linspace(0, 2*np.pi, sides)

    T, TH = np.meshgrid(t, theta)

    R = radius * (1 - taper*T)

    points = (
        start[:, None, None]
        + direction[:, None, None] * (length*T)[None, :, :]
        + axis1[:, None, None] * (R*np.cos(TH))[None, :, :]
        + axis2[:, None, None] * (R*np.sin(TH))[None, :, :]
    )

    return mesh_surface(
        points[0], points[1], points[2],
        color, name
    )


def heart_mesh(cx, cy, cz, scale=0.055, color="#d94b5b"):
    t = np.linspace(0, 2*np.pi, 100)

    hx = 16*np.sin(t)**3
    hz = (
        13*np.cos(t)
        - 5*np.cos(2*t)
        - 2*np.cos(3*t)
        - np.cos(4*t)
    )

    hx = hx * scale
    hz = hz * scale

    front_y = cy - 0.12
    back_y = cy + 0.12

    x = np.concatenate([cx + hx, [cx], cx + hx])
    y = np.concatenate([
        np.full(len(t), front_y),
        [cy],
        np.full(len(t), back_y)
    ])
    z = np.concatenate([cz + hz, [cz], cz + hz])

    i, j, k = [], [], []
    n = len(t)

    for q in range(n):
        nxt = (q + 1) % n
        i.extend([n, n + 2 + q, n + 1 + q])
        j.extend([q, q + 1 if q < n-1 else 0, q])
        k.extend([nxt, n + 1 + nxt, n + 2 + nxt])

    return go.Mesh3d(
        x=x, y=y, z=z,
        i=i, j=j, k=k,
        color=color,
        opacity=1,
        name="심장",
        flatshading=False
    )


# ============================================================
# 5. 인체 3D 모델
# ============================================================

def add_organ(fig, key, highlighted=False):

    info = ORGANS[key]
    x, y, z = info["position"]

    opacity = 1.0 if highlighted else 0.92
    color = info["color"]

    if key == "heart":
        fig.add_trace(heart_mesh(x, y, z, color=color))
        return

    if key == "brain":
        # 뇌의 좌우 반구와 주름을 가진 표면
        for side in [-1, 1]:
            u = np.linspace(0, 2*np.pi, 44)
            v = np.linspace(0, np.pi, 36)
            U, V = np.meshgrid(u, v)

            fold = 1 + 0.045*np.sin(8*U)*np.sin(6*V)

            X = x + side*0.12 + 0.23*np.sin(V)*np.cos(U)*fold
            Y = y + 0.18*np.sin(V)*np.sin(U)*fold
            Z = z + 0.18*np.cos(V)*fold

            fig.add_trace(mesh_surface(
                X, Y, Z, color, "뇌 반구", opacity
            ))

        # 뇌의 고랑을 나타내는 가는 곡선
        for q in range(8):
            t = np.linspace(0, 2*np.pi, 80)
            px = x + 0.22*np.cos(t)
            py = y + 0.185*np.sin(t)
            pz = z + 0.11*np.sin(4*t + q)*0.25

            fig.add_trace(go.Scatter3d(
                x=px, y=py, z=pz,
                mode="lines",
                line=dict(color="#9e626a", width=2),
                showlegend=False,
                hoverinfo="skip"
            ))
        return

    if key in ("left_lung", "right_lung"):
        side = -1 if key == "left_lung" else 1
        # 폐의 길쭉한 해부학적 윤곽
        fig.add_trace(ellipsoid(
            x, y, z, 0.22, 0.16, 0.43,
            color, info["name"], opacity
        ))
        # 엽을 구분하는 표면 곡선
        for q in range(3):
            t = np.linspace(-1, 1, 80)
            fig.add_trace(go.Scatter3d(
                x=x + 0.19*np.sin(t*2 + q),
                y=np.full_like(t, y - 0.155),
                z=z + t*0.35,
                mode="lines",
                line=dict(color="#a95762", width=2),
                showlegend=False,
                hoverinfo="skip"
            ))
        return

    if key == "liver":
        # 간의 비대칭적인 윤곽
        u = np.linspace(0, 2*np.pi, 44)
        v = np.linspace(0, np.pi, 36)
        U, V = np.meshgrid(u, v)

        shape = 1 + 0.18*np.cos(U) + 0.07*np.sin(3*U)
        X = x + 0.36*np.sin(V)*np.cos(U)*shape
        Y = y + 0.19*np.sin(V)*np.sin(U)
        Z = z + 0.22*np.cos(V) - 0.06*np.sin(V)

        fig.add_trace(mesh_surface(
            X, Y, Z, color, "간", opacity
        ))
        return

    if key == "stomach":
        fig.add_trace(ellipsoid(
            x, y, z, 0.20, 0.14, 0.28,
            color, "위", opacity
        ))
        tube = tube_between(
            (x-0.10, y, z+0.18),
            (x+0.10, y, z-0.15),
            0.12, color, "위의 연결부", taper=0.3
        )
        if tube:
            fig.add_trace(tube)
        return

    if key == "kidney":
        # 콩팥 모양에 가까운 비대칭 메시
        u = np.linspace(0, 2*np.pi, 42)
        v = np.linspace(0, np.pi, 36)
        U, V = np.meshgrid(u, v)

        shape = 1 - 0.25*np.cos(U)
        X = x + 0.16*np.sin(V)*np.cos(U)*shape
        Y = y + 0.12*np.sin(V)*np.sin(U)
        Z = z + 0.25*np.cos(V)

        fig.add_trace(mesh_surface(
            X, Y, Z, color, "신장", opacity
        ))
        return

    if key == "intestine":
        # 소장 고리
        for q in range(4):
            t = np.linspace(0, 2*np.pi, 100)
            xx = x + 0.17*np.cos(t + q*0.7)
            zz = z + 0.10*np.sin(2*t + q)
            yy = y + 0.045*np.sin(3*t + q)

            fig.add_trace(go.Scatter3d(
                x=xx, y=yy, z=zz,
                mode="lines",
                line=dict(color=color, width=9),
                showlegend=False,
                hoverinfo="skip"
            ))
        return

    if key == "pancreas":
        fig.add_trace(ellipsoid(
            x, y, z, 0.30, 0.10, 0.09,
            color, "췌장", opacity
        ))
        return


def body_figure(
    removed=None,
    selected=None,
    opened=False,
    zoom=None,
    highlight_trait=None
):

    removed = removed or []
    fig = go.Figure()

    # 몸통: 높이에 따라 반경이 달라지는 입체 표면
    z_levels = np.linspace(2.0, 4.85, 70)
    theta = np.linspace(0, 2*np.pi, 64)
    Z, TH = np.meshgrid(z_levels, theta)

    profile = (
        0.29
        + 0.20*np.exp(-((Z-3.15)/0.55)**2)
        + 0.14*np.exp(-((Z-4.15)/0.55)**2)
        - 0.10*np.exp(-((Z-3.75)/0.22)**2)
    )

    X = profile*np.cos(TH)
    Y = profile*0.62*np.sin(TH)

    fig.add_trace(mesh_surface(
        X, Y, Z,
        "#d7a38f", "인체 몸통", 0.30 if opened else 0.85
    ))

    # 목
    fig.add_trace(tube_between(
        (0, 0, 4.68), (0, 0, 5.02),
        0.115, "#d5a18d", "목"
    ))

    # 머리와 얼굴
    fig.add_trace(ellipsoid(
        0, -0.015, 5.40,
        0.25, 0.24, 0.38,
        "#d7a38f", "머리", 0.92
    ))

    # 얼굴의 앞쪽 특징
    for sx in [-1, 1]:
        fig.add_trace(ellipsoid(
            sx*0.09, -0.235, 5.46,
            0.025, 0.018, 0.035,
            "#27364b", "눈"
        ))

    fig.add_trace(ellipsoid(
        0, -0.255, 5.34,
        0.035, 0.03, 0.055,
        "#c58b77", "코"
    ))

    # 어깨와 팔
    for side in [-1, 1]:
        shoulder = (side*0.34, 0, 4.48)
        elbow = (side*0.67, 0.02, 3.58)
        wrist = (side*0.78, -0.02, 2.85)

        fig.add_trace(tube_between(
            shoulder, elbow, 0.12,
            "#d7a38f", "상완"
        ))
        fig.add_trace(tube_between(
            elbow, wrist, 0.085,
            "#d7a38f", "전완"
        ))
        fig.add_trace(ellipsoid(
            side*0.80, -0.02, 2.72,
            0.09, 0.07, 0.17,
            "#d7a38f", "손"
        ))

    # 다리
    for side in [-1, 1]:
        hip = (side*0.17, 0.02, 2.1)
        knee = (side*0.19, 0.02, 1.10)
        ankle = (side*0.19, 0.02, 0.15)

        fig.add_trace(tube_between(
            hip, knee, 0.14,
            "#d7a38f", "허벅지", taper=0.1
        ))
        fig.add_trace(tube_between(
            knee, ankle, 0.085,
            "#d7a38f", "종아리", taper=0.1
        ))
        fig.add_trace(ellipsoid(
            side*0.19, -0.09, 0.12,
            0.12, 0.23, 0.10,
            "#d7a38f", "발"
        ))

    # 절개된 복부를 표현하는 내부 시야
    if opened:
        fig.add_trace(ellipsoid(
            0, -0.205, 3.55,
            0.29, 0.035, 0.92,
            "#733e49", "절개된 내부", 0.38
        ))

    # 장기 렌더링
    if opened or zoom == "organ" or zoom == "body":
        for key in ORGANS:
            if key in removed:
                continue

            if not opened and zoom == "body":
                continue

            add_organ(
                fig, key,
                highlighted=(key == selected)
            )

    # 눈동자와 머리카락의 편집 결과
    if highlight_trait == "dark_eyes":
        for sx in [-1, 1]:
            fig.add_trace(ellipsoid(
                sx*0.09, -0.256, 5.46,
                0.013, 0.008, 0.020,
                "#49301f", "눈동자"
            ))

    if highlight_trait == "light_eyes":
        for sx in [-1, 1]:
            fig.add_trace(ellipsoid(
                sx*0.09, -0.256, 5.46,
                0.013, 0.008, 0.020,
                "#659bb8", "눈동자"
            ))

    # 절개선을 표현
    if opened:
        fig.add_trace(go.Scatter3d(
            x=[0, 0, 0.05],
            y=[-0.30, -0.31, -0.29],
            z=[4.5, 3.8, 2.7],
            mode="lines",
            line=dict(color="#ef4444", width=5),
            name="절개 부위"
        ))

    # 선택 장기의 위치 강조
    if selected in ORGANS and selected not in removed:
        x, y, z = ORGANS[selected]["position"]

        fig.add_trace(go.Scatter3d(
            x=[x], y=[y-0.23], z=[z],
            mode="markers+text",
            marker=dict(
                size=8,
                color="#facc15",
                line=dict(width=2, color="white")
            ),
            text=[ORGANS[selected]["name"]],
            textposition="top center",
            name="선택된 장기"
        ))

    # 화면 설정
    camera = dict(
        eye=dict(x=0, y=-2.7, z=0.20),
        up=dict(x=0, y=0, z=1)
    )

    if zoom == "organ" and selected in ORGANS:
        p = ORGANS[selected]["position"]
        camera = dict(
            eye=dict(x=p[0]*1.5, y=-1.5, z=5.5-p[2]+0.3),
            center=dict(x=p[0], y=0, z=p[2])
        )

    fig.update_layout(
        height=720,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#0b1020",
        plot_bgcolor="#0b1020",
        showlegend=False,
        scene=dict(
            bgcolor="#0b1020",
            xaxis=dict(visible=False, range=[-1.2, 1.2]),
            yaxis=dict(visible=False, range=[-0.7, 0.7]),
            zaxis=dict(visible=False, range=[-0.15, 6.0]),
            aspectmode="manual",
            aspectratio=dict(x=0.75, y=0.50, z=1.8),
            camera=camera
        ),
        uirevision="biology-model"
    )

    return fig


# ============================================================
# 6. 세포 3D 모델
# ============================================================

def cell_figure(cell_type="neuron", selected_organelle=None):

    fig = go.Figure()

    # 세포막: 불규칙한 3D 표면
    u = np.linspace(0, 2*np.pi, 65)
    v = np.linspace(0, np.pi, 55)
    U, V = np.meshgrid(u, v)

    irregular = (
        1
        + 0.045*np.sin(5*U)*np.sin(4*V)
        + 0.025*np.cos(8*U+2*V)
    )

    X = 0.95*np.sin(V)*np.cos(U)*irregular
    Y = 0.70*np.sin(V)*np.sin(U)*irregular
    Z = 0.65*np.cos(V)*irregular

    fig.add_trace(mesh_surface(
        X, Y, Z, "#6ba9d7", "세포막", 0.18
    ))

    # 핵
    fig.add_trace(ellipsoid(
        0, 0, 0.08,
        0.30, 0.27, 0.30,
        "#8877d9", "핵", 0.95
    ))

    # 핵소체
    fig.add_trace(ellipsoid(
        0.05, -0.06, 0.12,
        0.09, 0.08, 0.09,
        "#4b368f", "핵소체"
    ))

    # 미토콘드리아: 구불구불한 관 형태
    for q in range(4):
        t = np.linspace(0, 2*np.pi, 120)
        x = 0.50*np.cos(t+q)
        y = 0.39*np.sin(t+q)
        z = 0.25*np.sin(2*t+q*0.8)

        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode="lines",
            line=dict(color="#e7a34f", width=9),
            name="미토콘드리아"
        ))

    # 소포체: 핵 주변의 막 구조
    for q in range(5):
        t = np.linspace(0, 2*np.pi, 90)
        r = 0.34 + q*0.045

        fig.add_trace(go.Scatter3d(
            x=r*np.cos(t),
            y=r*np.sin(t),
            z=0.13 + 0.035*np.sin(3*t+q),
            mode="lines",
            line=dict(
                color="#4fc3ce" if q < 3 else "#65b79c",
                width=5
            ),
            name="소포체"
        ))

    # 골지체
    for q in range(5):
        t = np.linspace(-1.3, 1.3, 70)

        fig.add_trace(go.Scatter3d(
            x=0.50+0.08*np.cos(t),
            y=-0.30+q*0.035 + 0.04*np.sin(t),
            z=-0.10+q*0.025 + 0.04*np.sin(t),
            mode="lines",
            line=dict(color="#d88cc4", width=6),
            name="골지체"
        ))

    # 리보솜
    rng = np.random.default_rng(14)
    points = []

    for _ in range(50):
        px, py, pz = rng.uniform(-0.65, 0.65, 3)
        if (px/0.85)**2+(py/0.65)**2+(pz/0.60)**2 < 0.85:
            points.append((px, py, pz))

    if points:
        p = np.array(points)
        fig.add_trace(go.Scatter3d(
            x=p[:, 0], y=p[:, 1], z=p[:, 2],
            mode="markers",
            marker=dict(size=3, color="#f3df70"),
            name="리보솜"
        ))

    # 세포 유형에 따른 특징
    if cell_type == "neuron":
        # 가지돌기
        for q in range(8):
            angle = q*np.pi/4
            start = (0.55*np.cos(angle), 0.45*np.sin(angle), 0)
            end = (1.45*np.cos(angle), 1.0*np.sin(angle), 0.1)

            fig.add_trace(tube_between(
                start, end, 0.045,
                "#75a9d7", "가지돌기"
            ))

        # 축삭
        fig.add_trace(tube_between(
            (0, 0, -0.35), (0, 0, -1.75),
            0.065, "#75a9d7", "축삭"
        ))

        # 수초
        for q in range(5):
            z = -0.55-q*0.23
            fig.add_trace(ellipsoid(
                0, 0, z, 0.105, 0.105, 0.08,
                "#e3c57e", "수초"
            ))

    elif cell_type == "cardiac":
        # 근원섬유 배열
        for q in range(8):
            yy = -0.55 + q*0.15
            fig.add_trace(go.Scatter3d(
                x=np.linspace(-0.65, 0.65, 60),
                y=np.full(60, yy),
                z=0.15*np.sin(np.linspace(0, 8*np.pi, 60)),
                mode="lines",
                line=dict(color="#cf7183", width=3),
                name="근원섬유"
            ))

    elif cell_type == "alveolar":
        # 얇은 세포층을 강조
        for q in range(4):
            fig.add_trace(ellipsoid(
                -0.3+q*0.2, 0.35, -0.30,
                0.10, 0.06, 0.12,
                "#9ac6e5", "폐포세포"
            ))

    elif cell_type == "podocyte":
        # 족세포의 발돌기
        for q in range(12):
            a = q*np.pi/6
            fig.add_trace(tube_between(
                (0.15*np.cos(a), 0.15*np.sin(a), -0.1),
                (0.8*np.cos(a), 0.65*np.sin(a), -0.45),
                0.025, "#8db8df", "발돌기"
            ))

    fig.update_layout(
        height=650,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#0b1020",
        scene=dict(
            bgcolor="#0b1020",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(eye=dict(x=1.6, y=-1.8, z=1.3))
        ),
        showlegend=False
    )

    return fig


# ============================================================
# 7. 세포 소기관 확대 모델
# ============================================================

def organelle_figure(key):

    fig = go.Figure()
    info = ORGANELLES[key]
    color = info["color"]

    if key == "nucleus":
        # 핵막
        fig.add_trace(ellipsoid(
            0, 0, 0, 0.9, 0.75, 0.85,
            "#8172cc", "핵막", 0.25, 45
        ))

        # 핵공
        for q in range(16):
            a = 2*np.pi*q/16
            fig.add_trace(ellipsoid(
                0.91*np.cos(a),
                0.76*np.sin(a),
                0,
                0.07, 0.07, 0.07,
                "#d5c9ff", "핵공"
            ))

        # 염색질
        rng = np.random.default_rng(12)
        for q in range(12):
            t = np.linspace(0, 2*np.pi, 80)
            r = 0.3 + q*0.035

            fig.add_trace(go.Scatter3d(
                x=r*np.cos(t),
                y=r*np.sin(t),
                z=0.20*np.sin(3*t+q),
                mode="lines",
                line=dict(color="#a79bf5", width=4),
                name="염색질"
            ))

        fig.add_trace(ellipsoid(
            0.12, 0.10, 0.15,
            0.23, 0.19, 0.22,
            "#5545a0", "핵소체"
        ))

    elif key == "mitochondria":
        # 미토콘드리아 외막과 내막
        fig.add_trace(ellipsoid(
            0, 0, 0, 1.0, 0.48, 0.42,
            "#e99c56", "외막", 0.35
        ))

        for q in range(7):
            t = np.linspace(-1.5, 1.5, 100)
            fig.add_trace(go.Scatter3d(
                x=0.70*np.sin(t),
                y=np.full_like(t, -0.30+q*0.10),
                z=0.30*np.sin(3*t+q),
                mode="lines",
                line=dict(color="#ffe0a2", width=6),
                name="크리스타"
            ))

    elif key == "ribosome":
        fig.add_trace(ellipsoid(
            -0.12, 0, 0,
            0.48, 0.38, 0.30,
            "#d8c16a", "큰 소단위체"
        ))
        fig.add_trace(ellipsoid(
            0.22, 0, -0.32,
            0.37, 0.30, 0.23,
            "#f0df90", "작은 소단위체"
        ))

    elif key in ("rough_er", "smooth_er"):
        for q in range(9):
            t = np.linspace(-2, 2, 100)
            x = t
            y = 0.16*np.sin(t*2+q*0.6)
            z = -0.55+q*0.13 + 0.06*np.cos(t*2)

            fig.add_trace(go.Scatter3d(
                x=x, y=y, z=z,
                mode="lines",
                line=dict(color=color, width=6),
                name=info["name"]
            ))

            if key == "rough_er":
                fig.add_trace(go.Scatter3d(
                    x=x[::12],
                    y=y[::12],
                    z=z[::12]+0.05,
                    mode="markers",
                    marker=dict(size=3, color="#f1d86b"),
                    name="리보솜"
                ))

    elif key == "golgi":
        for q in range(7):
            t = np.linspace(-1.2, 1.2, 100)
            fig.add_trace(go.Scatter3d(
                x=0.70*np.sin(t),
                y=np.full_like(t, q*0.10),
                z=0.25*np.cos(t)+q*0.04,
                mode="lines",
                line=dict(color=color, width=9),
                name="골지체 막"
            ))

    elif key == "lysosome":
        fig.add_trace(ellipsoid(
            0, 0, 0, 0.65, 0.60, 0.65,
            color, "리소좀"
        ))

        for q in range(12):
            a = q*np.pi/6
            fig.add_trace(ellipsoid(
                0.30*np.cos(a),
                0.30*np.sin(a),
                0.2*np.sin(2*a),
                0.06, 0.06, 0.06,
                "#ffe0a0", "분해 효소"
            ))

    elif key == "membrane":
        # 인지질 이중층의 머리와 꼬리
        for q in range(9):
            x = -0.8 + q*0.2

            fig.add_trace(ellipsoid(
                x, -0.16, 0,
                0.07, 0.07, 0.07,
                "#6da8e9", "친수성 머리"
            ))
            fig.add_trace(tube_between(
                (x, -0.16, -0.05),
                (x, 0, -0.35),
                0.018, "#e6c77d", "소수성 꼬리"
            ))
            fig.add_trace(ellipsoid(
                x, 0.16, 0,
                0.07, 0.07, 0.07,
                "#6da8e9", "친수성 머리"
            ))
            fig.add_trace(tube_between(
                (x, 0.16, -0.05),
                (x, 0, 0.35),
                0.018, "#e6c77d", "소수성 꼬리"
            ))

    fig.update_layout(
        height=580,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#0b1020",
        scene=dict(
            bgcolor="#0b1020",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data"
        ),
        showlegend=False
    )

    return fig


# ============================================================
# 8. DNA 3D 이중나선
# ============================================================

BASES = ["A", "T", "G", "C"]

COMPLEMENT = {
    "A": "T",
    "T": "A",
    "G": "C",
    "C": "G"
}


def dna_figure(sequence):

    fig = go.Figure()

    n = len(sequence)
    t = np.linspace(0, 7*np.pi, n*10)

    radius = 0.75
    height = np.linspace(-2.5, 2.5, len(t))

    x1 = radius*np.cos(t)
    y1 = radius*np.sin(t)

    x2 = radius*np.cos(t+np.pi)
    y2 = radius*np.sin(t+np.pi)

    # 두 가닥
    fig.add_trace(go.Scatter3d(
        x=x1, y=y1, z=height,
        mode="lines",
        line=dict(color="#53b6ec", width=9),
        name="DNA 가닥 1"
    ))

    fig.add_trace(go.Scatter3d(
        x=x2, y=y2, z=height,
        mode="lines",
        line=dict(color="#e58aa8", width=9),
        name="DNA 가닥 2"
    ))

    # 염기쌍 연결
    for q in range(0, len(t), 12):
        fig.add_trace(go.Scatter3d(
            x=[x1[q], x2[q]],
            y=[y1[q], y2[q]],
            z=[height[q], height[q]],
            mode="lines",
            line=dict(color="#cbd5e1", width=3),
            showlegend=False,
            hoverinfo="skip"
        ))

    # 염기 배열
    for q, base in enumerate(sequence[:12]):
        idx = min(q*12, len(t)-1)

        fig.add_trace(go.Scatter3d(
            x=[x1[idx]],
            y=[y1[idx]],
            z=[height[idx]],
            mode="markers+text",
            marker=dict(
                size=7,
                color={
                    "A": "#5db6e9",
                    "T": "#e89b5b",
                    "G": "#65c89a",
                    "C": "#c18be6"
                }[base]
            ),
            text=[base],
            textposition="top center",
            showlegend=False
        ))

    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#0b1020",
        scene=dict(
            bgcolor="#0b1020",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="manual",
            aspectratio=dict(x=1, y=1, z=2.0)
        )
    )

    return fig


# ============================================================
# 9. 유전자 및 형질 데이터
# ============================================================

GENES = {
    "OCA2": {
        "name": "OCA2 유전자",
        "trait": "눈 색소 형성",
        "description": "멜라닌 생성과 관련된 단백질의 기능에 관여합니다.",
        "choices": {
            "기본 상태": "natural",
            "기능 변화 예시 A": "light_eyes",
            "기능 변화 예시 B": "dark_eyes"
        },
        "warning": "눈동자 색은 OCA2 하나만으로 결정되지 않습니다. 여러 유전자와 조절 요소가 함께 관여합니다."
    },
    "MC1R": {
        "name": "MC1R 유전자",
        "trait": "멜라닌 유형과 모발 색소",
        "description": "멜라닌 생성 경로의 조절에 관여합니다.",
        "choices": {
            "기본 상태": "natural",
            "기능 변화 예시": "red_hair"
        },
        "warning": "머리카락 색은 다유전자 형질이며 MC1R 하나만으로 결정되지 않습니다."
    },
    "TYR": {
        "name": "TYR 유전자",
        "trait": "멜라닌 합성",
        "description": "티로시나아제 효소를 암호화하며 멜라닌 합성에 관여합니다.",
        "choices": {
            "기본 상태": "natural",
            "기능 감소 예시": "reduced_pigment"
        },
        "warning": "색소 형성은 여러 유전자와 세포 환경의 영향을 받습니다."
    }
}

DEFAULT_SEQUENCE = "ATGCGTACGTTAGCTAGGCTAAC"


def sequence_mutation(sequence, position, base):
    sequence = list(sequence)
    if 0 <= position < len(sequence) and base in BASES:
        sequence[position] = base
    return "".join(sequence)


def create_gene_chart(gene, condition):

    labels = ["기본 상태", "유전자 발현", "단백질 기능", "표현형"]

    # 교육용 개념도 수치이며 실제 유전적 확률이나 실험값이 아님
    data = {
        "natural": [100, 100, 100, 100],
        "light_eyes": [100, 85, 75, 70],
        "dark_eyes": [100, 110, 110, 115],
        "red_hair": [100, 80, 70, 80],
        "reduced_pigment": [100, 55, 45, 50]
    }

    values = data.get(condition, data["natural"])

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=labels,
        y=values,
        text=[f"{v} (개념도)" for v in values],
        textposition="outside",
        marker_color=["#55a9df", "#7c9ee8", "#b38be6", "#64c8a5"]
    ))

    fig.update_layout(
        title="유전자 발현에서 표현형까지의 개념적 변화",
        height=370,
        paper_bgcolor="#0b1020",
        plot_bgcolor="#111827",
        font_color="#e5e7eb",
        yaxis_title="상대적 개념 지수",
        yaxis=dict(range=[0, 140]),
        showlegend=False
    )

    return fig


# ============================================================
# 10. 유전도
# ============================================================

def pedigree_figure():

    fig = go.Figure()

    # 부모
    fig.add_shape(
        type="rect",
        x0=1, x1=2, y0=3, y1=4,
        line=dict(color="#60a5fa", width=3),
        fillcolor="#1e3a5f"
    )

    fig.add_shape(
        type="circle",
        x0=4, x1=5, y0=3, y1=4,
        line=dict(color="#ec91ba", width=3),
        fillcolor="#572d46"
    )

    fig.add_trace(go.Scatter(
        x=[1.5, 4.5],
        y=[3.5, 3.5],
        mode="markers+text",
        text=["부모 A", "부모 B"],
        textposition="top center",
        marker=dict(size=1, opacity=0),
        showlegend=False
    ))

    # 부모 연결
    fig.add_shape(
        type="line",
        x0=2, x1=4, y0=3.5, y1=3.5,
        line=dict(color="white", width=2)
    )

    fig.add_shape(
        type="line",
        x0=3, x1=3, y0=3.5, y1=2,
        line=dict(color="white", width=2)
    )

    fig.add_shape(
        type="line",
        x0=1.5, x1=4.5, y0=2, y1=2,
        line=dict(color="white", width=2)
    )

    # 자녀
    for x in [1.5, 3, 4.5]:
        fig.add_shape(
            type="circle",
            x0=x-0.35, x1=x+0.35,
            y0=0.7, y1=1.4,
            line=dict(color="#7dd3fc", width=2),
            fillcolor="#1e3a5f"
        )

    fig.add_trace(go.Scatter(
        x=[1.5, 3, 4.5],
        y=[1.05]*3,
        mode="text",
        text=["자녀 1", "자녀 2", "자녀 3"],
        textposition="bottom center",
        showlegend=False
    ))

    fig.update_layout(
        title="가족 간 형질 전달을 이해하기 위한 개념적 유전도",
        height=440,
        paper_bgcolor="#0b1020",
        plot_bgcolor="#0b1020",
        font_color="#e5e7eb",
        xaxis=dict(visible=False, range=[0, 6]),
        yaxis=dict(visible=False, range=[0, 5])
    )

    return fig


# ============================================================
# 11. 장기 제거 실험
# ============================================================

def removal_analysis(removed):

    if not removed:
        return {
            "status": "정상 인체 상태",
            "systems": "모든 주요 장기가 표시된 상태입니다.",
            "effects": []
        }

    effects = []

    for key in removed:
        info = ORGANS[key]
        effects.append({
            "장기": info["name"],
            "계통": info["system"],
            "예상 변화": info["removed"]
        })

    return {
        "status": f"{len(removed)}개 장기 제거 실험 상태",
        "systems": "제거된 장기의 기능에 따른 생리적 변화를 학습합니다.",
        "effects": effects
    }


def system_chart(removed):

    systems = {
        "신경계": 100,
        "순환계": 100,
        "호흡계": 100,
        "소화·대사계": 100,
        "소화계": 100,
        "비뇨계": 100,
        "소화·내분비계": 100,
        "내분비계": 100
    }

    for key in removed:
        info = ORGANS[key]
        systems[info["system"]] = max(
            0,
            systems[info["system"]] - info["importance"]
        )

    fig = go.Figure(go.Bar(
        x=list(systems.keys()),
        y=list(systems.values()),
        marker_color="#59b6db"
    ))

    fig.update_layout(
        title="장기 기능 영향 개념도",
        yaxis_title="기능 지수 (교육용)",
        yaxis=dict(range=[0, 110]),
        height=350,
        paper_bgcolor="#0b1020",
        plot_bgcolor="#111827",
        font_color="#e5e7eb"
    )

    return fig


# ============================================================
# 12. 약리학 교육 데이터
# ============================================================

DRUGS = {
    "진통제": {
        "examples": "아세트아미노펜 등",
        "purpose": "통증 및 발열 완화",
        "mechanism": "약물 종류에 따라 통증 전달 및 통증 관련 신호에 영향을 줍니다.",
        "visual": "정상",
        "effects": "약물 종류에 따라 어지러움이나 시각적 불편감이 나타날 수 있습니다.",
        "risk": "약물마다 간 기능 등과 관련된 주의사항이 다릅니다."
    },
    "마취제": {
        "examples": "의료용 국소·전신 마취제",
        "purpose": "수술이나 의료 처치 중 통증 및 의식 조절",
        "mechanism": "신경 신호 전달 또는 중추신경계의 활동을 조절합니다.",
        "visual": "blur",
        "effects": "마취 과정에서는 시각 정보 처리와 의식 수준이 달라질 수 있습니다.",
        "risk": "전문 의료진의 감시와 적절한 의료 환경이 필요한 약물입니다."
    },
    "항생제": {
        "examples": "페니실린계 등",
        "purpose": "세균 감염 치료",
        "mechanism": "세균의 세포벽 합성이나 단백질 합성 등 특정 과정을 방해합니다.",
        "visual": "normal",
        "effects": "일반적으로 직접적인 시야 변화가 주요 작용은 아닙니다.",
        "risk": "알레르기 반응과 내성 문제 등에 주의해야 합니다."
    },
    "항히스타민제": {
        "examples": "일부 알레르기 치료제",
        "purpose": "알레르기 증상 완화",
        "mechanism": "히스타민 수용체를 차단하여 알레르기 반응을 줄입니다.",
        "visual": "blur",
        "effects": "일부 종류는 졸림이나 시야 흐림을 일으킬 수 있습니다.",
        "risk": "약물 종류에 따라 졸음과 집중력 저하가 발생할 수 있습니다."
    },
    "기관지확장제": {
        "examples": "베타2 수용체 작용제 등",
        "purpose": "기관지 평활근을 이완시켜 호흡을 돕습니다.",
        "mechanism": "기관지 평활근의 수용체에 작용하여 기도를 넓힙니다.",
        "visual": "normal",
        "effects": "일부 약물은 떨림이나 심박수 증가를 유발할 수 있습니다.",
        "risk": "심계항진 등 이상 반응을 확인해야 합니다."
    },
    "항우울제": {
        "examples": "SSRI 계열 등",
        "purpose": "우울증 및 일부 불안 관련 질환 치료",
        "mechanism": "신경전달물질의 재흡수 또는 신호 전달을 조절합니다.",
        "visual": "normal",
        "effects": "약물과 개인에 따라 어지러움이나 시각 관련 불편이 나타날 수 있습니다.",
        "risk": "효과와 부작용을 의료진과 함께 관찰해야 합니다."
    },
    "항경련제": {
        "examples": "의료용 항발작 약물",
        "purpose": "비정상적인 신경 활동을 조절하여 발작을 예방하거나 줄입니다.",
        "mechanism": "신경세포의 흥분성이나 신경전달에 영향을 줍니다.",
        "visual": "blur",
        "effects": "일부 약물은 복시, 어지러움, 졸림을 유발할 수 있습니다.",
        "risk": "약물별 부작용과 상호작용을 확인해야 합니다."
    },
    "오피오이드 진통제": {
        "examples": "펜타닐 등",
        "purpose": "특정 중증 통증이나 마취 상황에서 의료적으로 사용",
        "mechanism": "중추신경계의 오피오이드 수용체에 작용하여 통증 전달을 억제합니다.",
        "visual": "dim",
        "effects": "의식 저하, 시야 흐림, 반응 저하 등이 나타날 수 있습니다.",
        "risk": "호흡 억제 등 심각한 위험이 있으며 의료진의 엄격한 관리가 필요합니다."
    }
}


# ============================================================
# 13. 1인칭 시야 시뮬레이션
# ============================================================

def visual_field(mode):

    # 시야 효과는 실제 체험을 재현하는 것이 아니라
    # 의학적 부작용을 설명하기 위한 추상적 개념도임.

    if mode in ("정상", "normal"):
        blur = 0
        brightness = 1.0
        opacity = 0
        title = "정상적인 시각 정보 처리"

    elif mode == "blur":
        blur = 1
        brightness = 0.85
        opacity = 0.08
        title = "시야 흐림의 개념도"

    elif mode == "dim":
        blur = 2
        brightness = 0.45
        opacity = 0.28
        title = "의식 및 시각 반응 저하의 개념도"

    else:
        blur = 0
        brightness = 1.0
        opacity = 0
        title = "정상적인 시각 정보 처리"

    x = np.linspace(-1, 1, 180)
    y = np.linspace(-1, 1, 180)
    X, Y = np.meshgrid(x, y)

    R = np.sqrt(X**2 + Y**2)

    # 중심부 시야와 주변부 감도 차이
    Z = np.exp(-2*R**2) * brightness

    if mode == "blur":
        Z = 0.7*Z + 0.3*np.exp(-R**2)

    if mode == "dim":
        Z = 0.5*Z

    fig = go.Figure(go.Heatmap(
        x=x, y=y, z=Z,
        colorscale=[
            [0, "#111827"],
            [0.5, "#64748b"],
            [1, "#f1f5f9"]
        ],
        showscale=False,
        zmin=0,
        zmax=1
    ))

    # 시야 주변부
    if mode != "normal" and mode != "정상":
        fig.add_shape(
            type="circle",
            x0=-0.96, x1=0.96,
            y0=-0.96, y1=0.96,
            line=dict(color="#94a3b8", width=2),
            fillcolor="rgba(15,23,42,0.20)"
        )

    fig.update_layout(
        title=title,
        height=420,
        paper_bgcolor="#0b1020",
        plot_bgcolor="#111827",
        font_color="#e5e7eb",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False, scaleanchor="x")
    )

    return fig


# ============================================================
# 14. 제목과 사이드바
# ============================================================

st.markdown("""
# 🧬 BIOLOGY 3D LAB
### HUMAN BODY · CELL · GENETICS · PHARMACOLOGY
""")

st.markdown(
    '<p class="small-muted">3차원 인체를 통해 생명체의 구조와 기능을 탐구하는 통합형 교육 시뮬레이터</p>',
    unsafe_allow_html=True
)

with st.sidebar:
    st.markdown("## LAB NAVIGATION")

    page = st.radio(
        "탐구 영역",
        [
            "① 인체 해부 실험",
            "② 세포 및 소기관",
            "③ DNA와 유전자",
            "④ 약리학 실험실"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### 실험 상태")

    st.write("현재 단계:", st.session_state.stage)

    st.write(
        "제거한 장기:",
        len(st.session_state.removed_organs)
    )

    if st.button("전체 실험 초기화", use_container_width=True):
        reset_experiment()
        st.rerun()


# ============================================================
# 15. 인체 해부 실험 페이지
# ============================================================

if page == "① 인체 해부 실험":

    st.markdown("## HUMAN ANATOMY")
    st.caption("인체를 절개하고 장기를 선택하여 구조와 기능을 학습합니다.")

    tab1, tab2, tab3 = st.tabs([
        "3D 인체 해부",
        "장기 선택 및 분석",
        "장기 제거 실험"
    ])

    with tab1:

        left, right = st.columns([1.7, 1])

        with left:
            st.markdown("### 3D HUMAN MODEL")

            if st.button(
                "메스로 복부 절개하기",
                use_container_width=True
            ):
                st.session_state.incision = True
                st.rerun()

            if st.button(
                "절개 상태 되돌리기",
                use_container_width=True
            ):
                st.session_state.incision = False
                st.rerun()

            st.plotly_chart(
                body_figure(
                    removed=st.session_state.removed_organs,
                    selected=st.session_state.selected_organ,
                    opened=st.session_state.incision,
                    zoom="body"
                ),
                use_container_width=True,
                config={
                    "scrollZoom": True,
                    "displaylogo": False,
                    "responsive": True
                }
            )

        with right:
            st.markdown("### 해부 도구")

            st.info(
                "메스 버튼을 누르면 인체의 내부 장기 영역이 드러납니다. "
                "아래 장기 선택 메뉴를 통해 각 장기를 선택할 수 있습니다."
            )

            organ_keys = list(ORGANS.keys())

            selected = st.selectbox(
                "탐색할 장기",
                organ_keys,
                format_func=lambda k: ORGANS[k]["name"],
                key="body_organ_select"
            )

            st.session_state.selected_organ = selected

            info = ORGANS[selected]

            st.markdown(f"### {info['name']}")
            st.write(info["function"])

            st.markdown("**구성 세포**")
            for c in info["cells"]:
                st.write("•", c)

            if st.button(
                "선택한 장기 확대 탐구 →",
                use_container_width=True
            ):
                st.session_state.stage = "organ"
                st.rerun()

    with tab2:

        st.markdown("### ORGAN EXPLORATION")

        selected = st.selectbox(
            "장기",
            list(ORGANS.keys()),
            format_func=lambda k: ORGANS[k]["name"],
            key="organ_explore_select"
        )

        st.session_state.selected_organ = selected
        info = ORGANS[selected]

        col1, col2 = st.columns([1.4, 1])

        with col1:
            st.plotly_chart(
                body_figure(
                    removed=st.session_state.removed_organs,
                    selected=selected,
                    opened=True,
                    zoom="organ"
                ),
                use_container_width=True
            )

        with col2:
            st.markdown(f"## {info['name']}")
            st.write(info["function"])

            st.markdown("**조직을 구성하는 주요 세포**")

            for c in info["cells"]:
                st.markdown(f"- {c}")

            st.markdown(f"**관련 계통:** {info['system']}")

            if st.button(
                "이 장기의 세포 확대하기 →",
                use_container_width=True
            ):
                st.session_state.selected_cell = info["cell_type"]
                st.session_state.stage = "cell"
                st.rerun()

    with tab3:

        st.markdown("### ORGAN REMOVAL EXPERIMENT")
        st.warning(
            "실제 수술을 재현하는 것이 아닌, 장기 기능 상실에 따른 "
            "생리학적 영향을 이해하는 교육용 가상 실험입니다."
        )

        col1, col2 = st.columns([1.2, 1])

        with col1:
            target = st.selectbox(
                "실험 대상 장기",
                list(ORGANS.keys()),
                format_func=lambda k: ORGANS[k]["name"],
                key="removal_target"
            )

            st.markdown("#### 장기 제거")

            st.write(
                f"선택된 장기: **{ORGANS[target]['name']}**"
            )

            if st.button(
                "장기 제거 실험 실행",
                type="primary",
                use_container_width=True
            ):
                if target not in st.session_state.removed_organs:
                    st.session_state.removed_organs.append(target)
                    st.session_state.experiment_history.append(
                        f"{ORGANS[target]['name']} 제거 실험"
                    )
                st.rerun()

            if st.button(
                "모든 장기 복구",
                use_container_width=True
            ):
                st.session_state.removed_organs = []
                st.rerun()

            st.plotly_chart(
                body_figure(
                    removed=st.session_state.removed_organs,
                    selected=target,
                    opened=True,
                    zoom="body"
                ),
                use_container_width=True
            )

        with col2:
            result = removal_analysis(
                st.session_state.removed_organs
            )

            st.markdown("### 실험 결과")
            st.metric("실험 상태", result["status"])

            for effect in result["effects"]:
                st.markdown(
                    f"""
                    <div class="bio-panel">
                    <h3>{effect['장기']}</h3>
                    <p class="small-muted">{effect['계통']}</p>
                    <p>{effect['예상 변화']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            if not result["effects"]:
                st.info("아직 제거된 장기가 없습니다.")

            st.plotly_chart(
                system_chart(st.session_state.removed_organs),
                use_container_width=True
            )

            st.caption(
                "기능 지수는 학습용 개념 지표입니다. "
                "실제 인체의 생존 가능성이나 장기 기능을 수치로 예측하지 않습니다."
            )


# ============================================================
# 16. 세포 및 소기관 페이지
# ============================================================

elif page == "② 세포 및 소기관":

    st.markdown("## CELL BIOLOGY")
    st.caption("장기에서 세포로, 세포에서 소기관으로 확대합니다.")

    stage = st.radio(
        "확대 단계",
        ["장기 → 세포", "세포 → 소기관"],
        horizontal=True
    )

    if stage == "장기 → 세포":

        selected = st.selectbox(
            "어떤 장기의 세포를 탐구할까요?",
            list(ORGANS.keys()),
            format_func=lambda k: ORGANS[k]["name"],
            key="cell_organ_select"
        )

        organ = ORGANS[selected]
        cell_key = organ["cell_type"]
        cell = CELLS[cell_key]

        st.markdown(f"### {organ['name']} → {cell['name']}")

        left, right = st.columns([1.5, 1])

        with left:
            st.plotly_chart(
                cell_figure(cell_key),
                use_container_width=True,
                config={"scrollZoom": True}
            )

        with right:
            st.markdown(f"## {cell['name']}")
            st.write(cell["function"])

            st.markdown("### 구조적 특징")
            st.write(cell["features"])

            st.markdown("### 생명과학적 역할")
            st.success(cell["role"])

            st.markdown("### 세포 소기관")
            st.write(
                "세포의 종류와 기능에 따라 소기관의 발달 정도와 "
                "분포가 달라질 수 있습니다."
            )

            if st.button(
                "핵 내부로 확대 →",
                use_container_width=True
            ):
                st.session_state.stage = "cell"
                st.rerun()

    else:

        selected = st.selectbox(
            "확대할 세포 소기관",
            list(ORGANELLES.keys()),
            format_func=lambda k: ORGANELLES[k]["name"]
        )

        st.session_state.selected_organelle = selected

        info = ORGANELLES[selected]

        left, right = st.columns([1.5, 1])

        with left:
            st.plotly_chart(
                organelle_figure(selected),
                use_container_width=True,
                config={"scrollZoom": True}
            )

        with right:
            st.markdown(f"## {info['name']}")
            st.write(info["function"])

            st.markdown("### 구조적 특징")
            st.write(info["detail"])

            if selected == "nucleus":
                st.success(
                    "핵은 DNA를 보관하는 장소입니다. "
                    "다음 단계에서는 핵 속 DNA의 구조와 유전자 발현을 탐구합니다."
                )

                if st.button(
                    "DNA 이중나선 확대 →",
                    use_container_width=True
                ):
                    st.session_state.stage = "dna"
                    st.session_state.selected_organelle = "nucleus"
                    st.rerun()


# ============================================================
# 17. DNA 및 유전자 페이지
# ============================================================

elif page == "③ DNA와 유전자":

    st.markdown("## GENETICS & DNA")
    st.caption("DNA의 구조와 유전자 발현, 형질 변화의 관계를 탐구합니다.")

    tab1, tab2, tab3 = st.tabs([
        "DNA 3D 구조",
        "유전자 편집 실험",
        "유전과 형질 분석"
    ])

    with tab1:

        st.markdown("### DNA DOUBLE HELIX")

        sequence = st.session_state.get(
            "dna_sequence", DEFAULT_SEQUENCE
        )

        st.plotly_chart(
            dna_figure(sequence),
            use_container_width=True,
            config={"scrollZoom": True}
        )

        st.markdown("### 염기서열")

        st.code(
            "5' - " + sequence + " - 3'",
            language="text"
        )

        st.markdown("### 상보적 염기서열")

        complement = "".join(
            COMPLEMENT[b] for b in sequence
        )

        st.code(
            "3' - " + complement + " - 5'",
            language="text"
        )

        st.write("""
        - 아데닌(A)은 티민(T)과 상보적으로 결합합니다.
        - 구아닌(G)은 사이토신(C)과 상보적으로 결합합니다.
        - DNA의 특정 염기서열은 유전정보를 저장합니다.
        """)

    with tab2:

        st.markdown("### GENE EDITING LAB")

        st.info(
            "아래는 유전자와 형질의 관계를 이해하기 위한 교육용 가상 모델입니다. "
            "실제 유전자 편집 실험이나 임상적 결과를 예측하는 도구가 아닙니다."
        )

        gene = st.selectbox(
            "탐구할 유전자",
            list(GENES.keys()),
            format_func=lambda k: GENES[k]["name"]
        )

        gene_info = GENES[gene]

        st.markdown(f"### {gene_info['name']}")
        st.write(gene_info["description"])

        choice = st.radio(
            "유전자 기능 상태 선택",
            list(gene_info["choices"].keys()),
            horizontal=True,
            key=f"gene_choice_{gene}"
        )

        condition = gene_info["choices"][choice]

        # 사용자가 직접 염기 변경 위치와 대체 염기를 고르는 방식
        st.markdown("### 염기서열 간단 편집")

        sequence = st.session_state.get(
            "dna_sequence", DEFAULT_SEQUENCE
        )

        position = st.select_slider(
            "변경할 염기 위치",
            options=list(range(1, len(sequence)+1)),
            value=1
        )

        current_base = sequence[position-1]

        replacement = st.selectbox(
            "새로운 염기",
            BASES,
            index=BASES.index(current_base)
        )

        st.write(
            f"현재 {position}번째 염기: **{current_base}**"
        )

        if st.button("염기서열 변경 적용"):
            st.session_state.dna_sequence = sequence_mutation(
                sequence,
                position-1,
                replacement
            )

            st.session_state.gene_edits[gene] = {
                "position": position,
                "before": current_base,
                "after": replacement
            }

            st.rerun()

        st.markdown("### 편집 결과")

        edited_sequence = st.session_state.get(
            "dna_sequence", DEFAULT_SEQUENCE
        )

        st.code(edited_sequence)

        st.plotly_chart(
            dna_figure(edited_sequence),
            use_container_width=True
        )

        st.markdown("### 유전자 발현과 형질의 관계")

        st.plotly_chart(
            create_gene_chart(gene, condition),
            use_container_width=True
        )

        st.markdown("### 예상되는 형질 변화")

        trait_map = {
            "natural": "기본 상태를 기준으로 비교합니다.",
            "light_eyes": "눈동자 색소 형성 경로의 변화를 개념적으로 나타냅니다.",
            "dark_eyes": "눈동자 색소 형성 경로의 변화를 개념적으로 나타냅니다.",
            "red_hair": "모발의 멜라닌 유형과 관련된 변화를 개념적으로 나타냅니다.",
            "reduced_pigment": "멜라닌 합성 경로의 기능 저하를 개념적으로 나타냅니다."
        }

        st.write(trait_map[condition])

        st.warning(gene_info["warning"])

        # 인체에 적용하는 형질 표시
        trait_visual = (
            condition if condition in (
                "light_eyes", "dark_eyes"
            ) else None
        )

        if gene == "OCA2":
            st.plotly_chart(
                body_figure(
                    opened=False,
                    zoom="body",
                    highlight_trait=trait_visual
                ),
                use_container_width=True
            )

        elif gene == "MC1R":
            st.markdown(
                "모발 색 변화는 이 모델의 인체 렌더링에 "
                "실제 머리카락 메시가 추가된 경우 표현할 수 있습니다."
            )

        st.caption(
            "유전자 상태 선택과 임의 염기 치환은 서로 독립된 교육용 조작입니다. "
            "현재의 간단한 모델은 특정 염기 변화가 실제로 특정 형질을 일으킨다고 "
            "계산하지 않습니다."
        )

    with tab3:

        st.markdown("### INHERITANCE")

        st.write(
            "유전 형질은 부모에게서 전달되는 유전정보와 "
            "유전자 발현 및 환경적 요인의 상호작용으로 나타납니다."
        )

        st.plotly_chart(
            pedigree_figure(),
            use_container_width=True
        )

        st.markdown("### 유전 개념")

        st.markdown("""
        - **유전자형:** 개체가 가진 유전정보의 구성
        - **표현형:** 유전자와 환경의 영향을 받아 나타나는 관찰 가능한 특징
        - **우성:** 이형접합 상태에서도 표현형에 나타나는 대립유전자 관계
        - **열성:** 일반적인 완전 우성 관계에서 동형접합일 때 표현형에 나타나는 대립유전자 관계
        - **다유전자 유전:** 여러 유전자가 하나의 형질에 함께 관여하는 현상
        """)

        st.info(
            "눈동자 색과 머리카락 색은 단순한 멘델식 단일 유전자 형질이 아닙니다. "
            "실제 유전 현상을 이해하려면 여러 유전자와 환경의 영향을 함께 고려해야 합니다."
        )


# ============================================================
# 18. 약리학 페이지
# ============================================================

elif page == "④ 약리학 실험실":

    st.markdown("## PHARMACOLOGY LAB")
    st.caption("약물의 작용 원리와 인체 반응을 의학적으로 탐구합니다.")

    st.warning(
        "교육용 약리학 시뮬레이터입니다. 실제 약물 투여·사용법이나 "
        "개인별 효과를 재현하지 않습니다. 특히 오피오이드 계열은 "
        "호흡 억제와 의식 저하 등 생명을 위협할 수 있는 위험이 있습니다."
    )

    tab1, tab2 = st.tabs([
        "약물의 작용 원리",
        "1인칭 시각 정보 시뮬레이션"
    ])

    with tab1:

        drug = st.selectbox(
            "약물 분류",
            list(DRUGS.keys())
        )

        st.session_state.drug_selected = drug

        info = DRUGS[drug]

        st.markdown(f"## {drug}")

        st.markdown(
            f'<div class="bio-panel"><h3>대표 약물</h3>'
            f'<p>{info["examples"]}</p></div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 의학적 목적")
            st.write(info["purpose"])

            st.markdown("### 작용 기전")
            st.write(info["mechanism"])

        with col2:
            st.markdown("### 생리적 반응")
            st.write(info["effects"])

            st.markdown("### 주의할 점")
            st.error(info["risk"])

        st.markdown("### 약물 작용의 흐름")

        st.markdown("""
        <div class="bio-panel">
        <h3>약물의 작용 과정</h3>
        <p>약물과 표적 분자의 상호작용</p>
        <p>↓</p>
        <p>수용체 또는 효소의 기능 변화</p>
        <p>↓</p>
        <p>세포 신호 전달 변화</p>
        <p>↓</p>
        <p>조직과 기관의 생리적 반응</p>
        <p>↓</p>
        <p>치료 효과 또는 부작용</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 인체 내 작용 부위")

        st.plotly_chart(
            body_figure(
                opened=True,
                zoom="body"
            ),
            use_container_width=True
        )

        st.caption(
            "실제 약물마다 표적과 작용 부위가 다르며, "
            "위 인체 모형은 특정 약물의 정확한 분포를 표시하지 않습니다."
        )

    with tab2:

        st.markdown("### FIRST-PERSON VISUAL FIELD")

        st.write("""
        약물에 의해 시각 정보 처리와 의식 수준이 달라지는 현상을
        교육용으로 추상화한 화면입니다.

        실제 환자가 보는 화면을 그대로 재현한 것이 아니며,
        약물의 효과를 재미있거나 매력적인 경험으로 묘사하지 않습니다.
        """)

        drug = st.selectbox(
            "분석할 약물 분류",
            list(DRUGS.keys()),
            key="visual_drug"
        )

        info = DRUGS[drug]

        st.markdown(f"### {drug}")
        st.write(info["mechanism"])

        st.write("**관련 시각·신경계 변화**")
        st.write(info["effects"])

        st.plotly_chart(
            visual_field(info["visual"]),
            use_container_width=True
        )

        if drug == "오피오이드 진통제":
            st.error(
                "펜타닐과 같은 오피오이드 약물은 의료적 통증 조절에 사용되기도 하지만 "
                "호흡 억제와 의식 저하 등 심각한 부작용을 일으킬 수 있습니다. "
                "시각적 변화보다 이러한 생리적 위험을 이해하는 것이 중요합니다."
            )

        st.caption(
            "시야의 밝기나 흐림은 의학적 현상을 설명하기 위한 개념적 시각화입니다. "
            "약물별로 동일한 증상이 반드시 나타나는 것은 아닙니다."
        )


# ============================================================
# 19. 하단 정보
# ============================================================

st.divider()

st.markdown("""
<div style="text-align:center; color:#64748b; padding:15px;">
    BIOLOGY 3D LAB · HUMAN ANATOMY · CELL BIOLOGY · GENETICS · PHARMACOLOGY
    <br>
    Educational Simulation / Not for Clinical Diagnosis or Treatment
</div>
""", unsafe_allow_html=True)
