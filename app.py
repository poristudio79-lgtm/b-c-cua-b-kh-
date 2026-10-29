import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Dino Puzzle Parkour", layout="centered")

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
        #quiz-box {
            display: none;
            position: absolute;
            top: 35%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(30, 30, 30, 0.95);
            border: 2px solid #ffcc00;
            border-radius: 8px;
            padding: 15px;
            width: 80%;
            text-align: center;
            z-index: 30;
            box-shadow: 0 0 20px rgba(255, 204, 0, 0.5);
        }
        #quiz-question {
            color: #ffcc00;
            font-size: 15px;
            font-weight: bold;
            margin-bottom: 12px;
        }
        .quiz-option {
            background: #333;
            color: #fff;
            border: 1px solid #555;
            padding: 8px 12px;
            margin: 5px;
            font-size: 13px;
            border-radius: 4px;
            cursor: pointer;
            font-family: 'Courier New', Courier, monospace;
        }
        .quiz-option:hover { background: #555; border-color: #ffcc00; }
        
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

        #controls-hint {
            margin-top: 12px;
            color: #888;
            font-size: 13px;
            text-align: center;
        }
    </style>
</head>
<body>

    <div id="game-wrapper">
        <div id="intro-overlay">
            <div class="title">🦖 DINO PUZZLE PARKOUR</div>
            <div class="instructions">
                🎮 <b>Cách chơi:</b><br>
                • Nhấn <b>Space / W / Mũi tên Lên</b> để nhảy qua chướng ngại vật.<br>
                • Trên đường chạy, khủng long sẽ gặp các <b>câu hỏi trí tuệ / toán học / logic</b>.<br>
                • Trả lời đúng để nhận điểm thưởng và tăng tốc độ; trả lời sai sẽ bị giảm điểm!
            </div>
            <button id="start-btn" onclick="startGame()">▶️ CHƠI NGAY</button>
        </div>

        <div id="ui-bar">
            <div>ĐIỂM: <span id="score">00000</span></div>
            <div>CÂU HỎI TRÍ TUỆ: <span id="puzzle-count">0</span></div>
        </div>

        <div id="quiz-box">
            <div id="quiz-question">Đang tải câu hỏi...</div>
            <div id="quiz-options-container"></div>
        </div>

        <canvas id="gameCanvas" width="600" height="250"></canvas>
    </div>

    <div id="controls-hint">
        🎮 <b>Nhảy:</b> Space / Mũi tên Lên | Trả lời câu đố bằng cách bấm vào các đáp án.
    </div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const introOverlay = document.getElementById('intro-overlay');
const quizBox = document.getElementById('quiz-box');
const quizQuestion = document.getElementById('quiz-question');
const quizOptionsContainer = document.getElementById('quiz-options-container');

let gameRunning = false;
let score = 0;
let puzzleSolvedCount = 0;
let gameSpeed = 5;
let animFrame = 0;

// Dữ liệu câu hỏi trí tuệ / logic / toán học
const puzzleBank = [
    { q: "Số tiếp theo trong dãy là gì? 2, 4, 8, 16, ...", options: ["24", "32", "64"], answer: "32" },
    { q: "Cái gì có cổ nhưng không có đầu?", options: ["Cái áo", "Cái chai", "Cái quạt"], answer: "Cái áo" },
    { q: "5 quả táo lấy đi 2 quả, bạn còn mấy quả?", options: ["2 quả", "3 quả", "5 quả"], answer: "2 quả" },
    { q: "Lịch nào dài nhất trong năm?", options: ["Lịch treo tường", "Lịch tường", "Lịch Vạn Niên"], answer: "Lịch Vạn Niên" },
    { q: "Số nguyên tố nhỏ nhất là số mấy?", options: ["0", "1", "2"], answer: "2" },
    { q: "Từ gì bỏ đầu thì thành bay, bỏ đuôi thành bay?", options: ["Không có", "Máy bay", "Con chim"], answer: "Không có" }
];

const dino = {
    x: 50, y: 170, w: 30, h: 35, vy: 0, gravity: 0.6, jumpPower: -10, grounded: true,
    update() {
        this.vy += this.gravity;
        this.y += this.vy;
        if (this.y > 170) {
            this.y = 170;
            this.vy = 0;
            this.grounded = true;
        }
    },
    draw() {
        ctx.fillStyle = '#535353';
        // Thân khủng long
        ctx.fillRect(this.x, this.y + 10, 26, 20);
        // Đầu khủng long
        ctx.fillRect(this.x + 16, this.y, 14, 14);
        // Mắt
        ctx.fillStyle = '#fff';
        ctx.fillRect(this.x + 24, this.y + 3, 3, 3);
        // Chân
        ctx.fillStyle = '#535353';
        if (animFrame % 20 < 10) {
            ctx.fillRect(this.x + 4, this.y + 30, 6, 8);
            ctx.fillRect(this.x + 16, this.y + 30, 6, 5);
        } else {
            ctx.fillRect(this.x + 4, this.y + 30, 6, 5);
            ctx.fillRect(this.x + 16, this.y + 30, 6, 8);
        }
    }
};

let obstacles = [];
let clouds = [];

function spawnObstacle() {
    let type = Math.random() > 0.5 ? 'cactus' : 'bird';
    let obs = {
        x: canvas.width,
        y: type === 'cactus' ? 175 : 130,
        w: type === 'cactus' ? 20 : 30,
        h: type === 'cactus' ? 30 : 20,
        type: type
    };
    obstacles.push(obs);
}

function spawnCloud() {
    clouds.push({ x: canvas.width, y: Math.random() * 80 + 20, speed: 1.5 });
}

window.addEventListener('keydown', e => {
    if (!gameRunning || quizBox.style.display === 'block') return;
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
    puzzleSolvedCount = 0;
    gameSpeed = 5;
    obstacles = [];
    clouds = [];
    gameRunning = true;
    loop();
}

let obstacleTimer = 0;
let cloudTimer = 0;
let puzzleTriggerDistance = 0;

function triggerPuzzle() {
    gameRunning = false; // Tạm dừng game để giải đố
    let randomPuzzle = puzzleBank[Math.floor(Math.random() * puzzleBank.length)];
    quizQuestion.innerText = randomPuzzle.q;
    quizOptionsContainer.innerHTML = '';
    
    randomPuzzle.options.forEach(opt => {
        let btn = document.createElement('button');
        btn.className = 'quiz-option';
        btn.innerText = opt;
        btn.onclick = () => {
            if (opt === randomPuzzle.answer) {
                score += 500;
                puzzleSolvedCount++;
                document.getElementById('puzzle-count').innerText = puzzleSolvedCount;
            } else {
                score = Math.max(0, score - 200);
            }
            quizBox.style.display = 'none';
            gameRunning = true;
            loop();
        };
        quizOptionsContainer.appendChild(btn);
    });
    quizBox.style.display = 'block';
}

function loop() {
    if (!gameRunning) return;
    animFrame++;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Vẽ mặt đất
    ctx.strokeStyle = '#535353';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, 205);
    ctx.lineTo(canvas.width, 205);
    ctx.stroke();

    // Mây trôi
    cloudTimer++;
    if (cloudTimer > 120) {
        spawnCloud();
        cloudTimer = 0;
    }
    for (let i = clouds.length - 1; i >= 0; i--) {
        let c = clouds[i];
        c.x -= c.speed;
        ctx.fillStyle = '#e0e0e0';
        ctx.fillRect(c.x, c.y, 40, 12);
        if (c.x < -50) clouds.splice(i, 1);
    }

    // Chướng ngại vật
    obstacleTimer++;
    if (obstacleTimer > Math.floor(Math.random() * 60 + 90)) {
        spawnObstacle();
        obstacleTimer = 0;
    }

    for (let i = obstacles.length - 1; i >= 0; i--) {
        let obs = obstacles[i];
        obs.x -= gameSpeed;

        ctx.fillStyle = '#e52521';
        ctx.fillRect(obs.x, obs.y, obs.w, obs.h);

        // Kiểm tra va chạm
        if (
            dino.x < obs.x + obs.w &&
            dino.x + dino.w > obs.x &&
            dino.y < obs.y + obs.h &&
            dino.y + dino.h > obs.y
        ) {
            gameRunning = false;
            introOverlay.style.display = 'flex';
            document.querySelector('.title').innerText = "💀 GAME OVER";
            document.querySelector('.instructions').innerText = `Điểm số đạt được: ${score}\nSố câu đố giải được: ${puzzleSolvedCount}`;
            document.getElementById('start-btn').innerText = "🔄 CHƠI LẠI";
            return;
        }

        if (obs.x < -40) obstacles.splice(i, 1);
    }

    dino.update();
    dino.draw();

    score += 1;
    puzzleTriggerDistance++;
    document.getElementById('score').innerText = String(score).padStart(5, '0');

    // Cứ chạy được một quãng đường sẽ kích hoạt câu hỏi trí tuệ
    if (puzzleTriggerDistance > 450) {
        puzzleTriggerDistance = 0;
        triggerPuzzle();
        return;
    }

    // Tăng dần độ khó theo điểm số
    gameSpeed = 5 + Math.floor(score / 400);

    requestAnimationFrame(loop);
}
</script>
</body>
</html>
"""

components.html(html_code, height=350)
