import os

import anthropic
import streamlit as st

MODEL = "claude-sonnet-5-5"
SYSTEM_PROMPT = "당신은 친절한 한국어 어시스턴트입니다. 질문에 간결하고 정확하게 답하세요."
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


def stream_reply(client, messages):
    """응답을 글자 단위로 흘려보내고, 끝나면 거절 여부를 확인한다."""
    with client.beta.messages.stream(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=messages,
        output_config={"effort": "low"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    ) as stream:
        yield from stream.text_stream
        final = stream.get_final_message()
    if final.stop_reason == "refusal":
        yield "\n\n(이 요청에는 답변할 수 없습니다.)"


def show_error(e):
    if isinstance(e, anthropic.AuthenticationError):
        st.error("API 키가 올바르지 않습니다. `.env`의 `ANTHROPIC_API_KEY`를 확인해 주세요.")
    elif isinstance(e, anthropic.RateLimitError):
        st.warning("요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.")
    elif isinstance(e, anthropic.APIConnectionError):
        st.error("네트워크 오류가 발생했습니다. 인터넷 연결을 확인해 주세요.")
    elif isinstance(e, anthropic.APIStatusError):
        st.error(f"API 오류 ({e.status_code}): {e.message}")
    else:
        st.error(f"알 수 없는 오류: {e}")


def main():
    st.set_page_config(page_title="챗봇", page_icon="💬")
    st.title("💬 Claude 챗봇")

    load_env()
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key or api_key.startswith("여기에"):
        st.error("API 키가 없습니다.")
        st.info(
            "https://console.anthropic.com 에서 키를 발급받아 `.env` 파일의 "
            "`ANTHROPIC_API_KEY=` 뒤에 붙여 넣고 새로고침하세요."
        )
        return

    client = anthropic.Anthropic(api_key=api_key)
    st.session_state.setdefault("messages", [])

    with st.sidebar:
        st.caption(f"모델: {MODEL}")
        if st.button("새 대화", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if not st.session_state.messages:
        st.info("아래 입력창에 궁금한 것을 물어보세요. 예: \"파이썬 리스트 컴프리헨션 설명해줘\"")

    if prompt := st.chat_input("메시지를 입력하세요"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                reply = st.write_stream(stream_reply(client, st.session_state.messages))
            except anthropic.APIError as e:
                show_error(e)
                st.session_state.messages.pop()  # 실패한 질문은 기록에서 뺀다
                return
        st.session_state.messages.append({"role": "assistant", "content": reply})


main()
