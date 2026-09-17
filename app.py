
import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="창원 AI 생활안전 레이더",
    page_icon="🚨",
    layout="wide"
)

st.title("🚨 창원 AI 생활안전 레이더")
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

# 위험지역
st.header("🚨 AI 예측 위험지역")
# 위험지역 시각화 카드

st.subheader("🔴 주요 위험지역")
st.divider()

st.subheader("📊 위험도 분포")
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
risk_chart = (
    final_result["위험등급"]
    .value_counts()
    .reindex(["높음", "보통", "낮음"])
    .fillna(0)
)

st.bar_chart(risk_chart)
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
st.dataframe(
    final_result[
        [
            "우선순위",
            "구_y",
            "단속장소",
            "예측단속건수",
            "위험점수",
            "위험등급",
            "위험시간",
            "추천대응"
        ]
    ].head(20),
    use_container_width=True,
    hide_index=True
)

st.divider()

# 구별 위험도
st.header("🏙️ 구별 위험도")

st.bar_chart(
    district_risk.set_index("구_y")["위험점수"]
)

st.divider()

# 모델 성능
st.header("🤖 AI 모델 성능")

st.dataframe(
    model_performance,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "※ 본 모델의 예측 대상은 다음날 주정차 단속건수이며, "
    "생활불편 위험을 나타내는 대리 지표(proxy)로 활용했습니다."
)
st.divider()

st.header("🎯 AI 위험 레이더")

# 최고 위험점수
max_risk = float(
    pd.to_numeric(
        final_result["위험점수"],
        errors="coerce"
    ).max()
)

# 0~100 범위로 제한
risk = max(0, min(100, max_risk))

# 레이더 게이지
import streamlit.components.v1 as components

html = f"""
<div style="
    background:white;
    border-radius:20px;
    padding:25px;
    text-align:center;
    border:1px solid #dddddd;
">
<svg width="100%" height="300" viewBox="0 0 600 300">

<circle
    cx="300"
    cy="150"
    r="105"
    fill="none"
    stroke="#eeeeee"
    stroke-width="22"
/>

<circle
    cx="300"
    cy="150"
    r="105"
    fill="none"
    stroke="#e5484d"
    stroke-width="22"
    stroke-linecap="round"
    stroke-dasharray="{risk * 6.60} 660"
    transform="rotate(-90 300 150)"
/>

<circle
    cx="300"
    cy="150"
    r="75"
    fill="#f8f9fa"
/>

<text
    x="300"
    y="145"
    text-anchor="middle"
    font-size="42"
    font-weight="bold"
    fill="#222222">
    {risk:.1f}
</text>

<text
    x="300"
    y="175"
    text-anchor="middle"
    font-size="15"
    fill="#666666">
    AI 위험점수
</text>

</svg>

<div style="
    font-size:16px;
    color:#666666;
">
다음날 주정차 단속 위험 기반
</div>

</div>
"""

components.html(html, height=340)
st.divider()

st.subheader("📌 창원시 AI 위험예측 핵심지표")

c1, c2, c3, c4 = st.columns(4)

c1.metric("분석 대상 장소", "1,089곳")
c2.metric("고위험 장소", "3곳")
c3.metric("최고 위험점수", "100.0")
c4.metric("모델 R²", "0.400")
