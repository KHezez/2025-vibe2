import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="이모지 무지개 비", layout="wide")
st.title("🌈 이모지 무지개 비가 내린다! 🌟")

st.markdown("""
<center>
<b>쓰잘대기 없는 사이트 </b><br>
<br>
</center>
""", unsafe_allow_html=True)

html_code = """
<html>
  <head>
    <style>
      body {
        margin: 0; padding: 0; overflow: hidden;
        background: linear-gradient(120deg, #6ee7b7 0%, #a7c7e7 30%, #e0c3fc 60%, #f7d6e0 90%);
        width: 100vw; height: 90vh;
        transition: background 1s;
      }
      #emojiRain {
        position: fixed; left: 0; top: 0;
        width: 100vw; height: 90vh; pointer-events: none; z-index: 99;
      }
    </style>
  </head>
  <body>
    <div id="emojiRain"></div>
    <script>
      // 컬러 팔레트(무지개+파스텔)
      const bgColors = [
        'linear-gradient(120deg, #6ee7b7 0%, #a7c7e7 30%, #e0c3fc 60%, #f7d6e0 90%)',
        'linear-gradient(120deg, #fcb69f 0%, #ffecd2 100%)',
        'linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%)',
        'linear-gradient(120deg, #fbc2eb 0%, #a6c1ee 100%)',
        'linear-gradient(120deg, #fda085 0%, #f6d365 100%)'
      ];
      let colorIdx = 0;
      setInterval(()=>{
        colorIdx = (colorIdx + 1) % bgColors.length;
        document.body.style.background = bgColors[colorIdx];
      }, 2400);

      // 이모지 리스트
      const emojis = ["🌈","✨","💎","🌟","🍭","🎉","🦄","🍬","🌸","🔥","💜","🧊","🎆","🍀","🍡","🪐","⚡"];
      // 이모지 떨어뜨리는 함수
      function dropEmoji() {
        let e = document.createElement("span");
        e.innerText = emojis[Math.floor(Math.random()*emojis.length)];
        e.style.position = "absolute";
        e.style.left = (Math.random()*98)+"vw";
        e.style.fontSize = (32 + Math.random()*70) + "px";
        e.style.opacity = (0.75 + Math.random()*0.25).toFixed(2);
        e.style.top = "-70px";
        e.style.transition = `top 2.5s cubic-bezier(.6,1.8,.5,1), opacity 2.5s`;
        e.style.filter = `drop-shadow(0 0 8px #fff7)`;
        document.getElementById("emojiRain").appendChild(e);
        setTimeout(()=>{
          e.style.top = (75 + Math.random()*15) + "vh";
          e.style.opacity = "0.1";
        }, 10);
        setTimeout(()=>{
          e.remove();
        }, 2600);
      }
      // 계속 이모지 비 내리기
      setInterval(dropEmoji, 120);
      // 처음엔 좀 더 뿌려주기
      for(let i=0; i<18; i++) setTimeout(dropEmoji, i*80);
    </script>
  </body>
</html>
"""

components.html(html_code, height=600, scrolling=False)
