import streamlit as st
import random
import streamlit.components.v1 as components

st.title("🎱 트롤 숫자맞추기 with 빠따 (monday X fury)")

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
MSG_HIT = [
    "으아아아악!!!!!!!!", "꺄아아악!", "아파! 왜 때려 ㅋㅋㅋ", "세상에, 살려줘!!!", "으악 빠따!!!"
]

# 세션 관리
if "target" not in st.session_state:
    st.session_state.target = random.randint(1,100)
    st.session_state.try_count = 0
    st.session_state.bot_msg = ""
    st.session_state.paper_shown = False
    st.session_state.paper_revealed = False
    st.session_state.batta_mode = False
    st.session_state.batta_hits = 0
    st.session_state.true_clear = False

target = st.session_state.target
try_count = st.session_state.try_count
batta_mode = st.session_state.batta_mode
batta_hits = st.session_state.batta_hits
paper_shown = st.session_state.paper_shown
paper_revealed = st.session_state.paper_revealed
true_clear = st.session_state.true_clear

# 1. 기본 숫자입력
if not batta_mode and not true_clear:
    guess = st.number_input("숫자를 입력하세요 (1~100)", min_value=1, max_value=100, value=1, step=1, key="guess_input")
    if st.button("도전!"):
        st.session_state.try_count += 1
        if guess < target:
            msg = random.choice(MSG_UP)
        elif guess > target:
            msg = random.choice(MSG_DOWN)
        else:
            msg = random.choice(MSG_WRONG)
        st.session_state.bot_msg = msg

    if st.session_state.bot_msg:
        st.markdown(f"<span style='font-size:1.5rem;color:#4af;font-weight:700;'>{st.session_state.bot_msg}</span>", unsafe_allow_html=True)

    # 2. 빠따 버튼 (3번 이상 틀리면 나타남)
    if st.session_state.try_count >= 3 and not st.session_state.batta_mode:
        st.markdown('<span style="color:#f33;font-weight:700">진짜 너무하네…</span>', unsafe_allow_html=True)
        if st.button("빠따"):  # 빠따 버튼
            st.session_state.batta_mode = True

# 3. 빠따 모드 (공+빠따 등장)
if batta_mode and not paper_revealed and not true_clear:
    st.markdown("""
    <b>빠따를 드래그해서 공을 5번 맞추세요!</b>
    <br>끝부분을 잡고 휘둘러서 <span style="color:#07f">공</span>을 때려보세요!
    """, unsafe_allow_html=True)

    batta_js = f"""
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
          let ball = {{x:180, y:180, vx:0, vy:0, r:16}};
          let bat = {{x:280, y:290, a:0, dragging:false, offset:0}};
          let bat_len = 72;
          let hits = {batta_hits};
          let textToShow = "";
          let hitFrame = 0;
          function setup() {{
            createCanvas(360,360);
          }}
          function draw() {{
            background(245,251,255,255);
            // 물리
            if(!bat.dragging){{
              ball.x += ball.vx; ball.y += ball.vy;
              ball.vx *= 0.96; ball.vy *= 0.96;
              if(ball.x<ball.r){{ ball.x=ball.r; ball.vx=-ball.vx*0.7; }}
              if(ball.x>width-ball.r){{ ball.x=width-ball.r; ball.vx=-ball.vx*0.7; }}
              if(ball.y<ball.r){{ ball.y=ball.r; ball.vy=-ball.vy*0.7; }}
              if(ball.y>height-ball.r){{ ball.y=height-ball.r; ball.vy=-ball.vy*0.7; }}
            }}
            // 공
            noStroke();
            fill(74,180,255);
            ellipse(ball.x, ball.y, ball.r*2, ball.r*2);
            stroke(30,60,120,70); strokeWeight(2);
            ellipse(ball.x, ball.y, ball.r*2.1, ball.r*2.1);
            noStroke();

            // 빠따
            push();
            translate(bat.x, bat.y);
            rotate(bat.a);
            fill(210,180,100);
            rect(-bat_len+8,-6,bat_len,12, 12,6,16,6);
            fill(130,70,30);
            rect(-bat_len-6,-12,16,24, 8,7,12,7);
            pop();

            // 빠따 드래그
            if(bat.dragging){{
              let mx = constrain(mouseX, 60, width-24);
              let my = constrain(mouseY, 50, height-24);
              bat.x = mx;
              bat.y = my;
              bat.a = atan2(my-ball.y, mx-ball.x) + random(-0.09,0.09);
            }}

            // 충돌 판정(끝에서만 맞음)
            let tipX = bat.x - cos(bat.a)*bat_len;
            let tipY = bat.y - sin(bat.a)*bat_len;
            let d = dist(ball.x, ball.y, tipX, tipY);
            if(d < ball.r+16 && !bat.dragging && frameCount % 7 == 0){{
              ball.vx += (ball.x-tipX)*0.09 + random(-2,2);
              ball.vy += (ball.y-tipY)*0.09 + random(-2,2);
              if(hitFrame==0) {{
                hits += 1;
                hitFrame = 23;
                textToShow = "{random.choice(MSG_HIT)}";
                window.parent.postMessage({{"batta_hits":hits}}, "*");
              }}
            }}

            // 히트 이펙트
            if(hitFrame>0){{
              fill(255,100,30, 150*hitFrame/23);
              ellipse(ball.x, ball.y, 70, 32);
              textSize(20); fill(255,30,20, 200*hitFrame/23);
              textAlign(CENTER, CENTER);
              text(textToShow, width/2, 44);
              hitFrame--;
            }}

            // 정답 종이 뱉기
            if(hits>=5){{
              fill(250,250,240);
              rect(ball.x-26, ball.y+ball.r+8, 52,32, 9,9,9,9);
              fill(0); textSize(16); textAlign(CENTER,TOP);
              text("정답은\\n{target+0.1}", ball.x, ball.y+ball.r+16);
              textSize(11); fill(60);
              text("[종이 획득!]", ball.x, ball.y+ball.r+36);
              window.parent.postMessage({{"paper_revealed":1}}, "*");
            }}
          }}

          function mousePressed() {{
            let tipX = bat.x - cos(bat.a)*bat_len;
            let tipY = bat.y - sin(bat.a)*bat_len;
            if(dist(mouseX, mouseY, tipX, tipY)<22){{
              bat.dragging=true; bat.offset=dist(mouseX,mouseY,bat.x,bat.y);
            }}
          }}
          function mouseDragged() {{
            if(bat.dragging){{
              let mx = constrain(mouseX, 60, width-24);
              let my = constrain(mouseY, 50, height-24);
              bat.x = mx;
              bat.y = my;
              bat.a = atan2(my-ball.y, mx-ball.x) + random(-0.09,0.09);
            }}
          }}
          function mouseReleased() {{
            if(bat.dragging){{ bat.dragging=false; }}
          }}

          // 메시지 브릿지
          window.addEventListener("message", function(e) {{
            if(e.data && e.data.reset_batta){{ hits=0; }}
          }}, false);
        </script>
      </body>
    </html>
    """
    # 여기서 JS→파이썬으로 값 전달은 제한이 있지만(iframe) 히트/종이 노출은 아래 버튼으로 체크 가능
    components.html(batta_js, height=400)
    # 공이 5대 맞으면 종이 나옴. 종이 보이면 아래 입력창(아니면 안내만 표시)
    if not st.session_state.paper_revealed:
        if st.button("종이 나왔다! 정답 입력하기"):
            st.session_state.paper_revealed = True

# 4. 종이 등장, 진짜 정답 입력
if st.session_state.paper_revealed and not st.session_state.true_clear:
    st.markdown(f"종이에 적힌 정답은 **{target+0.1}** 입니다. 아래 숫자를 입력하세요!")
    real = st.number_input("진짜 정답 입력 (소수 가능)", value=0.0, format="%.1f", key="real_answer")
    if st.button("진짜 도전!"):
        if abs(real-(target+0.1)) < 1e-7:
            st.balloons()
            st.success("🎉 진짜 승리! (빠따로 트롤공 참교육 성공)")
            st.session_state.true_clear = True
        else:
            st.error("아직 아님! 종이에 적힌 정답을 입력해야 해요.")
