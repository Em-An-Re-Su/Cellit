
# ============================================================
# LIFE SCIENCE 3D LAB
# Streamlit Cloud용 통합 생명과학 시뮬레이터
#
# 주요 기능
# 1. 3D 인체 및 장기 탐색
# 2. 메스 절개 및 장기 제거 실험
# 3. 장기 -> 조직 -> 세포 -> 소기관 단계별 확대
# 4. 3D 세포 및 소기관 탐색
# 5. 3D DNA 이중나선 및 유전자 변이 실험
# 6. 유전자형 -> 형질 발현 교육용 시뮬레이션
# 7. 약물의 약리학적 작용 및 임상적 반응
# 8. 1인칭 시야의 교육용 시뮬레이션
#
# 주의:
# 이 프로그램의 생리학적 수치는 교육용 가상 모델이다.
# 실제 진단, 치료, 유전자 편집, 약물 투여에 사용할 수 없다.
# ============================================================

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.spatial.transform import Rotation
import math
import random

# ============================================================
# 0. 기본 설정
# ============================================================

st.set_page_config(
    page_title="Life Science 3D Lab",
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
        radial-gradient(circle at 15% 10%, #172b43 0%, transparent 35%),
        linear-gradient(135deg, #09121f, #101d2d 55%, #101827);
    color: #e8eef7;
}

h1, h2, h3 {
    color: #f0f5ff !important;
}

p, label, span {
    color: #d4deed;
}

[data-testid="stSidebar"] {
    background: #0d1827;
    border-right: 1px solid #263c55;
}

[data-testid="stMetric"] {
    background: #15263a;
    padding: 15px;
    border: 1px solid #2b405a;
    border-radius: 12px;
}

div[data-testid="stExpander"] {
    border: 1px solid #2b405a;
    border-radius: 12px;
}

.stButton > button {
    background: linear-gradient(135deg, #1678c9, #365ed9);
    color: white;
    border: 0;
    border-radius: 9px;
    font-weight: 600;
    min-height: 42px;
}

.stButton > button:hover {
    border: 1px solid #72baff;
    color: white;
}

div[data-testid="stAlert"] {
    border-radius: 10px;
}

.small-caption {
    color: #9eb3cb;
    font-size: 0.85rem;
}

.panel {
    padding: 17px;
    background: #142438;
    border: 1px solid #2a4058;
    border-radius: 14px;
    margin-bottom: 12px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 1. 상수 및 데이터
# ============================================================

ORGAN_DATA = {
    "뇌": {
        "position": (0, 0, 6.1),
        "size": (0.48, 0.39, 0.38),
        "color": "#d98ca6",
        "description": "신경계의 중추로 감각 정보 처리, 운동 조절, 기억, 사고 등을 담당한다.",
        "cells": ["신경세포", "성상교세포", "희소돌기아교세포", "미세아교세포"],
        "effects": [
            ("신경 정보 처리", 0.25),
            ("운동 조절", 0.35),
            ("기억 및 인지", 0.30),
            ("자율신경 조절", 0.20)
        ],
        "removal": "뇌의 기능이 광범위하게 소실되면 의식, 호흡 조절, 운동 및 감각 등 생명 유지 기능에 심각한 문제가 발생한다."
    },
    "심장": {
        "position": (0, -0.05, 4.55),
        "size": (0.30, 0.25, 0.43),
        "color": "#d94d58",
        "description": "수축과 이완을 반복하여 혈액을 온몸으로 순환시키는 펌프 기관이다.",
        "cells": ["심근세포", "내피세포", "섬유아세포", "박동조율세포"],
        "effects": [
            ("혈액 순환", 0.55),
            ("산소 운반", 0.25),
            ("혈압 유지", 0.20)
        ],
        "removal": "심장은 혈액 순환을 담당하므로 기능이 정지하면 산소와 영양분의 공급이 중단되어 생명 유지가 불가능해진다."
    },
    "폐": {
        "position": (0, 0.0, 4.55),
        "size": (0.78, 0.30, 0.53),
        "color": "#e58d9b",
        "description": "폐포에서 산소와 이산화탄소의 기체 교환이 일어난다.",
        "cells": ["폐포 1형 세포", "폐포 2형 세포", "섬모상피세포", "폐포 대식세포"],
        "effects": [
            ("산소 교환", 0.55),
            ("이산화탄소 배출", 0.35),
            ("혈액 pH 조절", 0.10)
        ],
        "removal": "폐의 기능이 감소하면 혈액의 산소 공급이 부족해지고 이산화탄소 배출과 산-염기 균형 유지에 문제가 생긴다."
    },
    "간": {
        "position": (0.37, 0.0, 3.85),
        "size": (0.68, 0.30, 0.32),
        "color": "#92583f",
        "description": "영양소 대사, 해독, 담즙 생성, 혈당 조절, 혈장 단백질 합성 등을 수행한다.",
        "cells": ["간세포", "쿠퍼세포", "간성상세포", "담관상피세포"],
        "effects": [
            ("대사 기능", 0.35),
            ("해독 및 물질 처리", 0.30),
            ("단백질 합성", 0.20),
            ("담즙 생성", 0.15)
        ],
        "removal": "간 기능이 심각하게 손상되면 대사와 해독, 혈액 응고 인자 합성, 영양소 처리 등에 문제가 발생한다."
    },
    "위": {
        "position": (-0.34, -0.02, 3.65),
        "size": (0.35, 0.27, 0.40),
        "color": "#d58d73",
        "description": "음식물을 일시적으로 저장하고 위산과 소화 효소를 이용해 소화를 시작한다.",
        "cells": ["점액분비세포", "벽세포", "주세포", "내분비세포"],
        "effects": [
            ("음식물 저장", 0.25),
            ("단백질 소화", 0.45),
            ("소화액 분비", 0.30)
        ],
        "removal": "위가 제거되면 음식물 저장과 초기 소화 기능이 달라지고 영양소 섭취 및 흡수 과정에 영향을 줄 수 있다."
    },
    "신장": {
        "position": (0.47, 0.12, 3.25),
        "size": (0.23, 0.22, 0.38),
        "color": "#9d4d55",
        "description": "혈액을 여과하여 노폐물을 제거하고 수분, 전해질, 산-염기 균형을 조절한다.",
        "cells": ["족세포", "근위세뇨관 세포", "원위세뇨관 세포", "집합관 세포"],
        "effects": [
            ("노폐물 배설", 0.35),
            ("수분 조절", 0.25),
            ("전해질 조절", 0.25),
            ("혈압 조절", 0.15)
        ],
        "removal": "신장 기능이 소실되면 노폐물과 수분이 축적되고 전해질 및 혈압 조절에 심각한 문제가 발생한다."
    },
    "췌장": {
        "position": (-0.32, 0.08, 3.30),
        "size": (0.44, 0.18, 0.20),
        "color": "#e5b58d",
        "description": "소화 효소를 분비하고 인슐린과 글루카곤을 통해 혈당을 조절한다.",
        "cells": ["췌장 선방세포", "베타세포", "알파세포", "델타세포"],
        "effects": [
            ("혈당 조절", 0.55),
            ("소화 효소 분비", 0.45)
        ],
        "removal": "인슐린과 소화 효소의 생성이 감소하여 혈당 조절 및 소화 과정에 문제가 발생할 수 있다."
    },
    "소장": {
        "position": (0.0, -0.03, 2.85),
        "size": (0.53, 0.25, 0.27),
        "color": "#e5a477",
        "description": "소화된 영양소의 대부분을 흡수하는 기관이다.",
        "cells": ["흡수상피세포", "배상세포", "파네트세포", "장내분비세포"],
        "effects": [
            ("영양소 흡수", 0.65),
            ("면역 방어", 0.20),
            ("소화 및 분비", 0.15)
        ],
        "removal": "흡수 면적이 감소하면 영양소 흡수 장애와 수분 및 전해질 균형 문제가 발생할 수 있다."
    },
    "방광": {
        "position": (0, -0.03, 1.55),
        "size": (0.30, 0.24, 0.30),
        "color": "#d4a7a0",
        "description": "소변을 저장하고 배뇨 과정에서 소변을 배출한다.",
        "cells": ["이행상피세포", "평활근세포", "섬유아세포"],
        "effects": [
            ("소변 저장", 0.60),
            ("배뇨 조절", 0.40)
        ],
        "removal": "소변 저장과 배출 방식이 달라져 정상적인 배뇨 기능에 문제가 생긴다."
    }
}

CELL_DATA = {
    "신경세포": {
        "description": "전기적 신호와 화학적 신호를 이용하여 정보를 전달하는 세포이다.",
        "function": "자극을 받아들이고 활동 전위를 발생시켜 다른 세포에 정보를 전달한다.",
        "organelles": ["핵", "미토콘드리아", "리보솜", "소포체", "골지체", "세포막"],
        "special": "가지돌기, 세포체, 축삭, 시냅스 구조를 가진다."
    },
    "성상교세포": {
        "description": "신경세포 주변의 환경을 조절하고 신경계의 항상성을 유지하는 세포이다.",
        "function": "이온 농도 조절, 신경전달물질 처리, 혈액뇌장벽 지원 등에 관여한다.",
        "organelles": ["핵", "미토콘드리아", "리보솜", "소포체", "골지체"],
        "special": "별 모양의 돌기를 통해 여러 신경세포 주변과 접촉한다."
    },
    "희소돌기아교세포": {
        "description": "중추신경계에서 축삭을 감싸는 수초 형성에 관여한다.",
        "function": "신경 신호가 효율적으로 전달되도록 돕는다.",
        "organelles": ["핵", "미토콘드리아", "소포체", "골지체"],
        "special": "수초를 형성하여 축삭을 절연하는 역할을 한다."
    },
    "미세아교세포": {
        "description": "중추신경계의 면역 방어와 손상된 세포의 제거에 관여한다.",
        "function": "병원체와 세포 잔해를 제거한다.",
        "organelles": ["핵", "리소좀", "미토콘드리아", "세포막"],
        "special": "면역 감시와 식세포 작용을 수행한다."
    },
    "심근세포": {
        "description": "심장 근육을 구성하며 규칙적인 수축과 이완을 수행한다.",
        "function": "혈액을 순환시키는 힘을 만든다.",
        "organelles": ["핵", "미토콘드리아", "근형질세망", "리보솜", "세포막"],
        "special": "가로무늬와 개재판을 가지며 수축이 서로 협응한다."
    },
    "내피세포": {
        "description": "혈관 내부 표면을 덮는 세포이다.",
        "function": "물질 이동과 혈관 기능을 조절한다.",
        "organelles": ["핵", "미토콘드리아", "소포체", "골지체"],
        "special": "혈액과 조직 사이의 경계면을 형성한다."
    },
    "섬유아세포": {
        "description": "결합 조직의 세포외기질을 생산하는 세포이다.",
        "function": "콜라겐 등 조직의 구조 단백질을 합성한다.",
        "organelles": ["핵", "리보솜", "소포체", "골지체"],
        "special": "상처 회복과 조직 유지에 중요하다."
    },
    "폐포 1형 세포": {
        "description": "폐포의 넓은 표면을 덮는 얇은 세포이다.",
        "function": "산소와 이산화탄소의 확산을 돕는다.",
        "organelles": ["핵", "미토콘드리아", "세포막"],
        "special": "얇은 구조로 기체 교환에 유리하다."
    },
    "폐포 2형 세포": {
        "description": "폐포 표면활성제를 분비하는 세포이다.",
        "function": "폐포가 쉽게 허탈되지 않도록 돕는다.",
        "organelles": ["핵", "미토콘드리아", "소포체", "골지체"],
        "special": "폐포 표면의 표면장력을 낮추는 물질을 분비한다."
    },
    "간세포": {
        "description": "간의 주요 기능을 수행하는 세포이다.",
        "function": "대사, 단백질 합성, 담즙 생성, 물질 처리에 관여한다.",
        "organelles": ["핵", "미토콘드리아", "활면소포체", "리보솜", "골지체"],
        "special": "다양한 대사 효소와 풍부한 소기관을 가진다."
    },
    "쿠퍼세포": {
        "description": "간의 혈관 내부에 위치하는 대식세포이다.",
        "function": "혈액 속 이물질과 세포 잔해를 제거한다.",
        "organelles": ["핵", "리소좀", "미토콘드리아"],
        "special": "간의 면역 방어에 기여한다."
    },
    "벽세포": {
        "description": "위샘에서 염산과 내인자를 분비한다.",
        "function": "위 내부의 산성 환경을 형성한다.",
        "organelles": ["핵", "미토콘드리아", "소포체", "골지체"],
        "special": "분비 활동에 필요한 미토콘드리아가 풍부하다."
    },
    "흡수상피세포": {
        "description": "소장 내부에서 영양소를 흡수한다.",
        "function": "소화된 영양소를 체내로 운반한다.",
        "organelles": ["핵", "미토콘드리아", "골지체", "소포체"],
        "special": "미세융모가 있어 흡수 표면적이 넓다."
    },
    "족세포": {
        "description": "신장의 사구체 여과 장벽을 구성하는 세포이다.",
        "function": "혈액 여과 과정에서 중요한 장벽 역할을 한다.",
        "organelles": ["핵", "미토콘드리아", "소포체"],
        "special": "발 모양의 돌기가 여과 틈을 형성한다."
    }
}

ORGANELLE_DATA = {
    "핵": ("유전 정보를 저장하고 세포의 활동을 조절한다.", "DNA가 존재하며 전사와 유전자 발현 조절이 일어난다.", "#8d78d9"),
    "미토콘드리아": ("세포 호흡을 통해 ATP를 생성한다.", "내막의 전자전달계와 ATP 합성효소가 에너지 생산에 관여한다.", "#d77c52"),
    "리보솜": ("mRNA의 정보를 바탕으로 단백질을 합성한다.", "큰 소단위체와 작은 소단위체로 구성된다.", "#e3c16f"),
    "소포체": ("단백질과 지질의 합성 및 처리에 관여한다.", "거친면소포체에는 리보솜이 붙어 있고 활면소포체는 지질 합성 등에 관여한다.", "#65b7aa"),
    "활면소포체": ("지질 합성 및 물질 대사에 관여한다.", "일부 세포에서 약물과 독성 물질의 대사에 관여한다.", "#65b7aa"),
    "골지체": ("단백질과 지질을 가공하고 분류하여 운반한다.", "납작한 막 주머니가 층층이 쌓인 구조이다.", "#df9c61"),
    "세포막": ("세포 내부와 외부를 구분하고 물질 이동을 조절한다.", "인지질 이중층과 막단백질로 이루어진 유동 모자이크 구조이다.", "#55a9d5"),
    "리소좀": ("세포 내 물질을 분해하고 재활용한다.", "가수분해 효소를 포함하는 막성 소기관이다.", "#b16f9d"),
    "근형질세망": ("근육세포에서 칼슘 이온을 저장하고 방출한다.", "칼슘 농도 변화가 근육 수축 조절에 관여한다.", "#68a4d2"),
}

DRUG_DATA = {
    "일반 진통제(비오피오이드)": {
        "category": "통증 조절",
        "target": "통증 및 염증 관련 생리 경로",
        "effect": "통증 신호와 염증 반응이 감소할 수 있다.",
        "risk": "약물 종류에 따라 간 또는 위장관 등에 부작용이 나타날 수 있다.",
        "vision": "시각 변화가 일반적인 대표 작용은 아니다.",
        "vision_type": "normal",
        "systems": {"통증 인지": 0.65, "간 대사": 0.10},
        "color": "#54a7db"
    },
    "오피오이드계 진통제(임상 교육)": {
        "category": "중추신경계 작용",
        "target": "중추신경계의 오피오이드 수용체",
        "effect": "의료 환경에서 통증 완화에 사용되지만 의식과 호흡에 영향을 줄 수 있다.",
        "risk": "과도한 중추신경 억제는 호흡 저하와 의식 저하 등 심각한 위험을 일으킬 수 있다.",
        "vision": "졸림과 반응 저하, 시야가 흐릿하게 느껴지는 상태를 교육적으로 표현한다.",
        "vision_type": "dim",
        "systems": {"통증 인지": 0.60, "의식 수준": 0.35, "호흡 기능": -0.40},
        "color": "#9b85cb"
    },
    "항히스타민제": {
        "category": "알레르기 조절",
        "target": "히스타민 수용체",
        "effect": "알레르기 반응으로 발생하는 가려움과 재채기 등의 증상을 줄일 수 있다.",
        "risk": "일부 약물은 졸림과 반응 속도 저하를 일으킬 수 있다.",
        "vision": "졸림이 나타나는 경우 시야의 선명도가 낮아진 것처럼 표현한다.",
        "vision_type": "blur",
        "systems": {"알레르기 반응": 0.65, "의식 수준": -0.10},
        "color": "#71b7a2"
    },
    "기관지확장제": {
        "category": "호흡기 치료",
        "target": "기관지 평활근 및 관련 수용체",
        "effect": "기관지 평활근을 이완시켜 공기 흐름을 개선하는 데 사용된다.",
        "risk": "종류에 따라 심박수 증가와 떨림 등이 나타날 수 있다.",
        "vision": "대표적인 시각 변화는 없다.",
        "vision_type": "normal",
        "systems": {"기관지 개방": 0.65, "심박 반응": 0.10},
        "color": "#56b6d4"
    },
    "인슐린(의료 교육)": {
        "category": "혈당 조절",
        "target": "인슐린 수용체 및 포도당 대사",
        "effect": "혈당 조절에 관여하며 포도당의 세포 흡수 등을 촉진한다.",
        "risk": "혈당이 지나치게 낮아지면 저혈당이 발생할 수 있다.",
        "vision": "저혈당 상태에서는 시야 흐림이나 집중력 저하가 나타날 수 있다.",
        "vision_type": "blur",
        "systems": {"혈당 조절": 0.70, "의식 수준": -0.05},
        "color": "#68b9a4"
    },
    "국소마취제": {
        "category": "신경 신호 조절",
        "target": "전압 개폐성 나트륨 통로",
        "effect": "신경의 활동 전위 전달을 일시적으로 차단하여 국소적인 감각을 줄인다.",
        "risk": "전신 독성 반응이 발생할 경우 신경계와 심혈관계에 영향을 줄 수 있다.",
        "vision": "약물의 일반적인 국소 작용 자체는 시야 변화가 아니다.",
        "vision_type": "normal",
        "systems": {"통증 신호 전달": 0.75, "감각 전달": 0.55},
        "color": "#b08ac9"
    },
    "카페인(각성 작용 교육)": {
        "category": "중추신경계 자극",
        "target": "아데노신 수용체",
        "effect": "각성 상태에 영향을 주며 졸음을 줄이는 작용을 한다.",
        "risk": "과도한 섭취는 수면 방해, 불안감, 심박 변화 등을 유발할 수 있다.",
        "vision": "일반적인 대표 작용은 시각적 환각이 아니다.",
        "vision_type": "normal",
        "systems": {"각성 상태": 0.30, "심박 반응": 0.10},
        "color": "#d8a85c"
    },
    "전신마취제(임상 교육)": {
        "category": "의식 및 감각 조절",
        "target": "중추신경계의 신경 전달",
        "effect": "의료진의 감시 아래 의식과 감각을 조절하는 데 사용된다.",
        "risk": "호흡 및 순환 기능에 영향을 줄 수 있어 전문적인 감시가 필요하다.",
        "vision": "의식 저하 및 시각 정보 처리 감소를 어두워지는 화면으로 표현한다.",
        "vision_type": "dark",
        "systems": {"의식 수준": -0.60, "호흡 기능": -0.25},
        "color": "#8a94bb"
    }
}

# ============================================================
# 2. 세션 상태
# ============================================================

DEFAULTS = {
    "stage": "body",
    "selected_organ": "뇌",
    "selected_cell": "신경세포",
    "selected_organelle": "핵",
    "removed_organs": [],
    "cutaway": False,
    "hair_color": "#49362d",
    "eye_color": "#6a4a30",
    "pigment": 65,
    "allele_a": "A",
    "allele_b": "a",
    "selected_drug": "일반 진통제(비오피오이드)",
    "drug_applied": False,
    "drug_view": False,
    "injection_progress": False,
    "orbit": 0,
    "show_labels": True,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# 3. 3D 메시 생성 함수
# ============================================================

def organic_mesh(center, radii, color, name,
                 resolution=28, opacity=1.0,
                 irregularity=0.10, phase=0.0):

    cx, cy, cz = center
    rx, ry, rz = radii

    u = np.linspace(0, 2 * np.pi, resolution)
    v = np.linspace(0, np.pi, resolution)

    U, V = np.meshgrid(u, v)

    distortion = (
        1
        + irregularity * np.sin(3 * U + phase) * np.sin(2 * V)
        + irregularity * 0.45 * np.cos(5 * U - phase) * np.sin(3 * V)
    )

    x = cx + rx * np.cos(U) * np.sin(V) * distortion
    y = cy + ry * np.sin(U) * np.sin(V) * distortion
    z = cz + rz * np.cos(V) * distortion * 0.92

    rows, cols = x.shape
    i, j, k = [], [], []

    for a in range(rows - 1):
        for b in range(cols - 1):
            p1 = a * cols + b
            p2 = p1 + 1
            p3 = (a + 1) * cols + b
            p4 = p3 + 1

            i.extend([p1, p1])
            j.extend([p2, p4])
            k.extend([p3, p3])

    return go.Mesh3d(
        x=x.flatten(),
        y=y.flatten(),
        z=z.flatten(),
        i=i, j=j, k=k,
        color=color,
        opacity=opacity,
        name=name,
        flatshading=False,
        lighting=dict(
            ambient=0.42,
            diffuse=0.82,
            specular=0.38,
            roughness=0.58,
            fresnel=0.12
        ),
        lightposition=dict(x=100, y=150, z=200),
        hovertemplate=f"<b>{name}</b><extra></extra>"
    )


def tube_mesh(start, end, radius1, radius2, color, name,
              segments=20, sides=16):

    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)

    direction = end - start
    length = np.linalg.norm(direction)

    if length == 0:
        return None

    direction /= length

    reference = np.array([0, 1, 0], dtype=float)

    if abs(np.dot(direction, reference)) > 0.9:
        reference = np.array([1, 0, 0], dtype=float)

    u = np.cross(direction, reference)
    u /= np.linalg.norm(u)

    v = np.cross(direction, u)
    v /= np.linalg.norm(v)

    t = np.linspace(0, 1, segments)
    angle = np.linspace(0, 2 * np.pi, sides)

    T, A = np.meshgrid(t, angle)

    radius = radius1 * (1 - T) + radius2 * T

    x = (
        start[0] + direction[0] * length * T
        + radius * (u[0] * np.cos(A) + v[0] * np.sin(A))
    )

    y = (
        start[1] + direction[1] * length * T
        + radius * (u[1] * np.cos(A) + v[1] * np.sin(A))
    )

    z = (
        start[2] + direction[2] * length * T
        + radius * (u[2] * np.cos(A) + v[2] * np.sin(A))
    )

    rows, cols = x.shape
    ii, jj, kk = [], [], []

    for a in range(rows - 1):
        for b in range(cols - 1):
            p = a * cols + b
            q = a * cols + (b + 1) % cols
            r = (a + 1) * cols + b
            s = (a + 1) * cols + (b + 1) % cols

            ii.extend([p, q])
            jj.extend([q, s])
            kk.extend([r, r])

    return go.Mesh3d(
        x=x.flatten(), y=y.flatten(), z=z.flatten(),
        i=ii, j=jj, k=kk,
        color=color,
        name=name,
        opacity=0.95,
        flatshading=False,
        lighting=dict(
            ambient=0.5,
            diffuse=0.85,
            specular=0.25
        ),
        hovertemplate=f"<b>{name}</b><extra></extra>"
    )


def add_ellipsoid(fig, center, radii, color, name,
                  opacity=1.0, irregularity=0.05):

    fig.add_trace(
        organic_mesh(
            center, radii, color, name,
            opacity=opacity,
            irregularity=irregularity,
            resolution=25
        )
    )


def add_body(fig, hair_color=None, eye_color=None,
             cutaway=False, removed=None):

    removed = removed or []

    skin = "#c88f78"

    # 몸통: 상체와 골반을 서로 다른 곡면으로 구성
    add_ellipsoid(
        fig, (0, 0, 4.15),
        (0.70, 0.37, 1.15),
        skin, "인체 몸통",
        opacity=0.17 if cutaway else 0.92,
        irregularity=0.13
    )

    add_ellipsoid(
        fig, (0, 0.01, 3.12),
        (0.51, 0.32, 0.53),
        "#bd806d", "골반",
        opacity=0.18 if cutaway else 0.92
    )

    # 머리와 목
    add_ellipsoid(
        fig, (0, 0, 6.05),
        (0.36, 0.31, 0.47),
        skin, "머리"
    )

    add_ellipsoid(
        fig, (0, 0, 5.63),
        (0.17, 0.19, 0.29),
        skin, "목"
    )

    # 머리카락
    if hair_color:
        add_ellipsoid(
            fig, (0, 0.015, 6.32),
            (0.36, 0.31, 0.24),
            hair_color, "머리카락",
            irregularity=0.16
        )

    # 눈
    for x in [-0.125, 0.125]:
        add_ellipsoid(
            fig, (x, -0.288, 6.12),
            (0.048, 0.027, 0.038),
            "#f3e8dd", "눈"
        )
        add_ellipsoid(
            fig, (x, -0.313, 6.12),
            (0.021, 0.014, 0.023),
            eye_color or "#49362d", "홍채"
        )

    # 팔과 다리
    limbs = [
        ((-0.58, 0, 4.95), (-0.92, 0, 4.05), 0.17, 0.12),
        ((0.58, 0, 4.95), (0.92, 0, 4.05), 0.17, 0.12),
        ((-0.92, 0, 4.05), (-1.02, -0.02, 3.15), 0.12, 0.075),
        ((0.92, 0, 4.05), (1.02, -0.02, 3.15), 0.12, 0.075),
        ((-0.29, 0, 2.95), (-0.34, 0, 1.65), 0.20, 0.115),
        ((0.29, 0, 2.95), (0.34, 0, 1.65), 0.20, 0.115),
        ((-0.34, 0, 1.65), (-0.35, 0, 0.35), 0.115, 0.07),
        ((0.34, 0, 1.65), (0.35, 0, 0.35), 0.115, 0.07),
    ]

    for idx, (a, b, r1, r2) in enumerate(limbs):
        part = tube_mesh(a, b, r1, r2, skin, f"인체 사지 {idx}")
        if part:
            part.opacity = 0.92
            fig.add_trace(part)

    # 손
    for x in [-1.02, 1.02]:
        add_ellipsoid(fig, (x, -0.02, 3.02),
                      (0.105, 0.08, 0.15), skin, "손")

    # 발
    for x in [-0.35, 0.35]:
        add_ellipsoid(fig, (x, -0.13, 0.23),
                      (0.15, 0.26, 0.09), skin, "발")

    # 장기
    for name, data in ORGAN_DATA.items():

        if name in removed:
            continue

        cx, cy, cz = data["position"]
        sx, sy, sz = data["size"]

        if name == "폐":
            # 좌우 폐를 분리하고 엽 구조를 표현
            for sign in [-1, 1]:
                add_ellipsoid(
                    fig,
                    (sign * 0.40, cy, cz),
                    (0.34, 0.24, 0.49),
                    data["color"],
                    f"{name} 좌우엽"
                )

                add_ellipsoid(
                    fig,
                    (sign * 0.40, cy - 0.02, cz - 0.25),
                    (0.28, 0.22, 0.23),
                    "#d98a9c",
                    f"{name} 하엽"
                )

        elif name == "뇌":
            add_ellipsoid(
                fig, (cx, cy, cz),
                (sx, sy, sz),
                data["color"], name,
                irregularity=0.23
            )

            # 뇌 표면의 주름을 표현하는 곡선
            for j in range(7):
                z = cz - 0.22 + j * 0.07
                theta = np.linspace(-1.2, 1.2, 45)

                fig.add_trace(go.Scatter3d(
                    x=0.46 * np.cos(theta),
                    y=-0.30 - 0.018 * np.sin(4 * theta + j),
                    z=z + 0.025 * np.sin(3 * theta + j),
                    mode="lines",
                    line=dict(color="#f4b1c5", width=2),
                    showlegend=False,
                    hoverinfo="skip"
                ))

        else:
            add_ellipsoid(
                fig,
                (cx, cy, cz),
                (sx, sy, sz),
                data["color"],
                name,
                irregularity=0.16
            )

    # 주요 혈관: 교육용 위치 표시
    vessels = [
        ((0, -0.12, 5.15), (0, -0.12, 3.55)),
        ((0, -0.12, 4.65), (-0.42, -0.12, 3.35)),
        ((0, -0.12, 4.65), (0.42, -0.12, 3.35)),
    ]

    for a, b in vessels:
        vessel = tube_mesh(a, b, 0.035, 0.025, "#c64e55", "주요 혈관")
        if vessel:
            vessel.opacity = 0.85
            fig.add_trace(vessel)

    # 절개선
    if cutaway:
        fig.add_trace(go.Scatter3d(
            x=[-0.60, -0.25, 0.05, 0.35, 0.60],
            y=[-0.38] * 5,
            z=[5.05, 4.72, 4.55, 4.72, 5.05],
            mode="lines",
            line=dict(color="#f15b64", width=7),
            name="절개선"
        ))


# ============================================================
# 4. 3D 장기 단독 모델
# ============================================================

def organ_scene(organ_name):

    data = ORGAN_DATA[organ_name]
    fig = go.Figure()

    cx, cy, cz = data["position"]
    sx, sy, sz = data["size"]

    if organ_name == "뇌":

        fig.add_trace(organic_mesh(
            (0, 0, 0),
            (1.0, 0.78, 0.78),
            "#d98ca6",
            "대뇌",
            resolution=42,
            irregularity=0.18
        ))

        # 대뇌 주름을 나타내는 여러 곡선
        for i in range(16):
            t = np.linspace(-2.0, 2.0, 100)
            x = 0.9 * np.sin(t + i * 0.25)
            y = 0.73 * np.cos(t * 1.2 + i * 0.17)
            z = 0.15 * np.sin(t * 2.5 + i * 0.6)

            fig.add_trace(go.Scatter3d(
                x=x, y=y, z=z,
                mode="lines",
                line=dict(color="#f5c1d0", width=3),
                showlegend=False,
                hoverinfo="skip"
            ))

        add_ellipsoid(fig, (0, 0, -0.65),
                      (0.42, 0.42, 0.38),
                      "#e2a4b8", "소뇌")

        add_ellipsoid(fig, (0, 0, -0.95),
                      (0.19, 0.20, 0.52),
                      "#c88199", "뇌줄기")

    elif organ_name == "심장":

        # 심장 근육의 비대칭 형태를 여러 곡면으로 표현
        add_ellipsoid(fig, (-0.24, 0, 0.12),
                      (0.43, 0.38, 0.62),
                      "#c94355", "좌심실")

        add_ellipsoid(fig, (0.24, 0, 0.12),
                      (0.36, 0.35, 0.55),
                      "#e05a66", "우심실")

        add_ellipsoid(fig, (0, 0, 0.57),
                      (0.38, 0.32, 0.29),
                      "#e77a84", "심방")

        for x in [-0.18, 0.18]:
            vessel = tube_mesh(
                (x, 0, 0.70),
                (x * 1.2, 0, 1.25),
                0.10, 0.07,
                "#bd444f",
                "대혈관"
            )
            if vessel:
                fig.add_trace(vessel)

    elif organ_name == "폐":

        for sign in [-1, 1]:
            add_ellipsoid(
                fig, (sign * 0.48, 0, 0),
                (0.48, 0.36, 0.85),
                "#dc8294",
                "폐"
            )

            for j in range(3):
                add_ellipsoid(
                    fig,
                    (sign * 0.48, -0.01, -0.35 + j * 0.30),
                    (0.38, 0.30, 0.23),
                    "#ed9dad",
                    "폐엽"
                )

        tube = tube_mesh(
            (0, 0, 1.25), (0, 0, 0.45),
            0.13, 0.09, "#b9c9d8", "기관"
        )
        if tube:
            fig.add_trace(tube)

    else:
        add_ellipsoid(
            fig, (0, 0, 0),
            data["size"],
            data["color"],
            organ_name,
            irregularity=0.23,
            opacity=1
        )

        # 내부 혈관 및 구조적 강조
        for i in range(3):
            x = -0.25 + i * 0.25
            line = tube_mesh(
                (x, -0.05, -0.25),
                (x * 0.8, -0.05, 0.30),
                0.025, 0.018,
                "#d8a3a3",
                "내부 혈관"
            )
            if line:
                fig.add_trace(line)

    fig.update_layout(
        title=dict(text=f"{organ_name} 3D 구조", font=dict(size=20)),
        height=560,
        margin=dict(l=0, r=0, t=55, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(eye=dict(x=1.7, y=1.7, z=1.2))
        ),
        showlegend=False
    )

    return fig


# ============================================================
# 5. 세포 및 세포 소기관 3D
# ============================================================

def cell_scene(cell_name, organelle_focus=None):

    cell = CELL_DATA.get(cell_name, CELL_DATA["신경세포"])

    fig = go.Figure()

    # 세포막
    fig.add_trace(organic_mesh(
        (0, 0, 0),
        (1.0, 0.78, 0.62),
        "#6aabc5",
        "세포막",
        resolution=38,
        irregularity=0.09,
        opacity=0.22
    ))

    # 핵
    add_ellipsoid(
        fig, (0.0, 0.05, 0.05),
        (0.37, 0.32, 0.34),
        "#9676cb",
        "핵",
        opacity=0.98
    )

    # 핵 내부 핵소체
    add_ellipsoid(
        fig, (0.0, -0.10, 0.10),
        (0.12, 0.12, 0.13),
        "#c8a4e5",
        "핵소체"
    )

    # 미토콘드리아
    mito_positions = [
        (-0.57, 0.0, 0.22),
        (0.57, 0.10, -0.17),
        (-0.35, -0.34, -0.27),
        (0.38, 0.32, 0.35)
    ]

    for i, pos in enumerate(mito_positions):
        add_ellipsoid(
            fig, pos,
            (0.24, 0.11, 0.10),
            "#d77c52",
            f"미토콘드리아 {i+1}",
            irregularity=0.18
        )

        # 미토콘드리아 내부 주름
        theta = np.linspace(0, 2 * np.pi, 50)
        x = pos[0] + 0.20 * np.cos(theta)
        y = pos[1] - 0.01 + 0.045 * np.sin(theta)
        z = pos[2] + 0.035 * np.sin(theta * 3)

        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode="lines",
            line=dict(color="#f1b68e", width=3),
            showlegend=False,
            hoverinfo="skip"
        ))

    # 소포체의 곡선형 막 구조
    for i in range(4):
        t = np.linspace(-1, 1, 70)
        x = -0.55 + 1.1 * (t + 1) / 2
        y = 0.38 + 0.04 * np.sin(t * 7 + i)
        z = -0.18 + i * 0.12 + 0.08 * np.cos(t * 4 + i)

        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode="lines",
            line=dict(color="#65b7aa", width=6),
            name="소포체"
        ))

    # 골지체: 층층이 휘어진 막
    for i in range(5):
        t = np.linspace(-1, 1, 60)
        x = 0.15 + 0.32 * t
        y = -0.30 - i * 0.035
        z = -0.45 + i * 0.11 + 0.07 * np.cos(t * np.pi)

        fig.add_trace(go.Scatter3d(
            x=x, y=np.full_like(x, y), z=z,
            mode="lines",
            line=dict(color="#df9c61", width=7),
            name="골지체"
        ))

    # 리보솜
    rng = np.random.default_rng(42)

    for i in range(45):
        p = rng.uniform(-0.75, 0.75, 3)

        if np.linalg.norm(p) < 0.9:
            add_ellipsoid(
                fig, tuple(p),
                (0.025, 0.025, 0.025),
                "#e8c66f",
                "리보솜",
                opacity=0.95,
                irregularity=0
            )

    # 세포 종류별 특징적 구조
    if cell_name == "신경세포":

        # 가지돌기
        for sign in [-1, 1]:
            for i in range(3):
                end = (sign * (1.0 + i * 0.12),
                       0.05 + i * 0.12,
                       0.2 + i * 0.15)

                branch = tube_mesh(
                    (sign * 0.65, 0, 0),
                    end,
                    0.09, 0.025,
                    "#75b7cf",
                    "가지돌기"
                )

                if branch:
                    fig.add_trace(branch)

        # 축삭
        axon = tube_mesh(
            (0.45, 0.0, -0.15),
            (1.65, 0.0, -0.55),
            0.09, 0.045,
            "#d7b16c",
            "축삭"
        )

        if axon:
            fig.add_trace(axon)

        # 수초
        for i in range(4):
            x = 0.62 + i * 0.25
            add_ellipsoid(
                fig, (x, 0, -0.21 - i * 0.075),
                (0.10, 0.13, 0.12),
                "#e7c78e",
                "수초"
            )

    fig.update_layout(
        title=f"{cell_name}의 3D 세포 구조",
        height=570,
        margin=dict(l=0, r=0, t=55, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(eye=dict(x=1.7, y=1.7, z=1.2))
        ),
        showlegend=False
    )

    return fig


# ============================================================
# 6. DNA 이중나선 3D
# ============================================================

def dna_scene():

    fig = go.Figure()

    t = np.linspace(0, 12 * np.pi, 420)

    radius = 0.75
    height = np.linspace(-3.0, 3.0, len(t))

    x1 = radius * np.cos(t)
    y1 = radius * np.sin(t)

    x2 = radius * np.cos(t + np.pi)
    y2 = radius * np.sin(t + np.pi)

    fig.add_trace(go.Scatter3d(
        x=x1, y=y1, z=height,
        mode="lines",
        line=dict(color="#4b9ee9", width=9),
        name="DNA 가닥 1"
    ))

    fig.add_trace(go.Scatter3d(
        x=x2, y=y2, z=height,
        mode="lines",
        line=dict(color="#d77cb1", width=9),
        name="DNA 가닥 2"
    ))

    # 염기쌍 연결
    for i in range(0, len(t), 18):
        fig.add_trace(go.Scatter3d(
            x=[x1[i], x2[i]],
            y=[y1[i], y2[i]],
            z=[height[i], height[i]],
            mode="lines",
            line=dict(color="#e8d18e", width=4),
            showlegend=False,
            hoverinfo="skip"
        ))

    fig.update_layout(
        title="DNA 이중나선 구조",
        height=590,
        margin=dict(l=0, r=0, t=55, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(eye=dict(x=1.7, y=1.7, z=1.2))
        ),
        showlegend=True
    )

    return fig


# ============================================================
# 7. 1인칭 시야 시뮬레이션
# ============================================================

def first_person_scene(drug_name):

    data = DRUG_DATA[drug_name]
    view_type = data["vision_type"]

    fig = go.Figure()

    # 가상의 실내 공간
    wall_color = "#526a83"
    floor_color = "#394c5e"

    if view_type == "dim":
        wall_color = "#344052"
        floor_color = "#253040"

    elif view_type == "dark":
        wall_color = "#111827"
        floor_color = "#0a101a"

    elif view_type == "blur":
        wall_color = "#758296"
        floor_color = "#536274"

    # 방의 모서리
    corners = [
        (-4, -4, -2), (4, -4, -2),
        (4, 4, -2), (-4, 4, -2),
        (-4, -4, 3), (4, -4, 3),
        (4, 4, 3), (-4, 4, 3)
    ]

    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    for a, b in edges:
        fig.add_trace(go.Scatter3d(
            x=[corners[a][0], corners[b][0]],
            y=[corners[a][1], corners[b][1]],
            z=[corners[a][2], corners[b][2]],
            mode="lines",
            line=dict(color=wall_color, width=4),
            showlegend=False,
            hoverinfo="skip"
        ))

    # 공간 안의 사물
    for x, y, z, name in [
        (-1.8, 0, -0.6, "책상"),
        (1.7, 0.4, -0.6, "의자"),
        (0, 2, -0.6, "벽면"),
        (0, -2.0, -0.6, "물체")
    ]:
        add_ellipsoid(
            fig, (x, y, z),
            (0.35, 0.25, 0.55),
            floor_color,
            name,
            opacity=0.85,
            irregularity=0
        )

    # 시야 중심
    if view_type in ["dim", "dark"]:
        overlay_color = "#111827"
    else:
        overlay_color = "#9aadc0"

    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode="markers",
        marker=dict(size=4, color=overlay_color),
        showlegend=False
    ))

    fig.update_layout(
        title="환자의 1인칭 시야 - 교육용 가상 장면",
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=55, b=0),
        scene=dict(
            bgcolor="rgba(5,10,18,0.95)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(
                eye=dict(x=0, y=-2.7, z=0.15),
                center=dict(x=0, y=0, z=0)
            ),
            aspectmode="manual",
            aspectratio=dict(x=1.5, y=1.5, z=1)
        ),
        showlegend=False
    )

    return fig


# ============================================================
# 8. 생리학적 장기 제거 모델
# ============================================================

def calculate_removal_effects(removed):

    effects = {
        "혈액 순환": 100,
        "산소 교환": 100,
        "대사 기능": 100,
        "노폐물 배설": 100,
        "영양소 흡수": 100,
        "혈당 조절": 100,
        "신경 정보 처리": 100,
        "소변 저장": 100
    }

    mapping = {
        "심장": {
            "혈액 순환": 100,
            "산소 교환": 35,
            "대사 기능": 15
        },
        "폐": {
            "산소 교환": 100,
            "혈액 순환": 20
        },
        "간": {
            "대사 기능": 85,
            "혈액 순환": 10
        },
        "신장": {
            "노폐물 배설": 95,
            "혈액 순환": 10
        },
        "소장": {
            "영양소 흡수": 90,
            "대사 기능": 15
        },
        "췌장": {
            "혈당 조절": 85,
            "대사 기능": 10
        },
        "뇌": {
            "신경 정보 처리": 100
        },
        "방광": {
            "소변 저장": 95
        },
        "위": {
            "영양소 흡수": 15
        }
    }

    for organ in removed:
        for function, loss in mapping.get(organ, {}).items():
            effects[function] = max(
                0,
                effects[function] - loss
            )

    return effects


def removal_scene(removed):

    fig = go.Figure()

    add_body(
        fig,
        hair_color=st.session_state.hair_color,
        eye_color=st.session_state.eye_color,
        cutaway=True,
        removed=removed
    )

    fig.update_layout(
        title="장기 제거 실험 - 인체 구조",
        height=650,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=50, b=0),
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(eye=dict(x=1.6, y=2.2, z=1.2))
        ),
        showlegend=False
    )

    return fig


# ============================================================
# 9. 유전 및 형질 변화
# ============================================================

def genetic_scene():

    fig = dna_scene()
    return fig


def genotype_description(a, b):

    genotype = "".join(sorted([a, b]))

    if genotype == "AA":
        phenotype = "가상 형질 A 발현"
    elif genotype == "Aa":
        phenotype = "가상 형질 A 발현"
    else:
        phenotype = "가상 형질 a 발현"

    return genotype, phenotype


def punnett_square(a, b):

    # 부모 1과 부모 2가 같은 유전자형을 가진다는
    # 교육용 단순 유전 모델
    rows = [a, b]
    cols = [a, b]

    values = []

    for r in rows:
        row = []
        for c in cols:
            row.append("".join(sorted([r, c])))
        values.append(row)

    return pd.DataFrame(
        values,
        index=["부모 1: " + a, "부모 1: " + b],
        columns=["부모 2: " + a, "부모 2: " + b]
    )


def phenotype_chart(pigment):

    pigment = int(pigment)

    categories = [
        "색소 생성 정도",
        "색소 전달 정도",
        "가상 색소 형질"
    ]

    values = [
        pigment,
        min(100, pigment * 0.85),
        min(100, pigment * 0.70)
    ]

    fig = go.Figure(go.Bar(
        x=categories,
        y=values,
        text=[f"{v:.0f}%" for v in values],
        textposition="outside",
        marker_color=["#d78a65", "#6d9bd0", "#b08bd0"]
    ))

    fig.update_layout(
        title="가상 형질 발현 지표",
        yaxis=dict(range=[0, 120], title="상대적 발현 지표"),
        height=330,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=15, r=15, t=45, b=20)
    )

    return fig


# ============================================================
# 10. 약물 반응 지표
# ============================================================

def drug_response_chart(drug_name):

    data = DRUG_DATA[drug_name]

    labels = list(data["systems"].keys())
    values = list(data["systems"].values())

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=labels,
        y=values,
        text=[f"{v:+.2f}" for v in values],
        textposition="outside",
        marker_color=[
            "#d76f73" if v < 0 else "#62a9cf"
            for v in values
        ]
    ))

    fig.update_layout(
        title="약물 작용의 상대적 교육 지표",
        yaxis=dict(
            title="가상 변화량",
            range=[-0.85, 0.85],
            zeroline=True
        ),
        height=340,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=45, b=20)
    )

    return fig


# ============================================================
# 11. 화면 공통 함수
# ============================================================

def page_header(title, subtitle):

    st.markdown(f"""
    <div style="
        padding: 12px 4px 20px 4px;
        border-bottom: 1px solid #29415c;
        margin-bottom: 20px;">
        <h1 style="font-size:2.1rem;margin-bottom:5px;">{title}</h1>
        <p style="color:#9eb3cb;margin-top:0;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def info_card(title, content):

    st.markdown(
        f"""
        <div class="panel">
            <h4>{title}</h4>
            <p>{content}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def set_stage(stage):
    st.session_state.stage = stage


def back_to_body():
    st.session_state.stage = "body"


# ============================================================
# 12. 사이드바
# ============================================================

with st.sidebar:

    st.markdown("## 🧬 LIFE SCIENCE LAB")
    st.caption("3D 생명과학 통합 탐구실")

    st.divider()

    menu_options = {
        "인체 3D 탐색": "body",
        "장기 상세 탐색": "organ",
        "장기 제거 실험": "removal",
        "세포 및 소기관": "cell",
        "DNA 및 유전": "dna",
        "약물 반응 실험": "drug"
    }

    reverse_options = {
        value: key
        for key, value in menu_options.items()
    }

    current_stage = st.session_state.stage

    if current_stage not in reverse_options:
        current_stage = "body"

    selected_menu = st.radio(
        "탐구 영역",
        list(menu_options.keys()),
        index=list(menu_options.keys()).index(
            reverse_options[current_stage]
        )
    )

    st.session_state.stage = menu_options[selected_menu]

    st.divider()

    st.markdown("### 탐구 단계")

    stages = [
        ("body", "01 인체 전체"),
        ("organ", "02 장기 확대"),
        ("removal", "03 장기 제거"),
        ("cell", "04 세포 및 소기관"),
        ("dna", "05 DNA 및 유전"),
        ("drug", "06 약물 반응")
    ]

    for stage_id, label in stages:

        if st.button(
            label,
            key=f"nav_{stage_id}",
            use_container_width=True
        ):
            st.session_state.stage = stage_id
            st.rerun()

    st.divider()

    st.markdown("### 현재 실험 상태")

    st.write(
        f"선택 장기: {st.session_state.selected_organ}"
    )

    st.write(
        f"선택 세포: {st.session_state.selected_cell}"
    )

    st.write(
        f"탐구 단계: {reverse_options[st.session_state.stage]}"
    )

    st.divider()

    st.caption(
        "LIFE SCIENCE 3D LAB | Educational Simulation"
    )


# ============================================================
# 13. 인체 3D 탐색 화면
# ============================================================

if st.session_state.stage == "body":

    page_header(
        "인체 3D 탐색실",
        "인체의 외부 구조에서 내부 장기까지 단계적으로 탐색합니다."
    )

    col1, col2 = st.columns([1.65, 1])

    with col1:

        st.markdown("### 3D 인체 모델")

        fig = go.Figure()

        add_body(
            fig,
            hair_color=st.session_state.hair_color,
            eye_color=st.session_state.eye_color,
            cutaway=st.session_state.cutaway,
            removed=st.session_state.removed_organs
        )

        fig.update_layout(
            height=690,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            scene=dict(
                bgcolor="rgba(0,0,0,0)",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                aspectmode="data",
                camera=dict(
                    eye=dict(
                        x=1.6,
                        y=2.0,
                        z=1.2
                    )
                )
            ),
            showlegend=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": True,
                "scrollZoom": True,
                "responsive": True
            },
            key="human_model"
        )

    with col2:

        st.markdown("### 장기 선택")

        selected = st.selectbox(
            "확대하고 싶은 장기를 선택하세요.",
            list(ORGAN_DATA.keys()),
            index=list(ORGAN_DATA.keys()).index(
                st.session_state.selected_organ
            )
        )

        st.session_state.selected_organ = selected

        data = ORGAN_DATA[selected]

        st.markdown(f"### {selected}")

        st.write(data["description"])

        st.markdown("#### 주요 구성 세포")

        for cell in data["cells"]:
            st.markdown(f"- {cell}")

        st.divider()

        if st.button(
            f"🔬 {selected} 확대 탐색",
            use_container_width=True
        ):
            st.session_state.stage = "organ"
            st.rerun()

        if st.button(
            "🧬 구성 세포로 이동",
            use_container_width=True
        ):
            available = [
                c for c in data["cells"]
                if c in CELL_DATA
            ]

            if available:
                st.session_state.selected_cell = available[0]

            st.session_state.stage = "cell"
            st.rerun()

        st.divider()

        st.markdown("### 절개 도구")

        if st.button("메스 절개 표시", use_container_width=True):
            st.session_state.cutaway = True
            st.rerun()

        if st.button("절개 상태 초기화", use_container_width=True):
            st.session_state.cutaway = False
            st.rerun()

        st.caption(
            "이 절개 표시는 해부학적 위치를 학습하기 위한 시각화입니다. "
            "실제 수술 절차를 안내하는 기능은 아닙니다."
        )


# ============================================================
# 14. 장기 상세 확대 화면
# ============================================================

elif st.session_state.stage == "organ":

    selected = st.session_state.selected_organ
    data = ORGAN_DATA[selected]

    page_header(
        f"{selected} 상세 탐구",
        "인체에서 선택한 장기를 확대하여 구조와 기능을 탐색합니다."
    )

    c1, c2 = st.columns([1.4, 1])

    with c1:
        st.plotly_chart(
            organ_scene(selected),
            use_container_width=True,
            config={"displayModeBar": True, "scrollZoom": True}
        )

    with c2:

        st.markdown(f"## {selected}")
        st.write(data["description"])

        info_card("장기의 주요 역할", data["description"])

        st.markdown("### 구성 세포")

        for cell in data["cells"]:
            st.markdown(f"- **{cell}**")

        st.markdown("### 장기 기능의 비중")

        names = [x[0] for x in data["effects"]]
        vals = [x[1] * 100 for x in data["effects"]]

        fig = go.Figure(go.Bar(
            x=vals,
            y=names,
            orientation="h",
            marker_color="#57a6d8"
        ))

        fig.update_layout(
            height=260,
            xaxis=dict(range=[0, 100]),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10)
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 관련 세포 탐색")

        cell_options = [
            c for c in data["cells"]
            if c in CELL_DATA
        ]

        if cell_options:

            selected_cell = st.selectbox(
                "확대할 세포",
                cell_options
            )

            st.session_state.selected_cell = selected_cell

            if st.button(
                "세포 단계로 확대하기",
                use_container_width=True
            ):
                st.session_state.stage = "cell"
                st.rerun()

        else:
            st.info("이 세포의 상세 모델은 다음 모델 확장 단계에서 추가할 수 있습니다.")

    if st.button("← 인체 전체로 돌아가기"):
        st.session_state.stage = "body"
        st.rerun()


# ============================================================
# 15. 장기 제거 실험
# ============================================================

elif st.session_state.stage == "removal":

    page_header(
        "장기 제거 실험실",
        "장기의 기능이 상실되었을 때 인체의 생리적 변화가 어떻게 나타나는지 탐색합니다."
    )

    st.warning(
        "실제 인체에서 장기를 제거하는 실험이 아닙니다. "
        "장기 기능 상실에 따른 생리학적 영향을 단순화한 교육용 가상 실험입니다."
    )

    c1, c2 = st.columns([1.3, 1])

    with c1:

        st.markdown("### 실험 대상 선택")

        removed = st.multiselect(
            "기능 상실을 가정할 장기",
            list(ORGAN_DATA.keys()),
            default=st.session_state.removed_organs
        )

        st.session_state.removed_organs = removed

        st.plotly_chart(
            removal_scene(removed),
            use_container_width=True,
            config={"displayModeBar": True}
        )

        if st.button("모든 장기 복원"):
            st.session_state.removed_organs = []
            st.rerun()

    with c2:

        st.markdown("### 기능 변화 분석")

        effects = calculate_removal_effects(removed)

        for name, value in effects.items():
            st.markdown(f"**{name}**")

            st.progress(
                int(value),
                text=f"교육용 상대 기능 지표: {value}%"
            )

        st.divider()

        st.markdown("### 발생 가능한 생리학적 문제")

        if not removed:
            st.info("장기를 선택하면 기능 변화가 나타납니다.")

        for organ in removed:

            st.markdown(f"#### {organ}")

            st.write(ORGAN_DATA[organ]["removal"])

        if len(removed) >= 2:
            st.warning(
                "여러 장기의 기능 상실이 동시에 발생하면 "
                "각 장기의 영향이 서로 연결되므로 실제 결과는 단순 합산으로 예측할 수 없습니다."
            )

    st.markdown("### 장기 기능 비교 그래프")

    chart = go.Figure()

    chart.add_trace(go.Bar(
        x=list(effects.keys()),
        y=list(effects.values()),
        marker_color="#55a7d5",
        text=[f"{v}%" for v in effects.values()],
        textposition="outside"
    ))

    chart.update_layout(
        height=370,
        yaxis=dict(range=[0, 120]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=20, b=10)
    )

    st.plotly_chart(chart, use_container_width=True)

    st.caption(
        "상대 기능 지표는 장기 기능의 중요도를 설명하기 위한 임의의 교육용 수치입니다. "
        "실제 환자의 생존율이나 임상적 예후를 나타내지 않습니다."
    )


# ============================================================
# 16. 세포 및 소기관 확대
# ============================================================

elif st.session_state.stage == "cell":

    page_header(
        "세포 탐구실",
        "장기를 구성하는 세포를 확대하고 세포 소기관의 구조와 기능을 확인합니다."
    )

    organ_name = st.session_state.selected_organ

    available = [
        c for c in ORGAN_DATA[organ_name]["cells"]
        if c in CELL_DATA
    ]

    if not available:
        available = list(CELL_DATA.keys())

    if st.session_state.selected_cell not in available:
        st.session_state.selected_cell = available[0]

    c1, c2 = st.columns([1.5, 1])

    with c1:

        st.markdown("### 세포 3D 모델")

        cell_name = st.selectbox(
            "세포 종류",
            available,
            index=available.index(st.session_state.selected_cell)
        )

        st.session_state.selected_cell = cell_name

        st.plotly_chart(
            cell_scene(cell_name),
            use_container_width=True,
            config={"displayModeBar": True, "scrollZoom": True}
        )

    with c2:

        data = CELL_DATA[cell_name]

        st.markdown(f"## {cell_name}")

        info_card("세포의 특징", data["description"])
        info_card("주요 기능", data["function"])
        info_card("구조적 특징", data["special"])

        st.markdown("### 소기관 선택")

        organelle = st.selectbox(
            "확대할 세포 소기관",
            data["organelles"]
        )

        st.session_state.selected_organelle = organelle

        if organelle in ORGANELLE_DATA:

            desc, detail, color = ORGANELLE_DATA[organelle]

            st.markdown(f"### {organelle}")
            st.write(desc)
            st.info(detail)

            if organelle == "핵":
                if st.button(
                    "🧬 핵 내부 DNA 확대",
                    use_container_width=True
                ):
                    st.session_state.stage = "dna"
                    st.rerun()

    st.divider()

    st.markdown("### 세포 소기관의 기능")

    organelle_rows = []

    for organelle in data["organelles"]:

        if organelle in ORGANELLE_DATA:
            desc, detail, color = ORGANELLE_DATA[organelle]

            organelle_rows.append({
                "소기관": organelle,
                "주요 기능": desc,
                "구조적 특징": detail
            })

    st.dataframe(
        pd.DataFrame(organelle_rows),
        use_container_width=True,
        hide_index=True
    )

    if st.button("← 장기 단계로 돌아가기"):
        st.session_state.stage = "organ"
        st.rerun()


# ============================================================
# 17. DNA 및 유전 탐구
# ============================================================

elif st.session_state.stage == "dna":

    page_header(
        "DNA 및 유전 탐구실",
        "DNA의 구조와 유전자형의 변화가 형질 발현에 미치는 영향을 살펴봅니다."
    )

    c1, c2 = st.columns([1.3, 1])

    with c1:

        st.plotly_chart(
            genetic_scene(),
            use_container_width=True,
            config={"displayModeBar": True, "scrollZoom": True}
        )

        st.markdown("### DNA 염기쌍")

        st.markdown("""
        | 염기 | 상보적 염기 |
        |---|---|
        | 아데닌(A) | 티민(T) |
        | 구아닌(G) | 사이토신(C) |
        """)

        st.info(
            "DNA는 A, T, G, C 네 가지 염기의 배열을 통해 유전 정보를 저장합니다."
        )

    with c2:

        st.markdown("### 가상 유전자 변이 실험")

        st.write(
            "복잡한 염기서열을 직접 입력하지 않고 "
            "가상의 대립유전자 조합을 선택하여 유전형과 형질 발현을 비교합니다."
        )

        a = st.selectbox(
            "대립유전자 1",
            ["A", "a"],
            index=0
        )

        b = st.selectbox(
            "대립유전자 2",
            ["A", "a"],
            index=1
        )

        genotype, phenotype = genotype_description(a, b)

        st.metric("현재 유전자형", genotype)
        st.metric("교육용 형질 결과", phenotype)

        st.markdown("### 형질 조절")

        hair_options = {
            "검은색": "#211b1a",
            "갈색": "#49362d",
            "밝은 갈색": "#956b48",
            "금발": "#d5b36d",
            "붉은색": "#9c4f3b"
        }

        hair_choice = st.selectbox(
            "머리카락 색상",
            list(hair_options.keys())
        )

        eye_options = {
            "갈색": "#6a4a30",
            "검은색": "#29231e",
            "파란색": "#5b8dbb",
            "녹색": "#6d9872",
            "회색": "#8999a9"
        }

        eye_choice = st.selectbox(
            "홍채 색상",
            list(eye_options.keys())
        )

        pigment = st.slider(
            "가상 색소 발현 지표",
            0, 100,
            int(st.session_state.pigment)
        )

        st.session_state.hair_color = hair_options[hair_choice]
        st.session_state.eye_color = eye_options[eye_choice]
        st.session_state.pigment = pigment

        st.caption(
            "머리카락과 눈동자 색은 실제로 여러 유전자와 발달·환경 요인의 영향을 받습니다. "
            "이 화면은 실제 인간 유전형을 예측하는 도구가 아닌 시각적 교육 모델입니다."
        )

    st.divider()

    st.markdown("### 형질 변화 시각화")

    col1, col2 = st.columns([1, 1])

    with col1:

        fig = phenotype_chart(st.session_state.pigment)
        st.plotly_chart(fig, use_container_width=True)

    with col2:

        st.markdown("#### 유전도 - 퍼넷 사각형")

        square = punnett_square(a, b)

        st.dataframe(
            square,
            use_container_width=True
        )

        st.markdown("#### 형질 발현 해석")

        st.write(
            f"선택한 가상 유전자형은 **{genotype}**이며, "
            f"단순 우성·열성 모델에서는 **{phenotype}**으로 나타납니다."
        )

    st.divider()

    st.markdown("### 변경된 형질을 인체에서 확인")

    fig = go.Figure()

    add_body(
        fig,
        hair_color=st.session_state.hair_color,
        eye_color=st.session_state.eye_color,
        cutaway=False,
        removed=[]
    )

    fig.update_layout(
        height=610,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(eye=dict(x=1.6, y=2.0, z=1.2))
        ),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    if st.button("← 세포 핵으로 돌아가기"):
        st.session_state.stage = "cell"
        st.rerun()


# ============================================================
# 18. 약물 반응 및 1인칭 시야
# ============================================================

elif st.session_state.stage == "drug":

    page_header(
        "약물 및 약리학 탐구실",
        "약물이 인체의 수용체와 생리 기능에 영향을 미치는 원리를 학습합니다."
    )

    st.warning(
        "모든 약물 실험은 가상의 임상 교육 모델입니다. "
        "실제 약물 투여량, 투여 방법, 오남용 방법을 안내하지 않습니다. "
        "위험 약물의 효과를 오락적으로 미화하지 않습니다."
    )

    c1, c2 = st.columns([1, 1])

    with c1:

        st.markdown("### 약물 선택")

        drug_name = st.selectbox(
            "교육용 약물 및 약리 작용",
            list(DRUG_DATA.keys()),
            index=list(DRUG_DATA.keys()).index(
                st.session_state.selected_drug
            )
        )

        st.session_state.selected_drug = drug_name

        data = DRUG_DATA[drug_name]

        st.markdown(f"#### {drug_name}")
        st.write("분류:", data["category"])
        st.write("주요 표적:", data["target"])

        info_card("약리학적 작용", data["effect"])
        info_card("주의할 위험", data["risk"])

        st.markdown("### 투여 시뮬레이션")

        st.caption(
            "주사 장면은 의료진이 수행하는 가상 임상 시각화이며 "
            "실제 주사 위치나 투여 방법을 안내하지 않습니다."
        )

        if st.button(
            "💉 가상 의료 투여 장면 재생",
            use_container_width=True
        ):
            st.session_state.drug_applied = True
            st.session_state.injection_progress = True
            st.session_state.drug_view = False
            st.rerun()

        if st.session_state.drug_applied:

            st.success(
                "가상 약물 투여 상태가 활성화되었습니다."
            )

            st.markdown("**가상 임상 반응 분석이 시작되었습니다.**")

            st.write(data["effect"])
            st.write("관찰해야 할 위험:", data["risk"])

        if st.button(
            "시뮬레이션 초기화",
            use_container_width=True
        ):
            st.session_state.drug_applied = False
            st.session_state.drug_view = False
            st.session_state.injection_progress = False
            st.rerun()

    with c2:

        st.markdown("### 3D 약물 반응 인체")

        fig = go.Figure()

        add_body(
            fig,
            hair_color=st.session_state.hair_color,
            eye_color=st.session_state.eye_color,
            cutaway=True,
            removed=[]
        )

        if st.session_state.injection_progress:

            # 주사기와 약물 전달을 표현하는 교육용 장면
            # 실제 주사 방법과 위치를 안내하지 않음
            syringe = tube_mesh(
                (0.88, -0.34, 4.75),
                (1.05, -0.34, 4.90),
                0.055, 0.055,
                "#d6e3ee",
                "가상 주사기"
            )

            if syringe:
                fig.add_trace(syringe)

            fig.add_trace(go.Scatter3d(
                x=[1.05, 0.92],
                y=[-0.34, -0.34],
                z=[4.90, 4.78],
                mode="lines",
                line=dict(color=data["color"], width=7),
                name="가상 약물 이동"
            ))

        fig.update_layout(
            height=610,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            scene=dict(
                bgcolor="rgba(0,0,0,0)",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                aspectmode="data",
                camera=dict(eye=dict(x=1.6, y=2.0, z=1.2))
            ),
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.markdown("### 약물의 생리학적 작용")

    st.plotly_chart(
        drug_response_chart(drug_name),
        use_container_width=True
    )

    st.markdown("### 환자의 1인칭 시야")

    st.write(
        "아래 화면은 약물에 따른 시각·의식 관련 생리 반응을 "
        "교육적으로 단순화한 가상 환경입니다."
    )

    st.write(data["vision"])

    if st.session_state.drug_applied:

        if st.button(
            "👁 환자의 1인칭 시야 관찰",
            use_container_width=True
        ):
            st.session_state.drug_view = True
            st.rerun()

        if st.session_state.drug_view:

            st.plotly_chart(
                first_person_scene(drug_name),
                use_container_width=True,
                config={"displayModeBar": True}
            )

            if data["vision_type"] == "dark":
                st.error(
                    "의식 및 시각 정보 처리 감소를 표현한 화면입니다. "
                    "이는 안전한 상태가 아니라 의료진의 감시가 필요한 임상 상황을 뜻합니다."
                )

            elif data["vision_type"] == "dim":
                st.warning(
                    "시각적 선명도와 반응이 감소할 수 있는 상황을 표현했습니다."
                )

            elif data["vision_type"] == "blur":
                st.warning(
                    "집중력 및 시각적 선명도에 영향을 줄 수 있는 상황을 단순화했습니다."
                )

            else:
                st.info(
                    "해당 약물의 대표 작용은 반드시 시각적 변화를 일으키는 것은 아닙니다. "
                    "따라서 실제 약리 작용에 맞추어 시야 변화를 과장하지 않았습니다."
                )

    else:
        st.info(
            "먼저 가상 투여 장면을 실행하면 1인칭 시야 관찰 기능이 활성화됩니다."
        )


# ============================================================
# 19. 공통 하단 정보
# ============================================================

st.divider()

st.markdown("""
<div style="
    text-align:center;
    padding:18px;
    color:#8fa5bc;
    font-size:0.85rem;
">
    <b>LIFE SCIENCE 3D LAB</b><br>
    Interactive Human Anatomy · Cell Biology · Genetics · Pharmacology<br><br>
    본 프로그램은 생명과학 학습을 위한 교육용 시뮬레이션이며
    실제 의료 행위 또는 임상적 판단을 대체하지 않습니다.
</div>
""", unsafe_allow_html=True)
