import streamlit as st
from googleapiclient.discovery import build
import pandas as pd

# ページ設定（モバイルファースト）
st.set_page_config(page_title="YT Trend Explorer", page_icon="📊", layout="centered")

# カスタムCSS（Tailwind風のモダンデザイン）
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #ff0000; color: white; border: none; }
    .video-card { background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .tag { background: #fee2e2; color: #dc2626; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; margin-right: 5px; }
    </style>
""", unsafe_allow_html=True)

# API設定（StreamlitのSecretsから取得）
API_KEY = st.secrets["AIzaSyAYZZ9EVRDhCAdX45MN3jvi9ANvFMsHjEk"]
youtube = build("youtube", "v3", developerKey=API_KEY)

st.title("📊 YouTube Trend")
st.caption("スマホで分析する最新トレンド動画")

# 1. Trend Catch & Smart Filter
col1, col2 = st.columns(2)
with col1:
    region = st.selectbox("国を選択", ["JP", "US", "KR"], index=0)
with col2:
    category = st.selectbox("カテゴリ", {"すべて": "0", "音楽": "10", "ゲーム": "20", "教育": "27"})

if st.button("トレンドを抽出する"):
    with st.spinner('分析中...'):
        # APIリクエスト
        request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode=region,
            videoCategoryId=category if category != "0" else None,
            maxResults=10
        )
        response = request.execute()

        # 2. Keyword Analysis & Display
        keywords = []
        for item in response['items']:
            snippet = item['snippet']
            stats = item['statistics']
            title = snippet['title']
            thumb = snippet['thumbnails']['high']['url']
            view_count = int(stats.get('viewCount', 0))
            tags = snippet.get('tags', [])[:3] # 上位3つのタグ
            keywords.extend(tags)

            # 4. Mobile First UI (カード表示)
            st.markdown(f"""
                <div class="video-card">
                    <img src="{thumb}" style="width:100%; border-radius:10px; margin-bottom:10px;">
                    <h4 style="font-size:1rem; margin-bottom:5px;">{title}</h4>
                    <p style="color:gray; font-size:0.8rem;">👁️ 再生数: {view_count:,}回</p>
                    <div style="margin-top:5px;">
                        {" ".join([f'<span class="tag">#{t}</span>' for t in tags])}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        # キーワード集計（簡易表示）
        if keywords:
            st.subheader("🔥 頻出キーワード")
            df_kw = pd.Series(keywords).value_counts().head(5)
            st.bar_chart(df_kw)

else:
    st.info("上のボタンを押して分析を開始してください。")
