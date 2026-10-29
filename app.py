import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Dino Chrome Puzzle Parkour - Large Edition", layout="centered")

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
            border: 4px solid #fff;
            border-radius: 8px;
            overflow: hidden;
            background: #f7f7f7;
        }
        canvas { display: block; }
        #ui-bar {
            position: absolute;
            top: 15px;
            left: 30px;
            right: 30px;
            display: flex;
            justify-content: space-between;
            font-size: 20px;
            font-weight: bold;
            color: #333;
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
            padding: 22px;
            width: 75%;
            text-align: center;
            z-index: 30;
            box-shadow: 0 0 25px rgba(255, 204, 0, 0.6);
        }
        #quiz-question {
            color: #ffcc00;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 16px;
        }
        .quiz-option {
            background: #333;
            color: #fff;
            border: 1px solid #666;
            padding: 10px 18px;
            margin: 6px;
            font-size: 15px;
            border-radius: 6px;
            cursor: pointer;
            font-family: 'Courier New', Courier, monospace;
        }
        .quiz-option:hover { background: #555; border-color: #ffcc00; }
        
        #intro-overlay {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.94);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 30px;
            z-index: 40;
        }
        .title {
            font-size: 38px;
            font-weight: bold;
            color: #ffcc00;
            margin-bottom: 12px;
            text-shadow: 2px 2px #ff0000;
        }
        .instructions {
            font-size: 15px;
            color: #ccc;
            max-width: 520px;
            line-height: 1.6;
            margin-bottom: 25px;
            background: rgba(255, 255, 255, 0.06);
            padding: 16px;
            border-radius: 8px;
            text-align: left;
        }
        #start-btn {
            padding: 12px 28px;
            font-size: 18px;
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
            margin-top: 14px;
            color: #aaa;
            font-size: 14px;
            text-align: center;
        }
    </style>
</head>
<body>

    <div id="game-wrapper">
        <div id="intro-overlay">
            <div class="title">🦖 DINO CHROME PUZZLE (BẢN LỚN)</div>
            <div class="instructions">
                🎮 <b>Cách chơi:</b><br>
                • Nhấn <b>Space / W / Mũi tên Lên</b> để nhảy.<br>
                • Vượt qua các chướng ngại vật xương rồng sắc nét.<br>
                • Giải các câu đố trí tuệ định kỳ trên đường chạy để ghi điểm!
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

        <!-- Tăng kích thước khung vẽ (Canvas) rộng 850px, cao 380px -->
        <canvas id="gameCanvas" width="850" height="380"></canvas>
    </div>

    <div id="controls-hint">
        🎮 <b>Nhảy:</b> Space / Mũi tên Lên | Tương tác giải câu đố bằng chuột.
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
let gameSpeed = 6;
let animFrame = 0;

const puzzleBank = [
    { q: "Số tiếp theo trong dãy là gì? 2, 4, 8, 16, ...", options: ["24", "32", "64"], answer: "32" },
    { q: "Cái gì có cổ nhưng không có đầu?", options: ["Cái áo", "Cái chai", "Cái quạt"], answer: "Cái áo" },
    { q: "5 quả táo lấy đi 2 quả, bạn còn mấy quả?", options: ["2 quả", "3 quả", "5 quả"], answer: "2 quả" },
    { q: "Lịch nào dài nhất trong năm?", options: ["Lịch treo tường", "Lịch tường", "Lịch Vạn Niên"], answer: "Lịch Vạn Niên" },
    { q: "Số nguyên tố nhỏ nhất là số mấy?", options: ["0", "1", "2"], answer: "2" },
    { q: "Bệnh gì bác sĩ phải bó tay?", options: ["Gãy tay", "Đau răng", "Ung thư"], answer: "Gãy tay" }
];

const dino = {
    x: 70, y: 260, w: 52, h: 58, vy: 0, gravity: 0.7, jumpPower: -12.5, grounded: true,
    update() {
        this.vy += this.gravity;
        this.y += this.vy;
        if (this.y > 260) {
            this.y = 260;
            this.vy = 0;
            this.grounded = true;
        }
    },
    draw() {
        ctx.fillStyle = '#535353';
        const px = this.x;
        const py = this.y;
        const s = 1.3; // Tỷ lệ phóng to nhân vật cho phù hợp màn hình lớn

        ctx.save();
        ctx.translate(px, py);
        ctx.scale(s, s);

        // 1. Phần đầu khủng long chuẩn tỉ lệ Chrome T-Rex[cite: 1]
        ctx.fillRect(24, 0, 16, 12);       
        ctx.fillRect(32, 8, 8, 4);      
        ctx.fillStyle = '#f7f7f7';                 
        ctx.fillRect(32, 3, 3, 3);

        // 2. Phần thân & tay
        ctx.fillStyle = '#535353';
        ctx.fillRect(12, 12, 16, 16);    
        ctx.fillRect(28, 16, 4, 5);     

        // 3. Phần đuôi
        ctx.fillRect(4, 14, 8, 8);
        ctx.fillRect(0, 16, 4, 6);
        ctx.fillRect(-4, 18, 4, 4);

        // 4. Chân khủng long
        if (animFrame % 20 < 10) {
            ctx.fillRect(12, 28, 4, 12);  
            ctx.fillRect(20, 28, 4, 8);   
        } else {
            ctx.fillRect(12, 28, 4, 8);   
            ctx.fillRect(20, 28, 4, 12);  
        }
        ctx.restore();
    }
};

let obstacles = [];
let clouds = [];

function spawnObstacle() {
    let type = Math.random() > 0.4 ? 'cactus' : 'bird';
    let obs = {
        x: canvas.width,
        y: type === 'cactus' ? 268 : 200,
        w: type === 'cactus' ? 28 : 42,
        h: type === 'cactus' ? 50 : 30,
        type: type
    };
    obstacles.push(obs);
}

function spawnCloud() {
    clouds.push({ x: canvas.width, y: Math.random() * 120 + 20, speed: 1.5 });
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
    gameSpeed = 6;
    obstacles = [];
    clouds = [];
    gameRunning = true;
    loop();
}

let obstacleTimer = 0;
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

    // Vẽ mặt đất
    ctx.strokeStyle = '#535353';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, 318);
    ctx.lineTo(canvas.width, 318);
    ctx.stroke();

    // Mây trôi
    cloudTimer++;
    if (cloudTimer > 100) {
        spawnCloud();
        cloudTimer = 0;
    }
    for (let i = clouds.length - 1; i >= 0; i--) {
        let c = clouds[i];
        c.x -= c.speed;
        ctx.fillStyle = '#d8d8d8';
        ctx.fillRect(c.x, c.y, 60, 16);
        if (c.x < -60) clouds.splice(i, 1);
    }

    // Sinh chướng ngại vật
    obstacleTimer++;
    if (obstacleTimer > Math.floor(Math.random() * 60 + 90)) {
        spawnObstacle();
        obstacleTimer = 0;
    }

    for (let i = obstacles.length - 1; i >= 0; i--) {
        let obs = obstacles[i];
        obs.x -= gameSpeed;

        ctx.fillStyle = '#535353';
        if (obs.type === 'cactus') {
            let cx = obs.x;
            let cy = obs.y;
            // Xương rồng sắc nét tỷ lệ lớn
            ctx.fillRect(cx + 8, cy + 6, 12, 44);
            ctx.fillRect(cx, cy + 16, 8, 12);
            ctx.fillRect(cx, cy + 10, 4, 8);
            ctx.fillRect(cx + 20, cy + 22, 8, 14);
            ctx.fillRect(cx + 24, cy + 16, 4, 8);
        } else {
            ctx.fillRect(obs.x, obs.y + (animFrame % 15 < 8 ? 0 : 8), obs.w, obs.h);
        }

        // Kiểm tra va chạm chuẩn xác theo kích thước mới
        if (
            dino.x < obs.x + obs.w - 6 &&
            dino.x + dino.w - 6 > obs.x &&
            dino.y < obs.y + obs.h - 6 &&
            dino.y + dino.h - 6 > obs.y
        ) {
            gameRunning = false;
            introOverlay.style.display = 'flex';
            document.querySelector('.title').innerText = "💀 GAME OVER";
            document.querySelector('.instructions').innerText = `Điểm số đạt được: ${score}\\nSố câu đố giải được: ${puzzleSolvedCount}`;
            document.getElementById('start-btn').innerText = "🔄 CHƠI LẠI";
            return;
        }

        if (obs.x < -60) obstacles.splice(i, 1);
    }

    dino.update();
    dino.draw();

    score += 1;
    puzzleTriggerDistance++;
    document.getElementById('score').innerText = String(score).padStart(5, '0');

    if (puzzleTriggerDistance > 480) {
        puzzleTriggerDistance = 0;
        triggerPuzzle();
        return;
    }

    gameSpeed = 6 + Math.floor(score / 350);

    requestAnimationFrame(loop);
}
</script>
</body>
</html>
"""

components.html(html_code, height=450)
