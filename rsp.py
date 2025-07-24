import streamlit as st
import streamlit.components.v1 as components

st.title("⚡ 반속 가위바위보: 진짜 페이스러시 리듬 (monday X fury)")

st.markdown("""
**[조작법]**  
- 1 = ✌️ (가위), 2 = ✊ (바위), 3 = ✋ (보)  
- **"가위! 바위! 보!"** 뜨는 동안 <kbd>1</kbd>/<kbd>2</kbd>/<kbd>3</kbd> 아무때나 눌러서 실시간 손 바꿀 수 있음!  
- CPU는 **항상 주먹(✊)으로 대기하다가**, “보!”에서만 랜덤하게 결정.  
- 이기면 cpu 손이 아래로 떨어지고, 새로운 cpu가 "오른쪽 바깥"에서 들어옴!  
- 지거나 시간초과면 ❤️이 1개 깎임 (0되면 게임오버)
""")

html_code = """
<html>
  <head>
    <meta charset="utf-8" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.2/p5.js"></script>
    <style>
      html, body { margin:0; padding:0; overflow:hidden; background:#21232a; }
      #canvas-container { width: 100vw; height: 390px;}
      .centermsg {
        position:absolute; top:65px; left:0; right:0; text-align:center;
        font-size:2.4rem; color:#fff; text-shadow:0 2px 12px #000d; font-family:sans-serif;
      }
      .gameover {
        position:absolute; top:150px; left:0; right:0; text-align:center;
        font-size:2.8rem; color:#ffd0d0; text-shadow:0 2px 12px #000d;
        font-family:sans-serif;
      }
    </style>
  </head>
  <body>
    <div id="canvas-container"></div>
    <div class="centermsg" id="msg"></div>
    <div class="gameover" id="over"></div>
    <script>
      // --------- 게임 변수
      let playerHand = 1; // 1=가위 2=바위 3=보
      let cpuHand = 2; // cpu 기본: 바위
      let playerHearts = 3;
      let gameState = "wait"; // wait, show, resolve, cpuDrop, cpuSlide, gameover
      let msg = "", handNames = ["", "✌️", "✊", "✋"];
      let cpuDropY = 0, cpuSlideX = 0;
      let timer = 0, phase = 0;
      let inputLock = false;
      let cpuAlive = true;
      let nextCpuHand = 2; // 다음 cpu 손
      let showCpuHand = 2; // 애니메이션용 "지금 화면에 보여줄 cpu 손"
      let cpuRandReady = false;

      // --------- 시작
      function setup() {
        let c = createCanvas(window.innerWidth, 390);
        c.parent('canvas-container');
        frameRate(60);
        document.getElementById("msg").innerHTML = "시작하기: 아무 키(1/2/3) 입력!";
      }

      function draw() {
        background(26,28,36);

        // 하트(플레이어) - 왼쪽 위
        textSize(30);
        let heartStr = "";
        for(let i=0; i<playerHearts; i++) heartStr += "❤️";
        fill(255); textAlign(LEFT, TOP);
        text(heartStr, 30, 14);

        // 플레이어 손(왼쪽)
        textSize(80); textAlign(CENTER, CENTER);
        fill(250,250,255);
        text(handNames[playerHand], 120, height/2+20);

        // cpu 손(오른쪽)
        let cpuY = height/2+20 + cpuDropY;
        let cpuX = width-120 - cpuSlideX;
        fill(cpuAlive?255:180, cpuAlive?255:180, cpuAlive?255:220);
        // showCpuHand: 현재 화면에 보여줄 손
        text(handNames[showCpuHand], cpuX, cpuY);

        // 중앙 구분선
        stroke(150,155,190,70);
        strokeWeight(2.1);
        line(width/2, 35, width/2, height-35);

        // 입력/상태 메시지
        document.getElementById("msg").innerHTML = msg;

        // 상태머신
        if (gameState==="wait") {
          // 대기: 아무 키 누르면 시작
        } else if (gameState==="show") {
          // "가위! 바위! 보!" 애니메이션+입력(0.9초)
          let t = millis()-timer;
          phase = int(t/300);
          cpuRandReady = false;

          // showCpuHand: "보!"전까지는 바위, "보!"시점에만 cpuHand 결정
          if (phase<2) {
            msg = phase==0 ? "가위!" : "바위!";
            showCpuHand = 2; // 바위
          } else if (phase==2) {
            msg = "보!";
            if (!cpuRandReady) {
              cpuHand = [1,2,3][int(random(3))];
              showCpuHand = cpuHand;
              cpuRandReady = true;
            }
          }
          if (t>=900) {
            gameState = "resolve"; msg="";
            inputLock = true;
            resolve();
          }
        } else if (gameState==="resolve") {
          // 판정 애니
          // cpu 패배시 손 아래로 떨어짐
          if (!cpuAlive) {
            cpuDropY += 16;
            if (cpuDropY > 160) {
              cpuDropY = 0;
              gameState = "cpuSlide";
              cpuAlive = true;
              // 다음 cpu는 오른쪽 바깥에서 등장
              cpuHand = 2; // 초기상태: 바위
              showCpuHand = 2;
              cpuSlideX = -width*0.6;
            }
          }
        } else if (gameState==="cpuSlide") {
          // 새로운 cpu 등장, 오른쪽 바깥에서 슬라이드 인
          cpuSlideX += 24;
          if (cpuSlideX>=0) {
            cpuSlideX = 0;
            gameState = "show";
            timer = millis();
            phase = 0;
            cpuRandReady = false;
            msg = "";
          }
        } else if (gameState==="gameover") {
          document.getElementById("over").innerHTML = "GAME OVER<br>다시 시작하려면 새로고침!";
          noLoop();
        }
      }

      // --------- 키보드 입력
      function keyPressed() {
        if (inputLock && gameState!=="show") return;
        if (gameState==="wait") {
          startRound();
          return false;
        }
        if (gameState==="show") {
          if (key=="1"||key=="2"||key=="3") {
            playerHand = int(key); // 쿨타임 없이 즉시 손 바꿀 수 있음
            return false;
          }
        }
      }

      function startRound() {
        // 새 라운드 시작
        msg="";
        cpuAlive=true;
        cpuDropY=0;
        cpuSlideX=0;
        cpuHand = 2;
        showCpuHand = 2;
        playerHand = 1;
        gameState = "show";
        timer = millis();
        phase = 0;
        cpuRandReady = false;
        document.getElementById("over").innerHTML = "";
        inputLock = false;
      }

      function resolve() {
        // 판정!
        let win = judge(playerHand, cpuHand); // 1:승, 0:무, -1:패
        if (win==1) {
          msg = "승리!";
          cpuAlive=false;
          gameState="resolve";
        } else if (win==-1) {
          msg = "패배!";
          playerHearts--;
          if (playerHearts<=0) {
            gameState = "gameover";
          } else {
            setTimeout(()=>{ startRound(); }, 650);
            gameState = "wait";
          }
        } else {
          msg = "무승부!";
          setTimeout(()=>{ startRound(); }, 650);
          gameState = "wait";
        }
        inputLock = true;
      }

      function judge(player, cpu) {
        if (player==cpu) return 0; // 무승부
        if ((player==1&&cpu==3)||(player==2&&cpu==1)||(player==3&&cpu==2)) return 1; // 승
        return -1; // 패
      }

      window.onresize = function() {
        resizeCanvas(window.innerWidth, 390);
      }
    </script>
  </body>
</html>
"""

components.html(html_code, height=420, scrolling=False)
