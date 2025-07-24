import streamlit as st
import streamlit.components.v1 as components

st.title("⚡ 반속 가위바위보: 페이스러시 (v2 by monday X fury)")

st.markdown("""
- **1 = ✌️(가위), 2 = ✊(바위), 3 = ✋(보)**  
- "가위! 바위! 보!" 진행 중 언제든 1/2/3 눌러 손 바꿀 수 있음  
- CPU는 "보!" 타이밍에 랜덤하게 손 결정, 그 전까지 ✊  
- 이기면 점수+1, CPU 손 떨어지고 새 CPU는 오른쪽에서 슬라이드 인  
- 지거나 시간초과: ❤️ 감소, 0되면 게임오버 + 점수 표시!
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
      let cpuHand = 2;
      let playerHearts = 3;
      let gameState = "wait"; // wait, show, judge, resolve, cpuDrop, cpuSlide, gameover
      let msg = "", handNames = ["", "✌️", "✊", "✋"];
      let cpuDropY = 0, cpuSlideX = 0;
      let timer = 0, phase = 0;
      let lastInput = 1;
      let inputLock = false;
      let showPhase = 0;
      let score = 0, bestScore = 0;
      let cpuAlive = true;
      let cpuHandDraw = 2; // 표시용 (보! 전까지 항상 ✊)
      let newCpuHand = 2; // 판정 후 슬라이드인용

      function setup() {
        let c = createCanvas(window.innerWidth, 390);
        c.parent('canvas-container');
        frameRate(60);
        document.getElementById("msg").innerHTML = "시작하기: 아무 키(1/2/3) 입력!";
        playerHand = 1; cpuHand = 2;
      }

      function draw() {
        background(26,28,36);

        // 하트(플레이어) - 왼쪽 위
        textSize(30);
        let heartStr = "";
        for(let i=0; i<playerHearts; i++) heartStr += "❤️";
        fill(255); textAlign(LEFT, TOP);
        text(heartStr, 30, 14);

        // 점수 (왼쪽 아래)
        textSize(20); fill(220);
        textAlign(LEFT, BOTTOM);
        text("점수: " + score, 32, height-14);

        // 플레이어 손(왼쪽)
        textSize(80); textAlign(CENTER, CENTER);
        fill(250,250,255);
        text(handNames[playerHand], 120, height/2+20);

        // cpu 손(오른쪽)
        let cpuY = height/2+20 + cpuDropY;
        let cpuX = width-120 - cpuSlideX;
        fill(cpuAlive?255:180, cpuAlive?255:180, cpuAlive?255:220);
        text(handNames[cpuHandDraw], cpuX, cpuY);

        // 중앙 구분선
        stroke(150,155,190,70);
        strokeWeight(2.1);
        line(width/2, 35, width/2, height-35);

        // 메시지
        document.getElementById("msg").innerHTML = msg;

        // 상태머신
        if (gameState==="wait") {
          // 대기: 아무 키 누르면 시작
        } else if (gameState==="show") {
          // "가위! 바위! 보!" 애니메이션
          let elapsed = millis() - timer;
          showPhase = int(elapsed / 300);
          if (showPhase==0) { msg="가위!"; cpuHandDraw=2; }
          else if (showPhase==1) { msg="바위!"; cpuHandDraw=2; }
          else if (showPhase==2) { msg="보!"; cpuHandDraw=2; }
          else {
            // "보!" 순간 cpu 손 결정!
            cpuHand = [1,2,3][int(random(3))];
            cpuHandDraw = cpuHand;
            msg="결과!";
            gameState = "judge";
            timer = millis();
          }
        } else if (gameState==="judge") {
          // 입력 마감 (0.1초 딜레이 후 판정)
          if (!inputLock && millis()-timer>100) {
            inputLock=true;
            resolve(playerHand);
          }
        } else if (gameState==="resolve") {
          // 판정 애니
          // cpu 패배시 손 아래로 떨어짐
          if (!cpuAlive) {
            cpuDropY += 18;
            if (cpuDropY > 150) {
              cpuDropY = 0;
              gameState = "cpuSlide";
              cpuAlive = true;
              // 새 cpu 오른쪽에서 등장
              cpuSlideX = width*0.65;
              newCpuHand = [1,2,3][int(random(3))];
              cpuHand = newCpuHand; cpuHandDraw = newCpuHand;
            }
          }
        } else if (gameState==="cpuSlide") {
          // cpu가 오른쪽 바깥에서 슬라이드 인
          cpuSlideX -= 26;
          if (cpuSlideX<=0) {
            cpuSlideX = 0;
            gameState = "show";
            timer = millis();
            showPhase = 0;
            msg = "";
            cpuHandDraw = 2; // "가위! 바위! 보!"엔 주먹
          }
        } else if (gameState==="gameover") {
          // 게임오버: 메시지+점수
          document.getElementById("over").innerHTML = "GAME OVER<br>점수: "+score+"<br><br>새로고침으로 재도전!";
          noLoop();
        }
      }

      function keyPressed() {
        if (inputLock) return;
        if (gameState==="wait") {
          score=0; playerHearts=3;
          startRound();
          return false;
        }
        if (gameState==="show") {
          if (key=="1"||key=="2"||key=="3") {
            playerHand = int(key); // 실시간 교체!
          }
        }
      }

      function startRound() {
        // 새 라운드 시작
        msg="";
        cpuAlive=true;
        cpuDropY=0;
        cpuSlideX=0;
        cpuHand = 2; // 바위로 대기
        cpuHandDraw = 2;
        playerHand = 1;
        gameState = "show";
        timer = millis();
        showPhase = 0;
        document.getElementById("over").innerHTML = "";
        inputLock = false;
      }

      function resolve(input) {
        // 판정
        let win = judge(input, cpuHand); // 1:승, 0:무, -1:패
        if (win==1) {
          msg = "승리!";
          score += 1;
          cpuAlive=false;
          gameState="resolve";
        } else if (win==-1) {
          msg = "패배!";
          playerHearts--;
          if (playerHearts<=0) {
            gameState = "gameover";
          } else {
            setTimeout(()=>{ startRound(); }, 700);
            gameState = "wait";
          }
        } else {
          msg = "무승부!";
          setTimeout(()=>{ startRound(); }, 700);
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
