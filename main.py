
# ============================================================
# CELLIT - 3D BIOLOGY EXPLORATION LAB
# Streamlit Cloud / Python 3.11
#
# Human -> Organ -> Cell -> Organelle -> Nucleus -> DNA
# Organ removal experiment
# Educational gene/trait simulation
# Medical pharmacology visualization
#
# NOTE:
# - Educational simulation, not a clinical diagnostic tool.
# - No real drug administration instructions or dosage data.
# - Trait relationships are simplified teaching models.
# ============================================================

from __future__ import annotations

import math
import hashlib
from typing import Callable, Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st


# ============================================================
# 0. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CELLIT | 3D Biology Lab",
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
        radial-gradient(ellipse at 20% 0%, #14243b 0%, transparent 50%),
        linear-gradient(145deg, #080e19, #0c1422 55%, #101b2b);
    color: #edf3fa;
}

section[data-testid="stSidebar"] {
    background: #0b1422;
    border-right: 1px solid #26364c;
}

h1, h2, h3 {
    color: #f3f7ff !important;
    letter-spacing: -0.5px;
}

p, label, span {
    color: #d4deeb;
}

div[data-testid="stMetric"] {
    background: rgba(25, 43, 64, .75);
    border: 1px solid #2c4058;
    border-radius: 12px;
    padding: 14px;
}

div[data-testid="stMetricValue"] {
    color: #7dd3fc;
}

.stButton > button {
    border-radius: 9px;
    border: 1px solid #38516e;
    background: #16283e;
    color: #e8f3ff;
    font-weight: 600;
}

.stButton > button:hover {
    border-color: #38bdf8;
    background: #203b59;
    color: white;
}

div[data-testid="stSelectbox"] {
    margin-bottom: 4px;
}

.lab-card {
    background: linear-gradient(135deg, #14263b, #101d30);
    border: 1px solid #2c435d;
    padding: 17px;
    border-radius: 14px;
    margin-bottom: 12px;
}

.lab-muted {
    color: #9fb1c7;
    font-size: 0.88rem;
}

.lab-tag {
    display: inline-block;
    border: 1px solid #375878;
    color: #7dd3fc;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.75rem;
    margin-right: 5px;
}

hr {
    border-color: #2a3b50;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 1. SESSION STATE
# ============================================================

DEFAULTS = {
    "page": "인체 탐구",
    "stage": "body",
    "selected_organ": "심장",
    "selected_cell": "심근세포",
    "selected_organelle": "미토콘드리아",
    "selected_gene": "OCA2",
    "removed_organs": [],
    "modified_traits": {},
    "original_traits": {
        "eye": "갈색",
        "hair": "검은색",
        "skin": "중간",
        "height": "평균",
    },
    "drug": "일반적인 진통제",
    "show_drug_effect": False,
    "dna_sequence": "ATGCGTACCGTTAGC",
    "cut_progress": 0,
    "model_rotation": 0,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# 2. SCIENCE DATABASE
# ============================================================

ORGANS = {
    "뇌": {
        "system": "신경계",
        "color": "#b38ad9",
        "function": "감각 정보 처리, 운동 조절, 기억, 학습, 항상성 조절",
        "structure": "대뇌, 소뇌, 뇌간 등으로 이루어진 중추신경계의 핵심 기관",
        "cells": ["신경세포", "성상교세포", "희소돌기아교세포", "미세아교세포"],
        "removal": "중추신경계의 핵심 기능이 상실되는 상황을 나타내는 가상 실험입니다.",
        "effects": {
            "신경 기능": 0,
            "산소 운반": 100,
            "소화 기능": 100,
            "대사 기능": 100,
        }
    },
    "심장": {
        "system": "순환계",
        "color": "#ed6476",
        "function": "혈액을 순환시켜 산소와 영양소를 조직에 공급",
        "structure": "심방 2개와 심실 2개, 심근과 판막 및 전도계로 구성",
        "cells": ["심근세포", "내피세포", "섬유아세포", "평활근세포"],
        "removal": "심장 기능이 사라지면 혈액 순환을 유지할 수 없습니다.",
        "effects": {
            "신경 기능": 100,
            "산소 운반": 0,
            "소화 기능": 45,
            "대사 기능": 20,
        }
    },
    "폐": {
        "system": "호흡계",
        "color": "#79b8e8",
        "function": "산소를 혈액으로 전달하고 이산화탄소를 배출",
        "structure": "기관지, 세기관지, 폐포와 모세혈관으로 구성",
        "cells": ["제1형 폐포세포", "제2형 폐포세포", "섬모상피세포", "대식세포"],
        "removal": "가스 교환 면적이 줄어들면 산소 공급과 이산화탄소 배출이 어려워집니다.",
        "effects": {
            "신경 기능": 75,
            "산소 운반": 0,
            "소화 기능": 100,
            "대사 기능": 70,
        }
    },
    "간": {
        "system": "소화계·대사계",
        "color": "#b98251",
        "function": "영양소 대사, 해독, 담즙 생성, 혈당 조절",
        "structure": "간소엽과 간세포, 동양혈관 및 담관으로 구성",
        "cells": ["간세포", "쿠퍼세포", "간성상세포", "담관세포"],
        "removal": "대사 조절과 여러 물질의 처리 기능이 크게 손상됩니다.",
        "effects": {
            "신경 기능": 90,
            "산소 운반": 100,
            "소화 기능": 65,
            "대사 기능": 0,
        }
    },
    "신장": {
        "system": "비뇨계",
        "color": "#bb6878",
        "function": "혈액 여과, 노폐물 배설, 수분과 전해질 균형 유지",
        "structure": "신피질, 신수질, 사구체, 세뇨관으로 구성",
        "cells": ["족세포", "근위세뇨관세포", "원위세뇨관세포", "간질세포"],
        "removal": "노폐물 배설과 수분·전해질 조절이 어려워집니다.",
        "effects": {
            "신경 기능": 80,
            "산소 운반": 100,
            "소화 기능": 90,
            "대사 기능": 45,
        }
    },
    "위": {
        "system": "소화계",
        "color": "#e7a35b",
        "function": "음식물을 저장하고 기계적·화학적으로 소화",
        "structure": "점막, 점막하층, 근육층, 장막으로 구성",
        "cells": ["벽세포", "주세포", "점액세포", "내분비세포"],
        "removal": "위의 저장 및 초기 소화 기능이 손상되는 상황입니다.",
        "effects": {
            "신경 기능": 100,
            "산소 운반": 100,
            "소화 기능": 35,
            "대사 기능": 90,
        }
    },
    "소장": {
        "system": "소화계",
        "color": "#d7ad75",
        "function": "영양소의 소화와 대부분의 영양소 흡수",
        "structure": "융모와 미세융모를 가진 점막 및 여러 층의 조직으로 구성",
        "cells": ["흡수상피세포", "배상세포", "파네트세포", "장내분비세포"],
        "removal": "영양소 흡수 면적이 줄어들어 영양 공급에 문제가 생깁니다.",
        "effects": {
            "신경 기능": 100,
            "산소 운반": 100,
            "소화 기능": 20,
            "대사 기능": 75,
        }
    },
}


CELLS = {
    "심근세포": {
        "organ": "심장",
        "shape": "가지가 뻗은 원통형에 가까운 세포",
        "function": "수축과 이완을 반복하여 심장 박동을 만들어 냅니다.",
        "features": "가로무늬, 개재판, 풍부한 미토콘드리아",
        "organelles": ["핵", "미토콘드리아", "근소포체", "리보솜", "골지체"],
    },
    "신경세포": {
        "organ": "뇌",
        "shape": "세포체에서 여러 수상돌기와 긴 축삭이 뻗는 형태",
        "function": "전기적 신호와 화학적 신호로 정보를 전달합니다.",
        "features": "수상돌기, 축삭, 시냅스, 수초",
        "organelles": ["핵", "미토콘드리아", "소포체", "골지체", "리보솜"],
    },
    "성상교세포": {
        "organ": "뇌",
        "shape": "별 모양으로 여러 돌기가 뻗는 형태",
        "function": "신경세포의 환경 유지와 대사적 지원에 관여합니다.",
        "features": "혈액뇌장벽 유지와 이온 항상성 조절",
        "organelles": ["핵", "미토콘드리아", "소포체", "리소좀"],
    },
    "제1형 폐포세포": {
        "organ": "폐",
        "shape": "매우 얇고 넓게 펼쳐진 세포",
        "function": "폐포와 모세혈관 사이에서 기체 확산을 가능하게 합니다.",
        "features": "얇은 세포질과 넓은 표면적",
        "organelles": ["핵", "미토콘드리아", "소포체", "리보솜"],
    },
    "제2형 폐포세포": {
        "organ": "폐",
        "shape": "입방형에 가까운 세포",
        "function": "폐 표면활성물질을 분비합니다.",
        "features": "층판소체를 통한 계면활성물질 저장",
        "organelles": ["핵", "층판소체", "미토콘드리아", "골지체"],
    },
    "간세포": {
        "organ": "간",
        "shape": "다각형에 가까운 세포",
        "function": "대사, 단백질 합성, 물질 처리에 관여합니다.",
        "features": "풍부한 소포체와 미토콘드리아",
        "organelles": ["핵", "미토콘드리아", "활면소포체", "골지체", "리소좀"],
    },
    "족세포": {
        "organ": "신장",
        "shape": "발돌기가 사구체 모세혈관을 감싸는 형태",
        "function": "사구체 여과 장벽을 구성합니다.",
        "features": "발돌기와 여과 틈새",
        "organelles": ["핵", "미토콘드리아", "소포체", "골지체"],
    },
    "벽세포": {
        "organ": "위",
        "shape": "둥근 형태에 가까운 분비세포",
        "function": "위산과 내인성 인자를 분비합니다.",
        "features": "분비세관과 풍부한 미토콘드리아",
        "organelles": ["핵", "미토콘드리아", "소포체", "골지체"],
    },
    "흡수상피세포": {
        "organ": "소장",
        "shape": "기둥 모양의 상피세포",
        "function": "소화된 영양소를 흡수합니다.",
        "features": "미세융모가 발달한 솔가장자리",
        "organelles": ["핵", "미토콘드리아", "골지체", "소포체"],
    },
    "내피세포": {
        "organ": "심장",
        "shape": "얇고 편평한 세포",
        "function": "혈관 안쪽 표면을 구성합니다.",
        "features": "혈관 투과성과 혈관 반응 조절",
        "organelles": ["핵", "미토콘드리아", "골지체", "소포체"],
    },
}


ORGANELLES = {
    "핵": {
        "function": "DNA를 보관하며 유전자 발현과 세포 활동을 조절합니다.",
        "structure": "핵막, 핵공, 염색질, 인으로 구성됩니다.",
        "detail": "핵막은 이중막이며 핵공을 통해 물질이 이동합니다.",
    },
    "미토콘드리아": {
        "function": "세포 호흡과 ATP 생산에 중요한 역할을 합니다.",
        "structure": "외막, 내막, 크리스타, 기질로 구성됩니다.",
        "detail": "내막의 전자전달계와 ATP 합성효소가 ATP 생산에 관여합니다.",
    },
    "소포체": {
        "function": "단백질 및 지질의 합성과 운반에 관여합니다.",
        "structure": "조면소포체와 활면소포체로 나뉩니다.",
        "detail": "조면소포체에는 리보솜이 붙어 있으며 활면소포체는 지질 합성 등에 관여합니다.",
    },
    "골지체": {
        "function": "단백질과 지질을 변형하고 분류하여 포장합니다.",
        "structure": "납작한 막성 주머니가 층층이 쌓인 구조입니다.",
        "detail": "소포를 통해 물질을 다른 세포 소기관이나 세포 밖으로 운반합니다.",
    },
    "리보솜": {
        "function": "mRNA의 정보를 이용하여 단백질을 합성합니다.",
        "structure": "크기가 다른 두 소단위체로 이루어진 복합체입니다.",
        "detail": "번역 과정에서 아미노산을 연결해 폴리펩타이드를 만듭니다.",
    },
    "리소좀": {
        "function": "세포 내부 물질을 분해하고 재활용합니다.",
        "structure": "분해 효소를 포함한 막성 소기관입니다.",
        "detail": "세포 내 소화와 오래된 소기관의 재활용에 관여합니다.",
    },
    "근소포체": {
        "function": "근육 수축에 필요한 칼슘 이온을 저장하고 방출합니다.",
        "structure": "근육세포에 특화된 소포체입니다.",
        "detail": "세포질 칼슘 농도 변화가 근육 수축 조절에 중요합니다.",
    },
    "층판소체": {
        "function": "폐 표면활성물질을 저장하고 분비합니다.",
        "structure": "막성 층판 구조를 가진 소기관입니다.",
        "detail": "폐포의 표면장력을 낮추는 계면활성물질을 저장합니다.",
    },
}


# ============================================================
# 3. 3D GEOMETRY ENGINE
# ============================================================

def hex_color(color: str) -> str:
    return color


def uv_mesh(
    surface: Callable,
    nu: int = 48,
    nv: int = 32
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:

    u = np.linspace(0, 2 * np.pi, nu)
    v = np.linspace(0, np.pi, nv)

    U, V = np.meshgrid(u, v)

    X, Y, Z = surface(U, V)

    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    Z = np.asarray(Z, dtype=float)

    i, j, k = [], [], []

    for row in range(nv - 1):
        for col in range(nu - 1):
            a = row * nu + col
            b = a + 1
            c = a + nu
            d = c + 1

            i.extend([a, b])
            j.extend([b, d])
            k.extend([c, c])

    return (
        X.ravel(),
        Y.ravel(),
        Z.ravel(),
        np.asarray(i),
        np.asarray(j),
        np.asarray(k),
    )


def add_mesh(
    fig,
    surface,
    color,
    name,
    opacity=1.0,
    nu=48,
    nv=32,
    flat=False
):
    x, y, z, i, j, k = uv_mesh(surface, nu, nv)

    fig.add_trace(go.Mesh3d(
        x=x,
        y=y,
        z=z,
        i=i,
        j=j,
        k=k,
        color=color,
        opacity=opacity,
        name=name,
        flatshading=flat,
        hovertemplate=f"{name}<extra></extra>",
        lighting=dict(
            ambient=0.48,
            diffuse=0.78,
            specular=0.32,
            roughness=0.48,
            fresnel=0.18,
        ),
        lightposition=dict(x=120, y=180, z=160),
    ))


def ellipsoid_surface(
    center,
    scale,
    deformation=0.0,
    phase=0.0
):
    cx, cy, cz = center
    sx, sy, sz = scale

    def fn(u, v):
        wave = (
            1
            + deformation
            * np.sin(3 * u + phase)
            * np.sin(2 * v)
        )

        x = cx + sx * np.cos(u) * np.sin(v) * wave
        y = cy + sy * np.sin(u) * np.sin(v) * wave
        z = cz + sz * np.cos(v) * wave

        return x, y, z

    return fn


def tube_surface(
    start,
    end,
    radius_a,
    radius_b=None,
    bend=0.0,
    phase=0.0
):
    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)

    direction = end - start
    length = np.linalg.norm(direction)

    if length < 1e-8:
        length = 1.0

    direction = direction / length

    helper = np.array([0.0, 0.0, 1.0])

    if abs(np.dot(direction, helper)) > 0.92:
        helper = np.array([0.0, 1.0, 0.0])

    axis1 = np.cross(direction, helper)
    axis1 /= np.linalg.norm(axis1)

    axis2 = np.cross(direction, axis1)
    axis2 /= np.linalg.norm(axis2)

    if radius_b is None:
        radius_b = radius_a

    def fn(u, v):
        t = (1 - np.cos(v)) / 2

        center = (
            start[None, None, :]
            + t[:, :, None] * direction[None, None, :] * length
        )

        center[:, :, 0] += bend * np.sin(np.pi * t)
        center[:, :, 1] += bend * 0.35 * np.sin(2 * np.pi * t)

        radius = (
            radius_a * (1 - t)
            + radius_b * t
        )

        radial = (
            axis1[None, None, :]
            * np.cos(u)[:, :, None]
            + axis2[None, None, :]
            * np.sin(u)[:, :, None]
        )

        xyz = center + radial * radius[:, :, None]

        return xyz[:, :, 0], xyz[:, :, 1], xyz[:, :, 2]

    return fn


def add_curve(fig, points, color, width=4, name=None):
    points = np.asarray(points, dtype=float)

    if len(points) == 0:
        return

    fig.add_trace(go.Scatter3d(
        x=points[:, 0],
        y=points[:, 1],
        z=points[:, 2],
        mode="lines",
        line=dict(color=color, width=width),
        name=name or "",
        hoverinfo="skip",
        showlegend=False,
    ))


def add_points(fig, points, color, size=5, name=""):
    points = np.asarray(points, dtype=float)

    if len(points) == 0:
        return

    fig.add_trace(go.Scatter3d(
        x=points[:, 0],
        y=points[:, 1],
        z=points[:, 2],
        mode="markers",
        marker=dict(
            size=size,
            color=color,
            opacity=0.95,
        ),
        name=name,
        hovertemplate=f"{name}<extra></extra>",
    ))


def base_figure(title="", height=680):
    fig = go.Figure()

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=19, color="#edf6ff"),
        ),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dce9f6"),
        margin=dict(l=0, r=0, t=55, b=0),
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(
                eye=dict(x=1.6, y=1.9, z=1.15)
            ),
        ),
        showlegend=False,
    )

    return fig


def add_organ_surface(fig, organ, center, scale=1.0, opacity=1.0):
    color = ORGANS[organ]["color"]

    cx, cy, cz = center

    if organ == "심장":
        def shape(u, v):
            x = 16 * np.sin(u) ** 3
            y = (
                13 * np.cos(u)
                - 5 * np.cos(2*u)
                - 2 * np.cos(3*u)
                - np.cos(4*u)
            )

            thickness = np.sin(v) * 0.45

            return (
                cx + x / 18 * scale,
                cy + y / 18 * scale,
                cz + np.cos(v) * 0.35 * scale + thickness * np.sin(u)
            )

        add_mesh(fig, shape, color, organ, opacity, 64, 36)

        # Aorta and major vessels
        add_mesh(
            fig,
            tube_surface(
                (cx, cy, cz + 0.15*scale),
                (cx + 0.05*scale, cy, cz + 1.05*scale),
                0.12*scale,
                0.10*scale
            ),
            "#d85d62",
            "대동맥",
            opacity
        )

    elif organ == "뇌":
        def shape(u, v):
            ridge = (
                1
                + 0.055*np.sin(8*u)*np.sin(7*v)
                + 0.025*np.sin(13*u + 2*v)
            )

            x = cx + 0.73*scale*np.cos(u)*np.sin(v)*ridge
            y = cy + 0.64*scale*np.sin(u)*np.sin(v)*ridge
            z = cz + 0.67*scale*np.cos(v)*ridge

            return x, y, z

        add_mesh(fig, shape, color, organ, opacity, 72, 48)

        # Brain folds, represented as surface curves
        for k in range(6):
            theta = np.linspace(0, 2*np.pi, 70)
            points = np.column_stack([
                cx + 0.72*scale*np.cos(theta),
                cy + (0.3 + k*0.055)*scale*np.sin(theta),
                cz + (k-2.5)*0.13*scale + 0.035*scale*np.sin(3*theta)
            ])
            add_curve(fig, points, "#e1b9ed", 2)

    elif organ == "폐":
        for side in [-1, 1]:
            x0 = cx + side*0.38*scale

            def lung_shape(u, v, side=side, x0=x0):
                lobes = (
                    1
                    + 0.10*np.cos(3*v)
                    + 0.035*np.sin(5*u)
                )

                x = x0 + 0.38*scale*np.cos(u)*np.sin(v)*lobes
                y = cy + 0.35*scale*np.sin(u)*np.sin(v)*lobes
                z = cz + 0.77*scale*np.cos(v)*lobes

                x += side*0.10*scale*np.cos(v)

                return x, y, z

            add_mesh(
                fig,
                lung_shape,
                color,
                "좌폐" if side < 0 else "우폐",
                opacity,
                48,
                36
            )

        # Bronchi
        for side in [-1, 1]:
            add_mesh(
                fig,
                tube_surface(
                    (cx, cy, cz + 0.45*scale),
                    (cx + side*0.43*scale, cy, cz + 0.15*scale),
                    0.075*scale,
                    0.045*scale
                ),
                "#e4d6c9",
                "기관지",
                opacity
            )

    elif organ == "간":
        def shape(u, v):
            asym = 1 + 0.18*np.cos(u) + 0.06*np.sin(3*u)

            x = cx + 0.92*scale*np.cos(u)*np.sin(v)*asym
            y = cy + 0.53*scale*np.sin(u)*np.sin(v)
            z = cz + 0.49*scale*np.cos(v)

            z += 0.13*scale*np.sin(u)*np.cos(u)

            return x, y, z

        add_mesh(fig, shape, color, organ, opacity, 64, 40)

    elif organ == "신장":
        for side in [-1, 1]:
            def shape(u, v, side=side):
                bean = 1 - 0.24*np.cos(u)

                x = cx + side*0.40*scale + 0.35*scale*np.cos(u)*np.sin(v)*bean
                y = cy + 0.31*scale*np.sin(u)*np.sin(v)
                z = cz + 0.54*scale*np.cos(v)

                return x, y, z

            add_mesh(fig, shape, color, f"{organ} {side}", opacity)

    elif organ == "위":
        def shape(u, v):
            x = cx + 0.53*scale*np.cos(u)*np.sin(v)
            y = cy + 0.40*scale*np.sin(u)*np.sin(v)
            z = cz + 0.70*scale*np.cos(v)

            x += 0.13*scale*np.sin(2*v)
            z += 0.13*scale*np.sin(u)

            return x, y, z

        add_mesh(fig, shape, color, organ, opacity, 64, 40)

    elif organ == "소장":
        # Coiled intestinal tube
        theta = np.linspace(0, 8*np.pi, 240)
        radius = 0.25 + 0.08*np.sin(5*theta)

        points = np.column_stack([
            cx + radius*np.cos(theta)*scale,
            cy + radius*np.sin(theta)*scale,
            cz + 0.14*np.sin(2*theta)*scale
        ])

        for idx in range(0, len(points)-1, 5):
            add_mesh(
                fig,
                tube_surface(
                    points[idx],
                    points[min(idx+5, len(points)-1)],
                    0.055*scale,
                    0.055*scale
                ),
                color,
                "장관",
                opacity,
                16,
                12
            )

    else:
        add_mesh(
            fig,
            ellipsoid_surface(center, (0.5*scale, 0.4*scale, 0.6*scale), 0.08),
            color,
            organ,
            opacity
        )


# ============================================================
# 4. HUMAN BODY MODEL
# ============================================================

def add_human_body(fig, traits=None, ghost=False):
    traits = traits or {}

    skin_palette = {
        "밝은색": "#e8c4a8",
        "중간": "#c99472",
        "어두운색": "#80533f",
    }

    skin = skin_palette.get(
        traits.get("skin", "중간"),
        "#c99472"
    )

    opacity = 0.17 if ghost else 1.0

    # Torso: variable-width anatomical silhouette
    def torso(u, v):
        z = 0.3 + 1.8*(1+np.cos(v))/2

        width = (
            0.43
            + 0.19*np.exp(-((z-1.85)/0.32)**2)
            - 0.10*np.exp(-((z-1.1)/0.35)**2)
            + 0.11*np.exp(-((z-0.45)/0.28)**2)
        )

        depth = 0.22 + 0.07*np.sin(np.pi*z/2.2)

        x = width*np.cos(u)
        y = depth*np.sin(u)

        return x, y, z

    add_mesh(
        fig,
        torso,
        skin,
        "인체 몸통",
        opacity,
        64,
        48
    )

    # Neck
    add_mesh(
        fig,
        tube_surface(
            (0, 0, 2.0),
            (0, 0, 2.43),
            0.17,
            0.15
        ),
        skin,
        "목",
        opacity
    )

    # Head with a slightly elongated anatomical profile
    add_mesh(
        fig,
        ellipsoid_surface(
            (0, 0, 2.75),
            (0.31, 0.29, 0.43),
            deformation=0.035
        ),
        skin,
        "머리",
        opacity,
        64,
        48
    )

    # Hair cap
    hair_palette = {
        "검은색": "#18191d",
        "갈색": "#69432d",
        "금발": "#d7b66e",
        "붉은색": "#a24f35",
    }

    hair = hair_palette.get(
        traits.get("hair", "검은색"),
        "#18191d"
    )

    def hair_shape(u, v):
        vv = v * 0.5
        x = 0.315*np.cos(u)*np.sin(vv)
        y = 0.295*np.sin(u)*np.sin(vv)
        z = 2.78 + 0.43*np.cos(vv)
        return x, y, z

    add_mesh(
        fig,
        hair_shape,
        hair,
        "머리카락",
        opacity,
        48,
        24
    )

    # Arms and legs
    limbs = [
        ((-0.40, 0, 1.95), (-0.67, 0, 1.12), 0.16, 0.105, "왼팔"),
        ((0.40, 0, 1.95), (0.67, 0, 1.12), 0.16, 0.105, "오른팔"),
        ((-0.21, 0, 0.43), (-0.23, 0, -0.75), 0.19, 0.12, "왼다리"),
        ((0.21, 0, 0.43), (0.23, 0, -0.75), 0.19, 0.12, "오른다리"),
    ]

    for start, end, r1, r2, name in limbs:
        add_mesh(
            fig,
            tube_surface(start, end, r1, r2),
            skin,
            name,
            opacity
        )

    # Eye colors
    eye_palette = {
        "갈색": "#754526",
        "파란색": "#478fcb",
        "초록색": "#4e9368",
        "회색": "#a5b2bd",
    }

    eye = eye_palette.get(
        traits.get("eye", "갈색"),
        "#754526"
    )

    if not ghost:
        for side in [-1, 1]:
            add_mesh(
                fig,
                ellipsoid_surface(
                    (side*0.12, 0.267, 2.79),
                    (0.055, 0.027, 0.035)
                ),
                "#f4e8d9",
                "눈",
                1
            )

            add_mesh(
                fig,
                ellipsoid_surface(
                    (side*0.12, 0.292, 2.79),
                    (0.023, 0.012, 0.025)
                ),
                eye,
                "홍채",
                1
            )


ORGAN_POSITIONS = {
    "뇌": (0, 0, 2.78),
    "심장": (0.12, -0.12, 1.45),
    "폐": (0, 0.0, 1.48),
    "간": (0.20, -0.02, 0.92),
    "신장": (0, 0.10, 0.82),
    "위": (-0.19, -0.08, 1.0),
    "소장": (0, -0.03, 0.63),
}


def body_scene(
    removed=None,
    traits=None,
    cutaway=False,
    selected=None
):
    removed = removed or []

    fig = base_figure(
        "HUMAN ANATOMY | 3D MODEL",
        760
    )

    add_human_body(fig, traits)

    if cutaway:
        # Transparent chest/abdominal context
        add_mesh(
            fig,
            ellipsoid_surface(
                (0, -0.015, 1.35),
                (0.47, 0.29, 0.95),
                0.04
            ),
            "#8db7d9",
            "절개 관찰 영역",
            0.12
        )

    for organ, position in ORGAN_POSITIONS.items():
        if organ in removed:
            continue

        scale = 0.55

        if organ == "뇌":
            scale = 0.55
        elif organ == "폐":
            scale = 0.72
        elif organ == "심장":
            scale = 0.52

        organ_opacity = 0.97 if cutaway else 0.83

        if selected == organ:
            organ_opacity = 1.0
            scale *= 1.13

        add_organ_surface(
            fig,
            organ,
            position,
            scale,
            organ_opacity
        )

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, range=[-1.2, 1.2]),
            yaxis=dict(visible=False, range=[-0.8, 0.8]),
            zaxis=dict(visible=False, range=[-1.0, 3.4]),
            aspectmode="manual",
            aspectratio=dict(x=1, y=0.75, z=2.1),
            camera=dict(
                eye=dict(x=1.8, y=2.2, z=1.2)
            )
        )
    )

    return fig


# ============================================================
# 5. ORGAN FOCUS MODEL
# ============================================================

def organ_scene(organ):
    fig = base_figure(
        f"ORGAN ZOOM | {organ}",
        700
    )

    add_organ_surface(
        fig,
        organ,
        (0, 0, 0),
        1.5,
        1.0
    )

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(
                eye=dict(x=1.8, y=2.1, z=1.5)
            )
        )
    )

    return fig


# ============================================================
# 6. CELL AND ORGANELLE MODEL
# ============================================================

def cell_scene(cell_name, selected_organelle=None):
    fig = base_figure(
        f"CELLULAR STRUCTURE | {cell_name}",
        720
    )

    cell_data = CELLS.get(
        cell_name,
        CELLS["심근세포"]
    )

    # Irregular cell membrane
    def cell_surface(u, v):
        distortion = (
            1
            + 0.07*np.sin(4*u)*np.sin(3*v)
            + 0.035*np.cos(7*u+v)
        )

        x = 1.2*np.cos(u)*np.sin(v)*distortion
        y = 0.84*np.sin(u)*np.sin(v)*distortion
        z = 0.65*np.cos(v)*distortion

        return x, y, z

    add_mesh(
        fig,
        cell_surface,
        "#68a6d1",
        "세포막",
        0.22,
        72,
        48
    )

    # Cytoplasm
    add_mesh(
        fig,
        ellipsoid_surface(
            (0, 0, 0),
            (1.13, 0.77, 0.59),
            0.035
        ),
        "#4b8eb8",
        "세포질",
        0.14
    )

    # Nucleus
    nucleus_color = (
        "#f3a4cc"
        if selected_organelle == "핵"
        else "#c18bda"
    )

    add_mesh(
        fig,
        ellipsoid_surface(
            (-0.18, 0.04, 0.05),
            (0.38, 0.34, 0.38),
            0.035
        ),
        nucleus_color,
        "핵",
        0.92
    )

    # Nuclear envelope
    add_mesh(
        fig,
        ellipsoid_surface(
            (-0.18, 0.04, 0.05),
            (0.405, 0.36, 0.40)
        ),
        "#e4b3e8",
        "핵막",
        0.15
    )

    # Mitochondria with folded internal membranes
    mito_positions = [
        (0.53, 0.23, 0.10),
        (0.45, -0.33, -0.10),
        (-0.62, -0.27, 0.14),
        (0.03, 0.47, -0.22),
    ]

    for index, pos in enumerate(mito_positions):
        highlight = selected_organelle == "미토콘드리아"

        add_mesh(
            fig,
            ellipsoid_surface(
                pos,
                (0.28, 0.13, 0.12),
                0.12,
                index
            ),
            "#ef9860" if highlight else "#d88c59",
            "미토콘드리아",
            1
        )

        # Cristae
        for fold in [-1, 0, 1]:
            points = []

            for t in np.linspace(-0.8, 0.8, 35):
                points.append([
                    pos[0] + t*0.22,
                    pos[1] + fold*0.027,
                    pos[2] + 0.035*np.sin(t*8 + fold)
                ])

            add_curve(
                fig,
                points,
                "#ffdfac",
                2
            )

    # Endoplasmic reticulum: connected curved membranes
    for layer in range(4):
        t = np.linspace(-1, 1, 70)

        points = np.column_stack([
            -0.60 + t*0.42,
            0.40 + layer*0.075 + 0.045*np.sin(t*8),
            -0.32 + 0.045*np.cos(t*7+layer)
        ])

        add_curve(fig, points, "#6ec7bd", 4)

    # Golgi stacks
    for layer in range(5):
        t = np.linspace(-0.6, 0.6, 45)

        points = np.column_stack([
            0.43 + 0.12*np.sin(t*3),
            -0.50 + layer*0.065,
            0.15 + t*0.12
        ])

        add_curve(fig, points, "#d5a8f0", 5)

    # Ribosomes
    rng = np.random.default_rng(42)

    ribosomes = []

    for _ in range(65):
        p = rng.uniform(-0.85, 0.85, 3)

        if np.linalg.norm(p) < 0.88:
            ribosomes.append(p)

    add_points(
        fig,
        ribosomes,
        "#f2d27d",
        3,
        "리보솜"
    )

    # Lysosomes
    for pos in [
        (0.65, -0.45, 0.35),
        (-0.70, 0.38, -0.25)
    ]:
        add_mesh(
            fig,
            ellipsoid_surface(pos, (0.12, 0.11, 0.13)),
            "#b8c66b",
            "리소좀",
            0.95
        )

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(
                eye=dict(x=1.6, y=1.8, z=1.4)
            )
        )
    )

    return fig


# ============================================================
# 7. ORGANELLE DETAIL MODEL
# ============================================================

def organelle_scene(name):
    fig = base_figure(
        f"ORGANELLE DETAIL | {name}",
        700
    )

    if name == "핵":
        add_mesh(
            fig,
            ellipsoid_surface(
                (0, 0, 0),
                (1.0, 0.8, 0.85),
                0.025
            ),
            "#b38bd7",
            "핵막",
            0.22,
            64,
            48
        )

        # Chromatin
        rng = np.random.default_rng(10)

        for i in range(12):
            points = []

            t = np.linspace(0, 1, 100)

            for q in t:
                angle = 10*np.pi*q + i*0.4
                radius = 0.2 + 0.5*q

                points.append([
                    radius*np.cos(angle),
                    radius*np.sin(angle)*0.75,
                    0.25*np.sin(angle*1.8)
                ])

            add_curve(
                fig,
                points,
                "#f0b7db",
                4
            )

        add_mesh(
            fig,
            ellipsoid_surface(
                (0.13, -0.12, 0.1),
                (0.19, 0.19, 0.19)
            ),
            "#f2c0d8",
            "인",
            1
        )

        # Nuclear pores
        for angle in np.linspace(0, 2*np.pi, 20):
            p = [
                1.0*np.cos(angle),
                0.8*np.sin(angle),
                0.0
            ]

            add_points(fig, [p], "#f6e4ff", 5, "핵공")

    elif name == "미토콘드리아":
        add_mesh(
            fig,
            ellipsoid_surface(
                (0, 0, 0),
                (1.25, 0.55, 0.55),
                0.09
            ),
            "#d58a55",
            "외막",
            0.85,
            72,
            36
        )

        # Inner membrane / cristae
        for idx in range(9):
            x = np.linspace(-0.85, 0.85, 70)

            points = np.column_stack([
                x,
                0.22*np.sin(x*8+idx*0.5),
                0.18*np.cos(x*6+idx*0.6)
            ])

            add_curve(fig, points, "#ffe1b3", 5)

        # Mitochondrial DNA
        theta = np.linspace(0, 4*np.pi, 150)

        points = np.column_stack([
            0.28*np.cos(theta),
            0.22*np.sin(theta),
            0.14*np.sin(theta*2)
        ])

        add_curve(fig, points, "#9ce4d4", 4, "미토콘드리아 DNA")

    elif name in ["소포체", "근소포체"]:
        for layer in range(9):
            t = np.linspace(-1, 1, 100)

            points = np.column_stack([
                t,
                0.12*np.sin(t*7+layer*0.4),
                (layer-4)*0.12 + 0.08*np.cos(t*5)
            ])

            add_curve(fig, points, "#66cbbd", 6)

    elif name == "골지체":
        for layer in range(8):
            t = np.linspace(-1, 1, 90)

            points = np.column_stack([
                0.85*t,
                0.10*np.sin(t*3),
                (layer-3.5)*0.13 + 0.05*np.cos(t*4)
            ])

            add_curve(fig, points, "#d7a3ed", 7)

        for pos in [
            (-0.95, 0.1, 0.1),
            (0.95, -0.1, -0.1),
            (0.4, 0.25, 0.55)
        ]:
            add_mesh(
                fig,
                ellipsoid_surface(pos, (0.12, 0.12, 0.12)),
                "#f5d0e7",
                "운반 소포"
            )

    elif name == "리보솜":
        add_mesh(
            fig,
            ellipsoid_surface(
                (0, 0, 0.18),
                (0.60, 0.52, 0.42)
            ),
            "#d5b36d",
            "대단위체"
        )

        add_mesh(
            fig,
            ellipsoid_surface(
                (0.05, 0, -0.26),
                (0.42, 0.37, 0.29)
            ),
            "#f0d18b",
            "소단위체"
        )

        points = np.column_stack([
            np.linspace(-0.8, 0.8, 80),
            0.05*np.sin(np.linspace(0, 10, 80)),
            0.48 + 0.08*np.cos(np.linspace(0, 10, 80))
        ])

        add_curve(fig, points, "#a3dfd0", 4, "mRNA")

    elif name == "리소좀":
        add_mesh(
            fig,
            ellipsoid_surface(
                (0, 0, 0),
                (0.75, 0.68, 0.72),
                0.04
            ),
            "#b4c46f",
            "리소좀 막"
        )

        rng = np.random.default_rng(21)

        points = rng.uniform(-0.5, 0.5, (55, 3))

        add_points(fig, points, "#f1e9a3", 5, "분해 효소")

    elif name == "층판소체":
        for layer in range(10):
            theta = np.linspace(0, 2*np.pi, 100)

            points = np.column_stack([
                0.7*np.cos(theta),
                0.7*np.sin(theta),
                (layer-4.5)*0.09 + 0.05*np.sin(theta*3)
            ])

            add_curve(fig, points, "#e4ad79", 5)

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data"
        )
    )

    return fig


# ============================================================
# 8. DNA DOUBLE HELIX
# ============================================================

BASE_COLORS = {
    "A": "#4da7f2",
    "T": "#e6b65c",
    "G": "#5dc69b",
    "C": "#d47bc7",
}

COMPLEMENT = {
    "A": "T",
    "T": "A",
    "G": "C",
    "C": "G",
}


def dna_scene(sequence):
    sequence = "".join(
        c for c in sequence.upper()
        if c in "ATGC"
    )

    if len(sequence) < 4:
        sequence = "ATGCGTAC"

    fig = base_figure(
        "DNA DOUBLE HELIX | BASE PAIRS",
        700
    )

    t = np.linspace(0, len(sequence)*0.75, 500)

    radius = 0.48

    strand_a = np.column_stack([
        radius*np.cos(t),
        radius*np.sin(t),
        t*0.45
    ])

    strand_b = np.column_stack([
        -radius*np.cos(t),
        -radius*np.sin(t),
        t*0.45
    ])

    add_curve(fig, strand_a, "#55b8ff", 7, "DNA strand A")
    add_curve(fig, strand_b, "#ef9c70", 7, "DNA strand B")

    for idx, base in enumerate(sequence):
        z = idx*0.75*0.45
        angle = idx*0.75

        p1 = np.array([
            radius*np.cos(angle),
            radius*np.sin(angle),
            z
        ])

        p2 = -p1.copy()
        p2[2] = z

        add_curve(
            fig,
            [p1, p2],
            "#e5d8a7",
            3
        )

        add_points(
            fig,
            [p1],
            BASE_COLORS[base],
            7,
            base
        )

        complement = COMPLEMENT[base]

        add_points(
            fig,
            [p2],
            BASE_COLORS[complement],
            7,
            complement
        )

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(
                eye=dict(x=1.5, y=1.8, z=1.0)
            )
        )
    )

    return fig


# ============================================================
# 9. GENE / TRAIT EDUCATIONAL MODEL
# ============================================================

GENES = {
    "OCA2": {
        "trait": "눈동자 색소",
        "description": "OCA2는 멜라닌 생성 및 색소 형성과 관련된 유전자입니다.",
        "variants": {
            "기본형": {
                "eye": "갈색",
                "expression": 0.85,
                "label": "색소 형성이 비교적 활발한 교육용 모델",
            },
            "색소 감소형": {
                "eye": "파란색",
                "expression": 0.25,
                "label": "색소량이 감소한 교육용 모델",
            },
            "중간형": {
                "eye": "초록색",
                "expression": 0.50,
                "label": "중간 수준의 색소 형성 모델",
            },
        },
    },
    "MC1R": {
        "trait": "머리카락 색",
        "description": "MC1R은 멜라닌 종류와 관련된 유전자 중 하나입니다.",
        "variants": {
            "기본형": {
                "hair": "검은색",
                "expression": 0.85,
                "label": "유멜라닌 중심의 단순화 모델",
            },
            "변이형 A": {
                "hair": "붉은색",
                "expression": 0.35,
                "label": "페오멜라닌 비율 변화의 교육용 모델",
            },
            "변이형 B": {
                "hair": "갈색",
                "expression": 0.60,
                "label": "색소 구성 변화의 교육용 모델",
            },
        },
    },
    "TYR": {
        "trait": "멜라닌 합성",
        "description": "TYR은 멜라닌 생합성 과정에 관여하는 티로시나아제 효소와 관련됩니다.",
        "variants": {
            "기본형": {
                "skin": "중간",
                "expression": 0.85,
                "label": "정상적인 멜라닌 합성의 단순화 모델",
            },
            "활성 감소형": {
                "skin": "밝은색",
                "expression": 0.25,
                "label": "멜라닌 합성 감소의 교육용 모델",
            },
            "중간형": {
                "skin": "어두운색",
                "expression": 0.55,
                "label": "합성 정도 차이를 보여주는 단순화 모델",
            },
        },
    },
}


def apply_gene_variant(gene, variant):
    result = dict(st.session_state.original_traits)

    for key, value in st.session_state.modified_traits.items():
        result[key] = value

    gene_data = GENES[gene]["variants"][variant]

    for key in ["eye", "hair", "skin"]:
        if key in gene_data:
            result[key] = gene_data[key]

    st.session_state.modified_traits = {
        k: v for k, v in result.items()
        if v != st.session_state.original_traits.get(k)
    }

    return result


def trait_scene():
    traits = dict(st.session_state.original_traits)
    traits.update(st.session_state.modified_traits)

    fig = base_figure(
        "MODIFIED HUMAN PHENOTYPE",
        700
    )

    # 변경된 형질을 실제 3D 인체 모델에 적용
    add_human_body(fig, traits, ghost=False)

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, range=[-1.4, 1.4]),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False, range=[-1, 3.4]),
            aspectmode="manual",
            aspectratio=dict(x=1, y=0.7, z=1.9),
        )
    )

    return fig


# ============================================================
# 10. ORGAN REMOVAL PHYSIOLOGY MODEL
# ============================================================

BASE_PHYSIOLOGY = {
    "신경 기능": 100,
    "산소 운반": 100,
    "소화 기능": 100,
    "대사 기능": 100,
}


def calculate_physiology(removed):
    values = dict(BASE_PHYSIOLOGY)

    if not removed:
        return values

    # Educational index model, not a clinical prediction.
    for organ in removed:
        effects = ORGANS[organ]["effects"]

        for key, value in effects.items():
            if key == "신경 기능":
                values[key] = min(values[key], value)
            else:
                values[key] = min(values[key], value)

    # Additional systemic interaction
    if "심장" in removed:
        values["산소 운반"] = 0

    if "폐" in removed:
        values["산소 운반"] = min(
            values["산소 운반"],
            10
        )

    if "뇌" in removed:
        values["신경 기능"] = 0

    return values


def physiology_chart(values):
    df = pd.DataFrame({
        "생리 기능": list(values.keys()),
        "상대 기능 지수": list(values.values())
    })

    fig = px.bar(
        df,
        x="생리 기능",
        y="상대 기능 지수",
        range_y=[0, 100],
        text="상대 기능 지수",
    )

    fig.update_traces(
        marker_color="#55b8d8",
        textposition="outside"
    )

    fig.update_layout(
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#dce9f6",
        margin=dict(l=10, r=10, t=20, b=10),
    )

    return fig


# ============================================================
# 11. DRUG EDUCATION DATABASE
# ============================================================

DRUGS = {
    "일반적인 진통제": {
        "category": "비마약성 진통제",
        "target": "통증 및 염증 관련 신호 전달",
        "effect": "통증 인식이나 염증 반응을 감소시키는 약물군입니다.",
        "risk": "약물 종류에 따라 위장관, 간, 신장 등에 부작용이 발생할 수 있습니다.",
        "vision": "시각 변화가 일반적인 주된 작용은 아닙니다.",
        "visual": "normal",
        "clinical": "통증 조절",
    },
    "국소마취제": {
        "category": "마취제",
        "target": "전압 개폐성 나트륨 통로",
        "effect": "신경의 활동전위 발생과 전도에 영향을 줍니다.",
        "risk": "부적절한 사용은 신경계와 심혈관계에 심각한 영향을 줄 수 있습니다.",
        "vision": "국소적인 감각 전달 변화가 핵심이며 환각을 목적으로 하는 약물이 아닙니다.",
        "visual": "blur",
        "clinical": "국소 마취",
    },
    "전신마취제": {
        "category": "마취제",
        "target": "중추신경계의 신경 전달",
        "effect": "의료진의 감시 아래 의식과 감각을 조절하는 데 사용됩니다.",
        "risk": "호흡과 순환에 영향을 줄 수 있어 전문적인 감시가 필요합니다.",
        "vision": "일반적인 각성 상태의 시각 경험과 구별되는 의식 변화가 나타날 수 있습니다.",
        "visual": "fade",
        "clinical": "수술 및 시술",
    },
    "항히스타민제": {
        "category": "알레르기 치료제",
        "target": "히스타민 수용체",
        "effect": "알레르기 반응과 관련된 신호 전달을 억제합니다.",
        "risk": "일부 약물은 졸림과 집중력 저하를 유발할 수 있습니다.",
        "vision": "졸림과 함께 주의력 및 시각적 집중이 저하될 수 있습니다.",
        "visual": "soft",
        "clinical": "알레르기 치료",
    },
    "기관지확장제": {
        "category": "호흡기 치료제",
        "target": "기관지 평활근",
        "effect": "기관지를 확장하여 공기 흐름을 개선합니다.",
        "risk": "종류에 따라 심박수 증가나 떨림이 나타날 수 있습니다.",
        "vision": "시각적 환각이 주된 작용은 아닙니다.",
        "visual": "normal",
        "clinical": "천식 등 호흡기 질환",
    },
    "항우울제": {
        "category": "정신건강 치료제",
        "target": "신경전달물질 관련 신호 체계",
        "effect": "특정 신경전달물질의 작용을 조절하여 증상 개선을 돕습니다.",
        "risk": "약물에 따라 부작용과 상호작용이 달라 전문적인 진료가 필요합니다.",
        "vision": "효과는 개인과 약물에 따라 다르며 즉각적인 시각 변화로 설명할 수 없습니다.",
        "visual": "soft",
        "clinical": "우울증 등 치료",
    },
    "중추신경계 자극제": {
        "category": "중추신경계 작용 약물",
        "target": "각성 및 주의력 관련 신경 회로",
        "effect": "특정 질환의 치료에서 각성과 주의력 조절에 활용됩니다.",
        "risk": "심박수, 수면, 식욕 등에 영향을 줄 수 있으며 의료적 관리가 필요합니다.",
        "vision": "주의력과 각성 상태가 달라질 수 있으나 시각 효과는 일정하지 않습니다.",
        "visual": "focus",
        "clinical": "일부 주의력 관련 질환 치료",
    },
    "오피오이드 진통제": {
        "category": "강력한 진통제",
        "target": "오피오이드 수용체",
        "effect": "통증 신호 전달과 통증 인식에 관여합니다.",
        "risk": "호흡 억제와 의식 저하 등 심각한 위험이 있어 의료적 관리가 필수적입니다.",
        "vision": "시각적 환각을 일반적인 효과로 단정할 수 없습니다. 의식과 각성 상태가 저하될 수 있습니다.",
        "visual": "fade",
        "clinical": "특정 상황의 중증 통증 관리",
    },
    "펜타닐 계열 진통제": {
        "category": "강력한 오피오이드 진통제",
        "target": "중추신경계 오피오이드 수용체",
        "effect": "의료 환경에서 특정 중증 통증을 관리하는 데 사용되는 강력한 진통제 계열입니다.",
        "risk": "호흡 억제와 의식 저하 등 생명을 위협할 수 있는 위험이 있습니다.",
        "vision": "다채로운 시각적 환각이 대표적이거나 예측 가능한 효과라는 근거는 없습니다.",
        "visual": "fade",
        "clinical": "엄격한 의료적 감독이 필요한 통증 관리",
    },
    "수면·진정제": {
        "category": "진정 작용 약물",
        "target": "중추신경계 억제성 신호",
        "effect": "불안 완화나 수면 유도 등 특정 의료 목적에 활용됩니다.",
        "risk": "과도한 진정과 호흡 억제, 다른 중추신경계 억제 약물과의 상호작용에 주의해야 합니다.",
        "vision": "졸림과 반응 속도 저하 등으로 시각적 집중이 저하될 수 있습니다.",
        "visual": "blur",
        "clinical": "불안 및 수면 관련 치료",
    },
    "항경련제": {
        "category": "신경계 치료제",
        "target": "신경세포의 흥분성 조절",
        "effect": "비정상적인 신경 흥분을 조절하여 발작을 예방하거나 줄이는 데 사용됩니다.",
        "risk": "약물별로 졸림, 어지러움 등 부작용이 다릅니다.",
        "vision": "일부 약물에서 시야 흐림이나 복시 등의 부작용이 보고됩니다.",
        "visual": "blur",
        "clinical": "뇌전증 등 신경계 질환",
    },
}


# ============================================================
# 12. MEDICAL DRUG DELIVERY VISUALIZATION
# ============================================================

def drug_delivery_scene(drug_name, frame=0):
    fig = base_figure(
        "CLINICAL DRUG DELIVERY | EDUCATIONAL MODEL",
        570
    )

    add_human_body(fig, ghost=True)

    # Abstract clinical pathway.
    # This is not a needle/injection procedure simulation.
    path = np.array([
        [-0.9, 0.0, 1.2],
        [-0.55, 0.0, 1.45],
        [-0.2, 0.0, 1.5],
        [0.0, 0.0, 1.45],
        [0.1, 0.0, 1.2],
    ])

    add_curve(
        fig,
        path,
        "#69d7e7",
        6,
        "가상 전달 경로"
    )

    t = (frame % 20) / 20.0

    particles = []

    for offset in np.linspace(0, 0.8, 9):
        pos = min(1.0, (t + offset) % 1.0)

        idx = min(
            len(path)-2,
            int(pos*(len(path)-1))
        )

        local = pos*(len(path)-1)-idx

        p = (
            path[idx]*(1-local)
            + path[idx+1]*local
        )

        particles.append(p)

    add_points(
        fig,
        particles,
        "#7ce8e2",
        7,
        "약물 전달 입자"
    )

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="manual",
            aspectratio=dict(x=1, y=0.7, z=1.7)
        )
    )

    return fig


def first_person_scene(drug_name, intensity=0.45):
    data = DRUGS[drug_name]
    visual = data["visual"]

    fig = base_figure(
        "ABSTRACT FIRST-PERSON VISUAL FIELD",
        580
    )

    # 3D field surface. Effects are schematic, not a real drug experience.
    x = np.linspace(-1, 1, 65)
    y = np.linspace(-1, 1, 65)

    X, Y = np.meshgrid(x, y)

    R = np.sqrt(X**2 + Y**2)

    if visual == "blur":
        distortion = intensity * 0.25 * np.sin(7*R)
        Z = 0.06*np.cos(4*R) + distortion

    elif visual == "fade":
        distortion = intensity * 0.3 * R
        Z = -distortion

    elif visual == "soft":
        Z = 0.10*np.cos(3*R)*intensity

    elif visual == "focus":
        Z = 0.13*np.exp(-5*R**2)*intensity

    else:
        Z = np.zeros_like(X)

    if visual in ["fade", "blur"]:
        colorscale = "Cividis"
    elif visual == "focus":
        colorscale = "Blues"
    else:
        colorscale = "Greys"

    fig.add_trace(go.Surface(
        x=X,
        y=Y,
        z=Z,
        surfacecolor=R,
        colorscale=colorscale,
        opacity=0.9,
        showscale=False,
        hoverinfo="skip",
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(
                eye=dict(x=0, y=0, z=2.3)
            ),
            aspectmode="manual",
            aspectratio=dict(x=1.5, y=1, z=0.35),
        )
    )

    return fig


# ============================================================
# 13. DNA MUTATION TOOLS
# ============================================================

def mutate_sequence(sequence, position, new_base):
    sequence = list(sequence.upper())

    if not sequence:
        return sequence

    position = int(position)

    if position < 0 or position >= len(sequence):
        return "".join(sequence)

    if new_base not in ["A", "T", "G", "C"]:
        return "".join(sequence)

    sequence[position] = new_base

    return "".join(sequence)


def sequence_comparison(original, changed):
    rows = []

    for i, (a, b) in enumerate(
        zip(original, changed),
        start=1
    ):
        rows.append({
            "위치": i,
            "기존 염기": a,
            "변경 염기": b,
            "변화": "변이" if a != b else "동일",
        })

    return pd.DataFrame(rows)


def codon_translation(sequence):
    codons = {
        "ATG": "메티오닌",
        "TTT": "페닐알라닌",
        "TTC": "페닐알라닌",
        "TAA": "종결",
        "TAG": "종결",
        "TGA": "종결",
        "GCT": "알라닌",
        "GCC": "알라닌",
        "GCA": "알라닌",
        "GCG": "알라닌",
        "GGT": "글리신",
        "GGC": "글리신",
        "GGA": "글리신",
        "GGG": "글리신",
        "CGT": "아르기닌",
        "CGC": "아르기닌",
        "CGA": "아르기닌",
        "CGG": "아르기닌",
    }

    result = []

    for i in range(0, len(sequence)-2, 3):
        codon = sequence[i:i+3]

        result.append({
            "코돈": codon,
            "아미노산": codons.get(
                codon,
                "기타 아미노산"
            )
        })

    return pd.DataFrame(result)


# ============================================================
# 14. SIDEBAR NAVIGATION
# ============================================================

st.sidebar.markdown("# 🧬 CELLIT")
st.sidebar.caption("3D BIOLOGY EXPLORATION LAB")
st.sidebar.divider()

PAGES = [
    "인체 탐구",
    "장기 제거 실험",
    "세포 탐구",
    "세포 소기관",
    "DNA 탐구",
    "유전 형질 실험",
    "약물과 생리 반응",
]

st.session_state.page = st.sidebar.radio(
    "탐구 실험실",
    PAGES,
    index=PAGES.index(st.session_state.page)
    if st.session_state.page in PAGES
    else 0
)

st.sidebar.divider()

st.sidebar.markdown("### 탐구 진행 단계")

stages = [
    ("body", "01 인체"),
    ("organ", "02 장기"),
    ("cell", "03 세포"),
    ("organelle", "04 소기관"),
    ("dna", "05 DNA"),
    ("trait", "06 형질"),
]

for stage_key, stage_label in stages:
    if st.session_state.stage == stage_key:
        st.sidebar.markdown(
            f"**<span style='color:#7dd3fc'>{stage_label} ●</span>**",
            unsafe_allow_html=True
        )
    else:
        st.sidebar.caption(stage_label)

st.sidebar.divider()

if st.sidebar.button("처음 상태로 초기화", use_container_width=True):
    for key, value in DEFAULTS.items():
        st.session_state[key] = value
    st.rerun()


# ============================================================
# 15. HEADER
# ============================================================

st.markdown("# CELLIT")
st.markdown(
    "### 3D 생명과학 탐구 실험실"
)

st.caption(
    "인체의 구조부터 세포, 소기관, DNA, 유전 형질과 생리 반응까지 "
    "하나의 연결된 3D 환경에서 탐구합니다."
)

st.divider()


# ============================================================
# 16. PAGE 1 - HUMAN / ORGAN EXPLORATION
# ============================================================

if st.session_state.page == "인체 탐구":

    left, right = st.columns([1.65, 1])

    with left:
        st.subheader("인체 3D 모델")

        cutaway = st.toggle(
            "해부 관찰 모드",
            value=True,
            help="인체 내부 장기를 관찰하기 위한 교육용 표현입니다."
        )

        fig = body_scene(
            removed=st.session_state.removed_organs,
            traits={
                **st.session_state.original_traits,
                **st.session_state.modified_traits,
            },
            cutaway=cutaway,
            selected=st.session_state.selected_organ,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="human_body_scene",
            config={
                "displaylogo": False,
                "scrollZoom": True,
                "responsive": True,
            }
        )

    with right:
        st.subheader("장기 선택")

        selected = st.selectbox(
            "탐구할 장기",
            list(ORGANS.keys()),
            index=list(ORGANS.keys()).index(
                st.session_state.selected_organ
            )
        )

        st.session_state.selected_organ = selected

        data = ORGANS[selected]

        st.markdown(
            f"<span class='lab-tag'>{data['system']}</span>",
            unsafe_allow_html=True
        )

        st.markdown(f"### {selected}")

        st.write(data["function"])

        st.markdown("**구조**")
        st.write(data["structure"])

        st.markdown("**구성 세포**")

        for cell in data["cells"]:
            st.write(f"• {cell}")

        if st.button(
            f"{selected} 확대 탐구 →",
            use_container_width=True
        ):
            st.session_state.stage = "organ"
            st.rerun()

        st.divider()

        st.markdown("**연결된 다음 탐구 단계**")
        st.info(
            "장기를 선택한 후 확대 탐구를 누르면 "
            "해당 장기의 3D 구조를 중심으로 탐구합니다."
        )


# ============================================================
# 17. PAGE 2 - ORGAN REMOVAL
# ============================================================

elif st.session_state.page == "장기 제거 실험":

    st.subheader("장기 제거에 따른 생리적 변화")
    st.caption(
        "가상의 장기 기능 상실 상황을 모델링합니다. "
        "실제 수술이나 인체 실험을 재현하는 기능은 아닙니다."
    )

    col1, col2 = st.columns([1.4, 1])

    with col1:
        removed = st.multiselect(
            "가상 실험에서 기능을 제거할 장기",
            list(ORGANS.keys()),
            default=st.session_state.removed_organs
        )

        st.session_state.removed_organs = removed

        fig = body_scene(
            removed=removed,
            cutaway=True,
            selected=None
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="removal_body"
        )

    with col2:
        values = calculate_physiology(removed)

        st.markdown("### 생리 기능 변화")

        for key, value in values.items():
            st.metric(
                key,
                f"{value}/100",
                delta=f"{value-100}",
                delta_color="normal"
            )

        st.plotly_chart(
            physiology_chart(values),
            use_container_width=True
        )

    st.divider()

    if not removed:
        st.success(
            "현재 모든 장기의 기능이 유지되는 기본 상태입니다."
        )
    else:
        st.markdown("### 예상되는 생물학적 문제")

        for organ in removed:
            st.markdown(
                f"<div class='lab-card'>"
                f"<h4>{organ}</h4>"
                f"<p>{ORGANS[organ]['removal']}</p>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.warning(
        "생리 기능 지수는 장기 기능의 관계를 학습하기 위한 "
        "임의의 상대 지표이며 실제 생존율이나 임상 수치가 아닙니다."
    )


# ============================================================
# 18. PAGE 3 - ORGAN TO CELL DRILL DOWN
# ============================================================

elif st.session_state.page == "세포 탐구":

    st.subheader("장기에서 세포로 확대")

    organ = st.selectbox(
        "상위 장기",
        list(ORGANS.keys()),
        index=list(ORGANS.keys()).index(
            st.session_state.selected_organ
        )
    )

    st.session_state.selected_organ = organ

    available_cells = ORGANS[organ]["cells"]

    selected_cell = st.selectbox(
        "해당 장기를 구성하는 세포",
        available_cells
    )

    st.session_state.selected_cell = selected_cell

    left, right = st.columns([1.5, 1])

    with left:
        fig = cell_scene(selected_cell)

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="cell_scene"
        )

    with right:
        data = CELLS.get(selected_cell)

        if data is None:
            st.info(
                "이 세포의 상세 3D 정보는 다음 모델 확장 단계에서 추가할 수 있습니다."
            )
        else:
            st.markdown(f"### {selected_cell}")

            st.write(f"**형태:** {data['shape']}")
            st.write(f"**기능:** {data['function']}")
            st.write(f"**특징:** {data['features']}")

            st.markdown("#### 포함된 소기관")

            for organelle in data["organelles"]:
                st.write(f"• {organelle}")

            if st.button(
                "세포 내부 소기관 확대 →",
                use_container_width=True
            ):
                st.session_state.stage = "organelle"
                st.rerun()


# ============================================================
# 19. PAGE 4 - ORGANELLES
# ============================================================

elif st.session_state.page == "세포 소기관":

    st.subheader("세포 내부 구조 탐구")

    cell_name = st.selectbox(
        "탐구할 세포",
        list(CELLS.keys()),
        index=list(CELLS.keys()).index(
            st.session_state.selected_cell
        )
        if st.session_state.selected_cell in CELLS
        else 0
    )

    available = CELLS[cell_name]["organelles"]

    selected_organelle = st.selectbox(
        "확대할 세포 소기관",
        available
    )

    st.session_state.selected_organelle = selected_organelle

    left, right = st.columns([1.5, 1])

    with left:
        fig = organelle_scene(selected_organelle)

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="organelle_scene"
        )

    with right:
        data = ORGANELLES.get(selected_organelle)

        if data:
            st.markdown(f"### {selected_organelle}")

            st.markdown("**기능**")
            st.write(data["function"])

            st.markdown("**구조**")
            st.write(data["structure"])

            st.markdown("**심화 설명**")
            st.write(data["detail"])

            if selected_organelle == "핵":
                if st.button(
                    "핵 내부 DNA 확대 →",
                    use_container_width=True
                ):
                    st.session_state.stage = "dna"
                    st.rerun()


# ============================================================
# 20. PAGE 5 - DNA EXPLORATION
# ============================================================

elif st.session_state.page == "DNA 탐구":

    st.subheader("DNA 이중나선과 염기서열")

    st.write(
        "DNA는 A(아데닌), T(티민), G(구아닌), "
        "C(사이토신)의 네 가지 염기로 구성됩니다."
    )

    original = st.session_state.dna_sequence

    left, right = st.columns([1.5, 1])

    with left:
        fig = dna_scene(original)

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="dna_model"
        )

    with right:
        st.markdown("### 염기서열 편집")

        st.code(
            " ".join(original),
            language="text"
        )

        position = st.number_input(
            "변경할 염기 위치",
            min_value=1,
            max_value=len(original),
            value=4,
            step=1
        )

        new_base = st.selectbox(
            "새로운 염기",
            ["A", "T", "G", "C"]
        )

        if st.button(
            "염기 변경",
            use_container_width=True
        ):
            st.session_state.dna_sequence = mutate_sequence(
                original,
                position-1,
                new_base
            )

            st.rerun()

        if st.button(
            "원래 서열로 복구",
            use_container_width=True
        ):
            st.session_state.dna_sequence = DEFAULTS["dna_sequence"]
            st.rerun()

    changed = st.session_state.dna_sequence

    st.divider()

    st.markdown("### 염기서열 비교")

    st.dataframe(
        sequence_comparison(original, changed),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### 코돈과 아미노산")

    st.dataframe(
        codon_translation(changed),
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "이 서열은 교육용 예시입니다. 실제 인간 유전자의 전체 서열이나 "
        "실제 단백질의 기능을 재현하는 모델이 아닙니다."
    )


# ============================================================
# 21. PAGE 6 - GENETIC TRAIT SIMULATION
# ============================================================

elif st.session_state.page == "유전 형질 실험":

    st.subheader("유전자 변이와 표현형 변화")

    st.write(
        "유전자의 차이가 단백질의 기능과 발현에 영향을 주고, "
        "그 결과 표현형의 차이로 연결될 수 있다는 원리를 "
        "단순화하여 탐구합니다."
    )

    left, right = st.columns([1.4, 1])

    with left:
        fig = trait_scene()

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="trait_scene"
        )

        st.caption(
            "왼쪽 모델은 기준 표현형, 오른쪽 모델은 변형 표현형을 "
            "비교하는 교육용 모형입니다."
        )

    with right:
        gene = st.selectbox(
            "탐구 유전자",
            list(GENES.keys())
        )

        st.session_state.selected_gene = gene

        gene_data = GENES[gene]

        st.markdown(f"### {gene}")
        st.write(gene_data["description"])

        variant = st.selectbox(
            "유전자 변이 유형",
            list(gene_data["variants"].keys())
        )

        if st.button(
            "유전자 변이 적용",
            use_container_width=True
        ):
            apply_gene_variant(gene, variant)
            st.rerun()

        if st.button(
            "기준 형질로 복구",
            use_container_width=True
        ):
            st.session_state.modified_traits = {}
            st.rerun()

    st.divider()

    traits = dict(st.session_state.original_traits)
    traits.update(st.session_state.modified_traits)

    st.markdown("### 현재 표현형")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "눈동자 색",
        traits["eye"],
        "변화" if traits["eye"] != st.session_state.original_traits["eye"] else "기준"
    )

    c2.metric(
        "머리카락 색",
        traits["hair"],
        "변화" if traits["hair"] != st.session_state.original_traits["hair"] else "기준"
    )

    c3.metric(
        "피부 색상 모델",
        traits["skin"],
        "변화" if traits["skin"] != st.session_state.original_traits["skin"] else "기준"
    )

    st.markdown("### 유전자 발현 수준의 교육용 비교")

    expression = GENES[gene]["variants"][variant]["expression"]

    expression_df = pd.DataFrame({
        "구분": ["기준형", "선택한 변이형"],
        "상대 발현 지수": [0.85, expression]
    })

    chart = px.bar(
        expression_df,
        x="구분",
        y="상대 발현 지수",
        range_y=[0, 1],
        text_auto=".2f"
    )

    chart.update_layout(
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#dce9f6",
    )

    st.plotly_chart(
        chart,
        use_container_width=True
    )

    st.info(
        "실제 눈동자·머리카락·피부 색은 여러 유전자와 환경 요인의 영향을 "
        "받습니다. 이 화면은 특정 유전자 하나가 하나의 형질을 결정한다고 "
        "단정하지 않는 교육용 단순화 모델입니다."
    )

    st.markdown("### 유전도 탐구")

    st.write(
        "아래는 특정 형질이 부모에게서 자손에게 전달되는 방식을 "
        "설명하기 위한 가상의 단일 유전자 우성·열성 모델입니다."
    )

    parent_a = st.selectbox(
        "부모 A의 대립유전자",
        ["AA", "Aa", "aa"]
    )

    parent_b = st.selectbox(
        "부모 B의 대립유전자",
        ["AA", "Aa", "aa"]
    )

    alleles_a = list(parent_a)
    alleles_b = list(parent_b)

    punnett = pd.DataFrame(
        [
            [alleles_a[0]+alleles_b[0], alleles_a[0]+alleles_b[1]],
            [alleles_a[1]+alleles_b[0], alleles_a[1]+alleles_b[1]],
        ],
        index=["A", "a"],
        columns=["B", "b"]
    )

    st.dataframe(
        punnett,
        use_container_width=True
    )

    offspring = [
        punnett.iloc[0, 0],
        punnett.iloc[0, 1],
        punnett.iloc[1, 0],
        punnett.iloc[1, 1],
    ]

    counts = pd.Series(offspring).value_counts()

    offspring_df = pd.DataFrame({
        "유전자형": counts.index,
        "예상 비율": counts.values/4*100
    })

    st.plotly_chart(
        px.pie(
            offspring_df,
            names="유전자형",
            values="예상 비율",
            hole=0.45
        ),
        use_container_width=True
    )


# ============================================================
# 22. PAGE 7 - PHARMACOLOGY / VISUAL FIELD
# ============================================================

elif st.session_state.page == "약물과 생리 반응":

    st.subheader("약물 작용과 인체의 생리 반응")

    st.warning(
        "이 실험실은 의학·약리학 학습을 위한 가상 모델입니다. "
        "실제 약물의 사용법이나 투여량을 제공하지 않습니다. "
        "약물은 의료진의 처방과 감독 아래 사용되어야 합니다."
    )

    drug_name = st.selectbox(
        "약물 분류 선택",
        list(DRUGS.keys())
    )

    st.session_state.drug = drug_name

    drug = DRUGS[drug_name]

    st.markdown(
        f"<span class='lab-tag'>{drug['category']}</span>"
        f"<span class='lab-tag'>{drug['clinical']}</span>",
        unsafe_allow_html=True
    )

    st.markdown(f"### {drug_name}")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**작용 대상**")
        st.write(drug["target"])

        st.markdown("**주요 작용**")
        st.write(drug["effect"])

    with c2:
        st.markdown("**위험과 부작용**")
        st.write(drug["risk"])

        st.markdown("**시각 및 인지 반응**")
        st.write(drug["vision"])

    st.divider()

    st.markdown("### 가상 약물 전달 시각화")

    st.caption(
        "실제 주사나 투약 방법을 묘사하지 않고, "
        "의료 환경에서 약물 성분이 체내에 전달되는 개념을 "
        "추상적인 입자 애니메이션으로 표현합니다."
    )

    frame = st.slider(
        "전달 과정 프레임",
        0,
        19,
        0,
        key="drug_frame"
    )

    fig = drug_delivery_scene(
        drug_name,
        frame
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="drug_delivery"
    )

    st.divider()

    st.markdown("### 1인칭 시야의 추상적 시각화")

    st.caption(
        "약물에 따라 달라질 수 있는 각성, 집중, 시야 흐림, "
        "의식 저하 등의 개념을 교육용 시각 효과로 나타냅니다. "
        "실제 경험을 재현하거나 특정 약물의 효과를 예측하지 않습니다."
    )

    intensity = st.slider(
        "시각 효과 표현 강도",
        0.0,
        1.0,
        0.45,
        0.05
    )

    vision_fig = first_person_scene(
        drug_name,
        intensity
    )

    st.plotly_chart(
        vision_fig,
        use_container_width=True,
        key="first_person_visual"
    )

    st.markdown("### 약리학적 학습 포인트")

    st.write(
        f"선택한 약물군은 **{drug['target']}**에 작용합니다. "
        f"주요 의학적 활용 분야는 **{drug['clinical']}**입니다."
    )

    st.info(
        "약물의 실제 반응은 개인의 건강 상태, 다른 약물과의 상호작용, "
        "의학적 상황 등에 따라 달라집니다. 위 시각화는 "
        "실제 약물 반응의 예측 모델이 아닙니다."
    )


# ============================================================
# 23. FOOTER
# ============================================================

st.divider()

st.markdown("""
<div style="text-align:center; padding:20px 0;">
    <div style="font-size:1.2rem; font-weight:800; color:#7dd3fc;">
        CELLIT
    </div>
    <div style="color:#8fa4ba; font-size:0.8rem;">
        3D Biology Exploration Lab
    </div>
    <div style="color:#71849a; font-size:0.72rem; margin-top:8px;">
        Educational visualization · Not a clinical diagnostic system
    </div>
</div>
""", unsafe_allow_html=True)
