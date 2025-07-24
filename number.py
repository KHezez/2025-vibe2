import streamlit as st
import random

st.title("🔢 숫자맞추기 게임 (이건 시간을 안썼다)")
st.markdown("1~100 사이의 숫자를 맞춰보세요!<br>힌트: <span style='color:#4af'>UP</span> / <span style='color:#fa4'>DOWN</span> (입력하고 Enter)", unsafe_allow_html=True)

# 세션 상태로 랜덤 숫자, 시도 횟수 유지
if "target" not in st.session_state:
    st.session_state.target = random.randint(1,100)
    st.session_state.count = 0
    st.session_state.last = None
    st.session_state.gameover = False

if not st.session_state.gameover:
    guess = st.number_input("숫자를 입력하세요 (1~100)", min_value=1, max_value=100, value=1, step=1, key="guess_input")
    if st.button("도전!"):
        st.session_state.count += 1
        st.session_state.last = guess
        if guess < st.session_state.target:
            st.info("🔺 UP! 더 큰 수!")
        elif guess > st.session_state.target:
            st.info("🔻 DOWN! 더 작은 수!")
        else:
            st.success(f"🎉 정답! {guess} 맞췄습니다. ({st.session_state.count}번 만에 성공)")
            st.session_state.gameover = True

    if st.session_state.last:
        st.write(f"▶️ 최근 입력: {st.session_state.last} (총 {st.session_state.count}회 시도)")
else:
    if st.button("다시하기"):
        st.session_state.target = random.randint(1,100)
        st.session_state.count = 0
        st.session_state.last = None
        st.session_state.gameover = False
    st.balloons()
