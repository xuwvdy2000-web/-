import requests
import streamlit as st

# 1. 페이지 설정
st.set_page_config(
    page_title="나만의 영단어장", page_icon="📖", layout="wide"
)

# 세션 상태(단어장) 초기화
if "vocab_list" not in st.session_state:
  st.session_state.vocab_list = []

st.title("📖 나만의 영단어장 Web App")
st.write(
    "영단어를 검색하고, 나만의 단어장에 저장하여 간편하게 관리해보세요!"
)

# 레이아웃 분할 (왼쪽: 검색 / 오른쪽: 단어장)
col1, col2 = st.columns(1)

# 검색 섹션
st.subheader("🔍 단어 검색하기")
search_col1, search_col2 = st.columns([4, 1])
with search_col1:
  search_word = st.text_input(
      "영단어 입력",
      placeholder="예: apple, resilient",
      label_visibility="collapsed",
  )
with search_col2:
  search_clicked = st.button("검색", use_container_width=True)

# 검색 실행
if search_clicked and search_word:
  word_clean = search_word.strip().lower()
  url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word_clean}"

  try:
    response = requests.get(url)
    if response.status_code == 200:
      data = response.json()[0]
      meaning = data["meanings"][0]
      def_obj = meaning["definitions"][0]

      # 데이터 정제
      word_info = {
          "word": data.get("word", word_clean),
          "phonetic": data.get("phonetic", ""),
          "partOfSpeech": meaning.get("partOfSpeech", ""),
          "definition": def_obj.get("definition", ""),
          "example": def_obj.get("example", "예문 없음"),
          "synonyms": ", ".join(meaning.get("synonyms", [])[:5]) or "없음",
      }

      st.session_state.current_word = word_info
    else:
      st.error(
          "❌ 단어를 찾을 수 없습니다. 올바른 영단어인지 확인해주세요."
      )
      st.session_state.current_word = None
  except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")

# 검색 결과 표시
if "current_word" in st.session_state and st.session_state.current_word:
  w = st.session_state.current_word

  with st.container(border=True):
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
      st.markdown(
          f"### {w['word']} <span style='font-size:16px; color:gray;'>{w['phonetic']}</span>",
          unsafe_allow_html=True,
      )
    with header_col2:
      if st.button("➕ 단어장에 추가", use_container_width=True):
        # 중복 체크
        if not any(item["word"] == w["word"] for item in st.session_state.vocab_list):
          st.session_state.vocab_list.append(w)
          st.success(f"'{w['word']}'이(가) 단어장에 추가되었습니다!")
        else:
          st.warning("이미 단어장에 존재하는 단어입니다.")

    st.markdown(f"**품사:** `{w['partOfSpeech']}`")
    st.markdown(f"**영영풀이:** {w['definition']}")
    st.markdown(f"**예문:** *{w['example']}*")
    st.markdown(f"**유의어:** {w['synonyms']}")

st.divider()

# 📚 내 단어장 섹션
st.subheader(f"📚 내 단어장 (총 {len(st.session_state.vocab_list)}개)")

if not st.session_state.vocab_list:
  st.info("아직 저장된 단어가 없습니다. 단어를 검색하고 추가해보세요!")
else:
  for idx, item in enumerate(st.session_state.vocab_list):
    with st.container(border=True):
      c1, c2 = st.columns([5, 1])
      with c1:
        st.markdown(
            f"**{item['word']}** `[{item['partOfSpeech']}]` —"
            f" *{item['definition']}*"
        )
        if item["example"] != "예문 없음":
          st.caption(f"예문: {item['example']}")
      with c2:
        if st.button("삭제", key=f"del_{idx}", use_container_width=True):
          st.session_state.vocab_list.pop(idx)
          st.rerun()
