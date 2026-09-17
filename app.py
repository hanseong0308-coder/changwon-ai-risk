import streamlit as st
import pandas as pd
import os
import folium

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
# 지도 좌표 데이터 불러오기
geocode_result = pd.read_csv(
    os.path.join(BASE_DIR, "geocode_result.csv"),
    encoding="utf-8-sig"
)

geocode_result.columns = geocode_result.columns.astype(str).str.strip()

geocode_result["위도"] = pd.to_numeric(
    geocode_result["위도"], errors="coerce"
)

geocode_result["경도"] = pd.to_numeric(
    geocode_result["경도"], errors="coerce"
)

geocode_result = geocode_result.dropna(
    subset=["위도", "경도"]
).copy()
st.write("📍 원본 좌표 수:", len(geocode_result))
st.write(
    geocode_result[
        ["단속장소", "위도", "경도"]
    ].head(10)
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
st.divider()

st.header("🎯 AI 위험 레이더")

max_risk = float(
    pd.to_numeric(
        final_result["위험점수"],
        errors="coerce"
    ).max()
)

risk = max(0, min(100, max_risk))

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

st.header("🔄 AI 기반 선제대응 프로세스")

p1, p2, p3, p4 = st.columns(4)

p1.markdown(
    """
    ### ① 데이터 분석
    주정차 단속 데이터를 수집하고  
    장소·시간·요일별 패턴을 분석
    """
)

p2.markdown(
    """
    ### ② 위험 예측
    AI가 다음날 단속 위험이  
    높아질 가능성이 있는 지역을 예측
    """
)

p3.markdown(
    """
    ### ③ 위험지역 선정
    위험점수와 위험시간을 기준으로  
    우선 대응지역을 선정
    """
)

p4.markdown(
    """
    ### ④ 선제 대응
    사전 안내·계도·순찰 강화 등  
    행정 대응을 지원
    """
)

st.info(
    "💡 핵심 가치: 민원이 발생한 뒤 대응하는 것이 아니라, "
    "데이터를 활용해 위험 가능성을 미리 파악하고 행정 대응을 앞당깁니다."
)
st.divider()

st.header("🗺️ 창원시 AI 위험 레이더")

from streamlit.components.v1 import html as st_html

# 지도 데이터 준비
map_points = geocode_result.copy()

map_points["위도"] = pd.to_numeric(
    map_points["위도"],
    errors="coerce"
)

map_points["경도"] = pd.to_numeric(
    map_points["경도"],
    errors="coerce"
)

map_points["위험점수"] = pd.to_numeric(
    map_points["위험점수"],
    errors="coerce"
)

map_points = map_points.dropna(
    subset=["위도", "경도", "위험점수"]
).copy()

st.write("📍 지도에 표시할 좌표 수:", len(map_points))
st.write(map_points[["단속장소", "위험점수", "위도", "경도"]])
# 창원 중심 지도
risk_map = folium.Map(
    location=[35.2281, 128.6811],
    zoom_start=11,
    tiles="OpenStreetMap"
)

# 위험지역 표시
for _, row in map_points.iterrows():

    score = float(row["위험점수"])

    if score >= 80:
        color = "#ff2b2b"
        radius = 12
    elif score >= 60:
        color = "#ff9800"
        radius = 9
    else:
        color = "#22c55e"
        radius = 7

    

    # 위험지역 핵심 포인트
    folium.CircleMarker(
        location=[
            float(row["위도"]),
            float(row["경도"])
        ],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.9,
        weight=3,
        popup=folium.Popup(
            f"""
            <div style="font-size:14px;">
                <b>🚨 {row['단속장소']}</b><br>
                위험점수: <b>{score:.1f}</b><br>
                위험등급: <b>{row['위험등급']}</b><br>
                위험시간: {row.get('위험시간', '정보 없음')}<br>
                추천대응: {row['추천대응']}
            </div>
            """,
            max_width=320
        )
    ).add_to(risk_map)

# 지도 범례
legend_html = """
<div style="
    position: fixed;
    bottom: 25px;
    left: 25px;
    z-index: 9999;
    background: white;
    padding: 15px 18px;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    font-size: 14px;
">
    <b>🚨 AI 위험등급</b><br><br>
    <span style="color:#ff2b2b;">●</span>
    높음 (80 이상)<br>
    <span style="color:#ff9800;">●</span>
    보통 (60~79)<br>
    <span style="color:#22c55e;">●</span>
    낮음 (60 미만)
</div>
"""

risk_map.get_root().html.add_child(
    folium.Element(legend_html)
)

# 지도 표시
map_html = risk_map._repr_html_()

st_html(
    map_html,
    height=700,
    scrolling=False
)

st.caption(
    "실제 좌표가 확보된 위험지역을 기준으로 AI 위험점수와 "
    "위험등급을 지도에 시각화합니다."
)
