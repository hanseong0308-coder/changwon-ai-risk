[Uploading app (1).py…]()

import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="창원 AI 생활안전 레이더",
    page_icon="🚨",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -----------------------------
# 데이터 불러오기
# -----------------------------
def load_csv(filename):
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        return pd.read_csv(path, encoding="utf-8-sig")
    return pd.DataFrame()

final_result = load_csv("final_result.csv")
district_risk = load_csv("district_risk.csv")
weekday_risk = load_csv("weekday_risk.csv")
time_risk = load_csv("time_risk.csv")
feature_importance = load_csv("feature_importance.csv")
model_performance = load_csv("model_performance.csv")
geocode_result = load_csv("geocode_result.csv")

# -----------------------------
# 제목
# -----------------------------
st.title("🚨 창원 AI 생활안전 레이더")
st.markdown(
    "### 민원이 발생한 뒤가 아니라, **발생하기 전에 대응하는 창원**"
)

st.info(
    "AI가 과거 주차단속 패턴을 분석하여 다음날 단속 위험이 높은 지역을 탐지하고 "
    "선제적인 행정 대응을 지원합니다."
)

# -----------------------------
# KPI
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📍 분석 위험지역",
        f"{len(final_result):,}"
    )

with col2:
    if "위험점수" in final_result.columns:
        high_count = (pd.to_numeric(
            final_result["위험점수"], errors="coerce"
        ) >= 70).sum()
    else:
        high_count = 0

    st.metric(
        "🔴 고위험 지역",
        f"{high_count:,}"
    )

with col3:
    if "평균예측단속건수" in final_result.columns:
        avg_pred = pd.to_numeric(
            final_result["평균예측단속건수"],
            errors="coerce"
        ).mean()
    else:
        avg_pred = 0

    st.metric(
        "🤖 평균 예측 단속",
        f"{avg_pred:.1f}건"
    )

with col4:
    if not model_performance.empty:
        st.metric("📊 AI 모델", "Random Forest")
    else:
        st.metric("📊 AI 모델", "분석 완료")

st.divider()

# -----------------------------
# 위험지역
# -----------------------------
st.subheader("🔥 AI가 탐지한 주요 위험지역")

if not final_result.empty:
    display_cols = [
        c for c in [
            "우선순위",
            "구_y",
            "단속장소",
            "평균예측단속건수",
            "최대예측단속건수",
            "위험점수",
            "위험등급",
            "시간대",
            "추천대응"
        ]
        if c in final_result.columns
    ]

    st.dataframe(
        final_result[display_cols].head(10),
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("위험지역 데이터를 불러오지 못했습니다.")

st.divider()

# -----------------------------
# 분석 그래프
# -----------------------------
left, right = st.columns(2)

with left:
    st.subheader("📊 구별 위험도")

    if not district_risk.empty:
        chart_cols = [
            c for c in ["구_y", "위험점수"]
            if c in district_risk.columns
        ]

        if len(chart_cols) == 2:
            chart_df = district_risk[chart_cols].copy()
            chart_df["위험점수"] = pd.to_numeric(
                chart_df["위험점수"], errors="coerce"
            )
            chart_df = chart_df.dropna()
            chart_df = chart_df.set_index("구_y")

            st.bar_chart(chart_df)

with right:
    st.subheader("🕐 시간대별 위험 패턴")

    if not time_risk.empty:
        numeric_cols = [
            c for c in ["시간대", "위험점수"]
            if c in time_risk.columns
        ]

        if len(numeric_cols) == 2:
            chart_df = time_risk[numeric_cols].copy()
            chart_df["위험점수"] = pd.to_numeric(
                chart_df["위험점수"], errors="coerce"
            )
            chart_df = chart_df.dropna()
            chart_df = chart_df.set_index("시간대")

            st.line_chart(chart_df)

st.divider()

# -----------------------------
# 변수 중요도
# -----------------------------
st.subheader("🧠 AI가 판단에 활용한 주요 변수")

if not feature_importance.empty:
    fi_cols = [
        c for c in ["변수", "중요도", "feature", "importance"]
        if c in feature_importance.columns
    ]

    if len(fi_cols) >= 2:
        st.dataframe(
            feature_importance.head(10),
            use_container_width=True,
            hide_index=True
        )

st.divider()

# -----------------------------
# 선제 대응
# -----------------------------
st.subheader("🚨 AI 기반 선제 대응 프로세스")

p1, p2, p3, p4 = st.columns(4)

with p1:
    st.markdown("### ① 데이터 수집")
    st.caption("주차단속·시간·요일 등 도시 데이터를 수집")

with p2:
    st.markdown("### ② AI 예측")
    st.caption("다음날 위험지역과 단속량을 예측")

with p3:
    st.markdown("### ③ 위험 탐지")
    st.caption("고위험 지역과 집중 시간대를 자동 탐지")

with p4:
    st.markdown("### ④ 선제 대응")
    st.caption("순찰·안내·계도 등 행정 대응을 제안")

st.success(
    "💡 목표: 문제가 발생한 뒤 대응하는 행정에서 "
    "**문제가 발생하기 전에 움직이는 선제 행정**으로 전환"
)

st.caption(
    "※ 본 서비스의 위험도는 주차단속 데이터를 활용한 분석 지표이며, "
    "실제 민원 발생 자체를 직접 예측하는 값과는 구분됩니다."
)
