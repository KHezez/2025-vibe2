import streamlit as st
import streamlit.components.v1 as components

st.title("🛡️ 탄막 패링 미니게임 (섬광+폭발ver)")
st.markdown("탄이 플레이어에 닿기 직전 **클릭**으로 패링!<br>패링 시 섬광처럼 화면 전체가 밝아지고 0.2초간 멈춤.<br>탄막은 이제 화면 전체에서 떨어집니다.", unsafe_allow_html=True)

html_code = """
<html>
  <head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.2/p5.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.2/addons/p5.sound.min.js"></script>
    <style>
      html, body { margin:0; padding:0; overflow:hidden; background:#20232a;}
      #canvas-container { width: 100vw; height: 470px;}
      .score { position:absolute; top:16px; right:40px; color:#fff; font-size:1.4rem; font-family:monospace; text-shadow:0 2px 8px #000c; }
    </style>
  </head>
  <body>
    <div id="canvas-container"></div>
    <div class="score" id="score"></div>
    <script>
      // ----- SETUP -----
      let px, py, r=22;
      let bullets = [];
      let parryWindow = 22;
      let score = 0, streak = 0, parryPerfect = false;
      let parryFlash = 0, parryFreeze = 0;
      let gameStarted = false, gameOver = false;
      let parrySound;
      function preload() {
        parrySound = loadSound("https://files.catbox.moe/wwyaov.mp3"); // 울트라킬 패링 사운드
      }
      function setup() {
        let c = createCanvas(window.innerWidth, 470);
        c.parent('canvas-container');
        frameRate(60);
        px = width/2; py = height*0.8;
        document.getElementById("score").innerHTML = "";
      }

      // ----- BULLET GENERATION -----
      function spawnBullet() {
        // x = 화면 가로 어디서나, 각도 = -0.75PI~ -0.25PI (더 넓게)
        let x = random(width*0.08, width*0.92);
        let y = 0;
        // 각도: -PI*0.7 ~ -PI*0.3 (더 다양화, 아래로 골고루)
        let angle = random(-PI*0.7, -PI*0.3);
        let speed = random(2.8, 3.7);
        let vx = sin(angle)*speed;
        let vy = cos(angle)*speed+2.2;
        bullets.push({x:x, y:y, vx:vx, vy:vy, alive:true, parried:false});
      }

      let lastBullet = 0;
      function draw() {
        let brightMode = (parryFlash>0);
        let brightness = brightMode ? min(1, parryFlash/12) : 0;
        // ----- 화면 그리기 -----
        // 1. 배경 (섬광)
        if (!gameStarted) {
          let bgcol = lerpColor(color(30,36,40), color(255,255,255), brightness*0.95);
          background(bgcol);
          fill(255);
          textAlign(CENTER,CENTER);
          textSize(34);
          text("클릭해서 시작!", width/2, height/2-20);
          textSize(18);
          text("탄이 닿기 직전 클릭으로 패링! 폭발 효과/사운드+섬광 연출", width/2, height/2+18);
          return;
        }
        if (gameOver) {
          let bgcol = lerpColor(color(20,12,12), color(255,245,200), brightness*0.95);
          background(bgcol);
          fill(255,60,60,160);
          textSize(44);
          textAlign(CENTER,CENTER);
          text("게임 오버!", width/2, height/2-22);
          textSize(22);
          text("스코어: "+score, width/2, height/2+24);
          return;
        }
        // 배경 섬광 (전체 밝기 up)
        let bgcol = lerpColor(color(34,36,45), color(255,255,245), brightness*0.86);
        background(bgcol);

        // 멈춤 연출 (패링 성공시 0.2초)
        if (parryFreeze>0) {
          parryFreeze--;
        } else {
          // 패링 플래시 점점 줄임 (0.2초 유지)
          if (parryFlash>0) parryFlash -= 6;
        }

        // 2. 플레이어 (밝기)
        let pcol = lerpColor(color(190,210,255), color(255,255,255), brightness*0.93);
        fill(pcol);
        ellipse(px, py, r*2.1, r*2.1);
        let pcol2 = lerpColor(color(60,90,190,160), color(240,250,255,180), brightness*0.95);
        fill(pcol2);
        ellipse(px, py, r*1.08, r*1.08);

        // 3. 총알 (밝기, 패링 상태)
        for (let i=bullets.length-1; i>=0; i--) {
          let b = bullets[i];
          if (!b.alive) continue;
          let bulletCol = b.parried ?
            lerpColor(color(70,240,180,150), color(255,255,255,200), brightness*0.75) :
            lerpColor(color(250,90,50), color(255,255,255), brightness*0.7);
          fill(bulletCol);
          ellipse(b.x, b.y, b.parried ? 25 : 20, b.parried ? 25 : 20);
          if (parryFreeze==0) {
            b.x += (b.vx||0);
            b.y += (b.vy||0);
          }
          // 플레이어 닿음 (미스)
          let d = dist(b.x,b.y,px,py);
          if (d < r*0.98 && !b.parried) {
            gameOver = true;
            document.getElementById("score").innerHTML = "";
          }
          // 화면 아래로 나가면 삭제
          if (b.y > height+30) bullets.splice(i,1);
        }
        // 4. 총알 생성 (멈춤중엔 멈춤)
        if (parryFreeze==0 && frameCount - lastBullet > 29) {
          spawnBullet();
          lastBullet = frameCount;
        }
        document.getElementById("score").innerHTML = "점수: "+score+(streak>4?"  🔥":"");
      }

      function mousePressed() {
        if (!gameStarted) {
          gameStarted = true;
          gameOver = false;
          px = width/2; py = height*0.8; r=22;
          bullets = []; score=0; streak=0;
          lastBullet = frameCount; parryFlash=0; parryFreeze=0;
          return;
        }
        if (gameOver) {
          gameStarted=false;
          return;
        }
        // 가장 가까운 탄과 거리 비교 → 패링 판정
        let hit = false;
        for (let i=0; i<bullets.length; i++) {
          let b = bullets[i];
          if (!b.alive || b.parried) continue;
          let d = dist(b.x,b.y,px,py);
          if (d < r+10 && d > r-11) {
            // 패링 성공!
            b.parried = true; hit=true;
            score += 100; streak += 1;
            parryFlash = 18; // 0.2초
            parryFreeze = 12; // 0.2초(60fps 기준)
            if (parrySound.isLoaded()) parrySound.play();
            break;
          }
        }
        if (!hit) {
          score -= 33; streak=0;
          parryFlash=0; parryFreeze=0;
        }
      }

      function mouseMoved() {
        if (gameStarted && !gameOver) {
          px = constrain(mouseX, r, width-r);
        }
      }

      window.onresize = function() {
        resizeCanvas(window.innerWidth, 470);
      }
    </script>
  </body>
</html>
"""
components.html(html_code, height=500, scrolling=False)
