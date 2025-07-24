import streamlit as st
import streamlit.components.v1 as components

st.title("⚡ 반속 가위바위보: '페이스러시' (by monday X fury)")

st.markdown("""
**[조작법]**  
- 1 = ✌️ (가위), 2 = ✊ (바위), 3 = ✋ (보)  
- 중앙에 "가위! 바위! 보!" 뜨는 동안 <kbd>1</kbd>/<kbd>2</kbd>/<kbd>3</kbd> 아무거나 누르세요  
- CPU는 랜덤하게 내고,  
- 이기면 cpu 손이 아래로 떨어지고,  
- 새로운 cpu가 오른쪽에서 등장합니다  
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
      let cpuHand = 1;
      let playerHearts = 3;
      let gameState = "wait"; // wait, show, input, resolve, cpuDrop, cpuSlide, gameover
      let msg = "", handNames = ["", "✌️", "✊", "✋"];
      let cpuDropY = 0, cpuSlideX = 0;
      let timer = 0, phase = 0;
      let inputLock = false, lastInput = 0;
      let cpuQueue = [2,3,1,2,3]; // 뒤에 무한 대기
      let cpuAlive = true;

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
        text(handNames[cpuHand], cpuX, cpuY);

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
          // "가위! 바위! 보!" 애니메이션
          phase = int((millis()-timer)/300);
          if (phase==0) { msg="가위!"; }
          else if (phase==1) { msg="바위!"; }
          else if (phase==2) { msg="보!"; }
          else {
            gameState = "input"; msg="손을 내세요! (1/2/3)";
            timer = millis();
            inputLock = false;
            lastInput = 0;
          }
        } else if (gameState==="input") {
          // 입력 타이밍(0.9초)
          if (!inputLock && millis()-timer>900) {
            // 입력 못함 = 패배
            inputLock = true;
            resolve(-1);
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
              cpuHand = cpuQueue.shift();
              cpuQueue.push([1,2,3][int(random(3))]);
              cpuSlideX = width*0.6;
            }
          }
        } else if (gameState==="cpuSlide") {
          // 새로운 cpu 등장, 오른쪽에서 왼쪽으로 슬라이드
          cpuSlideX -= 24;
          if (cpuSlideX<=0) {
            cpuSlideX = 0;
            gameState = "show";
            timer = millis();
            phase = 0;
            msg = "";
          }
        } else if (gameState==="gameover") {
          // 게임오버: 메시지
          document.getElementById("over").innerHTML = "GAME OVER<br>다시 시작하려면 새로고침!";
          noLoop();
        }
      }

      // --------- 키보드 입력
      function keyPressed() {
        if (inputLock) return;
        if (gameState==="wait") {
          startRound();
          return false;
        }
        if (gameState==="input") {
          if (key=="1"||key=="2"||key=="3") {
            inputLock = true;
            lastInput = int(key);
            resolve(lastInput);
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
        cpuHand = [1,2,3][int(random(3))];
        playerHand = 1;
        gameState = "show";
        timer = millis();
        phase = 0;
        document.getElementById("over").innerHTML = "";
      }

      function resolve(input) {
        // -1이면 시간초과/미입력
        playerHand = input>0?input:1; // 입력없으면 기본 1(가위)
        let win = judge(playerHand, cpuHand); // 1:승, 0:무, -1:패
        if (win==1) {
          msg = "승리!";
          cpuAlive=false;
          gameState="resolve";
        } else if (win==-1||input==-1) {
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
