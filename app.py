import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Dino T-Rex Helicopter Remote Edition", layout="wide")

html_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        html, body {
            width: 100%;
            height: 100%;
            background-color: #f7f7f7;
            color: #333;
            font-family: 'Courier New', Courier, monospace;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        #game-wrapper {
            position: relative;
            width: 100vw;
            height: 100vh;
            background: #f7f7f7;
            overflow: hidden;
        }
        canvas {
            display: block;
            width: 100%;
            height: 100%;
        }
        #ui-bar {
            position: absolute;
            top: 20px;
            left: 30px;
            right: 30px;
            display: flex;
            justify-content: space-between;
            font-size: 20px;
            font-weight: bold;
            color: #535353;
            z-index: 10;
        }
        #buff-status {
            position: absolute;
            top: 60px;
            left: 30px;
            font-size: 18px;
            font-weight: bold;
            color: #0275d8;
            z-index: 10;
        }
        #quiz-box {
            display: none;
            position: absolute;
            top: 40%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(30, 30, 30, 0.96);
            border: 3px solid #ffcc00;
            border-radius: 10px;
            padding: 25px;
            width: 80%;
            max-width: 600px;
            text-align: center;
            z-index: 30;
            box-shadow: 0 0 30px rgba(0,0,0,0.5);
            color: #fff;
        }
        #quiz-question {
            color: #ffcc00;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .quiz-option {
            background: #444;
            color: #fff;
            border: 1px solid #666;
            padding: 12px 20px;
            margin: 8px;
            font-size: 16px;
            border-radius: 6px;
            cursor: pointer;
            font-family: 'Courier New', Courier, monospace;
        }
        .quiz-option:hover { background: #666; border-color: #ffcc00; }
        
        #intro-overlay {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(247, 247, 247, 0.95);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 30px;
            z-index: 40;
            color: #535353;
        }
        .title {
            font-size: 40px;
            font-weight: bold;
            color: #535353;
            margin-bottom: 15px;
        }
        .instructions {
            font-size: 15px;
            color: #666;
            max-width: 580px;
            line-height: 1.6;
            margin-bottom: 30px;
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #ddd;
            text-align: left;
        }
        #start-btn {
            padding: 14px 36px;
            font-size: 20px;
            font-weight: bold;
            font-family: 'Courier New', Courier, monospace;
            color: #fff;
            background: #535353;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }
        #start-btn:hover { background: #333; transform: scale(1.05); }
    </style>
</head>
<body>

    <div id="game-wrapper">
        <div id="intro-overlay">
            <div class="title">🦖 DINO HELICOPTER REMOTE</div>
            <div class="instructions">
                🎮 <b>Cách chơi:</b><br>
                • Nhấn <b>Space / W / Mũi tên Lên</b> để nhảy vượt chướng ngại vật.<br>
                • 📡 <b>Lụm Remote Điều Khiển:</b> Khủng long sẽ leo lên trực thăng bay vút lên trời trong <b>10 giây</b> và tự động hạ cánh an toàn!<br>
                • Trả lời các câu đố trí tuệ định kỳ trên đường chạy để tích lũy điểm!
            </div>
            <button id="start-btn" onclick="startGame()">▶️ CHƠI NGAY</button>
        </div>

        <div id="ui-bar">
            <div>ĐIỂM: <span id="score">00000</span></div>
            <div>CÂU HỎI ĐÃ GIẢI: <span id="puzzle-count">0</span></div>
        </div>

        <div id="buff-status">TRẠNG THÁI: CHẠY BỘ</div>

        <div id="quiz-box">
            <div id="quiz-question">Đang tải câu hỏi...</div>
            <div id="quiz-options-container"></div>
        </div>

        <canvas id="gameCanvas"></canvas>
    </div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const introOverlay = document.getElementById('intro-overlay');
const quizBox = document.getElementById('quiz-box');
const quizQuestion = document.getElementById('quiz-question');
const quizOptionsContainer = document.getElementById('quiz-options-container');
const buffStatusEl = document.getElementById('buff-status');

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

let gameRunning = false;
let score = 0;
let puzzleSolvedCount = 0;
let gameSpeed = 7;
let animFrame = 0;

// Trạng thái bay bằng Trực Thăng
let isFlying = false;
let flyTimer = 0; // 600 frames = 10 giây
let heliY = 0;
let targetHeliY = 0;

const puzzleBank = [
    { q: "Số tiếp theo trong dãy là gì? 2, 4, 8, 16, ...", options: ["24", "32", "64"], answer: "32" },
    { q: "Cái gì có cổ nhưng không có đầu?", options: ["Cái áo", "Cái chai", "Cái quạt"], answer: "Cái áo" },
    { q: "5 quả táo lấy đi 2 quả, bạn còn mấy quả?", options: ["2 quả", "3 quả", "5 quả"], answer: "2 quả" },
    { q: "Lịch nào dài nhất trong năm?", options: ["Lịch treo tường", "Lịch tường", "Lịch Vạn Niên"], answer: "Lịch Vạn Niên" },
    { q: "Số nguyên tố nhỏ nhất là số mấy?", options: ["0", "1", "2"], answer: "2" },
    { q: "Bệnh gì bác sĩ phải bó tay?", options: ["Gãy tay", "Đau răng", "Ung thư"], answer: "Gãy tay" }
];

const dino = {
    x: 80, y: 0, w: 56, h: 60, vy: 0, gravity: 0.8, jumpPower: -14, grounded: true,
    update(groundY) {
        if (isFlying) {
            // Khi đang bay trực thăng
            this.y += (heliY - 40 - this.y) * 0.1;
            return;
        }

        this.vy += this.gravity;
        this.y += this.vy;
        if (this.y > groundY - this.h) {
            this.y = groundY - this.h;
            this.vy = 0;
            this.grounded = true;
        }
    },
    draw() {
        const px = this.x;
        const py = this.y;
        const s = 1.4;

        ctx.save();
        ctx.translate(px, py);
        ctx.scale(s, s);

        ctx.fillStyle = '#535353';

        // 1. Đầu khủng long T-Rex
        ctx.fillRect(20, 0, 18, 14);       
        ctx.fillRect(28, 9, 10, 5);      
        ctx.fillStyle = '#f7f7f7'; // Mắt
        ctx.fillRect(28, 3, 3, 3);

        // 2. Thân chính
        ctx.fillStyle = '#535353';
        ctx.fillRect(10, 14, 18, 16);    

        // 3. Đôi tay vươn ra
        ctx.fillRect(26, 18, 7, 3); 
        ctx.fillRect(31, 20, 2, 4); 

        // 4. Đuôi
        ctx.fillRect(2, 16, 8, 8);
        ctx.fillRect(-2, 18, 4, 6);
        ctx.fillRect(-6, 20, 4, 4);

        // 5. Chân
        if (isFlying) {
            ctx.fillRect(10, 30, 5, 8);  
            ctx.fillRect(18, 30, 5, 8);   
        } else if (animFrame % 18 < 9) {
            ctx.fillRect(10, 30, 5, 12);  
            ctx.fillRect(18, 30, 5, 7);   
        } else {
            ctx.fillRect(10, 30, 5, 7);   
            ctx.fillRect(18, 30, 5, 12);  
        }

        ctx.restore();
    }
};

function drawHelicopter(x, y) {
    ctx.save();
    ctx.translate(x, y);

    // Bánh quạt quay
    ctx.fillStyle = '#333';
    let rotorOffset = (animFrame % 4) * 8;
    ctx.fillRect(-35 + rotorOffset, -20, 70 - rotorOffset * 2, 4);

    // Trục cánh quạt
    ctx.fillRect(-2, -16, 4, 6);

    // Thân trực thăng
    ctx.fillStyle = '#2b5b54'; // Màu xanh quân sự mờ
    ctx.beginPath();
    ctx.ellipse(0, 0, 38, 22, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#1a3a35';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Cửa kính trực thăng
    ctx.fillStyle = '#8ce8ff';
    ctx.beginPath();
    ctx.arc(16, -4, 12, -Math.PI / 2, Math.PI / 2);
    ctx.fill();

    // Đuôi trực thăng
    ctx.fillStyle = '#2b5b54';
    ctx.fillRect(-60, -6, 30, 10);
    ctx.fillRect(-65, -16, 8, 20);

    // Chân hạ cánh
    ctx.fillStyle = '#333';
    ctx.fillRect(-22, 20, 44, 4);
    ctx.fillRect(-12, 16, 4, 6);
    ctx.fillRect(10, 16, 4, 6);

    ctx.restore();
}

let obstacles = [];
let remotes = [];
let clouds = [];

function spawnObstacle(groundY) {
    let type = Math.random() > 0.4 ? 'cactus' : 'bird';
    let obs = {
        x: canvas.width,
        y: type === 'cactus' ? groundY - 52 : groundY - 110,
        w: type === 'cactus' ? 32 : 46,
        h: type === 'cactus' ? 52 : 32,
        type: type
    };
    obstacles.push(obs);
}

function spawnRemote(groundY) {
    remotes.push({
        x: canvas.width,
        y: groundY - 70,
        w: 26,
        h: 30
    });
}

function spawnCloud() {
    clouds.push({ x: canvas.width, y: Math.random() * 120 + 40, speed: 1.5 });
}

window.addEventListener('keydown', e => {
    if (!gameRunning || quizBox.style.display === 'block' || isFlying) return;
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
    gameSpeed = 7;
    obstacles = [];
    remotes = [];
    clouds = [];
    isFlying = false;
    flyTimer = 0;
    gameRunning = true;
    loop();
}

let obstacleTimer = 0;
let remoteTimer = 0;
let cloudTimer = 0;
let puzzleTriggerDistance = 0;

function triggerPuzzle() {
    gameRunning = false; 
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

    const groundY = canvas.height - 80;

    // Quản lý Trạng thái Trực Thăng 10 Giây
    if (isFlying) {
        flyTimer--;
        let secondsLeft = Math.ceil(flyTimer / 60);
        buffStatusEl.innerText = `🚁 ĐANG LÁI TRỰC THĂNG BAY TRÊN TRỜI: ${secondsLeft}s`;
        buffStatusEl.style.color = "#0275d8";

        if (flyTimer > 60) {
            targetHeliY = groundY - 220; // Bay trên cao
        } else {
            targetHeliY = groundY - 50; // Từ từ hạ cánh 1 giây cuối
        }
        heliY += (targetHeliY - heliY) * 0.08;

        if (flyTimer <= 0) {
            isFlying = false;
            buffStatusEl.innerText = "TRẠNG THÁI: CHẠY BỘ";
            buffStatusEl.style.color = "#535353";
        }
    }

    // Đường mặt đất
    ctx.strokeStyle = '#535353';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, groundY);
    ctx.lineTo(canvas.width, groundY);
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
        ctx.fillStyle = '#d0d0d0';
        ctx.fillRect(c.x, c.y, 65, 18);
        if (c.x < -70) clouds.splice(i, 1);
    }

    // Sinh Remote Điều Khiển Trực Thăng
    remoteTimer++;
    if (remoteTimer > 350 && !isFlying) {
        spawnRemote(groundY);
        remoteTimer = 0;
    }

    for (let i = remotes.length - 1; i >= 0; i--) {
        let rm = remotes[i];
        rm.x -= gameSpeed;

        // Vẽ chiếc Remote Điều Khiển
        ctx.save();
        ctx.fillStyle = '#333';
        ctx.fillRect(rm.x, rm.y, 22, 28);
        // Anten
        ctx.fillRect(rm.x + 9, rm.y - 8, 4, 8);
        // Màn hình remote
        ctx.fillStyle = '#00ffcc';
        ctx.fillRect(rm.x + 3, rm.y + 3, 16, 10);
        // Nút bấm đỏ
        ctx.fillStyle = '#ff0000';
        ctx.fillRect(rm.x + 6, rm.y + 16, 10, 8);
        ctx.restore();

        // Lụm Remote
        if (
            dino.x < rm.x + rm.w &&
            dino.x + dino.w > rm.x &&
            dino.y < rm.y + rm.h &&
            dino.y + dino.h > rm.y
        ) {
            isFlying = true;
            flyTimer = 600; // 10 giây (600 khung hình)
            heliY = dino.y;
            remotes.splice(i, 1);
        }

        if (rm.x < -40) remotes.splice(i, 1);
    }

    // Sinh chướng ngại vật
    obstacleTimer++;
    if (obstacleTimer > Math.floor(Math.random() * 60 + 80)) {
        spawnObstacle(groundY);
        obstacleTimer = 0;
    }

    for (let i = obstacles.length - 1; i >= 0; i--) {
        let obs = obstacles[i];
        obs.x -= gameSpeed;

        ctx.fillStyle = '#535353';
        if (obs.type === 'cactus') {
            let cx = obs.x;
            let cy = obs.y;
            ctx.fillRect(cx + 10, cy + 6, 12, 46);
            ctx.fillRect(cx, cy + 18, 10, 12);
            ctx.fillRect(cx, cy + 12, 4, 8);
            ctx.fillRect(cx + 22, cy + 24, 10, 14);
            ctx.fillRect(cx + 28, cy + 18, 4, 8);
        } else {
            ctx.fillRect(obs.x, obs.y + (animFrame % 14 < 7 ? 0 : 8), obs.w, obs.h);
        }

        // Kiểm tra va chạm (Nếu đang bay trực thăng thì bỏ qua mọi va chạm)
        if (!isFlying) {
            if (
                dino.x < obs.x + obs.w - 8 &&
                dino.x + dino.w - 8 > obs.x &&
                dino.y < obs.y + obs.h - 8 &&
                dino.y + dino.h - 8 > obs.y
            ) {
                gameRunning = false;
                introOverlay.style.display = 'flex';
                document.querySelector('.title').innerText = "💀 GAME OVER";
                document.querySelector('.instructions').innerText = `Điểm số đạt được: ${score}\nSố câu đố giải được: ${puzzleSolvedCount}`;
                document.getElementById('start-btn').innerText = "🔄 CHƠI LẠI";
                return;
            }
        }

        if (obs.x < -70) obstacles.splice(i, 1);
    }

    dino.update(groundY);
    dino.draw();

    if (isFlying) {
        drawHelicopter(dino.x + 20, heliY);
    }

    score += 1;
    puzzleTriggerDistance++;
    document.getElementById('score').innerText = String(score).padStart(5, '0');

    if (puzzleTriggerDistance > 500) {
        puzzleTriggerDistance = 0;
        triggerPuzzle();
        return;
    }

    gameSpeed = 7 + Math.floor(score / 400);

    requestAnimationFrame(loop);
}
</script>
</body>
</html>
"""

components.html(html_code, height=700)
