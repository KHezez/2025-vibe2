import streamlit as st
import random
import streamlit.components.v1 as components

st.title("🎱 숫자맞추기: 트롤 빠따 모드 (by monday X fury)")

st.markdown("""
> 숫자 입력하고 <kbd>Enter</kbd> 또는 버튼 클릭!  
> (파란 공을 마우스로 던져보세요!)  
""", unsafe_allow_html=True)

MSG_UP = [
    "아닌데?!?!?! 더 위인데? ㅋㅋㅋ", "아니지~ 좀 더 높은 숫자인데?",
    "땡! 위야 위!", "그거보다 위임 ㅇㅇ", "ㄴㄴ 위쪽 봐봐", 
    "으악 아니야 더 큰 수임!", "아쉽다 위쪽 숫자임", "거기 아님 위에 있음", "방향 잘못잡았음 위쪽임", "더! 높이!"
]
MSG_DOWN = [
    "아닌데???? 더 아랜데???", "아니야 좀 더 작은 수임", "땡! 아래야 ㅋㅋ", "그거보다 아래임 ㅇㅇ", "ㄴㄴ 아래쪽 봐봐",
    "아쉽다 아래 숫자임", "으응 아님 아래임", "그 숫자 넘 큼! 더 작게", "방향 틀렸음 아래임", "더! 낮게!"
]
MSG_WRONG = [
    "뭐야 정답 아니야ㅋㅋ", "아니 이게 왜 맞음? 다시 해", "그거 아니야~", "이상한데? 정답 아님;;", "안 맞았는데??",
    "뭐지? 정답 아닌데?", "아직 멀었어! 또 해봐", "누가 정답이라 그랬음? 아님 ㅋㅋ", "어림없지~", "정답 아직임 ㅋ"
]

if "target" not in st.session_state:
    st.session_state.target = random.randint(1,100)
    st.session_state.last = None
    st.session_state.correct_count = 0
    st.session_state.batta_mode = False
    st.session_state.win = False
    st.session_state.paper_shown = False

# 정답(진짜 정답) = 0.1 더한 float
true_answer = round(st.session_state.target + 0.1, 1)

# 입력 + 빠따 조건
guess = st.number_input("숫자를 입력하세요 (1~100, 혹은 ???)", min_value=1.0, max_value=150.0, value=1.0, step=0.1, key="guess_input")

if not st.session_state.win:
    clicked = st.button("도전!") or (st.session_state.last != guess and "guess_input" in st.session_state)
    if clicked:
        st.session_state.last = guess
        if not st.session_state.batta_mode and not st.session_state.paper_shown:
            if int(guess) == st.session_state.target:
                st.session_state.correct_count += 1
                msg = random.choice(MSG_WRONG)
            elif guess < st.session_state.target:
                msg = random.choice(MSG_UP)
            elif guess > st.session_state.target:
                msg = random.choice(MSG_DOWN)
            else:
                msg = random.choice(MSG_WRONG)
            st.session_state.bot_msg = msg
            # 3번 이상 정답 맞췄으면 빠따 버튼 ON
            if st.session_state.correct_count >= 3:
                st.session_state.batta_mode = True
        elif st.session_state.paper_shown:
            # 정답지 입력만 허용
            if abs(guess - true_answer) < 1e-6:
                st.success(f"🎉 승리! 진짜 정답은 {true_answer} 였습니다!")
                st.session_state.win = True
                st.balloons()
            else:
                st.info("이게 진짜 정답이라니까? (종이에 적힌 수를 입력해봐!)")
        else:
            st.info("빠따 모드에서는 캔버스에서 공을 때려주세요!")

    if "bot_msg" in st.session_state and not st.session_state.paper_shown:
        st.markdown(f"<span style='font-size:1.6rem;color:#4af;font-weight:700;'>{st.session_state.bot_msg}</span>", unsafe_allow_html=True)
else:
    st.success(f"🎉 승리! 진짜 정답은 {true_answer} 였습니다!")
    st.balloons()

# ----- 빠따 버튼 (숨김/표시) -----
if st.session_state.batta_mode and not st.session_state.paper_shown and not st.session_state.win:
    st.markdown("""
    <div style="margin-top:12px; margin-bottom:-10px; text-align:right;">
    <button id="battaBtn" style="font-size:1.1rem;padding:8px 16px 8px 30px;background:#f2c200;color:#222;border:none;border-radius:17px;cursor:pointer;box-shadow:1px 2px 8px #a88b08a2;position:relative;">🪓 빠따 (비밀)</button>
    </div>
    <script>
    document.getElementById('battaBtn').onclick = function(){
      window.parent.postMessage('batta', '*');
    }
    </script>
    """, unsafe_allow_html=True)

# ---- 캔버스 (공+빠따) ----
custom_js = f"""
<html>
  <head>
    <meta charset="utf-8" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.2/p5.js"></script>
    <style>
      html, body {{ margin:0; padding:0; background:transparent; }}
    </style>
  </head>
  <body>
    <script>
      let x, y, vx=0, vy=0, dragging=false, offsetX=0, offsetY=0, r=16;
      let showBatta = false, battaHit=0, battaDragging=false, bx=240, by=180, br=68, hitWait=0;
      let paperShow = {str(st.session_state.paper_shown).lower()};
      let paperAlpha = 0, paperY = 0, win = {str(st.session_state.win).lower()};
      let battaAngle=0, battaDragX=0, battaDragY=0, battaDragGrip=false, scream=0, screamMsg="", paperVal={true_answer};

      function setup() {{
        createCanvas(360,360);
        x = width/2; y = height/2;
      }}
      window.addEventListener("message", function(event) {{
        if(event.data=="batta") showBatta=true;
      }});
      function draw() {{
        background(245,251,255,255);
        // 공
        if(!dragging) {{
          x += vx; y += vy;
          vx *= 0.96; vy *= 0.96;
          if(x<r){{ x=r; vx=-vx*0.72; }}
          if(x>width-r){{ x=width-r; vx=-vx*0.72; }}
          if(y<r){{ y=r; vy=-vy*0.72; }}
          if(y>height-r){{ y=height-r; vy=-vy*0.72; }}
        }}
        fill(74,180,255);
        ellipse(x, y, r*2, r*2);
        stroke(30,60,120,70); strokeWeight(2);
        ellipse(x, y, r*2.1, r*2.1);
        noStroke();
        // 빠따
        if(showBatta && !win) {{
          // 빠따 막대
          push();
          let cx = bx, cy = by;
          if(battaDragGrip) {{
            // 끝부분 마우스 따라감, 각도 변환
            let dx = mouseX-bx, dy = mouseY-by;
            battaAngle = atan2(dy,dx);
            let len = dist(mouseX,mouseY,bx,by);
            battaDragX = bx+cos(battaAngle)*min(len,110);
            battaDragY = by+sin(battaAngle)*min(len,110);
          }} else {{
            battaDragX = bx+cos(battaAngle)*100;
            battaDragY = by+sin(battaAngle)*100;
          }}
          translate(cx, cy);
          rotate(battaAngle);
          fill('#f2c200'); stroke(80,65,20,120); strokeWeight(6);
          rect(0,-12,100,24,18,18,15,14);
          fill(180,110,30); noStroke();
          ellipse(100,-2,17,32); // 끝부분(잡는곳)
          pop();
          // 마우스 근처면 잡기
          if(!battaDragGrip && dist(mouseX,mouseY,battaDragX,battaDragY)<19 && mouseIsPressed){{
            battaDragGrip=true;
          }}
          if(battaDragGrip && !mouseIsPressed){{ battaDragGrip=false; }}
          // 빠따와 공 충돌 감지(끝부분)
          if(!dragging && !battaDragGrip && showBatta && dist(battaDragX,battaDragY,x,y)<r+17 && hitWait==0) {{
            vx += cos(battaAngle)*12; vy += sin(battaAngle)*12;
            battaHit++; hitWait=12;
            scream=26; screamMsg="으아아아악!!!";
          }}
          if(hitWait>0) hitWait--;
        }}
        // "으아아아악!!!" 출력
        if(scream>0) {{
          fill(255,40,80,210);
          textSize(26); textAlign(CENTER);
          text(screamMsg, x, y-36);
          scream--;
        }}
        // 종이 등장
        if(battaHit>=5 && !paperShow) {{
          paperShow=true; paperAlpha=0; paperY = -70;
          window.parent.postMessage("paper", "*");
        }}
        if(paperShow && !win) {{
          if(paperAlpha<255) paperAlpha+=12;
          if(paperY<44) paperY+=4;
          push();
          translate(width/2, paperY+44);
          fill(255,255,235,paperAlpha);
          stroke(130,130,70,160); strokeWeight(3);
          rect(-52,-28,105,56,17,15,12,12);
          fill(40,50,80,paperAlpha);
          noStroke();
          textSize(21);
          textAlign(CENTER,CENTER);
          text("진짜 정답\n"+paperVal, 0, 0);
          pop();
        }}
      }}
      function mousePressed() {{
        let d = dist(mouseX, mouseY, x, y);
        if(d<r){{
          dragging=true;
          offsetX = mouseX-x;
          offsetY = mouseY-y;
          vx=vy=0;
        }}
        // 빠따 끝부분
        if(showBatta && dist(mouseX,mouseY,battaDragX,battaDragY)<19) {{
          battaDragGrip=true;
        }}
      }}
      function mouseDragged() {{
        if(dragging){{
          x = mouseX-offsetX;
          y = mouseY-offsetY;
        }}
      }}
      function mouseReleased() {{
        if(dragging){{
          vx = movedX*0.3; vy = movedY*0.3;
          dragging=false;
        }}
        battaDragGrip=false;
      }}
    </script>
  </body>
</html>
"""

# 종이 등장시 체크
if "paper" not in st.session_state:
    st.session_state.paper_shown = False

# streamlit -> JS 빠따 활성/종이 등장 sync (자동반영)
def _paper_callback():
    st.session_state.paper_shown = True
components.html(custom_js, height=400)
# JS에서 "paper" signal 오면 세션 반영
components.html("""
<script>
window.addEventListener("message",function(event){
  if(event.data=="paper"){ window.parent.postMessage("streamlit:setComponentValue:paper", "*"); }
});
</script>
""", height=0)

# (승리 로직은 위쪽에서 이미 처리됨)

