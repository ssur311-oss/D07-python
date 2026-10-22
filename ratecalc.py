import json
import os
import urllib.error
import urllib.request

import streamlit as st

API_URL = "https://v6.exchangerate-api.com/v6/{key}/latest/{base}"
ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

CURRENCIES = {
    "KRW": "🇰🇷 원 (KRW)",
    "USD": "🇺🇸 미국 달러 (USD)",
    "EUR": "🇪🇺 유로 (EUR)",
    "JPY": "🇯🇵 일본 엔 (JPY)",
    "CNY": "🇨🇳 중국 위안 (CNY)",
    "GBP": "🇬🇧 영국 파운드 (GBP)",
    "AUD": "🇦🇺 호주 달러 (AUD)",
    "CAD": "🇨🇦 캐나다 달러 (CAD)",
    "CHF": "🇨🇭 스위스 프랑 (CHF)",
    "HKD": "🇭🇰 홍콩 달러 (HKD)",
    "SGD": "🇸🇬 싱가포르 달러 (SGD)",
    "THB": "🇹🇭 태국 바트 (THB)",
    "VND": "🇻🇳 베트남 동 (VND)",
}
CARD_COLORS = ["#FF6B6B", "#FFA94D", "#FFD43B", "#51CF66", "#22B8CF", "#339AF0", "#845EF7", "#F06595"]

STYLE = """
<style>
.stApp { background: linear-gradient(135deg, #fff5f5 0%, #f3f0ff 50%, #e7f5ff 100%); }
.title { font-size: 2.2rem; font-weight: 800; text-align: center;
         background: linear-gradient(90deg, #ff6b6b, #fcc419, #51cf66, #339af0, #845ef7);
         -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.result { background: linear-gradient(135deg, #845ef7, #339af0); color: #fff; border-radius: 20px;
          padding: 1.5rem; text-align: center; box-shadow: 0 8px 24px rgba(132, 94, 247, .35); }
.result .from { font-size: 1.1rem; opacity: .9; }
.result .to { font-size: 2.4rem; font-weight: 800; margin-top: .3rem; }
.result .rate { font-size: .95rem; opacity: .85; margin-top: .4rem; }
.chip { color: #fff; border-radius: 14px; padding: .8rem 1rem; text-align: center; font-weight: 700;
        box-shadow: 0 4px 12px rgba(0, 0, 0, .12); }
.chip small { display: block; font-weight: 400; opacity: .9; }
</style>
"""


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


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_rates(base, api_key):
    url = API_URL.format(key=api_key, base=base)
    with urllib.request.urlopen(url, timeout=10) as response:
        data = json.load(response)
    if data.get("result") != "success":
        raise ValueError(data.get("error-type", "unknown-error"))
    return data["conversion_rates"], data["time_last_update_utc"]


def swap():
    st.session_state.src, st.session_state.dst = st.session_state.dst, st.session_state.src


def show_error(e):
    messages = {
        "invalid-key": "API 키가 올바르지 않습니다. `.env`의 키를 다시 확인해 주세요.",
        "inactive-account": "이메일 인증이 안 된 계정입니다. 가입 메일의 인증 링크를 눌러 주세요.",
        "quota-reached": "이번 달 무료 요청 한도를 모두 사용했습니다.",
        "unsupported-code": "지원하지 않는 통화입니다.",
    }
    st.error(messages.get(str(e), f"환율 정보를 가져오지 못했습니다. ({e})"))


def main():
    st.set_page_config(page_title="환율 계산기", page_icon="💱")
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown('<div class="title">💱 환율 계산기</div>', unsafe_allow_html=True)

    load_env()
    api_key = os.environ.get("EXCHANGERATE_API_KEY", "")
    if not api_key or api_key.startswith("여기에"):
        st.error("API 키가 없습니다.")
        st.info(
            "https://www.exchangerate-api.com 에서 무료 키를 발급받아 `.env` 파일의 "
            "`EXCHANGERATE_API_KEY=` 뒤에 붙여 넣고 새로고침하세요."
        )
        return

    st.session_state.setdefault("src", "USD")
    st.session_state.setdefault("dst", "KRW")

    amount = st.number_input("금액", min_value=0.0, value=1.0, step=1.0, format="%.2f")
    col1, col2, col3 = st.columns([5, 1, 5])
    col1.selectbox("보내는 통화", list(CURRENCIES), format_func=CURRENCIES.get, key="src")
    col2.markdown("<div style='height:1.9rem'></div>", unsafe_allow_html=True)
    col2.button("⇄", on_click=swap, help="통화 바꾸기")
    col3.selectbox("받는 통화", list(CURRENCIES), format_func=CURRENCIES.get, key="dst")
    src, dst = st.session_state.src, st.session_state.dst

    try:
        with st.spinner("환율을 가져오는 중..."):
            rates, updated = fetch_rates(src, api_key)
    except urllib.error.HTTPError as e:
        try:
            show_error(json.load(e).get("error-type", f"HTTP {e.code}"))
        except (ValueError, AttributeError):
            show_error(f"HTTP {e.code}")
        return
    except urllib.error.URLError as e:
        st.error(f"네트워크 오류: {e.reason}")
        return
    except ValueError as e:
        show_error(e)
        return

    rate = rates[dst]
    st.markdown(
        f'<div class="result"><div class="from">{amount:,.2f} {src} =</div>'
        f'<div class="to">{amount * rate:,.2f} {dst}</div>'
        f'<div class="rate">1 {src} = {rate:,.4f} {dst}</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"##### 1 {src} 기준 주요 환율")
    others = [c for c in CURRENCIES if c != src]
    for row_start in range(0, len(others), 4):
        cols = st.columns(4)
        for i, code in enumerate(others[row_start:row_start + 4]):
            color = CARD_COLORS[(row_start + i) % len(CARD_COLORS)]
            cols[i].markdown(
                f'<div class="chip" style="background:{color}">{code}<small>{rates[code]:,.4f}</small></div>',
                unsafe_allow_html=True,
            )
    st.caption(f"마지막 갱신: {updated}")


main()
