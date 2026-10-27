
import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="BioSphere 3D",
    page_icon="🧬",
    layout="wide"
)

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background: #10141e;
    color: #edf2f7;
}
header {
    visibility: hidden;
}
.block-container {
    padding-top: 1rem;
    max-width: 1500px;
}
h1, h2, h3 {
    color: #dce9ff;
}
[data-testid="stSidebar"] {
    background: #171d2b;
}
</style>
""", unsafe_allow_html=True)

st.title("🧬 BioSphere 3D")
st.caption(
    "인체에서 세포, DNA, 형질까지 연결하는 "
    "3D 생명과학 탐구 시뮬레이터"
)

st.info(
    "교육용 개념 모델입니다. 실제 인체의 해부학적 구조, "
    "유전자 발현, 약물의 효과를 의학적으로 예측하는 프로그램은 아닙니다."
)

# --------------------------------------------------
# 3D 도형 생성 함수
# --------------------------------------------------

def ellipsoid(
    center,
    scale,
    color,
    name,
    opacity=1.0,
    resolution=24
):
    """
    3D 타원체를 생성한다.
    center: (x, y, z)
    scale: (rx, ry, rz)
    """

    u = np.linspace(
        0,
        2 * np.pi,
        resolution
    )

    v = np.linspace(
        0,
        np.pi,
        resolution
    )

    x = (
        center[0]
        + scale[0]
        * np.outer(
            np.cos(u),
            np.sin(v)
        )
    )

    y = (
        center[1]
        + scale[1]
        * np.outer(
            np.sin(u),
            np.sin(v)
        )
    )

    z = (
        center[2]
        + scale[2]
        * np.outer(
            np.ones_like(u),
            np.cos(v)
        )
    )

    return go.Surface(
        x=x,
        y=y,
        z=z,
        colorscale=[
            [0, color],
            [1, color]
        ],
        showscale=False,
        opacity=opacity,
        name=name,
        hovertemplate=name + "<extra></extra>"
    )


def line3d(
    x,
    y,
    z,
    color,
    width=5,
    name=""
):
    return go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="lines",
        line=dict(
            color=color,
            width=width
        ),
        name=name
    )


def make_figure(title):

    fig = go.Figure()

    fig.update_layout(
        title=title,
        height=680,
        margin=dict(
            l=0,
            r=0,
            t=50,
            b=0
        ),
        paper_bgcolor="#10141e",
        plot_bgcolor="#10141e",
        font=dict(
            color="#edf2f7"
        ),
        scene=dict(
            bgcolor="#10141e",
            aspectmode="data",
            xaxis=dict(
                visible=False
            ),
            yaxis=dict(
                visible=False
            ),
            zaxis=dict(
                visible=False
            ),
            camera=dict(
                eye=dict(
                    x=1.6,
                    y=1.6,
                    z=1.2
                )
            )
        ),
        legend=dict(
            bgcolor="rgba(20,25,35,0.7)"
        )
    )

    return fig


# --------------------------------------------------
# 인체 구조 데이터
# --------------------------------------------------

ORGANS = {

    "뇌": {
        "center": (0, 0, 3.3),
        "scale": (0.48, 0.40, 0.45),
        "color": "#d78dba",
        "cells": [
            "신경세포",
            "성상세포",
            "희소돌기아교세포"
        ],
        "function": (
            "감각 정보 처리, 운동 조절, 기억, "
            "사고 및 신체 기능 조절"
        ),
        "loss": (
            "손상된 뇌 영역에 따라 운동, 감각, "
            "언어 또는 인지 기능에 문제가 발생할 수 있다."
        )
    },

    "심장": {
        "center": (0.28, -0.22, 2.15),
        "scale": (0.28, 0.23, 0.38),
        "color": "#e85d75",
        "cells": [
            "심근세포",
            "내피세포",
            "섬유아세포"
        ],
        "function": (
            "혈액을 순환시켜 산소와 영양소를 "
            "각 조직으로 운반한다."
        ),
        "loss": (
            "혈액 순환이 중단되면 조직에 산소와 "
            "영양소를 공급할 수 없게 된다."
        )
    },

    "폐": {
        "center": (-0.48, 0, 2.0),
        "scale": (0.38, 0.25, 0.55),
        "color": "#8bc9dc",
        "cells": [
            "폐포 제1형 세포",
            "폐포 제2형 세포",
            "섬모상피세포"
        ],
        "function": (
            "산소와 이산화탄소의 교환을 담당한다."
        ),
        "loss": (
            "산소 공급과 이산화탄소 배출이 "
            "어려워진다."
        )
    },

    "간": {
        "center": (0.40, -0.10, 1.55),
        "scale": (0.48, 0.30, 0.22),
        "color": "#b87a48",
        "cells": [
            "간세포",
            "쿠퍼세포",
            "담관세포"
        ],
        "function": (
            "물질 대사, 담즙 생성, 혈장 단백질 합성, "
            "독성 물질의 대사"
        ),
        "loss": (
            "대사 조절, 혈액 응고 단백질 합성, "
            "담즙 생성 등에 문제가 생길 수 있다."
        )
    },

    "신장": {
        "center": (0.50, 0.10, 1.0),
        "scale": (0.24, 0.20, 0.35),
        "color": "#a66f8f",
        "cells": [
            "족세포",
            "근위세뇨관 세포",
            "원위세뇨관 세포"
        ],
        "function": (
            "혈액을 여과하고 수분, 전해질, "
            "노폐물 배출을 조절한다."
        ),
        "loss": (
            "노폐물 배출과 체액 및 전해질 "
            "균형 유지에 문제가 생길 수 있다."
        )
    },

    "위": {
        "center": (-0.30, -0.15, 1.35),
        "scale": (0.32, 0.22, 0.28),
        "color": "#e5a16b",
        "cells": [
            "위벽세포",
            "주세포",
            "점액분비세포"
        ],
        "function": (
            "음식물을 저장하고 위산과 소화 효소를 "
            "통해 소화를 시작한다."
        ),
        "loss": (
            "소화 과정과 음식물의 저장 및 "
            "이동에 문제가 발생할 수 있다."
        )
    }
}


# --------------------------------------------------
# 3D 인체 모델
# --------------------------------------------------

def draw_human(removed_organs=None):

    if removed_organs is None:
        removed_organs = []

    fig = make_figure(
        "3D Human Anatomy"
    )

    # 머리
    fig.add_trace(
        ellipsoid(
            (0, 0, 3.3),
            (0.48, 0.40, 0.45),
            "#d4a17f",
            "머리"
        )
    )

    # 목
    fig.add_trace(
        ellipsoid(
            (0, 0, 2.85),
            (0.18, 0.18, 0.25),
            "#c99576",
            "목"
        )
    )

    # 몸통
    fig.add_trace(
        ellipsoid(
            (0, 0, 2.05),
            (0.70, 0.38, 0.90),
            "#c99576",
            "몸통",
            opacity=0.22
        )
    )

    # 골반
    fig.add_trace(
        ellipsoid(
            (0, 0, 1.05),
            (0.55, 0.34, 0.35),
            "#c99576",
            "골반",
            opacity=0.35
        )
    )

    # 팔
    for side in [-1, 1]:

        fig.add_trace(
            ellipsoid(
                (
                    side * 0.90,
                    0,
                    1.95
                ),
                (
                    0.20,
                    0.20,
                    0.70
                ),
                "#c99576",
                "팔",
                opacity=0.35
            )
        )

    # 다리
    for side in [-1, 1]:

        fig.add_trace(
            ellipsoid(
                (
                    side * 0.25,
                    0,
                    0.30
                ),
                (
                    0.23,
                    0.23,
                    0.85
                ),
                "#c99576",
                "다리",
                opacity=0.35
            )
        )

    # 장기
    for name, organ in ORGANS.items():

        if name in removed_organs:
            continue

        fig.add_trace(
            ellipsoid(
                organ["center"],
                organ["scale"],
                organ["color"],
                name
            )
        )

    fig.update_layout(
        scene=dict(
            xaxis=dict(
                range=[-1.5, 1.5]
            ),
            yaxis=dict(
                range=[-1, 1]
            ),
            zaxis=dict(
                range=[-0.5, 4]
            )
        )
    )

    return fig


# --------------------------------------------------
# 세포 모델
# --------------------------------------------------

def draw_cell(cell_name):

    fig = make_figure(
        "3D Cell Model"
    )

    # 세포막
    fig.add_trace(
        ellipsoid(
            (0, 0, 0),
            (2, 1.5, 1.5),
            "#70c7d9",
            "세포막",
            opacity=0.18
        )
    )

    # 세포질
    fig.add_trace(
        ellipsoid(
            (0, 0, 0),
            (1.85, 1.38, 1.38),
            "#7db8a5",
            "세포질",
            opacity=0.12
        )
    )

    # 핵
    fig.add_trace(
        ellipsoid(
            (0, 0, 0),
            (0.65, 0.65, 0.65),
            "#a68be0",
            "핵"
        )
    )

    # 미토콘드리아
    for center in [
        (1.0, 0.4, 0.2),
        (-1.0, -0.5, 0.4),
        (0.5, -0.8, -0.4)
    ]:

        fig.add_trace(
            ellipsoid(
                center,
                (0.35, 0.18, 0.15),
                "#e9a66b",
                "미토콘드리아"
            )
        )

    # 소포체
    for i in range(4):

        x = np.linspace(
            -0.9,
            0.9,
            100
        )

        y = (
            0.5
            + 0.15
            * np.sin(
                x * 5 + i
            )
        )

        z = np.full_like(
            x,
            -0.2 + i * 0.12
        )

        fig.add_trace(
            line3d(
                x,
                y,
                z,
                "#7a9fe0",
                width=5,
                name="소포체"
            )
        )

    # 골지체
    for i in range(5):

        x = np.linspace(
            -0.4,
            0.4,
            50
        )

        y = np.full_like(
            x,
            -0.8
        )

        z = (
            -0.3
            + i * 0.12
            + 0.05
            * np.sin(
                x * 5
            )
        )

        fig.add_trace(
            line3d(
                x,
                y,
                z,
                "#e3c36d",
                width=5,
                name="골지체"
            )
        )

    # 리보솜
    rng = np.random.default_rng(42)

    for i in range(30):

        px = rng.uniform(
            -1.3,
            1.3
        )

        py = rng.uniform(
            -0.9,
            0.9
        )

        pz = rng.uniform(
            -0.9,
            0.9
        )

        if (
            px**2 + py**2 + pz**2
            < 1.4
        ):

            fig.add_trace(
                go.Scatter3d(
                    x=[px],
                    y=[py],
                    z=[pz],
                    mode="markers",
                    marker=dict(
                        size=3,
                        color="#e6e6e6"
                    ),
                    name="리보솜"
                )
            )

    return fig


# --------------------------------------------------
# DNA 이중나선
# --------------------------------------------------

def draw_dna(sequence):

    fig = make_figure(
        "DNA Double Helix"
    )

    t = np.linspace(
        0,
        8 * np.pi,
        500
    )

    radius = 0.8

    x1 = radius * np.cos(t)
    y1 = radius * np.sin(t)
    z1 = t / 5

    x2 = radius * np.cos(t + np.pi)
    y2 = radius * np.sin(t + np.pi)
    z2 = t / 5

    fig.add_trace(
        line3d(
            x1,
            y1,
            z1,
            "#5a9be6",
            width=8,
            name="DNA 가닥 1"
        )
    )

    fig.add_trace(
        line3d(
            x2,
            y2,
            z2,
            "#e56b9c",
            width=8,
            name="DNA 가닥 2"
        )
    )

    # 염기쌍
    for i in range(
        0,
        len(t),
        12
    ):

        fig.add_trace(
            line3d(
                [
                    x1[i],
                    x2[i]
                ],
                [
                    y1[i],
                    y2[i]
                ],
                [
                    z1[i],
                    z2[i]
                ],
                "#e5d9a0",
                width=3,
                name="염기쌍"
            )
        )

    fig.update_layout(
        scene=dict(
            aspectmode="data"
        )
    )

    return fig


# --------------------------------------------------
# DNA 염기서열 교육용 모델
# --------------------------------------------------

def analyze_sequence(sequence):

    sequence = sequence.upper().replace(
        " ",
        ""
    )

    if not sequence:

        return (
            "염기서열이 입력되지 않았습니다.",
            "변화 없음"
        )

    invalid = [
        base
        for base in sequence
        if base not in "ATGC"
    ]

    if invalid:

        return (
            "A, T, G, C만 입력할 수 있습니다.",
            "변화 없음"
        )

    if len(sequence) % 3 != 0:

        return (
            "염기서열 길이가 3의 배수가 아닙니다. "
            "코돈 단위로 입력해 주세요.",
            "단백질 변화 모델을 적용할 수 없음"
        )

    codons = [
        sequence[i:i + 3]
        for i in range(
            0,
            len(sequence),
            3
        )
    ]

    return (
        "입력된 염기서열: "
        + " - ".join(codons),
        "단백질 합성의 교육용 예시"
    )


# --------------------------------------------------
# 화면 구성
# --------------------------------------------------

mode = st.sidebar.radio(
    "탐구 단계",
    [
        "인체",
        "장기",
        "세포",
        "DNA와 형질",
        "약물 반응"
    ]
)

# --------------------------------------------------
# 인체
# --------------------------------------------------

if mode == "인체":

    st.header("인체 3D 탐구")

    removed = st.multiselect(
        "제거할 장기를 선택하세요.",
        list(ORGANS.keys())
    )

    fig = draw_human(
        removed_organs=removed
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    if removed:

        st.subheader(
            "장기 제거에 따른 기능 변화"
        )

        for name in removed:

            st.markdown(
                f"**{name}**: "
                + ORGANS[name]["loss"]
            )

    st.caption(
        "장기 제거에 따른 결과는 "
        "교육용 개념 설명이며 실제 생리학적 예측이 아닙니다."
    )


# --------------------------------------------------
# 장기
# --------------------------------------------------

elif mode == "장기":

    st.header("장기 3D 탐구")

    organ_name = st.selectbox(
        "탐구할 장기",
        list(ORGANS.keys())
    )

    organ = ORGANS[organ_name]

    fig = make_figure(
        organ_name + " 3D"
    )

    fig.add_trace(
        ellipsoid(
            organ["center"],
            organ["scale"],
            organ["color"],
            organ_name
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "장기의 기능"
    )

    st.write(
        organ["function"]
    )

    st.subheader(
        "구성 세포"
    )

    for cell in organ["cells"]:

        st.markdown(
            "- " + cell
        )

    st.info(
        "장기별 세포 구성은 대표적인 세포를 "
        "교육 목적으로 단순화한 목록입니다."
    )


# --------------------------------------------------
# 세포
# --------------------------------------------------

elif mode == "세포":

    st.header("세포 3D 탐구")

    cell_name = st.selectbox(
        "세포 종류",
        [
            "심근세포",
            "신경세포",
            "간세포",
            "폐포 제1형 세포",
            "근위세뇨관 세포"
        ]
    )

    st.plotly_chart(
        draw_cell(cell_name),
        use_container_width=True
    )

    st.subheader(
        "세포 소기관"
    )

    organelle = st.selectbox(
        "알아볼 소기관",
        [
            "세포막",
            "핵",
            "미토콘드리아",
            "리보솜",
            "소포체",
            "골지체"
        ]
    )

    descriptions = {

        "세포막":
            "세포의 경계를 이루며 물질 이동과 신호 전달을 조절한다.",

        "핵":
            "DNA를 보관하며 유전자 발현 조절에 중요한 역할을 한다.",

        "미토콘드리아":
            "세포 호흡을 통해 ATP를 생산한다.",

        "리보솜":
            "mRNA의 정보를 바탕으로 단백질을 합성한다.",

        "소포체":
            "단백질 및 지질의 합성과 처리에 관여한다.",

        "골지체":
            "단백질과 지질을 가공하고 분류 및 운반한다."
    }

    st.write(
        descriptions[organelle]
    )


# --------------------------------------------------
# DNA와 형질
# --------------------------------------------------

elif mode == "DNA와 형질":

    st.header("DNA와 형질 변화")

    st.markdown(
        """
        DNA의 염기서열은 유전정보를 저장한다.

        유전자 발현을 통해 만들어진 단백질은
        세포의 구조와 기능에 영향을 준다.

        세포의 변화가 조직과 기관의 변화로 이어질 수 있다.
        """
    )

    sequence = st.text_input(
        "DNA 염기서열",
        value="ATG GCT CAA",
        help="A, T, G, C를 입력하세요."
    )

    clean_sequence = sequence.replace(
        " ",
        ""
    ).upper()

    st.plotly_chart(
        draw_dna(clean_sequence),
        use_container_width=True
    )

    result, interpretation = analyze_sequence(
        clean_sequence
    )

    st.write(result)

    st.subheader(
        "교육용 형질 시각화"
    )

    # 교육용 가상 형질
    # 실제 인간 유전자나 표현형을 예측하지 않음
    variation = clean_sequence.count("G")

    color_strength = min(
        1.0,
        variation / max(
            len(clean_sequence),
            1
        )
    )

    st.write(
        "모형의 G 염기 비율:",
        f"{color_strength * 100:.1f}%"
    )

    fig = draw_human()

    fig.update_layout(
        title="DNA 변화에 따른 가상 인체 표현"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.warning(
        "이 시각화는 실제 인간의 형질을 예측하지 않습니다. "
        "특정 염기서열과 형질 사이의 관계는 유전자, "
        "발현 조절, 환경 등 여러 요인에 의해 결정됩니다."
    )


# --------------------------------------------------
# 약물 반응
# --------------------------------------------------

elif mode == "약물 반응":

    st.header("약물과 생리 반응")

    st.warning(
        "이 기능은 약물의 생리학적 작용을 학습하기 위한 "
        "개념 모델입니다. 실제 약물 투여, 주입, 용량 또는 "
        "개인의 반응을 예측하지 않습니다."
    )

    drug = st.selectbox(
        "탐구할 약물 계열",
        [
            "카페인 계열",
            "진정 작용 약물 계열",
            "오피오이드 계열",
            "각성 작용 약물 계열"
        ]
    )

    effects = {

        "카페인 계열": {
            "system": "중추신경계",
            "effect":
                "아데노신 수용체 신호를 억제하여 "
                "각성 상태에 영향을 줄 수 있다.",
            "visual":
                "각성 상태와 관련된 개념적 신경 신호 표시"
        },

        "진정 작용 약물 계열": {
            "system": "중추신경계",
            "effect":
                "일부 약물은 신경계의 억제성 신호를 "
                "강화하여 졸림이나 반응 저하를 일으킬 수 있다.",
            "visual":
                "신경 신호 활동 감소의 개념적 표현"
        },

        "오피오이드 계열": {
            "system": "신경계 및 호흡 조절",
            "effect":
                "통증 신호 전달에 영향을 주며, "
                "호흡 억제 등 심각한 부작용이 나타날 수 있다.",
            "visual":
                "통증 신호와 호흡 조절의 관계를 나타내는 "
                "개념적 시각화"
        },

        "각성 작용 약물 계열": {
            "system": "중추신경계",
            "effect":
                "신경전달물질 신호에 영향을 주어 "
                "각성이나 심박수 등의 변화가 나타날 수 있다.",
            "visual":
                "신경 신호 전달 변화의 개념적 표현"
        }
    }

    selected = effects[drug]

    st.subheader(
        "작용 계통"
    )

    st.write(
        selected["system"]
    )

    st.subheader(
        "생리학적 설명"
    )

    st.write(
        selected["effect"]
    )

    st.subheader(
        "3D 인체 반응"
    )

    fig = draw_human()

    fig.update_layout(
        title=selected["visual"]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "사람이 보는 화면의 개념적 표현"
    )

    st.markdown(
        """
        아래 화면은 실제 약물 사용자의 시야를 재현하는 것이 아니라,
        신경계의 정보 처리와 감각 변화에 대한 개념을 설명하기 위한
        추상적 시각화입니다.
        """
    )

    if drug == "카페인 계열":

        st.info(
            "각성 상태와 주의 집중의 관계를 "
            "학습하는 개념적 화면입니다."
        )

    elif drug == "진정 작용 약물 계열":

        st.info(
            "신경계 억제와 반응 시간의 관계를 "
            "학습하는 개념적 화면입니다."
        )

    elif drug == "오피오이드 계열":

        st.error(
            "오피오이드 계열 약물은 호흡 억제 등 "
            "생명을 위협할 수 있는 부작용을 일으킬 수 있습니다."
        )

    else:

        st.info(
            "신경전달물질과 각성 상태의 관계를 "
            "학습하는 개념적 화면입니다."
        )

st.divider()

st.caption(
    "BioSphere 3D | 생명과학 교육용 시각화 프로젝트"
)
