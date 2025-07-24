import streamlit as st
import streamlit.components.v1 as components

st.title("⚡ 패링 가위바위보")

st.markdown("""
- 1 = ✌️ (가위), 2 = ✊ (바위), 3 = ✋ (보)  (키보드 눌러서 시작)
- "가위! 바위! 보!" 나오는 동안 키보드 1번 2번 3번 아무때나 눌러서 실시간 손 바꾸기 
- 패배 시 한번 바꿀 기회가 주워짐
- 이때 바꿔서 역전하면 개꿀  
- 같은 손 또 눌러서 지면 그냥 패배
""")

html_code = """
<html>
  <head>
    <meta charset="utf-8" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.2/p5.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.2/addons/p5.sound.min.js"></script>
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
    <audio id="parrySound" src="https://files.catbox.moe/wwyaov.mp3" preload="auto"></audio>
    <script>
      // --------- 게임 변수
      let playerHand = 1; // 1=가위 2=바위 3=보
      let cpuHand = 2;
      let playerHearts = 3;
      let gameState = "wait"; // wait, show, resolve, cpuDrop, cpuSlide, gameover, parry, flash
      let msg = "", handNames = ["", "✌️", "✊", "✋"];
      let cpuDropY = 0, cpuSlideX = 0;
      let timer = 0, phase = 0;
      let inputLock = false;
      let cpuAlive = true;
      let showCpuHand = 2;
      let cpuRandReady = false;
      let flashTime = 0; // 화면 번쩍(프레임수)
      let quakeTime = 0; // 지진 남은 프레임
      let origHand = 1; // 패배시 내 원래 손(연타 방지)
      let parryState = 0; // 0: 패배시 대기, 1: 바꿨는지
      let parryTimer = 0; // 패링창 0.4초
      let afterParry = 0; // 1: 패리성공, 2: 패리무승부, 3: 패리실패

      // --------- 사운드
      let parrySound;
      function preload() {}

      function setup() {
        let c = createCanvas(window.innerWidth, 390);
        c.parent('canvas-container');
        frameRate(60);
        document.getElementById("msg").innerHTML = "시작하기: 아무 키(1/2/3) 입력!";
        parrySound = document.getElementById("parrySound");
      }

      function draw() {
        // ---- 지진/플래시 효과 계산 ----
        let doFlash = (flashTime>0);
        let doQuake = (quakeTime>0);
        let qStrength = doQuake ? (quakeTime/30) : 0; // 0~1, (30프레임=0.5초)
        let shakeX=0, shakeY=0;

        if (doQuake) {
          let maxShake = 22*qStrength; // 초반에 세게, 점점 줄어듦
          shakeX = random(-maxShake, maxShake);
          shakeY = random(-maxShake, maxShake);
          quakeTime--;
        }

        push();
        translate(shakeX, shakeY);

        // ---- 화면 번쩍 (플래시)
        if (doFlash) {
          background(255,255,255, 210);
          flashTime--;
        } else {
          background(26,28,36);
        }

        // 하트(플레이어) - 왼쪽 위
        textSize(30);
        let heartStr = "";
        for(let i=0; i<playerHearts; i++) heartStr += "❤️";
        fill(doFlash?32:255,doFlash?32:255,doFlash?32:255);
        textAlign(LEFT, TOP);
        text(heartStr, 30, 14);

        // 플레이어 손(왼쪽)
        textSize(80); textAlign(CENTER, CENTER);
        fill(doFlash?255:250,doFlash?240:250,doFlash?200:255);
        text(handNames[playerHand], 120, height/2+20);

        // 패링 타이밍 원 (gameState=="parry"에서만)
        if (gameState==="parry" && parryTimer>0) {
          noFill();
          stroke(64,180,250, 190);
          strokeWeight(10);
          let t = parryTimer/24.0;
          ellipse(120, height/2+20, 160*t, 160*t);
          strokeWeight(1);
        }

        // cpu 손(오른쪽)
        let cpuY = height/2+20 + cpuDropY;
        let cpuX = width-120 - cpuSlideX;
        fill(cpuAlive?(doFlash?64:255):(doFlash?180:180),
              cpuAlive?(doFlash?64:255):(doFlash?180:180),
              cpuAlive?(doFlash?60:220):(doFlash?160:220));
        text(handNames[showCpuHand], cpuX, cpuY);

        // 중앙 구분선
        stroke(doFlash?200:150,doFlash?210:155,doFlash?230:190,70);
        strokeWeight(2.1);
        line(width/2, 35, width/2, height-35);

        pop();

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
          // 판정! 패배면 패링 찬스
          if (parryState==1) {
            gameState="parry";
            msg = "바꿔!!!!!";
            parryTimer = 24; // 0.4초(60fps 기준)
            parryState=2;
          } else if (!cpuAlive) {
            // cpu 패배시 손 아래로 떨어짐
            cpuDropY += 16;
            if (cpuDropY > 160) {
              cpuDropY = 0;
              gameState = "cpuSlide";
              cpuAlive = true;
              cpuHand = 2; // 초기상태: 바위
              showCpuHand = 2;
              cpuSlideX = -width*0.6;
            }
          }
        } else if (gameState==="parry") {
          // 패링 타이밍
          if (parryTimer>0) {
            parryTimer--;
          } else {
            // 0.4초내에 못 바꿈 or 또 패배면 그냥 패배
            if (afterParry==0) {
              loseLife();
            }
          }
        } else if (gameState==="flash") {
          // 패링 성공 연출(0.5초간 멈춤+번쩍+지진)
          if (flashTime<=0 && quakeTime<=0) {
            startRound();
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
        if (inputLock && gameState!=="show" && gameState!=="parry") return;
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
        if (gameState==="parry" && parryTimer>0) {
          if (key=="1"||key=="2"||key=="3") {
            let newHand = int(key);
            // 같은 손으로 또 지면 그냥 패배
            if (newHand == origHand) {
              afterParry = 0;
              parryTimer=0;
              return false;
            }
            playerHand = newHand;
            let win = judge(playerHand, cpuHand); // 1:승, 0:무, -1:패
            if (win==1) {
              // 패링 성공!
              msg="패링!";
              flashTime = 18; // 0.3초
              quakeTime = 30; // 0.5초(60fps기준)
              gameState = "flash";
              parrySound.play();
              afterParry=1;
              setTimeout(()=>{cpuAlive=false;},400);
            } else if (win==0) {
              msg="비겼다!";
              afterParry=2;
              setTimeout(()=>{ startRound(); }, 680);
              gameState = "wait";
            } else {
              // 또 패배
              afterParry=0;
              setTimeout(()=>{ loseLife(); }, 180);
              parryTimer=0;
            }
            parryTimer=0;
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
        parryState = 0; afterParry=0; origHand=1;
      }

      function resolve() {
        // 판정!
        origHand = playerHand;
        let win = judge(playerHand, cpuHand); // 1:승, 0:무, -1:패
        if (win==1) {
          msg = "승리!";
          cpuAlive=false;
          gameState="resolve";
        } else if (win==-1) {
          // 패배: "바꿔!!!!!" 찬스
          parryState=1;
          // 이후 draw()에서 gameState를 parry로 전환
        } else {
          msg = "무승부!";
          setTimeout(()=>{ startRound(); }, 650);
          gameState = "wait";
        }
        inputLock = true;
      }

      function loseLife() {
        msg = "패배!";
        playerHearts--;
        if (playerHearts<=0) {
          gameState = "gameover";
        } else {
          setTimeout(()=>{ startRound(); }, 650);
          gameState = "wait";
        }
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
