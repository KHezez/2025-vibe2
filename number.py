import streamlit as st
import random
import streamlit.components.v1 as components

st.title("🎱 숫자맞추기")

st.markdown("""
> 숫자 입력하고 <kbd>Enter</kbd> 또는 버튼 클릭!  
> (파란 공을 마우스로 던질 수 있음.  
> 3번 이상 '가짜정답' 입력 후 '때리기' ON+공 클릭+버튼으로 종이 뱉기!)  
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

# --- 상태 변수, 항상 선언해줘야 함! ---
if "target" not in st.session_state:
    st.session_state.target = random.randint(1,100)
if "last" not in st.session_state:
    st.session_state.last = None
if "tried" not in st.session_state:
    st.session_state.tried = 0           # 전체 시도 횟수
if "fake_count" not in st.session_state:
    st.session_state.fake_count = 0      # "가짜정답" 시도 누적
if "smash_mode" not in st.session_state:
    st.session_state.smash_mode = False
if "paper_shown" not in st.session_state:
    st.session_state.paper_shown = False
if "win" not in st.session_state:
    st.session_state.win = False
if "show_button" not in st.session_state:
    st.session_state.show_button = False
if "bot_msg" not in st.session_state:
    st.session_state.bot_msg = ""

def get_fake_answer():
    return int(st.session_state.target)

def get_real_answer():
    return round(float(st.session_state.target)+0.1, 1)

def reset():
    st.session_state.target = random.randint(1,100)
    st.session_state.last = None
    st.session_state.tried = 0
    st.session_state.fake_count = 0
    st.session_state.smash_mode = False
    st.session_state.paper_shown = False
    st.session_state.win = False
    st.session_state.show_button = False
    st.session_state.bot_msg = ""

# --- 입력창+버튼 ---
if not st.session_state.win:
    guess = st.number_input("숫자를 입력하세요 (1~100, or 진짜정답)", min_value=1.0, max_value=100.1, value=1.0, step=0.1, key="guess_input")
    pressed = st.button("도전!")

    if pressed or (st.session_state.last != guess and "guess_input" in st.session_state):
        st.session_state.last = guess
        st.session_state.tried += 1
        # 진짜 정답(소수점까지)!
        if st.session_state.paper_shown and abs(guess-get_real_answer()) < 0.00001:
            st.session_state.win = True
            st.session_state.bot_msg = f"🎉 진짜 정답 {get_real_answer()} 맞춤! (최후의 승리자!)"
        else:
            # 가짜정답(정수) 입력시만 fake_count 증가
            if not st.session_state.paper_shown and int(guess) == get_fake_answer() and abs(guess-get_fake_answer()) < 0.00001:
                st.session_state.fake_count += 1
            # UP/DOWN/WRONG 로직
            if guess < st.session_state.target:
                msg = random.choice(MSG_UP)
            elif guess > st.session_state.target:
                msg = random.choice(MSG_DOWN)
            else:
                msg = random.choice(MSG_WRONG)
            st.session_state.bot_msg = msg
            # 가짜정답 3회 이상 입력해야 버튼 노출!
            if st.session_state.fake_count >= 3 and not st.session_state.paper_shown:
                st.session_state.show_button = True

    # 숨겨진 버튼 (가짜정답 3회만 노출)
    if st.session_state.show_button:
        st.session_state.smash_mode = st.toggle("클릭해서 때리기 on/off", value=st.session_state.smash_mode, key="smash_onoff")

else:
    if st.button("다시하기"):
        reset()
    st.balloons()

# --- 메시지 및 종이 ---
if "bot_msg" in st.session_state and not st.session_state.win:
    st.markdown(f"<span style='font-size:1.6rem;color:#4af;font-weight:700;'>{st.session_state.bot_msg}</span>", unsafe_allow_html=True)
    if st.session_state.paper_shown:
        st.markdown(f"""
        <div style='padding:18px 0; text-align:center'>
        <span style="font-size:2.2rem;background:#fffbe6;padding:12px 30px 16px 30px;border-radius:18px;border:2.5px solid #bbb;">
        <b>진짜 정답은<br> <span style='color:#d94'>{get_real_answer()}</span> 입니다!</b>
        </span>
        <br><br>
        <span style="color:#aaa">이 값을 입력해야 이길 수 있음 ㅋㅋㅋㅋ</span>
        </div>
        """, unsafe_allow_html=True)

# --- 공/종이 (JS, 실제로는 종이 뱉는 애니만, python 상태변화는 버튼) ---
bot_code = f"""
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
      let smash_mode = {"true" if st.session_state.smash_mode else "false"};
      let paper_shown = {"true" if st.session_state.paper_shown else "false"};
      let paperY = 9999, paperV = 0, showPaper = false, paperVal = "{get_real_answer()}";
      let smashAnim = 0;
      function setup() {{
        createCanvas(360,360);
        x = width/2; y = height/2;
      }}
      function draw() {{
        background(245, 251, 255, 255);
        // smash 애니 (때리기 on+공 클릭)
        if(smashAnim>0) {{
          smashAnim--;
          vx += random(-6,6);
          vy += random(-7,7);
          fill(255,60,60); textSize(22); textAlign(CENTER,CENTER);
          text("으아아아악!!!!", x, y-r-26-random(0,5));
          if(smashAnim==1) {{
            // 종이 등장
            showPaper = true;
            paperY = y; paperV = -10;
          }}
        }}
        // 물리
        if(!dragging) {{
          x += vx; y += vy;
          vx *= 0.96; vy *= 0.96;
          if(x<r){{ x=r; vx=-vx*0.72; }}
          if(x>width-r){{ x=width-r; vx=-vx*0.72; }}
          if(y<r){{ y=r; vy=-vy*0.72; }}
          if(y>height-r){{ y=height-r; vy=-vy*0.72; }}
        }}
        // 공
        noStroke();
        fill(74,180,255);
        ellipse(x, y, r*2, r*2);
        stroke(30,60,120,70); strokeWeight(2);
        ellipse(x, y, r*2.1, r*2.1);
        noStroke();
        // 종이 뱉기 애니
        if(showPaper) {{
          paperY += paperV;
          paperV += 1.5;
          if(paperY > height-38) paperY = height-38;
          drawPaper(width/2, paperY, paperVal);
        }}
      }}
      function mousePressed() {{
        let d = dist(mouseX, mouseY, x, y);
        if(d<r){{
          if(smash_mode && !showPaper && !paper_shown){{
            // smash 애니만, python상태는 버튼에서 처리
            smashAnim = 26;
          }} else {{
            dragging=true;
            offsetX = mouseX-x;
            offsetY = mouseY-y;
            vx=vy=0;
          }}
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
      }}
      function drawPaper(px, py, val) {{
        push();
        translate(px, py);
        fill(255,255,210);
        stroke(180,150,100); strokeWeight(2.3);
        rect(-38,-22,76,44,9);
        noStroke(); fill(170,120,70);
        textSize(14); textAlign(CENTER,CENTER);
        text("진짜 정답", 0, -6);
        textSize(21);
        fill(200,52,52);
        text(val, 0, 14);
        pop();
      }}
    </script>
  </body>
</html>
"""

components.html(bot_code, height=380)

# 종이 뱉기 "진짜로" python상태 변환용 버튼 (공 클릭 애니 후 누르는 방식)
if not st.session_state.paper_shown and st.session_state.smash_mode and st.session_state.show_button:
    st.markdown("---")
    if st.button("종이 뱉게 하기(공 눌렀으면 누르기)"):
        st.session_state.paper_shown = True
