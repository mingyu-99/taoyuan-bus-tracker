# 🚌 桃園公車即時查詢系統

這是一個基於 **Streamlit** 與 **Folium** 開發的桃園市公車即時動態查詢系統。透過串接交通部 **TDX 運輸資料流通服務 API**，提供即時路線搜尋、預估到站時間（ETA）、公車即時位置與車牌資訊，並在互動式地圖上繪製公車行駛軌跡與站點動態。

---

## 📌 功能特色
* **即時動態查詢**：查詢桃園市公車各路線之預估到站時間（進站中、即將到站、尚需等待等狀態標示）。
* **互動式地圖繪製**：
  * 使用 Folium 呈現地圖與公車路線軌跡（Polyline 解碼）。
  * 標記各公車站點，並以不同顏色圖示標示到站狀態。
  * 地圖彈出視窗（Popup）與懸停標籤（Tooltip）即時顯示站名、到站分鐘數及車牌號碼。
* **路線搜尋與篩選**：支援關鍵字即時過濾路線（如：`112`、`BR`）。
* **快取優化 (Streamlit Cache)**：使用 `st.cache_data` 對 API 請求進行快取（Token、路線、站點及預估到站時間），提升載入速度與節省 API 調用次數。

---

## 🛠️ 環境與套件需求
* **Python 3.x**
* **第三方套件**：
  * `streamlit`：Web 應用程式介面
  * `requests`：API 請求
  * `python-dotenv`：管理環境變數 (.env)
  * `folium` & `streamlit-folium`：互動式地圖繪製
  * `polyline`：解碼路線軌跡座標

### 安裝必要套件
請在終端機或命令提示字元（CMD）執行以下指令：
```bash
pip install streamlit requests python-dotenv folium streamlit-folium polyline
