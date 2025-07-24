import streamlit as st
import streamlit.components.v1 as components

st.title("🛡️ 탄막 패링 미니게임 (by monday X fury, 버그패치판)")
st.markdown("탄이 플레이어 근처에 오면 클릭으로 패링!<br>번쩍이는 폭발 이펙트, 자유 이동, 탄막 다양화.", unsafe_allow_html=True)

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
      let px, py, r=22;
      let bullets = [];
      let parryWindow = 22;
      let score = 0, streak = 0;
      let parryFlash = 0, parryFreeze = 0;
      let gameStarted = false, gameOver = false;
      let parrySound;
      let startScreen = true;

      function preload() {
        parrySound = loadSound("https://files.catbox.moe/wwyaov.mp3");
      }
      function setup() {
        let c = createCanvas(window.innerWidth, 470);
        c.parent('canvas-container');
        frameRate(60);
        px = width/2; py = height*0.8;
        document.getElementById("score").innerHTML = "";
        startScreen = true;
      }

      // --- 탄막 다양화 ---
      function spawnBullet() {
        let x = random(width*0.08, width*0.92);
        let y = -20;
        let angle = atan2(py-y, px-x) + random(-PI/6, PI/6);
        let speed = random(2.6, 4.0);
        bullets.push({
          x: x, y: y,
          vx: cos(angle)*speed,
          vy: sin(angle)*speed,
          alive: true, parried: false
        });
      }

      let lastBullet = 0;
      function draw() {
        if (startScreen) {
          background(30,36,40);
          fill(255);
          textAlign(CENTER,CENTER);
          textSize(34);
          text("클릭해서 시작!", width/2, height/2-20);
          textSize(18);
          text("탄이 플레이어에 닿기 직전 클릭으로 패링!\n폭발 효과/사운드가 뜸", width/2, height/2+18);
          return;
        }
        if (!gameStarted) {
          background(30,36,40);
          fill(255);
          textAlign(CENTER,CENTER);
          textSize(34);
          text("클릭해서 시작!", width/2, height/2-20);
          textSize(18);
          text("탄이 플레이어에 닿기 직전 클릭으로 패링!\n폭발 효과/사운드가 뜸", width/2, height/2+18);
          return;
        }
        if (gameOver) {
          background(20,12,12);
          fill(255,60,60,160);
          textSize(44);
          textAlign(CENTER,CENTER);
          text("게임 오버!", width/2, height/2-22);
          textSize(22);
          text("스코어: "+score, width/2, height/2+24);
          return;
        }
        // 극딜 플래시
        if (parryFlash > 0) {
          if (parryFlash === 15) {
            background(255,255,255);
          } else {
            background(255,255,220, parryFlash*10);
          }
          parryFlash--;
        } else {
          background(34,36,45);
        }
        if (parryFreeze>0) {
          parryFreeze--;
          return;
        }

        // 플레이어
        fill(190,210,255);
        ellipse(px, py, r*2.1, r*2.1);
        fill(60,90,190,160);
        ellipse(px, py, r*1.08, r*1.08);

        // 탄막 (0.5초에 1발, 점점 짧아짐)
        let bulletDelay = 30 - Math.min(score//300, 16);
        if (frameCount - lastBullet > bulletDelay) {
          spawnBullet();
          lastBullet = frameCount;
        }

        // 탄 이동/그리기
        for (let i=bullets.length-1; i>=0; i--) {
          let b = bullets[i];
          if (!b.alive) continue;
          if (!b.parried) {
            fill(250,90,50);
            ellipse(b.x, b.y, 20,20);
          } else {
            fill(70,240,180,160);
            ellipse(b.x, b.y, 25,25);
          }
          b.x += (b.vx||0);
          b.y += (b.vy||0);

          // 플레이어 닿음 (미스)
          let d = dist(b.x,b.y,px,py);
          if (d < r*0.98 && !b.parried) {
            gameOver = true;
            document.getElementById("score").innerHTML = "";
          }
          if (b.y > height+30 || b.x < -50 || b.x > width+50) bullets.splice(i,1);
        }
        document.getElementById("score").innerHTML = "점수: "+score+(streak>4?"  🔥":"");
      }

      function mousePressed() {
        if (startScreen || !gameStarted) {
          gameStarted = true;
          gameOver = false;
          px = width/2; py = height*0.8; r=22;
          bullets = []; score=0; streak=0;
          lastBullet = frameCount; parryFlash=0; parryFreeze=0;
          startScreen = false;
          return;
        }
        if (gameOver) {
          gameStarted=false;
          startScreen=true;
          return;
        }
        // 가장 가까운 탄 판정
        let hit = false;
        for (let i=0; i<bullets.length; i++) {
          let b = bullets[i];
          if (!b.alive || b.parried) continue;
          let d = dist(b.x,b.y,px,py);
          if (d < r+11 && d > r-14) {
            b.parried = true; hit=true;
            score += 100; streak += 1;
            parryFlash = 15;
            parryFreeze = 18;
            if (parrySound.isLoaded()) parrySound.play();
            break;
          }
        }
        if (!hit) {
          score -= 33; streak=0;
          parryFlash=0; parryFreeze=0;
        }
      }

      // 마우스 이동: 반드시 게임 중에만 적용
      function mouseMoved() {
        if (gameStarted && !gameOver && !startScreen) {
          px = constrain(mouseX, r, width-r);
          py = constrain(mouseY, r, height-r);
        }
      }
      function touchMoved() {
        if (gameStarted && !gameOver && !startScreen) {
          px = constrain(mouseX, r, width-r);
          py = constrain(mouseY, r, height-r);
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
