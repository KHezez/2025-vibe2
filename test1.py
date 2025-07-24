import streamlit as st
import streamlit.components.v1 as components

st.title("🛡️ 탄막 패링 미니게임 (by monday X fury)")
st.markdown("적 탄이 다가오면 **정확한 타이밍에 클릭**으로 패링!<br>맞으면 폭발 사운드와 화면 효과가 나옴.", unsafe_allow_html=True)

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
        parrySound = loadSound("https://files.catbox.moe/wwyaov.mp3"); // 여기에 울트라킬 패링 사운드 넣으면 됨
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
        let angle = random(-PI/3, -2*PI/3);
        let dist = random(width*0.1, width*0.9);
        let x = dist, y = 0;
        let speed = random(2.5, 3.7);
        bullets.push({x:x, y:y, vx:sin(angle)*speed, vy:cos(angle)*speed+2, alive:true, parried:false});
      }

      let lastBullet = 0;
      function draw() {
        if (!gameStarted) {
          background(30,36,40);
          fill(255);
          textAlign(CENTER,CENTER);
          textSize(34);
          text("클릭해서 시작!", width/2, height/2-20);
          textSize(18);
          text("탄이 플레이어에 닿기 직전 클릭으로 패링! 폭발 효과/사운드가 뜸", width/2, height/2+18);
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

        // 패링 성공시 화면 플래시+멈춤
        if (parryFlash>0) {
          background(255,255,200,parryFlash*1.6);
          parryFlash -= 7;
        } else {
          background(34,36,45);
        }
        if (parryFreeze>0) {
          parryFreeze--;
          return; // 일시정지
        }

        // 플레이어
        fill(190,210,255);
        ellipse(px, py, r*2.1, r*2.1);
        fill(60,90,190,160);
        ellipse(px, py, r*1.08, r*1.08);

        // 총알 생성
        if (frameCount - lastBullet > 30) { // 0.5초에 1발씩
          spawnBullet();
          lastBullet = frameCount;
        }

        // 총알 이동/그리기
        for (let i=bullets.length-1; i>=0; i--) {
          let b = bullets[i];
          if (!b.alive) continue;
          if (!b.parried) {
            fill(250,90,50);
            ellipse(b.x, b.y, 20,20);
          } else {
            fill(70,240,180,150);
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
          // 화면 아래로 나가면 삭제
          if (b.y > height+30) bullets.splice(i,1);
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
          if (d < r+10 && d > r-11) { // 패링 타이밍(±10px)
            // 패링 성공!
            b.parried = true; hit=true;
            score += 100; streak += 1;
            parryFlash = 70; // 0.3초
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
