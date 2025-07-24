import streamlit as st
import random
import streamlit.components.v1 as components

st.title("🎱 좀 꼴받는 숫자맞추기")

st.markdown("""
> 봇: <span style="color:#fa6">내가 생각한 숫자 맞춰보시지! (1~100)</span>  
> 숫자 입력하고 <kbd>Enter</kbd> 또는 버튼 클릭!  
> 내 공을 마우스로 드래그/던질 수 있음 😎  
""", unsafe_allow_html=True)

# 봇 대사 세트 (랜덤)
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

# 세션 상태
if "target" not in st.session_state:
    st.session_state.target = random.randint(1,100)
    st.session_state.last = None

# 입력창 + 버튼
guess = st.number_input("숫자를 입력하세요 (1~100)", min_value=1, max_value=100, value=1, step=1, key="guess_input")
if st.button("도전!") or (st.session_state.last != guess and "guess_input" in st.session_state):
    st.session_state.last = guess
    if guess < st.session_state.target:
        msg = random.choice(MSG_UP)
    elif guess > st.session_state.target:
        msg = random.choice(MSG_DOWN)
    else:
        msg = random.choice(MSG_WRONG)
    st.session_state.bot_msg = msg

if "bot_msg" in st.session_state:
    st.markdown(f"<span style='font-size:1.6rem;color:#4af;font-weight:700;'>{st.session_state.bot_msg}</span>", unsafe_allow_html=True)

# --- 드래그 가능한 봇 공 (p5.js) ---
bot_code = """
<html>
  <head>
    <meta charset="utf-8" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.2/p5.js"></script>
    <style>
      html, body { margin:0; padding:0; background:transparent;}
    </style>
  </head>
  <body>
    <script>
      let x, y, vx=0, vy=0, dragging=false, offsetX=0, offsetY=0, r=48;
      function setup() {
        createCanvas(120,120);
        x = width/2; y = height/2;
      }
      function draw() {
        background(0,0,0,0);
        if(!dragging) {
          x += vx; y += vy;
          vx *= 0.95; vy *= 0.95;
          // 경계 튕기기
          if(x<r){ x=r; vx=-vx*0.7; }
          if(x>width-r){ x=width-r; vx=-vx*0.7; }
          if(y<r){ y=r; vy=-vy*0.7; }
          if(y>height-r){ y=height-r; vy=-vy*0.7; }
        }
        // 공 그림자
        noStroke(); fill(40,70,160,50); ellipse(x, y+10, r*1.05, r*0.36);
        // 공
        fill(80,170,255);
        ellipse(x, y, r*2, r*2);
        // 얼굴 (눈+입)
        fill(255);
        ellipse(x-18, y-7, 19,19); ellipse(x+18, y-7, 19,19);
        fill(40,80,120);
        ellipse(x-18, y-7, 9,13); ellipse(x+18, y-7, 9,13);
        // 입
        stroke(28,60,110); strokeWeight(3); noFill();
        arc(x, y+13, 30,14, 0,PI);
        noStroke();
        // 발그레
        fill(220,120,180,90);
        ellipse(x-18, y+10, 12,5); ellipse(x+18, y+10, 12,5);
        // 눈썹
        stroke(30,50,110,200); strokeWeight(4);
        arc(x-18, y-17, 18,6, PI, PI*2);
        arc(x+18, y-17, 18,6, PI, PI*2);
      }
      function mousePressed() {
        let d = dist(mouseX, mouseY, x, y);
        if(d<r){
          dragging=true;
          offsetX = mouseX-x;
          offsetY = mouseY-y;
          vx=vy=0;
        }
      }
      function mouseDragged() {
        if(dragging){
          x = mouseX-offsetX;
          y = mouseY-offsetY;
        }
      }
      function mouseReleased() {
        if(dragging){
          vx = movedX*0.3; vy = movedY*0.3;
          dragging=false;
        }
      }
    </script>
  </body>
</html>
"""
components.html(bot_code, height=130)
