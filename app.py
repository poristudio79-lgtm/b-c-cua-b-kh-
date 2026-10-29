import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Dino Chrome T-Rex Game", layout="centered")

html_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        body {
            background-color: #121212;
            color: #fff;
            font-family: 'Courier New', Courier, monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            overflow: hidden;
        }
        #game-wrapper {
            position: relative;
            box-shadow: 0 10px 40px rgba(0,0,0,0.8);
            border: 3px solid #fff;
            border-radius: 6px;
            overflow: hidden;
            background: #f7f7f7;
        }
        canvas { display: block; }
        #ui-bar {
            position: absolute;
            top: 10px;
            left: 20px;
            right: 20px;
            display: flex;
            justify-content: space-between;
            font-size: 16px;
            font-weight: bold;
            color: #333;
            z-index: 10;
        }
        #intro-overlay {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.92);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 20px;
            z-index: 40;
        }
        .title {
            font-size: 32px;
            font-weight: bold;
            color: #ffcc00;
            margin-bottom: 10px;
            text-shadow: 2px 2px #ff0000;
        }
        .instructions {
            font-size: 13px;
            color: #ccc;
            max-width: 420px;
            line-height: 1.5;
            margin-bottom: 20px;
            background: rgba(255, 255, 255, 0.05);
            padding: 12px;
            border-radius: 6px;
            text-align: left;
        }
        #start-btn {
            padding: 10px 24px;
            font-size: 16px;
            font-weight: bold;
            font-family: 'Courier New', Courier, monospace;
            color: #000;
            background: #ffcc00;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }
        #start-btn:hover { background: #fff; transform: scale(1.05); }
    </style>
</head>
<body>

    <div id="game-wrapper">
        <div id="intro-overlay">
            <div class="title">🦖 DINO CHROME GAME</div>
            <div class="instructions">
                🎮 <b>Cách chơi:</b><br>
                • Nhấn <b>Space / W / Mũi tên Lên</b> để nhảy qua chướng ngại vật.<br>
                • Tránh né cây xương rồng và sinh tồn càng lâu càng tốt!
            </div>
            <button id="start-btn" onclick="startGame()">▶️ CHƠI NGAY</button>
        </div>

        <div id="ui-bar">
            <div>ĐIỂM: <span id="score">00000</span></div>
        </div>

        <canvas id="gameCanvas" width="600" height="250"></canvas>
    </div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const introOverlay = document.getElementById('intro-overlay');

let gameRunning = false;
let score = 0;
let gameSpeed = 5;
let animFrame = 0;

const dino = {
    x: 50, y: 165, w: 36, h: 40, vy: 0, gravity: 0.6, jumpPower: -10, grounded: true,
    update() {
        this.vy += this.gravity;
        this.y += this.vy;
        if (this.y > 165) {
            this.y = 165;
            this.vy = 0;
            this.grounded = true;
        }
    },
    draw() {
        ctx.fillStyle = '#535353';
        const px = this.x;
        const py = this.y;
        
        ctx.fillRect(px + 18, py, 16, 12);
        ctx.fillRect(px + 26, py + 8, 8, 4);
        ctx.fillStyle = '#f7f7f7';
        ctx.fillRect(px + 26, py + 3, 3, 3);
        
        ctx.fillStyle = '#535353';
        ctx.fillRect(px + 10, py + 12, 16, 16);
        ctx.fillRect(px + 22, py + 16, 5, 4);
        
        ctx.fillRect(px + 2, py + 14, 8, 8);
        ctx.fillRect(px, py + 16, 2, 6);
        
        if (animFrame % 20 < 10) {
            ctx.fillRect(px + 12, py + 28, 4, 12);
            ctx.fillRect(px + 20, py + 28, 4, 8);
        } else {
            ctx.fillRect(px + 12, py + 28, 4, 8);
            ctx.fillRect(px + 20, py + 28, 4, 12);
        }
    }
};

let obstacles = [];
let clouds = [];

function spawnObstacle() {
    obstacles.push({ x: canvas.width, y: 175, w: 18, h: 30 });
}

function spawnCloud() {
    clouds.push({ x: canvas.width, y: Math.random() * 80 + 20, speed: 1.5 });
}

window.addEventListener('keydown', e => {
    if (!gameRunning) return;
    if (e.key === ' ' || e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') {
        if (dino.grounded) {
            dino.vy = dino.jumpPower;
            dino.grounded = false;
        }
    }
});

function startGame() {
    introOverlay.style.display = 'none';
    score = 0;
    gameSpeed = 5;
    obstacles = [];
    clouds = [];
    gameRunning = true;
    loop();
}

let obstacleTimer = 0;
let cloudTimer = 0;

function loop() {
    if (!gameRunning) return;
    animFrame++;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = '#535353';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, 205);
    ctx.lineTo(canvas.width, 205);
    ctx.stroke();

    cloudTimer++;
    if (cloudTimer > 120) {
        spawnCloud();
        cloudTimer = 0;
    }
    for (let i = clouds.length - 1; i >= 0; i--) {
        let c = clouds[i];
        c.x -= c.speed;
        ctx.fillStyle = '#d0d0d0';
        ctx.fillRect(c.x, c.y, 40, 12);
        if (c.x < -50) clouds.splice(i, 1);
    }

    obstacleTimer++;
    if (obstacleTimer > Math.floor(Math.random() * 60 + 90)) {
        spawnObstacle();
        obstacleTimer = 0;
    }

    for (let i = obstacles.length - 1; i >= 0; i--) {
        let obs = obstacles[i];
        obs.x -= gameSpeed;

        ctx.fillStyle = '#535353';
        ctx.fillRect(obs.x, obs.y, obs.w, obs.h);

        if (
            dino.x < obs.x + obs.w &&
            dino.x + dino.w > obs.x &&
            dino.y < obs.y + obs.h &&
            dino.y + dino.h > obs.y
        ) {
            gameRunning = false;
            introOverlay.style.display = 'flex';
            document.querySelector('.title').innerText = "💀 GAME OVER";
            document.querySelector('.instructions').innerText = `Điểm số đạt được: ${score}`;
            document.getElementById('start-btn').innerText = "🔄 CHƠI LẠI";
            return;
        }

        if (obs.x < -40) obstacles.splice(i, 1);
    }

    dino.update();
    dino.draw();
document.getElementById('score').innerText = String(score).padStart(5, '0');
    gameSpeed = 5 + Math.floor(score / 500);

    requestAnimationFrame(loop);
}
</script>
</body>
</html>
"""

components.html(html_code, height=350)
    score += 1;
