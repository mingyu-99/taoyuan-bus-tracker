# 🚌 桃園公車即時動態與地圖視覺化系統

這是一個基於 Python 與 Streamlit 打造的即時公車查詢網頁應用，專門串接交通部 TDX RESTful API，並結合 Folium 動態地圖與 Polyline 路線還原，提供直觀流暢的公車動態追蹤體驗。

---

## 🌟 核心功能

* **智慧路線查詢**：支援關鍵字即時搜尋桃園公車路線（例如 112、BR 等），並透過下拉選單快速切換。
* **地圖軌跡視覺化**：透過 `polyline` 解析 TDX 提供的圖資，在地圖上精準繪製公車行經路線與沿途站牌。
* **即時互動標記**：
  * **Tooltip**：滑鼠游標懸停即可檢視站名。
  * **Popup**：點擊站牌即可查看詳細的即時預估到站時間（ETA）與車牌號碼。
* **效能與資安優化**：導入 Streamlit 快取機制（`@st.cache_data`）與 `.env` 環境變數管理，兼具高效能與高度資安防護。

---

## 🛠️ 使用技術 (Tech Stack)

* **Language**: Python
* **Frontend / UI**: Streamlit
* **API Integration**: 交通部 TDX RESTful API (OAuth2 Token 認證)
* **Map & Visualization**: Folium, Streamlit-Folium, Polyline
* **Environment & Security**: python-dotenv (`.env`)

---

## 🚀 本地端執行步驟 (Installation & Running)

1. **Clone 本專案至本地端**：
   ```bash
   git clone https://github.com/mingyu-99/taoyuan-bus-tracker.git
   cd taoyuan-bus-tracker
