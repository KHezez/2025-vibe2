import streamlit as st
import streamlit.components.v1 as components

st.title("🌈 Gradient Party")
st.markdown("실시간 그라디언트 컬러 + 클릭하면 애니메이션/사운드까지! 아무것도 안해도 멋진 뽕맛. ")

html_code = """
<html>
  <head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.2/p5.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.2/addons/p5.sound.min.js"></script>
    <style>
      html, body { margin:0; padding:0; overflow:hidden; height:100%; }
      #canvas-container { width: 100vw; height: 85vh; }
      .fade-msg {
        position: absolute; bottom: 25px; left: 0; right: 0;
        text-align: center; font-size: 2rem; color: #fff;
        text-shadow: 0 2px 8px #000b;
        opacity: 0.86; z-index: 5;
        pointer-events: none; user-select: none;
        font-family: 'Segoe UI', 'Pretendard', sans-serif;
      }
    </style>
  </head>
  <body>
    <div id="canvas-container"></div>
    <div class="fade-msg" id="msg"></div>
    <script>
      let phase = 0;
      let dots = [];
      let lastClick = 0;
      let colorModes = ["rainbow", "cool", "fire"];
      let modeIdx = 0;

      let osc, env;
      let loaded = false;

      function setup() {
        let c = createCanvas(window.innerWidth, window.innerHeight*0.85);
        c.parent('canvas-container');
        frameRate(60);
        osc = new p5.Oscillator('triangle');
        env = new p5.Envelope();
        env.setADSR(0.01, 0.2, 0.05, 0.6);
        osc.amp(env);
        loaded = true;
        window.addEventListener('resize', ()=>resizeCanvas(window.innerWidth, window.innerHeight*0.85));
      }

      function draw() {
        phase += 0.006;
        let grad;
        if (colorModes[modeIdx]=="rainbow") {
          grad = lerpColor(
            color(255*Math.abs(Math.sin(phase)), 255*Math.abs(Math.sin(phase+1)), 255*Math.abs(Math.sin(phase+2))),
            color(255*Math.abs(Math.cos(phase+1)), 255*Math.abs(Math.cos(phase+2)), 255*Math.abs(Math.cos(phase))),
            0.5 + 0.5*Math.sin(phase*0.9)
          );
        } else if (colorModes[modeIdx]=="cool") {
          grad = lerpColor(
            color(60, 100, 255), color(0,255,180), 0.5+0.5*Math.sin(phase)
          );
        } else {
          grad = lerpColor(
            color(255,80,40), color(250,220,70), 0.5+0.5*Math.cos(phase)
          );
        }
        background(grad);

        // 큰 중앙원 (wave 느낌)
        let r = 180 + 80*Math.sin(phase*1.6);
        noStroke();
        fill(255,255,255,60+110*Math.abs(Math.cos(phase*1.7)));
        ellipse(width/2, height/2, r, r);

        // 클릭 애니메이션
        for (let i=dots.length-1; i>=0; i--) {
          let d = dots[i];
          d.t += 1;
          let alpha = 230 - d.t*6;
          fill(d.c[0],d.c[1],d.c[2], alpha);
          ellipse(d.x, d.y, 20+d.t*5, 20+d.t*5);
          if (alpha<0) dots.splice(i,1);
        }
      }

      function mousePressed() {
        // 애니메이션
        for (let i=0; i<12; i++) {
          let angle = i * Math.PI*2/12;
          let px = mouseX + Math.cos(angle)*38;
          let py = mouseY + Math.sin(angle)*38;
          let cc = [255*Math.random(), 255*Math.random(), 255*Math.random()];
          dots.push({x:px, y:py, c:cc, t:0});
        }
        showMsg("펑!!!!!!!!!!!!!!!!!11");
        userStartAudio();
        // 사운드
        if (loaded) {
          osc.freq(220+Math.random()*620);
          osc.start();
          env.play(osc, 0, 0.2);
          setTimeout(()=>{osc.stop()}, 300);
        }
      }

      function doubleClicked() {
        // 컬러모드 바꾸기
        modeIdx = (modeIdx+1)%colorModes.length;
        showMsg("🎨 컬러모드: " + colorModes[modeIdx]);
      }

      function showMsg(txt) {
        let el = document.getElementById("msg");
        if (!el) return;
        el.innerHTML = txt;
        el.style.opacity = "0.86";
        setTimeout(()=>{el.style.opacity="0"}, 1500);
      }

      window.onresize = function() {
        resizeCanvas(window.innerWidth, window.innerHeight*0.85);
      }
    </script>
    <div style="text-align:center;color:#fff;font-size:1.1rem;opacity:0.72;margin-top:10px;">
      <b>클릭</b>: 파티클+사운드! &nbsp; | &nbsp; <b>더블클릭</b>: 컬러모드 체인지!
    </div>
  </body>
</html>
"""

components.html(html_code, height=480, scrolling=False)
