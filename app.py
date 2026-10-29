import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Dino T-Rex Super Buffs Edition", layout="wide")

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
            color: #0275d8;
            margin-bottom: 15px;
        }
        .instructions {
            font-size: 15px;
            color: #666;
            max-width: 600px;
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
            background: #0275d8;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }
        #start-btn:hover { background: #025aa5; transform: scale(1.05); }
    </style>
</head>
<body>

    <div id="game-wrapper">
        <div id="intro-overlay">
            <div class="title">🦖 DINO SUPER BUFFS EDITION</div>
            <div class="instructions">
                🎮 <b>Cách chơi:</b><br>
                • Nhấn <b>Space / W / Mũi tên Lên</b> để nhảy.<br>
                • <b>ĐA DẠNG THỰC PHẨM CHỨC NĂNG & VẬT PHẨM:</b><br>
                &nbsp;&nbsp;🚁 <b>Remote Trực Thăng:</b> Bay lượn trên trời trong 10s.<br>
                &nbsp;&nbsp;💊 <b>Viên Thuốc Khổng Lồ:</b> Phóng to gấp đôi, húc nát xương rồng.<br>
                &nbsp;&nbsp;🗡️ <b>Thánh Kiếm:</b> Vung kiếm chém xuyên mọi bẫy.<br>
                &nbsp;&nbsp;🛡️ <b>Giáp Năng Lượng:</b> Đỡ 1 lần dính bẫy an toàn.<br>
                • Trả lời các câu đố trí tuệ định kỳ để ghi điểm!
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

// Các loại Buff
let activeBuff = null; // 'heli', 'giant', 'sword', 'shield'
let buffTimer = 0;

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
        let currentHeight = activeBuff === 'giant' ? 110 : 60;
        if (activeBuff === 'heli') {
            this.y += (heliY - 40 - this.y) * 0.1;
            return;
        }

        this.vy += this.gravity;
        this.y += this.vy;
        if (this.y > groundY - currentHeight) {
            this.y = groundY - currentHeight;
            this.vy = 0;
            this.grounded = true;
        }
    },
    draw() {
        const px = this.x;
        const py = this.y;
        const s = activeBuff === 'giant' ? 2.6 : 1.4;

        ctx.save();
        ctx.translate(px, py);
        ctx.scale(s, s);

        if (activeBuff === 'giant') ctx.fillStyle = '#e52521';
        else if (activeBuff === 'sword') ctx.fillStyle = '#f0ad4e';
        else ctx.fillStyle = '#535353';

        // 1. Đầu khủng long T-Rex
        ctx.fillRect(20, 0, 18, 14);       
        ctx.fillRect(28, 9, 10, 5);      
        ctx.fillStyle = '#f7f7f7';
        ctx.fillRect(28, 3, 3, 3);

        // 2. Thân chính
        if (activeBuff === 'giant') ctx.fillStyle = '#e52521';
        else if (activeBuff === 'sword') ctx.fillStyle = '#f0ad4e';
        else ctx.fillStyle = '#535353';
        ctx.fillRect(10, 14, 18, 16);    

        // 3. Đôi tay vươn ra (Vẽ kiếm nếu có Buff Sword)
        ctx.fillRect(26, 18, 7, 3); 
        ctx.fillRect(31, 20, 2, 4); 
        if (activeBuff === 'sword') {
            ctx.fillStyle = '#333';
            ctx.fillRect(33, 10, 16, 5); // Thanh kiếm
            ctx.fillStyle = '#e52521';
            ctx.fillRect(33, 11, 4, 3); // Chuôi kiếm
        }

        // 4. Đuôi
        ctx.fillRect(2, 16, 8, 8);
        ctx.fillRect(-2, 18, 4, 6);
        ctx.fillRect(-6, 20, 4, 4);

        // 5. Chân
        if (activeBuff === 'heli') {
            ctx.fillRect(10, 30, 5, 8);  
            ctx.fillRect(18, 30, 5, 8);   
        } else if (animFrame % 18 < 9) {
            ctx.fillRect(10, 30, 5, 12);  
            ctx.fillRect(18, 30, 5, 7);   
        } else {
            ctx.fillRect(10, 30, 5, 7);   
            ctx.fillRect(18, 30, 5, 12);  
        }

        // Hào quang khi có giáp
        if (activeBuff === 'shield') {
            ctx.strokeStyle = '#0275d8';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(20, 20, 26, 0, Math.PI * 2);
            ctx.stroke();
        }

        ctx.restore();
    }
};

function drawHelicopter(x, y) {
    ctx.save();
    ctx.translate(x, y);

    ctx.fillStyle = '#333';
    let rotorOffset = (animFrame % 4) * 8;
    ctx.fillRect(-35 + rotorOffset, -20, 70 - rotorOffset * 2, 4);
    ctx.fillRect(-2, -16, 4, 6);

    ctx.fillStyle = '#2b5b54';
    ctx.beginPath();
    ctx.ellipse(0, 0, 38, 22, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#1a3a35';
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.fillStyle = '#8ce8ff';
    ctx.beginPath();
    ctx.arc(16, -4, 12, -Math.PI / 2, Math.PI / 2);
    ctx.fill();

    ctx.fillStyle = '#2b5b54';
    ctx.fillRect(-60, -6, 30, 10);
    ctx.fillRect(-65, -16, 8, 20);

    ctx.fillStyle = '#333';
    ctx.fillRect(-22, 20, 44, 4);
    ctx.fillRect(-12, 16, 4, 6);
    ctx.fillRect(10, 16, 4, 6);

    ctx.restore();
}

let obstacles = [];
let items = [];
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

function spawnItem(groundY) {
    let types = ['heli', 'giant', 'sword', 'shield'];
    let chosenType = types[Math.floor(Math.random() * types.length)];
    items.push({
        x: canvas.width,
        y: groundY - 75,
        w: 28,
        h: 28,
        type: chosenType
    });
}

function spawnCloud() {
    clouds.push({ x: canvas.width, y: Math.random() * 120 + 40, speed: 1.5 });
}

window.addEventListener('keydown', e => {
    if (!gameRunning || quizBox.style.display === 'block' || activeBuff === 'heli') return;
    if (e.key === ' ' || e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') {
        if (dino.grounded) {
            dino.vy = activeBuff === 'giant' ? -16 : dino.jumpPower;
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
    items = [];
    clouds = [];
    activeBuff = null;
    buffTimer = 0;
    gameRunning = true;
    loop();
}

let obstacleTimer = 0;
let itemTimer = 0;
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

    // Quản lý thời gian hiệu lực Buff
    if (buffTimer > 0) {
        buffTimer--;
        let secondsLeft = Math.ceil(buffTimer / 60);

        if (activeBuff === 'heli') {
            buffStatusEl.innerText = `🚁 LÁI TRỰC THĂNG BAY TRÊN TRỜI: ${secondsLeft}s`;
            buffStatusEl.style.color = "#0275d8";
            if (buffTimer > 60) targetHeliY = groundY - 220;
            else targetHeliY = groundY - 50;
            heliY += (targetHeliY - heliY) * 0.08;
        } else if (activeBuff === 'giant') {
            buffStatusEl.innerText = `💪 KHỔNG LỒ HÚC NÁT XƯƠNG RỒNG: ${secondsLeft}s`;
            buffStatusEl.style.color = "#e52521";
        } else if (activeBuff === 'sword') {
            buffStatusEl.innerText = `🗡️ THÁNH KIẾM CHÉM NÁT BẪY: ${secondsLeft}s`;
            buffStatusEl.style.color = "#f0ad4e";
        } else if (activeBuff === 'shield') {
            buffStatusEl.innerText = `🛡️ GIÁP NĂNG LƯỢNG BẢO VỆ (ĐỠ 1 ĐÒN)`;
            buffStatusEl.style.color = "#0275d8";
        }

        if (buffTimer <= 0) {
            activeBuff = null;
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

    // Sinh Vật Phẩm
    itemTimer++;
    if (itemTimer > 300 && !activeBuff) {
        spawnItem(groundY);
        itemTimer = 0;
    }

    for (let i = items.length - 1; i >= 0; i--) {
        let it = items[i];
        it.x -= gameSpeed;

        ctx.save();
        if (it.type === 'heli') {
            // Remote Trực Thăng
            ctx.fillStyle = '#333';
            ctx.fillRect(it.x, it.y, 22, 28);
            ctx.fillRect(it.x + 9, it.y - 8, 4, 8);
            ctx.fillStyle = '#00ffcc';
            ctx.fillRect(it.x + 3, it.y + 3, 16, 10);
            ctx.fillStyle = '#ff0000';
            ctx.fillRect(it.x + 6, it.y + 16, 10, 8);
        } else if (it.type === 'giant') {
            // Thuốc Khổng Lồ
            ctx.fillStyle = '#e52521';
            ctx.fillRect(it.x, it.y, 14, 20);
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(it.x + 14, it.y, 14, 20);
        } else if (it.type === 'sword') {
            // Thánh Kiếm
            ctx.fillStyle = '#f0ad4e';
            ctx.fillRect(it.x + 10, it.y, 6, 22);
            ctx.fillRect(it.x + 4, it.y + 16, 18, 4);
        } else if (it.type === 'shield') {
            // Giáp
            ctx.fillStyle = '#0275d8';
            ctx.fillRect(it.x + 2, it.y + 2, 22, 22);
        }
        ctx.restore();

        // Lụm Vật Phẩm
        let dWidth = activeBuff === 'giant' ? 100 : 56;
        let dHeight = activeBuff === 'giant' ? 110 : 60;
        if (
            dino.x < it.x + it.w &&
            dino.x + dWidth > it.x &&
            dino.y < it.y + it.h &&
            dino.y + dHeight > it.y
        ) {
            activeBuff = it.type;
            buffTimer = 600; // 10 giây hiệu lực
            if (it.type === 'heli') heliY = dino.y;
            items.splice(i, 1);
        }

        if (it.x < -40) items.splice(i, 1);
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

        // Kiểm tra va chạm theo từng Buff
        let checkW = activeBuff === 'giant' ? 90 : 48;
        let checkH = activeBuff === 'giant' ? 100 : 52;

        if (activeBuff !== 'heli') {
            if (
                dino.x < obs.x + obs.w - 6 &&
                dino.x + checkW > obs.x &&
                dino.y < obs.y + obs.h - 6 &&
                dino.y + checkH > obs.y
            ) {
                if (activeBuff === 'giant' || activeBuff === 'sword') {
                    // Húc nát hoặc chém nát bẫy!
                    obstacles.splice(i, 1);
                    score += 150;
                    continue;
                } else if (activeBuff === 'shield') {
                    // Đỡ 1 đòn dính bẫy
                    activeBuff = null;
                    buffTimer = 0;
                    buffStatusEl.innerText = "TRẠNG THÁI: CHẠY BỘ";
                    buffStatusEl.style.color = "#535353";
                    obstacles.splice(i, 1);
                    continue;
                } else {
                    gameRunning = false;
                    introOverlay.style.display = 'flex';
                    document.querySelector('.title').innerText = "💀 GAME OVER";
                    document.querySelector('.instructions').innerText = `Điểm số đạt được: ${score}\nSố câu đố giải được: ${puzzleSolvedCount}`;
                    document.getElementById('start-btn').innerText = "🔄 CHƠI LẠI";
                    return;
                }
            }
        }

        if (obs.x < -70) obstacles.splice(i, 1);
    }

    dino.update(groundY);
    dino.draw();

    if (activeBuff === 'heli') {
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
