import streamlit as st
import streamlit.components.v1 as components

st.title("🔥 멋진 가위바위보")
st.markdown("아래 손을 클릭해서 선택! 승리/패배에 따라 화려한 연출과 점수가 나타납니다.")

html_code = """
<html>
<head>
<script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.2/p5.js"></script>
<style>
  html, body { margin:0; padding:0; background:#222;}
  #canvas-container { width: 100vw; height: 430px;}
  .score { position:absolute; top:16px; right:40px; color:#fff; font-size:1.3rem; font-family:monospace; text-shadow:0 2px 8px #000c;}
  .msg { position:absolute; top:56px; left:0; right:0; text-align:center; color:#fff; font-size:1.2rem; opacity:0.92;}
</style>
</head>
<body>
<div id="canvas-container"></div>
<div class="score" id="score"></div>
<div class="msg" id="msg"></div>
<script>
let hands = ["✌️","✊","✋"];
let handNames = ["가위", "바위", "보"];
let playerPick = -1, cpuPick = -1, animT=0;
let phase="pick";
let score=0, streak=0, bestStreak=0;
let resultMsg="";
let particleArr=[];
let colorWin=[255,220,90], colorLose=[250,70,70], colorDraw=[80,180,255];

function setup() {
  let c = createCanvas(window.innerWidth, 420);
  c.parent('canvas-container');
  frameRate(60);
  drawUI();
}

function draw() {
  background(30,36,40);
  textAlign(CENTER,CENTER);
  textSize(32);

  // 메시지
  document.getElementById("score").innerHTML =
    "점수: " + score + (streak>1 ? "🔥" + streak : "") +
    (bestStreak>2 ? " | 최고연승: "+bestStreak : "");
  document.getElementById("msg").innerHTML = resultMsg;

  // 결과 애니메이션
  if (phase=="show") {
    // VS 타이밍
    let colorR, msgR;
    if (animT < 20) {
      fill(255);
      textSize(32+8*Math.sin(animT/2));
      text("VS", width/2, height/2);
    }
    // 손들 애니
    if (animT < 35) {
      // 손들 "슬라이드 인"
      drawHand(playerPick, width/2-90+40*Math.cos(animT/8), height/2+25, 1, true);
      drawHand(cpuPick, width/2+90-40*Math.cos(animT/8), height/2-25, 1, false);
    } else {
      // 고정 위치에서 결과 강조
      let outcome = getOutcome(playerPick, cpuPick);
      let glow = animT<55 ? min(1, (animT-34)/12) : 1;
      let colorE = (outcome==1) ? colorWin : (outcome==-1? colorLose : colorDraw);
      // 파티클
      for(let i=0; i<particleArr.length; i++) {
        let p = particleArr[i];
        fill(p.c[0],p.c[1],p.c[2],p.a);
        ellipse(p.x, p.y, p.r, p.r);
        p.x += p.vx; p.y += p.vy; p.a -= 2.4;
        if (p.a<2) { particleArr.splice(i,1); i--;}
      }
      drawHand(playerPick, width/2-90, height/2+25, 1+0.1*glow, true, colorE);
      drawHand(cpuPick, width/2+90, height/2-25, 1+0.1*glow, false, colorE);

      // 결과 메시지/컬러플래시
      if (animT==40) {
        if (outcome==1) {
          for(let k=0; k<19; k++) addParticle(width/2-90, height/2+25, colorWin);
        } else if (outcome==-1) {
          for(let k=0; k<15; k++) addParticle(width/2+90, height/2-25, colorLose);
        }
      }
      if (animT > 60) phase="pick";
    }
    animT++;
    return;
  }

  // 선택창
  for(let i=0; i<3; i++) {
    let x=width/2-100+i*100, y=height*0.75;
    drawHand(i, x, y, 1.28+(playerPick==i?0.15:0));
    if (phase=="pick") {
      if (dist(mouseX,mouseY,x,y)<42) {
        cursor("pointer");
        fill(255,255,255,30+sin(frameCount/5)*30);
        ellipse(x,y,80,80);
      }
    }
  }
  // CPU 선택(랜덤)
  if (phase=="cpu_anim") {
    drawHand(int(random(3)), width/2+90, height/2-25, 1, false);
    if (animT<28) animT++;
    else { cpuPick=int(random(3)); phase="show"; animT=0;}
  }
}

function drawHand(idx, x, y, scale=1, player=true, colorE=null) {
  push();
  translate(x, y);
  scale*=1.22;
  textAlign(CENTER,CENTER);
  textSize(60*scale);
  let txtColor=color(220,240,255);
  if (colorE) txtColor=color(colorE[0],colorE[1],colorE[2]);
  fill(txtColor);
  text(hands[idx],0,0);
  pop();
  // 아래에 손이름
  push();
  textAlign(CENTER);
  textSize(17*scale);
  fill(180,195,255,170);
  text(handNames[idx],x,y+48*scale);
  pop();
}

function mousePressed() {
  if (phase!="pick") return;
  // 손 클릭
  for(let i=0; i<3; i++) {
    let x=width/2-100+i*100, y=height*0.75;
    if (dist(mouseX,mouseY,x,y)<50) {
      playerPick=i;
      phase="cpu_anim";
      animT=0; cpuPick=-1;
      setTimeout(()=>{
        let out=getOutcome(playerPick, cpuPick);
        if (out==1) {
          resultMsg="🔥 이겼다! 멋짐!";
          score+=111; streak+=1; bestStreak=max(bestStreak,streak);
        } else if (out==-1) {
          resultMsg="😵 패배… 역전각?";
          score-=99; streak=0;
        } else {
          resultMsg="😎 무승부, 자존심 싸움";
        }
      }, 880);
      break;
    }
  }
}

function getOutcome(a, b) {
  if (a==b) return 0; // 무
  if ((a==0&&b==2)||(a==1&&b==0)||(a==2&&b==1)) return 1; // 승
  return -1; // 패
}

function addParticle(x,y,c) {
  let a=210+random(-40,25), ang=random(TWO_PI);
  let r=18+random(12);
  particleArr.push({x:x,y:y,c:c.slice(),a:a,vx:cos(ang)*random(2,6),vy:sin(ang)*random(2,6),r:r});
}

window.onresize = function() { resizeCanvas(window.innerWidth, 420);}
</script>
</body>
</html>
"""

components.html(html_code, height=500, scrolling=False)
