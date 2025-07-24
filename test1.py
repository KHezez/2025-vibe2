import streamlit as st
import streamlit.components.v1 as components

st.title("🛡️ 탄막 패링 미니게임 (섬광 패링/XY컨트롤/방향수정 by monday X fury)")
st.markdown("탄이 다가올 때 **정확히 클릭**해서 패링!<br>패링 순간 밝아지며 멈추는 연출, 총알은 모든 방향에서 쏟아짐!", unsafe_allow_html=True)

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
      let score = 0, streak = 0;
      let parryFlash = 0, parryFreeze = 0;
      let gameStarted = false, gameOver = false;
      let parrySound;
      function preload() {
        parrySound = loadSound("https://files.catbox.moe/wwyaov.mp3");
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
        // 탄막이 화면 전체(상단)에서 다양한 각도로 내려오게끔
        let edge = random();
        let x, y, angle, speed;
        speed = random(2.8, 3.7);
        // 상단(50%) / 좌측(25%) / 우측(25%) 스폰
        if (edge < 0.5) {
          // 상단 출현
          x = random(40, width-40);
          y = -10;
          angle = random(PI*0.7, PI*1.3); // 대략 아래쪽(±40도)
        } else if (edge < 0.75) {
          // 왼쪽 출현
          x = -10; y = random(60, height*0.8);
          angle = random(-PI*0.1, PI*0.5); // 오른쪽+약간 아래
        } else {
          // 오른쪽 출현
          x = width+10; y = random(60, height*0.8);
          angle = random(PI*0.5, PI*1.1); // 왼쪽+약간 아래
        }
        bullets.push({x:x, y:y, vx:cos(angle)*speed, vy:sin(angle)*speed, alive:true, parried:false});
      }

      let lastBullet = 0;
      function draw() {
        // --- START 화면
        if (!gameStarted) {
          background(30,36,40);
          fill(255);
          textAlign(CENTER,CENTER);
          textSize(34);
          text("클릭해서 시작!", width/2, height/2-20);
          textSize(18);
          text("탄이 플레이어에 닿기 직전 클릭으로 패링!\n패링시 섬광+멈춤+사운드", width/2, height/2+24);
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

        // 패링 성공시 밝아지는 섬광 이펙트+멈춤
        if (parryFlash>0) {
          // 화면 전체 밝기 올리기 (섬광 연출, 다 덮진 않음)
          background(140+parryFlash*0.8, 180+parryFlash*1.1, 220+parryFlash*0.8);
          parryFlash -= 17; // 0.2초만(빠르게 fade out)
        } else {
          background(34,36,45);
        }
        if (parryFreeze>0) {
          parryFreeze--;
          // freeze중에도 플레이어, 총알 멈춤
          // 단, 섬광은 draw됨
          // 스코어 표시
          document.getElementById("score").innerHTML = "점수: "+score+(streak>4?"  🔥":"");
          return;
        }

        // 플레이어
        fill(190,210,255, 230);
        ellipse(px, py, r*2.1, r*2.1);
        fill(60,90,190,170);
        ellipse(px, py, r*1.08, r*1.08);

        // 총알 생성
        if (frameCount - lastBullet > 27) { // 0.45초에 1발
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
          // 화면 밖으로 나가면 삭제
          if (b.y > height+30 || b.x < -50 || b.x > width+50) bullets.splice(i,1);
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
          if (d < r+11 && d > r-11) { // 패링 타이밍(±11px)
            // 패링 성공!
            b.parried = true; hit=true;
            score += 100; streak += 1;
            parryFlash = 64; // 0.2초(강한 섬광)
            parryFreeze = 12; // 0.2초 멈춤
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
        // 마우스 위치 따라 x/y 모두 이동
        if (gameStarted && !gameOver) {
          px = constrain(mouseX, r, width-r);
          py = constrain(mouseY, height*0.5, height*0.93);
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
