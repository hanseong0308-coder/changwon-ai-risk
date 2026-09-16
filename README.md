[Uploading app_backup.py…]()

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
