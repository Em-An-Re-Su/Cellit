import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random

st.set_page_config(page_title="Gene Studio | 3D 유전자 실험실", page_icon="🧬", layout="wide")

st.title("🧬 Gene Studio")
st.caption("3D DNA 편집과 유전자–형질 관계를 탐구하는 교육용 시뮬레이터")
st.info(
    "교육용 단순 모델입니다. 실제 생물의 형질은 여러 유전자와 환경의 영향을 받을 수 있으며, "
    "아래 색소 형질은 원리를 설명하기 위해 가상으로 설정했습니다."
)

BASES = ["A", "T", "C", "G"]
BASE_COLORS = {"A": "#E76F51", "T": "#2A9D8F", "C": "#457B9D", "G": "#E9C46A"}
COMPLEMENT = {"A": "T", "T": "A", "C": "G", "G": "C"}
DEFAULT_SEQ = "ATGCGTACCTGACTGGAACCTGATCGTACG"

def normalize_sequence(raw):
    seq = "".join(ch for ch in raw.upper() if ch in BASES)
    return seq[:60]

def pigment_score(seq):
    # Deliberately simplified teaching rule:
    # the number of G/C bases represents a fictional pigment-production score.
    if not seq:
        return 0.0
    gc_ratio = sum(ch in "GC" for ch in seq) / len(seq)
    return round(100 * gc_ratio, 1)

def phenotype(score):
    # Map the teaching score to a color gradient from pale yellow to deep purple.
    t = max(0.0, min(1.0, score / 100.0))
    start = np.array([245, 222, 150], dtype=float)
    end = np.array([91, 45, 130], dtype=float)
    rgb = (start * (1 - t) + end * t).astype(int)
    return "#{:02x}{:02x}{:02x}".format(*rgb), t

def make_dna_figure(seq, selected_index=None):
    if not seq:
        seq = "ATGC"
    n = len(seq)
    theta = np.linspace(0, 2 * np.pi * max(n / 10, 1), n)
    z = np.linspace(0, max(n / 3.3, 1), n)
    radius = 1.0
    x1, y1 = radius * np.cos(theta), radius * np.sin(theta)
    x2, y2 = radius * np.cos(theta + np.pi), radius * np.sin(theta + np.pi)

    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=x1, y=y1, z=z, mode="lines+markers",
        line=dict(color="#3A86FF", width=6),
        marker=dict(size=4, color=[BASE_COLORS[b] for b in seq],
                    line=dict(color="white", width=0.5)),
        name="가닥 1", hovertemplate="가닥 1<br>염기: %{text}<extra></extra>",
        text=list(seq)
    ))
    comp = "".join(COMPLEMENT[b] for b in seq)
    fig.add_trace(go.Scatter3d(
        x=x2, y=y2, z=z, mode="lines+markers",
        line=dict(color="#8338EC", width=6),
        marker=dict(size=4, color=[BASE_COLORS[b] for b in comp],
                    line=dict(color="white", width=0.5)),
        name="가닥 2 (상보적)", hovertemplate="상보 가닥<br>염기: %{text}<extra></extra>",
        text=list(comp)
    ))

    # Base-pair rungs
    for i in range(n):
        highlight = (i == selected_index)
        fig.add_trace(go.Scatter3d(
            x=[x1[i], x2[i]], y=[y1[i], y2[i]], z=[z[i], z[i]],
            mode="lines",
            line=dict(color="#FF006E" if highlight else "rgba(130,140,150,0.65)",
                      width=5 if highlight else 2),
            showlegend=False,
            hovertemplate=f"위치 {i+1}: {seq[i]}–{comp[i]}<extra></extra>"
        ))

    fig.update_layout(
        height=520,
        margin=dict(l=0, r=0, t=10, b=0),
        scene=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            zaxis=dict(visible=False, title=""),
            aspectmode="manual", aspectratio=dict(x=1, y=1, z=1.5),
            camera=dict(eye=dict(x=1.6, y=1.6, z=1.1)),
            bgcolor="rgba(0,0,0,0)"
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
    )
    return fig

if "sequence" not in st.session_state:
    st.session_state.sequence = DEFAULT_SEQ
if "original_sequence" not in st.session_state:
    st.session_state.original_sequence = DEFAULT_SEQ
if "selected_index" not in st.session_state:
    st.session_state.selected_index = 0

with st.sidebar:
    st.header("🧪 유전자 편집 도구")
    st.write("A, T, C, G 네 가지 염기를 사용합니다.")
    edit_mode = st.radio("편집 방식", ["염기 하나 바꾸기", "전체 서열 직접 입력", "무작위 변이"], index=0)

    if edit_mode == "염기 하나 바꾸기":
        pos = st.number_input("편집할 위치 (1부터 시작)", min_value=1, max_value=len(st.session_state.sequence), value=min(st.session_state.selected_index + 1, len(st.session_state.sequence)), step=1)
        current_base = st.session_state.sequence[pos - 1]
        st.write(f"현재 위치의 염기: **{current_base}**")
        new_base = st.selectbox("새 염기", BASES, index=BASES.index(current_base))
        if st.button("선택한 염기 적용", use_container_width=True):
            seq = list(st.session_state.sequence)
            seq[pos - 1] = new_base
            st.session_state.sequence = "".join(seq)
            st.session_state.selected_index = pos - 1
            st.rerun()

    elif edit_mode == "전체 서열 직접 입력":
        typed = st.text_area("DNA 서열 (A/T/C/G)", value=st.session_state.sequence, height=110)
        if st.button("서열 적용", use_container_width=True):
            cleaned = normalize_sequence(typed)
            if len(cleaned) < 4:
                st.error("A, T, C, G로 된 염기를 4개 이상 입력해 주세요.")
            else:
                st.session_state.sequence = cleaned
                st.session_state.selected_index = 0
                st.rerun()

    else:
        mutation_count = st.slider("변이시킬 염기 수", 1, min(10, len(st.session_state.sequence)), 1)
        if st.button("무작위 변이 적용", use_container_width=True):
            seq = list(st.session_state.sequence)
            indices = random.sample(range(len(seq)), k=mutation_count)
            for i in indices:
                choices = [b for b in BASES if b != seq[i]]
                seq[i] = random.choice(choices)
            st.session_state.sequence = "".join(seq)
            st.session_state.selected_index = indices[0]
            st.rerun()

    st.divider()
    if st.button("원래 서열로 초기화", use_container_width=True):
        st.session_state.sequence = st.session_state.original_sequence
        st.session_state.selected_index = 0
        st.rerun()
    if st.button("현재 서열을 원본으로 저장", use_container_width=True):
        st.session_state.original_sequence = st.session_state.sequence
        st.success("현재 서열을 원본으로 저장했습니다.")

seq = st.session_state.sequence
original = st.session_state.original_sequence
score = pigment_score(seq)
original_score = pigment_score(original)
color, _ = phenotype(score)
original_color, _ = phenotype(original_score)

left, right = st.columns([1.55, 1])
with left:
    st.subheader("3D DNA 이중 나선")
    st.plotly_chart(make_dna_figure(seq, st.session_state.selected_index), use_container_width=True)
    st.caption("마우스로 회전·확대할 수 있습니다. 점 위에 마우스를 올리면 염기 정보가 표시됩니다.")

with right:
    st.subheader("가상 형질: 색소 생성")
    st.markdown("이 모델에서는 **G와 C의 비율**을 가상의 색소 생성 지표로 사용합니다. 실제 유전학에서 GC 비율만으로 색을 예측할 수 있는 것은 아닙니다.")
    st.metric("가상 색소 지수", f"{score:.1f} / 100", delta=f"{score - original_score:+.1f} (원본 대비)")
    st.markdown(
        f"""
        <div style="border:1px solid rgba(128,128,128,.35); border-radius:16px; padding:18px; text-align:center;">
          <div style="font-size:14px; opacity:.8; margin-bottom:10px;">시뮬레이션된 생물의 색</div>
          <div style="width:130px;height:130px;border-radius:50%;margin:auto;background:{color};
          border:5px solid rgba(255,255,255,.7);box-shadow:0 5px 22px rgba(0,0,0,.18);"></div>
          <div style="font-family:monospace;margin-top:12px;">{color}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write(f"원본 서열의 가상 지수: **{original_score:.1f}**")
    st.write(f"현재 서열 길이: **{len(seq)} 염기쌍 위치**")

st.divider()
st.subheader("유전자 서열 비교")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**원본 서열**")
    st.code(original, language=None)
with col2:
    st.markdown("**현재 서열**")
    st.code(seq, language=None)

diffs = [i for i, (a, b) in enumerate(zip(original, seq)) if a != b]
if len(original) != len(seq):
    st.warning("원본과 현재 서열의 길이가 다릅니다. 아래 위치별 비교는 공통 길이 안에서만 표시합니다.")
if diffs:
    st.write("변경된 위치:", ", ".join(str(i + 1) for i in diffs))
else:
    st.success("원본과 현재 서열이 같습니다.")

st.subheader("염기쌍과 상보적 결합")
st.caption("DNA에서 A는 T와, C는 G와 상보적으로 결합합니다.")
pair_cols = st.columns(min(len(seq), 15))
for i, base in enumerate(seq[:15]):
    with pair_cols[i]:
        st.markdown(
            f"<div style='text-align:center;border:1px solid #8885;border-radius:8px;padding:8px 2px;'>"
            f"<b>{i+1}</b><br><span style='color:{BASE_COLORS[base]};font-size:20px;font-weight:700'>{base}</span>"
            f"<br>│<br><span style='color:{BASE_COLORS[COMPLEMENT[base]]};font-size:20px;font-weight:700'>{COMPLEMENT[base]}</span></div>",
            unsafe_allow_html=True
        )

st.caption("참고: 이 앱은 DNA 염기쌍의 상보성과 가상의 형질 지표를 보여주는 교육용 시각화입니다. 실제 단백질 번역, 유전자 조절, 우성·열성, 다유전자 형질은 구현하지 않았습니다.")
