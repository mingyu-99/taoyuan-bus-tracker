# 🚌 桃園公車即時動態與地圖視覺化系統

這是一個基於 Python 與 Streamlit 打造的即時公車查詢系統，串接交通部 TDX API 並結合地圖視覺化呈現公車即時動態。

## 🌟 核心功能
- **路線查詢**：支援關鍵字搜尋公車路線，並在地圖上記錄即時軌跡與各站牌到站倒數。
- **站牌查詢**：快速檢索特定站牌所有行經公車的預估到達時間與車牌號碼。
- **快取優化**：設定 API Cache TTL 機制，有效減少不必要的網路請求。

## 🛠️ 使用技術
- **Language**: Python
- **Frontend / Web Framework**: Streamlit
- **API Integration**: 交通部 TDX RESTful API
- **Map & Visualization**: Folium, Streamlit-Folium, Polyline

## 🚀 本地端執行步驟

1. Clone 本專案：
```bash
git clone https://github.com/mingyu-99/taoyuan-bus-tracker.git
cd taoyuan-bus-tracker
