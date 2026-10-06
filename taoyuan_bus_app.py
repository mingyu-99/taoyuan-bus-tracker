import streamlit as st
import requests
import os
from dotenv import load_dotenv
import folium
from streamlit_folium import st_folium
import polyline

#基本設定
st.set_page_config(page_title="🚏公車查詢系統")
st.title("🚌 桃園公車即時查詢系統")

DEFAULT_CENTER = [24.95, 121.22]

#env
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

#安全請求
def safe_get(url, headers):
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        else:
            return []
    except:
        return []

#Token
@st.cache_data(ttl=3600)
def get_token():
    url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    res = requests.post(url, data=data)
    if res.status_code != 200:
        st.error("Token 取得失敗")
        return None
    return res.json().get('access_token')


@st.cache_data(ttl=86400)
def get_routes(token):
    url = "https://tdx.transportdata.tw/api/basic/v2/Bus/Route/City/Taoyuan?$format=JSON"
    headers = {"authorization": "Bearer " + str(token)}
    return safe_get(url, headers)

@st.cache_data(ttl=86400)
def get_stops(route, token):
    url = "https://tdx.transportdata.tw/api/basic/v2/Bus/StopOfRoute/City/Taoyuan/" + str(route) + "?$format=JSON"
    headers = {"authorization": "Bearer " + str(token)}
    return safe_get(url, headers)

@st.cache_data(ttl=60)
def get_eta(route, token):
    url = "https://tdx.transportdata.tw/api/basic/v2/Bus/EstimatedTimeOfArrival/City/Taoyuan/" + str(route) + "?$format=JSON"
    headers = {"authorization": "Bearer " + str(token)}
    return safe_get(url, headers)

@st.cache_data(ttl=86400)
def get_shape(route, token):
    url = "https://tdx.transportdata.tw/api/basic/v2/Bus/Shape/City/Taoyuan/" + str(route) + "?$format=JSON"
    headers = {"authorization": "Bearer " + str(token)}
    return safe_get(url, headers)

#預估到達時間
def get_status(time):
    if time is None:
        return "⚫ 無資料", "gray"
    if time <= 60:
        return "🚍 進站中", "green"
    elif time <= 180:
        return "🟢 即將到站", "green"
    elif time <= 600:
        return "🟡 即將到達", "orange"
    else:
        return "🔴 尚需等待", "red"

#主程式執行
mode = st.radio("🔄 選擇模式", ["🚌 路線查詢", "📍站牌查詢"])
token = get_token()

if not token:
    st.stop()


# 模式一：路線查詢

if mode == "🚌 路線查詢":
    with st.spinner("🚀 載入路線中..."):
        routes = get_routes(token)

    route_options = {}
    for r in routes:
        name = r['RouteName']['Zh_tw']
        start = r.get('DepartureStopNameZh', '未知起點')
        end = r.get('DestinationStopNameZh', '未知終點')
        label = str(name) + "｜" + str(start) + " → " + str(end)
        route_options[label] = name

    search_text = st.text_input("🔍 搜尋路線（例如：112、BR）")
    
    
    if search_text:
        filtered = [k for k in route_options if route_options[k].startswith(search_text.strip())]
    else:
        filtered = list(route_options.keys())

    if filtered:
        selected = st.selectbox("選擇路線", filtered)
        if selected:
            route_input = route_options[selected]

            with st.spinner("📡 取得即時資料..."):
                stop_data = get_stops(route_input, token)
                eta_data = get_eta(route_input, token)
                shape_data = get_shape(route_input, token)

            eta_dict = {}
            for item in (eta_data if isinstance(eta_data, list) else ''):
                key = (route_input, item.get('StopUID'), item.get('Direction'))
                eta_dict[key] = {
                    "time": item.get('EstimateTime'), 
                    "plate": item.get('PlateNumb') # 車牌
                }

            m = folium.Map(location=DEFAULT_CENTER, zoom_start=13)
            all_coords = []
            if isinstance(shape_data, list):
                for s in shape_data:
                    if 'EncodedPolyline' in s:
                        coords = polyline.decode(s['EncodedPolyline'])
                        all_coords.extend(coords)
                        folium.PolyLine(coords, color="#0066FF", weight=4, opacity=0.8).add_to(m)

            if all_coords: m.fit_bounds(all_coords)

            all_stops = []
            if not isinstance(stop_data, list) or len(stop_data) == 0:
                st.warning("⚠️ 沒有站點資料")
            else:
                for route_item in stop_data:
                    direction = route_item.get('Direction', 0)
                    stops = sorted(route_item.get('Stops', []), key=lambda x: x.get('StopSequence', 0))

                    for stop in stops:
                        name = stop.get('StopName', {}).get('Zh_tw', '未知站')
                        lat, lon = stop.get('StopPosition', {}).get('PositionLat'), stop.get('StopPosition', {}).get('PositionLon')
                        if not lat or not lon: continue

                        key = (route_input, stop.get('StopUID'), direction)
                        info = eta_dict.get(key)
                        status, color = get_status(info.get("time") if info else None)
                        
                        popup_text = str(name) + "<br>" + str(status)
                        if info and info.get("time"):
                            popup_text += " (" + str(round(info['time'] / 60)) + " 分)"
                        if info and info.get("plate"):
                            popup_text += "<br>車牌: " + str(info['plate']) # 地圖標記顯示車牌

                        folium.Marker([lat, lon], popup=popup_text, tooltip=name, icon=folium.Icon(color=color)).add_to(m)
                        all_stops.append((name, info, direction))

            st.subheader("🗺️ 路線地圖")
            st_folium(m, width=700, height=500)

            with st.expander("📍 查看所有站名"):
                for name, info, dir_idx in all_stops:
                    dir_text = "往" if dir_idx == 0 else "返"
                    status_text = "【" + str(dir_text) + "】" + str(name)
                    if info:
                        time = info.get("time")
                        plate = info.get("plate", "無車牌")
                        status, _ = get_status(time)
                        status_text += " - " + str(status)
                        if time: status_text += " (" + str(round(time/60)) + " 分)"
                        status_text += " [" + str(plate) + "]" # 列表顯示車牌
                    else:
                        status_text += " - ⚫ 無資料"
                    st.write(status_text)


# 模式二：站牌查詢

elif mode == "📍站牌查詢":
    st.subheader("📍 站牌即時動態")
    stop_name_input = st.text_input("🔍 輸入站牌名稱搜尋 (如：桃園車站)")

    if stop_name_input:
        with st.spinner("📡 搜尋中..."):
            filter_str = "contains(StopName/Zh_tw, '" + str(stop_name_input) + "')"
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/EstimatedTimeOfArrival/City/Taoyuan?$filter=" + filter_str + "&$format=JSON"
            headers = {"authorization": "Bearer " + str(token)}
            arrival_data = safe_get(url, headers)

        if not arrival_data:
            st.warning("查無此站牌或目前該站無公車資訊。")
        else:
            stops_grouped = {}
            for item in arrival_data:
                s_name = item.get('StopName', {}).get('Zh_tw', '未知')
                if s_name not in stops_grouped:
                    stops_grouped[s_name] = []
                stops_grouped[s_name].append(item)

            selected_stop = st.selectbox("請選擇確定的站點", list(stops_grouped.keys()))

            if selected_stop:
                st.write("### 🚩", selected_stop)
                for bus in stops_grouped[selected_stop]:
                    route_name = bus.get('RouteName', {}).get('Zh_tw', '未知路線')
                    dest_name = bus.get('DestinationStopNameZh')
                    
                    dir_label = dest_name if dest_name else ("去程" if bus.get('Direction') == 0 else "返程")
                    
                    time = bus.get('EstimateTime')
                    plate = bus.get('PlateNumb', '查無車牌') # 取 API 中的車牌欄位
                    status, color = get_status(time)
                    
                    time_display = " (" + str(round(time/60)) + " 分鐘)" if time is not None else ""
                    plate_display = " `" + str(plate) + "`" if time is not None else "" # 有車才顯示車牌
                    
                    color_map = {"green": "green", "orange": "orange", "red": "red", "gray": "gray"}
                    display_color = color_map.get(color, 'black')
                    
                    st.markdown("**" + str(route_name) + "** (" + str(dir_label) + ") → :" + str(display_color) + "[" + str(status) + str(time_display) + "]" + str(plate_display))