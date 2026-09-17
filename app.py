
import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="창원 AI 생활안전 레이더",
    page_icon="🚨",
    layout="wide"
)

st.title("🚨 창원 AI 생활안전 레이더")
st.markdown(
    """
    ### 🛡️ 민원이 발생한 뒤가 아니라, 발생하기 전에 대응하는 창원

    과거 주정차 단속 데이터를 AI로 분석하여
    **어디에서 · 언제 · 생활불편 위험이 높아질 가능성이 있는지** 파악하고,
    행정의 선제적 대응을 지원하는 데이터 기반 플랫폼입니다.
    """
)
st.subheader("민원이 발생한 뒤가 아니라, 발생하기 전에 대응하는 창원")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 데이터 불러오기
final_result = pd.read_csv(
    os.path.join(BASE_DIR, "final_result.csv"),
    encoding="utf-8-sig"
)

district_risk = pd.read_csv(
    os.path.join(BASE_DIR, "district_risk.csv"),
    encoding="utf-8-sig"
)

model_performance = pd.read_csv(
    os.path.join(BASE_DIR, "model_performance.csv"),
    encoding="utf-8-sig"
)

# KPI
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "분석 대상 장소",
    f"{final_result['단속장소'].nunique():,}곳"
)

col2.metric(
    "고위험 장소",
    f"{(final_result['위험등급'] == '높음').sum():,}곳"
)

col3.metric(
    "최고 위험점수",
    f"{final_result['위험점수'].max():.1f}"
)

col4.metric(
    "모델 R²",
    f"{model_performance.loc[model_performance['평가지표'] == 'R²', '값'].iloc[0]:.3f}"
)
st.divider()

st.header("🚨 AI 예측 위험지역")

top_risk = final_result.head(10)

for i, (_, row) in enumerate(top_risk.iterrows(), 1):
    place = row["단속장소"]
    score = row["위험점수"]
    grade = row["위험등급"]
    district = row["구_y"]

    st.markdown(
        f"""
        <div style="
            background:white;
            border-left:6px solid #e5484d;
            padding:16px 20px;
            margin:8px 0;
            border-radius:12px;
            box-shadow:0 2px 8px rgba(0,0,0,0.08);
        ">
            <b style="font-size:19px;">
                #{i} {place}
            </b>
            <br>
            <span style="color:#667085;">
                {district} · 위험등급 {grade}
            </span>
            <br>
            <span style="font-size:17px;">
                🎯 위험점수 <b>{score:.1f}</b>
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
st.divider()

st.subheader("📊 위험도 분포")

risk_chart = (
    final_result["위험등급"]
    .value_counts()
    .reindex(["높음", "보통", "낮음"])
    .fillna(0)
)

st.bar_chart(risk_chart)
st.divider()

st.subheader("🚨 AI 선제대응 TOP 10")

action_cols = [
    "우선순위",
    "구_y",
    "단속장소",
    "위험점수",
    "위험등급",
    "위험시간",
    "추천대응"
]

st.dataframe(
    final_result[action_cols].head(10),
    use_container_width=True,
    hide_index=True
)
