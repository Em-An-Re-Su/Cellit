
from __future__ import annotations

import math
from typing import Dict, Tuple

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from streamlit_plotly_events import plotly_events


st.set_page_config(
    page_title="인체·세포·DNA 탐험실",
    page_icon="🧬",
    layout="wide"
)


# ============================================================
# 1. 기본 설정
# ============================================================

COLORS = {
    "body": "#D8A58F",
    "heart": "#D94B59",
    "lung": "#E99A9A",
    "liver": "#8B4C35",
    "stomach": "#E9B36F",
    "intestine": "#E5A45D",
    "kidney": "#9C5965",
    "brain": "#D98BA7",
    "cell": "#F3C969",
    "nucleus": "#8C70C6",
    "mitochondria": "#D96D57",
    "membrane": "#68B7B0",
    "dna_a": "#4F91D8",
    "dna_b": "#E28A4A"
}


ORGAN_INFO = {
    "brain": (
        "뇌",
        "신경계의 중심으로 감각 정보를 통합하고 "
        "운동, 기억, 언어 등 다양한 기능을 조절합니다.",
        "신경세포(뉴런), 신경교세포"
    ),

    "heart": (
        "심장",
        "수축과 이완을 반복해 혈액을 폐와 온몸으로 "
        "순환시키는 근육성 기관입니다.",
        "심근세포, 혈관 내피세포"
    ),

    "lung_l": (
        "왼쪽 폐",
        "폐포에서 산소와 이산화탄소가 확산을 통해 교환됩니다.",
        "폐포 상피세포, 모세혈관 내피세포"
    ),

    "lung_r": (
        "오른쪽 폐",
        "폐포에서 산소와 이산화탄소가 확산을 통해 교환됩니다.",
        "폐포 상피세포, 모세혈관 내피세포"
    ),

    "liver": (
        "간",
        "영양소 대사, 혈장 단백질 합성, 담즙 생성 및 "
        "여러 물질의 대사에 관여합니다.",
        "간세포, 쿠퍼세포"
    ),

    "stomach": (
        "위",
        "음식물을 일시적으로 저장하고 위액과 근육 운동으로 "
        "잘게 섞어 소화합니다.",
        "벽세포, 주세포, 점액세포"
    ),

    "kidney_l": (
        "왼쪽 신장",
        "혈액을 여과하고 수분과 전해질 균형 및 "
        "노폐물 배설을 조절합니다.",
        "족세포, 세뇨관 상피세포"
    ),

    "kidney_r": (
        "오른쪽 신장",
        "혈액을 여과하고 수분과 전해질 균형 및 "
        "노폐물 배설을 조절합니다.",
        "족세포, 세뇨관 상피세포"
    ),

    "intestine": (
        "장",
        "소장에서는 영양소 흡수가, 대장에서는 "
        "수분 흡수와 대변 형성이 주로 이루어집니다.",
        "장 상피세포, 술잔세포"
    )
}


# ============================================================
# 2. 3D 타원체 생성 함수
# ============================================================

def ellipsoid(
    center: Tuple[float, float, float],
    radii: Tuple[float, float, float],
    color: str,
    name: str,
    opacity: float = 1.0,
    resolution: int = 18,
    rotation: float = 0.0
) -> go.Mesh3d:

    cx, cy, cz = center
    rx, ry, rz = radii

    u = np.linspace(0, 2 * np.pi, resolution)
    v = np.linspace(0, np.pi, resolution)

    uu, vv = np.meshgrid(u, v)

    x0 = rx * np.sin(vv) * np.cos(uu)
    y0 = ry * np.sin(vv) * np.sin(uu)
    z0 = rz * np.cos(vv)

    c = math.cos(rotation)
    s = math.sin(rotation)

    x = c * x0 - s * z0 + cx
    z = s * x0 + c * z0 + cz
    y = y0 + cy

    rows, cols = x.shape

    ii, jj, kk = [], [], []

    for r in range(rows - 1):
        for col in range(cols - 1):

            a = r * cols + col

            b = a + 1
            d = (r + 1) * cols + col
            e = (r + 1) * cols + col + 1

            ii.extend([a, a])
            jj.extend([b, d])
            kk.extend([e, e])

    return go.Mesh3d(
        x=x.flatten(),
        y=y.flatten(),
        z=z.flatten(),
        i=ii,
        j=jj,
        k=kk,
        color=color,
        opacity=opacity,
        name=name,
        hovertemplate=f"{name}<extra></extra>",
        flatshading=False,
        showscale=False
    )


# ============================================================
# 3. 장기 생성
# ============================================================

def add_organ(
    fig,
    organ_id,
    center,
    radii,
    color,
    label=None,
    rotation=0.0
):

    title = label or ORGAN_INFO[organ_id][0]

    mesh = ellipsoid(
        center,
        radii,
        color,
        title,
        0.98,
        22,
        rotation
    )

    mesh.customdata = np.full(
        len(mesh.x),
        organ_id,
        dtype=object
    )

    fig.add_trace(mesh)


# ============================================================
# 4. 인체 3D 모델
# ============================================================

def make_human_figure():

    fig = go.Figure()

    body_parts = [

        ((0, 0, 5.05), (0.43, 0.30, 0.55), "몸통"),
        ((0, 0, 4.05), (0.56, 0.27, 0.78), "골반"),
        ((0, 0, 6.00), (0.68, 0.29, 0.72), "흉곽"),
        ((0, 0, 7.02), (0.28, 0.27, 0.35), "목"),
        ((0, 0, 7.62), (0.48, 0.42, 0.55), "머리"),

        ((-0.82, 0, 5.95), (0.20, 0.22, 1.18), "왼쪽 위팔"),
        ((-1.00, 0, 4.65), (0.17, 0.18, 1.05), "왼쪽 아래팔"),

        ((0.82, 0, 5.95), (0.20, 0.22, 1.18), "오른쪽 위팔"),
        ((1.00, 0, 4.65), (0.17, 0.18, 1.05), "오른쪽 아래팔"),

        ((-0.30, 0, 2.65), (0.23, 0.24, 1.55), "왼쪽 다리"),
        ((0.30, 0, 2.65), (0.23, 0.24, 1.55), "오른쪽 다리"),

        ((-0.30, -0.06, 1.05), (0.24, 0.43, 0.16), "왼쪽 발"),
        ((0.30, -0.06, 1.05), (0.24, 0.43, 0.16), "오른쪽 발")
    ]

    for center, radii, label in body_parts:

        fig.add_trace(
            ellipsoid(
                center,
                radii,
                COLORS["body"],
                label,
                0.20,
                20
            )
        )

    # 주요 장기

    add_organ(
        fig, "brain",
        (0, -0.04, 7.65),
        (0.34, 0.28, 0.34),
        COLORS["brain"]
    )

    add_organ(
        fig, "lung_l",
        (-0.27, -0.22, 6.08),
        (0.27, 0.15, 0.63),
        COLORS["lung"]
    )

    add_organ(
        fig, "lung_r",
        (0.27, -0.22, 6.08),
        (0.27, 0.15, 0.63),
        COLORS["lung"]
    )

    add_organ(
        fig, "heart",
        (0.02, -0.34, 5.88),
        (0.20, 0.16, 0.31),
        COLORS["heart"],
        rotation=-0.18
    )

    add_organ(
        fig, "liver",
        (-0.30, -0.25, 5.05),
        (0.43, 0.18, 0.25),
        COLORS["liver"]
    )

    add_organ(
        fig, "stomach",
        (0.30, -0.27, 5.00),
        (0.24, 0.15, 0.31),
        COLORS["stomach"],
        rotation=0.35
    )

    add_organ(
        fig, "kidney_l",
        (-0.37, -0.15, 4.55),
        (0.15, 0.13, 0.27),
        COLORS["kidney"]
    )

    add_organ(
        fig, "kidney_r",
        (0.37, -0.15, 4.55),
        (0.15, 0.13, 0.27),
        COLORS["kidney"]
    )

    add_organ(
        fig, "intestine",
        (0, -0.29, 4.40),
        (0.36, 0.12, 0.36),
        COLORS["intestine"]
    )

    fig.update_layout(
        title="인체 정면 모형 · 장기를 선택해 탐색하세요",
        height=680,
        margin=dict(l=0, r=0, t=55, b=0),
        showlegend=False,

        scene=dict(
            xaxis=dict(visible=False, range=[-1.5, 1.5]),
            yaxis=dict(visible=False, range=[-0.8, 0.8]),
            zaxis=dict(visible=False, range=[0.7, 8.4]),

            aspectmode="manual",
            aspectratio=dict(
                x=0.58,
                y=0.30,
                z=1.45
            ),

            camera=dict(
                eye=dict(x=0, y=-2.8, z=0.15)
            )
        )
    )

    return fig


# ============================================================
# 5. 장기 확대 모델
# ============================================================

def make_organ_figure(organ_id):

    title, description, cells = ORGAN_INFO[organ_id]

    fig = go.Figure()

    color = {
        "brain": COLORS["brain"],
        "heart": COLORS["heart"],
        "lung_l": COLORS["lung"],
        "lung_r": COLORS["lung"],
        "liver": COLORS["liver"],
        "stomach": COLORS["stomach"],
        "kidney_l": COLORS["kidney"],
        "kidney_r": COLORS["kidney"],
        "intestine": COLORS["intestine"]
    }[organ_id]

    fig.add_trace(
        ellipsoid(
            (0, 0, 0),
            (1.05, 0.62, 0.72),
            color,
            title,
            0.95,
            32,
            rotation=0.18 if organ_id == "heart" else 0
        )
    )

    # 주변 세포 표현

    for i in range(7):

        angle = i * 2 * math.pi / 7

        p = (
            1.22 * math.cos(angle),
            0.72 * math.sin(angle),
            0.12 * math.sin(2 * angle)
        )

        fig.add_trace(
            ellipsoid(
                p,
                (0.12, 0.10, 0.12),
                "#F2D6A2",
                "세포 예시",
                0.95,
                12
            )
        )

    fig.update_layout(
        title=f"{title} · 장기 구조 개요",
        height=470,
        margin=dict(l=0, r=0, t=55, b=0),
        showlegend=False,

        scene=dict(
            xaxis_visible=False,
            yaxis_visible=False,
            zaxis_visible=False,
            aspectmode="data",
            camera=dict(
                eye=dict(x=1.8, y=-2.2, z=1.4)
            )
        )
    )

    return fig


# ============================================================
# 6. 세포와 소기관 모델
# ============================================================

def make_cell_figure():

    fig = go.Figure()

    components = [

        ("membrane", (0, 0, 0),
         (1.55, 1.05, 0.88), COLORS["membrane"],
         "세포막", 0.22, 0.0),

        ("cytoplasm", (0, 0, 0),
         (1.42, 0.94, 0.77), COLORS["cell"],
         "세포질", 0.30, 0.0),

        ("nucleus", (0.05, 0.02, 0.05),
         (0.48, 0.42, 0.42), COLORS["nucleus"],
         "핵", 0.95, 0.0),

        ("mitochondria", (-0.78, -0.28, 0.12),
         (0.34, 0.13, 0.13), COLORS["mitochondria"],
         "미토콘드리아", 1.0, 0.3),

        ("mitochondria", (0.82, 0.24, -0.12),
         (0.34, 0.13, 0.13), COLORS["mitochondria"],
         "미토콘드리아", 1.0, -0.5),

        ("mitochondria", (-0.20, 0.63, -0.25),
         (0.30, 0.12, 0.11), COLORS["mitochondria"],
         "미토콘드리아", 1.0, 0.8),

        ("golgi", (0.75, -0.48, 0.28),
         (0.28, 0.13, 0.12), "#D6A6C8",
         "골지체", 0.95, 0.3),

        ("er", (-0.65, 0.48, -0.35),
         (0.30, 0.12, 0.10), "#7A9DCE",
         "소포체", 0.95, -0.4)
    ]

    for component_id, center, radii, color, label, opacity, rotation in components:

        trace = ellipsoid(
            center,
            radii,
            color,
            label,
            opacity,
            18,
            rotation
        )

        trace.customdata = np.full(
            len(trace.x),
            component_id,
            dtype=object
        )

        fig.add_trace(trace)

    fig.update_layout(
        title="동물세포의 대표 소기관 · 구조를 클릭해 확인하세요",
        height=500,
        margin=dict(l=0, r=0, t=55, b=0),
        showlegend=False,

        scene=dict(
            xaxis_visible=False,
            yaxis_visible=False,
            zaxis_visible=False,
            aspectmode="data",
            camera=dict(
                eye=dict(x=1.8, y=-2.0, z=1.5)
            )
        )
    )

    return fig


# ============================================================
# 7. DNA 서열 처리
# ============================================================

def normalize_sequence(sequence):

    cleaned = "".join(
        ch for ch in sequence.upper()
        if ch in "ATGC"
    )

    return cleaned[:30] or "ATGCGTAC"


def complementary_base(base):

    return {
        "A": "T",
        "T": "A",
        "G": "C",
        "C": "G"
    }[base]


# ============================================================
# 8. DNA 이중 나선
# ============================================================

def make_dna_figure(sequence):

    sequence = normalize_sequence(sequence)

    n = len(sequence)

    t = np.linspace(
        0,
        max(n - 1, 1) * 0.55,
        max(n * 12, 24)
    )

    z = t * 0.48

    x1 = np.cos(t)
    y1 = np.sin(t)

    x2 = -np.cos(t)
    y2 = -np.sin(t)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter3d(
            x=x1,
            y=y1,
            z=z,
            mode="lines",
            line=dict(
                color=COLORS["dna_a"],
                width=8
            ),
            name="가닥 1"
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=x2,
            y=y2,
            z=z,
            mode="lines",
            line=dict(
                color=COLORS["dna_b"],
                width=8
            ),
            name="가닥 2"
        )
    )

    for i, base in enumerate(sequence):

        ti = i * 0.55

        fig.add_trace(
            go.Scatter3d(
                x=[
                    math.cos(ti),
                    -math.cos(ti)
                ],

                y=[
                    math.sin(ti),
                    -math.sin(ti)
                ],

                z=[
                    ti * 0.48,
                    ti * 0.48
                ],

                mode="lines+markers+text",

                line=dict(
                    color="#B7C2D0",
                    width=3
                ),

                marker=dict(
                    size=4,
                    color="#B7C2D0"
                ),

                text=[
                    base,
                    complementary_base(base)
                ],

                textposition="middle center",

                textfont=dict(
                    color="white",
                    size=10
                ),

                showlegend=False,

                hovertemplate=(
                    f"염기쌍 {i+1}: "
                    f"{base}–{complementary_base(base)}"
                    "<extra></extra>"
                )
            )
        )

    fig.update_layout(
        title="DNA 이중 나선 · A-T, G-C 상보적 염기쌍",
        height=520,
        margin=dict(l=0, r=0, t=55, b=0),

        scene=dict(
            xaxis_visible=False,
            yaxis_visible=False,
            zaxis_visible=False,
            aspectmode="manual",
            aspectratio=dict(
                x=1,
                y=1,
                z=2.0
            )
        )
    )

    return fig


# ============================================================
# 9. 교육용 가상 형질 시뮬레이션
# ============================================================

def simulated_traits(sequence):

    seq = normalize_sequence(sequence).ljust(9, "A")

    eye = {
        "A": "청색(데모)",
        "T": "갈색(데모)",
        "G": "녹색(데모)",
        "C": "회색(데모)"
    }[seq[0]]

    hair = {
        "A": "금발(데모)",
        "T": "흑발(데모)",
        "G": "갈색(데모)",
        "C": "적갈색(데모)"
    }[seq[3]]

    skin = {
        "A": "밝은 톤(데모)",
        "T": "중간 톤(데모)",
        "G": "짙은 톤(데모)",
        "C": "올리브 톤(데모)"
    }[seq[6]]

    return {
        "눈 색": eye,
        "머리 색": hair,
        "피부 톤": skin
    }


# ============================================================
# 10. 가상 인간 아바타
# ============================================================

def avatar_figure(traits):

    eye_map = {
        "청색(데모)": "#5C9BD6",
        "갈색(데모)": "#75452A",
        "녹색(데모)": "#5D9865",
        "회색(데모)": "#9AA3AA"
    }

    hair_map = {
        "금발(데모)": "#D8B45A",
        "흑발(데모)": "#302B2A",
        "갈색(데모)": "#80563D",
        "적갈색(데모)": "#A34D36"
    }

    skin_map = {
        "밝은 톤(데모)": "#E9C2A8",
        "중간 톤(데모)": "#C98F70",
        "짙은 톤(데모)": "#87583F",
        "올리브 톤(데모)": "#B58A63"
    }

    fig = go.Figure()

    skin = skin_map[traits["피부 톤"]]

    fig.add_trace(
        ellipsoid(
            (0, 0, 0),
            (0.55, 0.38, 0.72),
            skin,
            "얼굴(데모 아바타)",
            1,
            24
        )
    )

    fig.add_trace(
        ellipsoid(
            (0, 0.0, 0.58),
            (0.56, 0.39, 0.24),
            hair_map[traits["머리 색"]],
            "머리카락(데모)",
            1,
            18
        )
    )

    for x in [-0.20, 0.20]:

        fig.add_trace(
            ellipsoid(
                (x, -0.36, 0.10),
                (0.07, 0.045, 0.055),
                eye_map[traits["눈 색"]],
                "눈(데모)",
                1,
                12
            )
        )

    fig.update_layout(
        title="서열 변경에 따른 아바타 색상 예시",
        height=390,
        margin=dict(l=0, r=0, t=55, b=0),
        showlegend=False,

        scene=dict(
            xaxis_visible=False,
            yaxis_visible=False,
            zaxis_visible=False,
            aspectmode="data",
            camera=dict(
                eye=dict(x=0, y=-2.8, z=0.2)
            )
        )
    )

    return fig


# ============================================================
# 11. 메인 UI
# ============================================================

st.title("🧬 인체·세포·DNA 탐험실")

st.caption(
    "인체 → 장기 → 세포 → 소기관, "
    "그리고 DNA 염기 서열을 단계적으로 살펴보는 "
    "교육용 시뮬레이터"
)

st.warning(
    "교육용 개념 모형입니다. 실제 인체의 정밀 해부학, "
    "의료 진단, 유전자 편집 결과를 재현하지 않습니다. "
    "형질 변화는 실제 유전자와 무관한 임의의 시각화 규칙입니다."
)


if "selected_organ" not in st.session_state:
    st.session_state.selected_organ = "heart"

if "sequence" not in st.session_state:
    st.session_state.sequence = "ATGCGTACG"


anatomy_tab, dna_tab, guide_tab = st.tabs([
    "🫀 인체와 세포",
    "🧬 DNA 탐험",
    "📘 사용 안내"
])


# ============================================================
# 인체 및 세포 탭
# ============================================================

with anatomy_tab:

    st.subheader("1. 인체 내부 장기 선택")

    st.write(
        "3D 모형에서 장기를 클릭하거나 아래 목록에서 선택하세요. "
        "마우스로 회전·확대할 수 있습니다."
    )

    left, right = st.columns([1.35, 1])

    with left:

        body_fig = make_human_figure()

        clicked = plotly_events(
            body_fig,
            click_event=True,
            select_event=False,
            hover_event=False,
            override_height=680,
            key="human_3d_click"
        )

        if clicked:

            point = clicked[0].get("pointNumber")
            curve = clicked[0].get("curveNumber")

            if curve is not None and 0 <= curve < len(body_fig.data):

                trace = body_fig.data[curve]
                custom = getattr(trace, "customdata", None)

                if custom is not None:

                    try:

                        candidate = str(custom[int(point)])

                        if candidate in ORGAN_INFO:
                            st.session_state.selected_organ = candidate

                    except (ValueError, TypeError, IndexError):
                        pass

    with right:

        organ_options = {
            v[0]: k
            for k, v in ORGAN_INFO.items()
        }

        selected_label = next(
            (
                label
                for label, key in organ_options.items()
                if key == st.session_state.selected_organ
            ),
            "심장"
        )

        chosen_label = st.selectbox(
            "장기 선택",
            list(organ_options.keys()),
            index=list(organ_options.keys()).index(selected_label)
        )

        st.session_state.selected_organ = organ_options[chosen_label]

        organ_id = st.session_state.selected_organ

        title, description, cell_types = ORGAN_INFO[organ_id]

        st.plotly_chart(
            make_organ_figure(organ_id),
            use_container_width=True,
            config={"displaylogo": False}
        )

        st.markdown(f"**{title}의 기능**")

        st.write(description)

        st.markdown("**대표 세포 유형**")

        st.write(cell_types)

        st.info(
            "장기 모형은 위치와 대략적인 형태를 설명하기 위한 "
            "단순화된 타원체입니다."
        )

    st.divider()

    st.subheader("2. 세포와 소기관으로 확대")

    st.write(
        "선택한 장기와 관련된 대표 세포를 예시로 살펴봅니다. "
        "아래 세포 모형은 일반적인 동물세포의 개념도입니다."
    )

    cell_left, cell_right = st.columns([1.2, 1])

    with cell_left:

        cell_fig = make_cell_figure()

        cell_clicked = plotly_events(
            cell_fig,
            click_event=True,
            select_event=False,
            hover_event=False,
            override_height=500,
            key="cell_3d_view"
        )

        if cell_clicked:

            event = cell_clicked[0]

            curve = event.get("curveNumber")
            point = event.get("pointNumber")

            if curve is not None and 0 <= curve < len(cell_fig.data):

                custom = getattr(
                    cell_fig.data[curve],
                    "customdata",
                    None
                )

                if custom is not None:

                    try:

                        st.session_state["selected_cell_part"] = str(
                            custom[int(point)]
                        )

                    except (ValueError, TypeError, IndexError):
                        pass

    with cell_right:

        cell_details = {

            "membrane": (
                "세포막",
                "인지질 이중층과 막단백질로 이루어져 "
                "물질 이동과 세포 간 신호 전달을 조절합니다."
            ),

            "cytoplasm": (
                "세포질",
                "세포 내부에서 여러 대사 반응이 일어나는 "
                "환경으로, 세포소기관이 위치합니다."
            ),

            "nucleus": (
                "핵",
                "핵막으로 둘러싸인 공간에 대부분의 DNA가 있으며 "
                "유전자 발현 조절의 중심 역할을 합니다."
            ),

            "mitochondria": (
                "미토콘드리아",
                "세포 호흡과 ATP 생산에 핵심적으로 관여합니다."
            ),

            "golgi": (
                "골지체",
                "단백질과 지질을 수정하고 분류해 "
                "필요한 위치로 운반되도록 포장합니다."
            ),

            "er": (
                "소포체",
                "거친면 소포체는 단백질 합성·가공에, "
                "활면 소포체는 지질 합성 등에 관여합니다."
            )
        }

        chosen_part = st.session_state.get(
            "selected_cell_part",
            "nucleus"
        )

        part_title, part_description = cell_details.get(
            chosen_part,
            cell_details["nucleus"]
        )

        st.markdown(f"**선택한 구조: {part_title}**")

        st.write(part_description)

        st.markdown("**세포 소기관과 기능**")

        st.markdown("""
- **세포막:** 물질의 출입과 세포 신호 전달을 조절합니다.
- **핵:** DNA를 보관하고 유전자 발현을 조절합니다.
- **미토콘드리아:** 세포 호흡을 통해 ATP 생산에 관여합니다.
- **소포체:** 단백질·지질 합성과 가공에 관여합니다.
- **골지체:** 단백질과 지질을 분류·수정·포장합니다.
- **리보솜:** mRNA 정보를 바탕으로 단백질을 합성합니다.
- **세포질:** 여러 대사 반응이 일어나는 세포 내부 환경입니다.
""")

        st.caption(
            f"현재 장기 선택: {title} · "
            f"관련 세포 예시: {cell_types}"
        )


# ============================================================
# DNA 탭
# ============================================================

with dna_tab:

    st.subheader("DNA 이중 나선과 염기 서열 편집")

    st.write(
        "A(아데닌), T(티민), G(구아닌), C(사이토신)를 "
        "입력해 서열을 바꿔 볼 수 있습니다."
    )

    seq_input = st.text_input(
        "DNA 서열 (최대 30개 염기)",
        value=st.session_state.sequence,
        max_chars=30,
        help="A, T, G, C만 사용합니다."
    )

    normalized = normalize_sequence(seq_input)

    if normalized != seq_input.upper().strip():

        st.caption(
            f"표시용으로 정리된 서열: {normalized}"
        )

    st.session_state.sequence = normalized

    st.plotly_chart(
        make_dna_figure(normalized),
        use_container_width=True,
        config={"displaylogo": False}
    )

    st.markdown("**현재 서열의 상보 가닥**")

    st.code(
        "".join(
            complementary_base(b)
            for b in normalized
        )
    )

    st.divider()

    st.subheader("서열 변경에 따른 형질 아바타 데모")

    st.error(
        "중요: 피부색·머리색·눈 색은 다수의 유전자와 "
        "유전자 조절, 발달·환경 요인 등이 복합적으로 관여합니다. "
        "아래 규칙은 앱 작동을 보여주기 위한 임의의 가상 규칙이며 "
        "실제 생물학적 예측이 아닙니다."
    )

    traits = simulated_traits(normalized)

    avatar_left, avatar_right = st.columns([1, 1])

    with avatar_left:

        st.plotly_chart(
            avatar_figure(traits),
            use_container_width=True,
            config={"displaylogo": False}
        )

    with avatar_right:

        st.markdown("**가상 규칙에 따른 표시 결과**")

        for trait, value in traits.items():

            st.metric(
                trait,
                value
            )

        st.caption(
            "서열의 1번째·4번째·7번째 염기를 각각 "
            "눈·머리·피부 색상으로 연결한 임의 규칙입니다."
        )

        if st.button(
            "기본 DNA 서열로 초기화",
            key="reset_dna"
        ):

            st.session_state.sequence = "ATGCGTACG"

            st.rerun()


# ============================================================
# 사용 안내
# ============================================================

with guide_tab:

    st.subheader("이 앱의 범위와 한계")

    st.markdown("""
- **인체 화면:** 정면 인체 실루엣과 주요 장기를 단순화된 3D 도형으로 배치합니다.
- **장기 탐색:** 장기를 선택하면 해당 장기의 개요와 대표 세포 유형을 확인할 수 있습니다.
- **세포 화면:** 세포막, 핵, 미토콘드리아, 소포체, 골지체 등 대표 소기관을 3D로 구분합니다.
- **DNA 화면:** 이중 나선과 상보적 염기쌍을 확인하고 염기 서열을 바꿔 볼 수 있습니다.
- **형질 데모:** 실제 유전학적 예측이 아닌 임의 규칙으로 아바타 색상을 바꾸는 시각적 예시입니다.

**정확성에 관한 안내**

이 앱은 교육용 시각화의 출발점입니다.
인체·장기·세포 형상은 정밀 스캔 기반 메시가 아니며,
실제 장기의 입체적 해부학과 내부 조직 구조를 완전히 재현하지 않습니다.

실제 유전자 편집, 사람에 대한 적용,
질병 위험도 또는 외모 예측 기능은 제공하지 않습니다.
""")

st.caption(
    "제작 목적: 생명과학 개념 학습용 · "
    "의료적 판단이나 실제 유전자 조작에 사용하지 마세요."
)
