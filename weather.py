import json
import os
import urllib.error
import urllib.parse
import urllib.request

import streamlit as st

API_URL = "https://api.openweathermap.org/data/2.5/weather"
DEFAULT_CITY = "Seoul"
ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def load_env(path=ENV_PATH):
    """.env의 KEY=VALUE 줄을 환경 변수로 등록한다. 이미 설정된 값은 덮어쓰지 않는다."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


@st.cache_data(ttl=600, show_spinner=False)
def fetch_weather(city, api_key):
    query = urllib.parse.urlencode(
        {"q": city, "appid": api_key, "units": "metric", "lang": "kr"}
    )
    with urllib.request.urlopen(f"{API_URL}?{query}", timeout=10) as response:
        return json.load(response)


def main():
    st.set_page_config(page_title="날씨", page_icon="🌤️")
    st.title("현재 날씨")

    load_env()
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        st.error("API 키가 없습니다.")
        st.info("같은 폴더의 `.env` 파일에 `OPENWEATHER_API_KEY=발급받은키`를 한 줄 추가한 뒤 새로고침하세요.")
        return

    city = st.text_input("도시 (영문)", value=DEFAULT_CITY).strip()
    if not city:
        st.info("날씨를 보고 싶은 도시 이름을 영문으로 입력해 주세요. 예: Seoul, Busan, Tokyo")
        return

    try:
        with st.spinner("날씨를 가져오는 중..."):
            data = fetch_weather(city, api_key)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            st.error("API 키가 올바르지 않거나 아직 활성화되지 않았습니다. 발급 직후라면 몇 시간 뒤에 다시 시도해 보세요.")
        elif e.code == 404:
            st.warning(f"'{city}' 도시를 찾을 수 없습니다. 영문 철자를 확인해 주세요.")
        else:
            st.error(f"날씨 정보를 가져오지 못했습니다. (HTTP {e.code})")
        return
    except urllib.error.URLError as e:
        st.error(f"네트워크 오류: {e.reason}")
        return

    main_info = data["main"]
    st.subheader(f"{data['name']} · {data['weather'][0]['description']}")
    st.metric("기온", f"{main_info['temp']:.1f}°C")
    col1, col2 = st.columns(2)
    col1.metric("체감 온도", f"{main_info['feels_like']:.1f}°C")
    col2.metric("습도", f"{main_info['humidity']}%")


main()
