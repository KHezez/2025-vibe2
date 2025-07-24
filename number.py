import streamlit as st
import random
import streamlit.components.v1 as components

st.title("🎱 숫자맞추기: 트롤 봇 + 깡패 소환 에디션")

st.markdown("""
> 파란 공에 정답을 맞춰도 봇이 인정 안 함 ㅋㅋ  
> 세 번 이상 클릭하면… "깡패 소환" 버튼이 나옴!  
> 깡패공으로 트롤공을 5번 맞춰야 진짜 정답(종이)이 떨어진다!
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
MSG_HIT = [
    "으아아아악!!!!!!!!", "아야야야야야!!", "살려줘!!", "도망쳐!!!", "아악! 그만!!",
    "공격하지 마!!", "괜히 깝쳤다!!", "으아아아아!!!!", "어, 어림없지… 아악!", "깡패다 깡패!!!!!!"
]

if "target" not in st.session_state:
    st.session_state.target = random.randint(1,100)
    st.session_state.last = None
    st.session_state.troll_clicks = 0
    st.session_state.summon_gang = False
    st.session_state.hits = 0
    st.session_state.paper = False
    st.session_state.final_win = False
    st.session_state.show_paper = False

# 숫자 입력/판정
if not st.session_state.final_win:
    guess = st.number_input("숫자를 입력하세요 (1~100 또는 소수점 가능)", min_value=1.0, max_value=100.9, value=1.0, step=0.1, key="guess_input")
    btn_click = st.button("도전!")

    # "종이" 입력
    if st.session_state.show_paper and not st.session_state.final_win and abs(guess - (st.session_state.target+0.1)) < 1e-6:
        st.session_state.final_win = True

    # 도전 버튼 처리
    if btn_click:
        if st.session_state.show_paper:
            if abs(guess - (st.session_state.target+0.1)) < 1e-6:
                st.session_state.final_win = True
            else:
                st.session_state.bot_msg = "이제 진짜 정답만 입력하면 돼!"
        elif guess < st.session_state.target:
            msg = random.choice(MSG_UP)
            st.session_state.bot_msg = msg
        elif guess > st.session_state.target:
            msg = random.choice(MSG_DOWN)
            st.session_state.bot_msg = msg
        else:
            msg = random.choice(MSG_WRONG)
            st.session_state.troll_clicks += 1
            st.session_state.bot_msg = msg

if "bot_msg" in st.session_state and not st.session_state.final_win:
    st.markdown(f"<span style='font-size:1.6rem;color:#4af;font-weight:700;'>{st.session_state.bot_msg}</span>", unsafe_allow_html=True)

# 깡패 소환 버튼
if st.session_state.troll_clicks >= 3 and not st.session_state.summon_gang:
    if st.button("😈 깡패 소환"):
        st.session_state.summon_gang = True
        st.session_state.hits = 0

# p5.js 공 (파란 트롤공 + 깡패공, 깡패 공격횟수 판정)
custom_code = f"""
<html>
  <head>
    <meta charset="utf-8" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.2/p5.js"></script>
    <style>
      html, body {{ margin:0; padding:0; background:transparent; }}
    </style>
  </head>
  <body>
    <div id="paperhint"></div>
    <script>
      let tx = 110, ty = 180, tvx=0, tvy=0, tr=16;
      let draggingT = false, t_offsetX=0, t_offsetY=0;
      let gx = 250, gy = 270, gvx=0, gvy=0, gr=40;
      let draggingG = false, g_offsetX=0, g_offsetY=0;
      let hits = {st.session_state.hits};
      let showGang = {str(st.session_state.summon_gang).lower()};
      let showPaper = {str(st.session_state.show_paper).lower()};
      let paperMsg = "";
      let lastHitFrame = -80;
      function setup() {{
        createCanvas(360,360);
        tx = 110; ty = 180; tvx = tvy = 0;
        gx = 250; gy = 270; gvx = gvy = 0;
      }}
      function draw() {{
        background(245,251,255,255);
        // 트롤 공
        fill(74,180,255); noStroke();
        ellipse(tx, ty, tr*2, tr*2);
        stroke(30,60,120,70); strokeWeight(2);
        ellipse(tx, ty, tr*2.1, tr*2.1);
        noStroke();
        // 깡패공
        if(showGang && hits<5) {{
            fill(220,70,80);
            ellipse(gx, gy, gr*2, gr*2);
            stroke(90,12,20,100); strokeWeight(3.2);
            ellipse(gx, gy, gr*2.08, gr*2.08);
            noStroke();
        }}
        // 종이 뱉기
        if(showPaper) {{
            fill(255,255,220); stroke(120,120,100); strokeWeight(1.2);
            rect(tx+tr+12, ty-16, 48, 32, 5);
            fill(80,80,30); noStroke();
            textSize(15);
            text("정답", tx+tr+18, ty+2);
            textSize(17);
            text("{round(st.session_state.target+0.1, 1)}", tx+tr+18, ty+22);
        }}
        // 메시지
        if(lastHitFrame > frameCount-50) {{
            fill(240,30,50,200);
            textSize(18);
            textAlign(CENTER,TOP);
            text(paperMsg, tx, ty-tr-18);
        }}
        // 물리
        if(!draggingT) {{
            tx += tvx; ty += tvy;
            tvx *= 0.96; tvy *= 0.96;
            if(tx<tr){{ tx=tr; tvx=-tvx*0.75; }}
            if(tx>width-tr){{ tx=width-tr; tvx=-tvx*0.75; }}
            if(ty<tr){{ ty=tr; tvy=-tvy*0.75; }}
            if(ty>height-tr){{ ty=height-tr; tvy=-tvy*0.75; }}
        }}
        if(showGang && hits<5 && !draggingG) {{
            gx += gvx; gy += gvy;
            gvx *= 0.96; gvy *= 0.96;
            if(gx<gr){{ gx=gr; gvx=-gvx*0.75; }}
            if(gx>width-gr){{ gx=width-gr; gvx=-gvx*0.75; }}
            if(gy<gr){{ gy=gr; gvy=-gvy*0.75; }}
            if(gy>height-gr){{ gy=height-gr; gvy=-gvy*0.75; }}
        }}
        // 충돌 체크 (깡패공+트롤공)
        if(showGang && hits<5) {{
            let d = dist(tx,ty,gx,gy);
            if(d < tr+gr+2 && !draggingT && !draggingG && frameCount-lastHitFrame>14) {{
                let angle = atan2(ty-gy,tx-gx);
                let force = 3;
                tvx += cos(angle)*force; tvy += sin(angle)*force;
                gvx -= cos(angle)*force*0.6; gvy -= sin(angle)*force*0.6;
                // 충돌시 메시지, 충돌카운트
                paperMsg = "{random.choice(MSG_HIT)}";
                lastHitFrame = frameCount;
                hits += 1;
                if(hits>=5) {{
                    setTimeout(function() {{
                        showPaper = true;
                        document.getElementById("paperhint").innerHTML = "<div style='font-size:1.4rem;margin:10px;color:#443'>트롤공이 정답 종이를 뱉었다!<br><b>정답: {round(st.session_state.target+0.1,1)}</b>를 입력하세요</div>";
                    }}, 700);
                }}
                // 세션에 저장
                window.parent.postMessage({{event:"hit",hits:hits,showPaper:showPaper}}, "*");
            }}
        }}
      }}
      function mousePressed() {{
        // 깡패공부터 체크
        if(showGang && hits<5) {{
            let d2 = dist(mouseX, mouseY, gx, gy);
            if(d2<gr){{
                draggingG=true; g_offsetX = mouseX-gx; g_offsetY = mouseY-gy; gvx=gvy=0;
                return;
            }}
        }}
        let d = dist(mouseX, mouseY, tx, ty);
        if(d<tr){{
          draggingT=true; t_offsetX = mouseX-tx; t_offsetY = mouseY-ty; tvx=tvy=0;
        }}
      }}
      function mouseDragged() {{
        if(showGang && hits<5 && draggingG){{
            gx = mouseX-g_offsetX; gy = mouseY-g_offsetY;
            return;
        }}
        if(draggingT){{
            tx = mouseX-t_offsetX; ty = mouseY-t_offsetY;
        }}
      }}
      function mouseReleased() {{
        if(draggingT){{
          tvx = movedX*0.3; tvy = movedY*0.3; draggingT=false;
        }}
        if(showGang && draggingG){{
            gvx = movedX*0.3; gvy = movedY*0.3; draggingG=false;
        }}
      }}
      // 세션 hit count 동기화
      window.addEventListener("message", (e)=>{
        if(e.data && e.data.event=="sethit"){
            hits = e.data.hits;
            showPaper = e.data.showPaper;
        }
      });
    </script>
  </body>
</html>
"""

# p5.js와 streamlit 세션 상태 연동용: 충돌 count/종이 상태 동기화
import streamlit_javascript as st_js
js_code = """
window.addEventListener("message", (e)=>{
    if(e.data && e.data.event=="hit"){
        window.parent.postMessage(e.data, "*");
    }
});
"""

st_js.st_javascript(js_code, key="st_js_sync")
components.html(custom_code, height=400)

if st.session_state.final_win:
    st.balloons()
    st.success("🎉 드디어 승리! 트롤공을 이겼다! (깡패공 5대, 정답 입력)")
elif st.session_state.show_paper:
    st.info(f"트롤공이 종이를 뱉었다! 정답은 {round(st.session_state.target+0.1,1)}")
