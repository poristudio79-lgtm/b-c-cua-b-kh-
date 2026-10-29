import streamlit as st

st.set_page_config(page_title="Chrome T-Rex: Boss Xương Rồng", layout="centered")

# Mã nguồn HTML/JS của game được nhúng gọn gàng trong Streamlit
game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chrome T-Rex: Boss Xương Rồng & Máy Bay</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        * {
            box-sizing: border-box;
            user-select: none;
        }
        body {
            margin: 0;
            padding: 0;
            background: #f7f7f7;
            font-family: 'Press Start 2P', monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            overflow: hidden;
        }
        h1 {
            font-size: 14px;
            color: #535353;
            margin-bottom: 10px;
            text-align: center;
        }
        .game-container {
            position: relative;
            width: 800px;
            height: 250px;
            background: #ffffff;
            border-bottom: 2px solid #535353;
            overflow: hidden;
        }
        canvas {
            display: block;
            background: #ffffff;
        }
        .ui-panel {
            width: 800px;
            display: flex;
            justify-content: space-between;
            padding: 5px 10px;
            font-size: 10px;
            color: #535353;
        }
        #boss-modal {
            display: none;
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.85);
            color: #fff;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
            z-index: 10;
            text-align: center;
        }
        #boss-modal h2 {
            color: #ff4757;
            font-size: 13px;
            margin-bottom: 8px;
        }
        .boss-status {
            font-size: 9px;
            margin-bottom: 12px;
            color: #ffa502;
        }
        #question-box {
            font-size: 10px;
            margin-bottom: 15px;
            line-height: 1.6;
            max-width: 700px;
        }
        .answers-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            width: 100%;
            max-width: 600px;
        }
        .answer-btn {
            background: #2ed573;
            border: none;
            color: #fff;
            padding: 10px;
            font-family: 'Press Start 2P', monospace;
            font-size: 8px;
            cursor: pointer;
            border-radius: 4px;
            transition: 0.2s;
        }
        .answer-btn:hover {
            background: #26af5f;
        }
        #notification {
            position: absolute;
            top: 15px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(53, 53, 53, 0.9);
            color: #fff;
            padding: 8px 15px;
            font-size: 8px;
            border-radius: 20px;
            display: none;
            z-index: 5;
        }
    </style>
</head>
<body>

    <h1>CHROME T-REX: ĐẤU BOSS XƯƠNG RỒNG (1000 MÉT)</h1>
    <div class="game-container">
        <div id="notification">ĐÃ LỤM REMOTE! MÁY BAY XUẤT PHÁT (10s)!</div>
        
        <div id="boss-modal">
            <h2>ĐẠT 1000 MÉT - ĐẤU BOSS XƯƠNG RỒNG!</h2>
            <div class="boss-status" id="boss-hp-text">Máu Boss Xương Rồng: 3 / 3 (Cần 3 câu đúng liên tiếp)</div>
            <div id="question-box">Đang tải câu hỏi...</div>
            <div class="answers-grid" id="answers-container"></div>
        </div>

        <canvas id="gameCanvas" width="800" height="250"></canvas>
    </div>
    
    <div class="ui-panel">
        <div>HI: <span id="highScore">00000</span> M</div>
        <div>MET: <span id="currentScore">00000</span> M</div>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const highScoreEl = document.getElementById("highScore");
        const currentScoreEl = document.getElementById("currentScore");
        const bossModal = document.getElementById("boss-modal");
        const bossHpText = document.getElementById("boss-hp-text");
        const questionBox = document.getElementById("question-box");
        const answersContainer = document.getElementById("answers-container");
        const notificationEl = document.getElementById("notification");

        let gameState = "START";
        let score = 0;
        let highScore = localStorage.getItem("trex_highscore") || 0;
        highScoreEl.innerText = String(highScore).padStart(5, '0');

        let gameSpeed = 5;
        let gravity = 0.6;

        let trex = {
            x: 50,
            y: 175,
            width: 34,
            height: 36,
            vy: 0,
            jumpPower: -11,
            grounded: true,
            isFlying: false,
            flyTimer: 0,
            isCrying: false
        };

        let obstacles = [];
        let items = []; 
        let clouds = [];

        const questions = [
            { q: "Thủ đô của Việt Nam là gì?", answers: ["TP. Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Hải Phòng"], correct: 1 },
            { q: "Kết quả của phép tính: 15 + 25 * 2 là bao nhiêu?", answers: ["80", "55", "65", "90"], correct: 2 },
            { q: "Hành tinh nào gần mặt trời nhất trong hệ Mặt Trời?", answers: ["Sao Kim", "Sao Hỏa", "Sao Thủy", "Trái Đất"], correct: 2 },
            { q: "Ngôn ngữ lập trình nào phổ biến nhất cho web trên trình duyệt?", answers: ["Python", "C++", "JavaScript", "Java"], correct: 2 },
            { q: "Nước nào có diện tích lớn nhất thế giới?", answers: ["Trung Quốc", "Mỹ", "Canada", "Nga"], correct: 3 },
            { q: "Đỉnh núi cao nhất Việt Nam (nóc nhà Đông Dương) tên là gì?", answers: ["Fansipan", "Pu Si Lung", "Lao Than", "Ngọc Linh"], correct: 0 }
        ];
        let bossHp = 3;
        let currentQuestion = null;

        for (let i = 0; i < 3; i++) {
            clouds.push({ x: Math.random() * 800, y: Math.random() * 80 + 20, speed: 1 });
        }

        window.addEventListener("keydown", (e) => {
            if (e.code === "Space" || e.code === "ArrowUp") {
                if (gameState === "START") {
                    startGame();
                } else if (gameState === "PLAYING" && trex.grounded && !trex.isFlying) {
                    trex.vy = trex.jumpPower;
                    trex.grounded = false;
                } else if (gameState === "GAMEOVER" || gameState === "VICTORY") {
                    resetGame();
                    startGame();
                }
            }
        });

        canvas.addEventListener("click", () => {
            if (gameState === "START") {
                startGame();
            } else if (gameState === "PLAYING" && trex.grounded && !trex.isFlying) {
                trex.vy = trex.jumpPower;
                trex.grounded = false;
            } else if (gameState === "GAMEOVER" || gameState === "VICTORY") {
                resetGame();
                startGame();
            }
        });

        function startGame() {
            gameState = "PLAYING";
            score = 0;
            gameSpeed = 5;
            obstacles = [];
            items = [];
            trex.isFlying = false;
            trex.flyTimer = 0;
            trex.isCrying = false;
        }

        function resetGame() {
            trex.y = 175;
            trex.vy = 0;
            trex.grounded = true;
            trex.isFlying = false;
            trex.isCrying = false;
            bossHp = 3;
        }

        let spawnTimer = 0;
        function handleSpawns() {
            spawnTimer++;
            if (spawnTimer > Math.max(50, 120 - Math.floor(score / 100))) {
                spawnTimer = 0;
                let typeRand = Math.random();
                if (typeRand < 0.2 && score < 950) {
                    items.push({ x: 800, y: 150, width: 22, height: 22, type: 'remote' });
                } else {
                    let isBird = Math.random() > 0.7 && score > 300;
                    obstacles.push({
                        x: 800,
                        y: isBird ? 135 : 175,
                        width: isBird ? 30 : 20,
                        height: isBird ? 24 : 36,
                        isBird: isBird
                    });
                }
            }
        }

        function triggerAirplane() {
            trex.isFlying = true;
            trex.flyTimer = 10 * 60;
            notificationEl.style.display = "block";
            setTimeout(() => { notificationEl.style.display = "none"; }, 3000);
        }

        function startBossFight() {
            gameState = "BOSS_FIGHT";
            bossHp = 3;
            bossModal.style.display = "flex";
            loadNewQuestion();
        }

        function loadNewQuestion() {
            bossHpText.innerText = `Máu Boss Xương Rồng: ${bossHp} / 3 (Cần đúng liên tiếp)`;
            if (bossHp <= 0) {
                bossModal.style.display = "none";
                gameState = "VICTORY";
                return;
            }
            currentQuestion = questions[Math.floor(Math.random() * questions.length)];
            questionBox.innerText = currentQuestion.q;
            answersContainer.innerHTML = "";
            currentQuestion.answers.forEach((ans, index) => {
                let btn = document.createElement("button");
                btn.className = "answer-btn";
                btn.innerText = `${index + 1}. ${ans}`;
                btn.onclick = () => checkAnswer(index);
                answersContainer.appendChild(btn);
            });
        }

        function checkAnswer(selectedIndex) {
            if (selectedIndex === currentQuestion.correct) {
                bossHp--;
                loadNewQuestion();
            } else {
                alert("Trả lời sai! Mất chuỗi đúng, thử lại câu hỏi tiếp theo để hạ Boss!");
                loadNewQuestion();
            }
        }

        function update() {
            if (gameState === "PLAYING") {
                score += 0.2;
                currentScoreEl.innerText = String(Math.floor(score)).padStart(5, '0');

                if (Math.floor(score) >= 1000 && score < 1005) {
                    startBossFight();
                    return;
                }

                gameSpeed = 5 + Math.floor(score / 200);

                if (trex.isFlying) {
                    trex.flyTimer--;
                    trex.y = 80;
                    trex.vy = 0;
                    if (trex.flyTimer <= 0) { trex.isFlying = false; }
                } else {
                    trex.vy += gravity;
                    trex.y += trex.vy;
                    if (trex.y > 175) {
                        trex.y = 175;
                        trex.vy = 0;
                        trex.grounded = true;
                    }
                }

                clouds.forEach(c => {
                    c.x -= c.speed;
                    if (c.x < -50) c.x = 850;
                });

                handleSpawns();

                for (let i = obstacles.length - 1; i >= 0; i--) {
                    obstacles[i].x -= gameSpeed;

                    if (!trex.isFlying &&
                        trex.x < obstacles[i].x + obstacles[i].width &&
                        trex.x + trex.width > obstacles[i].x &&
                        trex.y < obstacles[i].y + obstacles[i].height &&
                        trex.y + trex.height > obstacles[i].y) {
                        gameState = "GAMEOVER";
                        trex.isCrying = true;
                        if (Math.floor(score) > highScore) {
                            highScore = Math.floor(score);
                            localStorage.setItem("trex_highscore", highScore);
                            highScoreEl.innerText = String(highScore).padStart(5, '0');
                        }
                    }

                    if (obstacles[i].x < -50) { obstacles.splice(i, 1); }
                }

                for (let i = items.length - 1; i >= 0; i--) {
                    items[i].x -= gameSpeed;
                    if (
                        trex.x < items[i].x + items[i].width &&
                        trex.x + trex.width > items[i].x &&
                        trex.y < items[i].y + items[i].height &&
                        trex.y + trex.height > items[i].y
                    ) {
                        triggerAirplane();
                        items.splice(i, 1);
                        continue;
                    }
                    if (items[i] && items[i].x < -50) { items.splice(i, 1); }
                }
            }
        }

        function drawTrex(x, y, isFlying, isCrying) {
            ctx.fillStyle = "#535353";
            if (isFlying) {
                ctx.fillStyle = "#e17055";
                ctx.fillRect(x - 10, y - 5, 55, 20);
                ctx.fillStyle = "#74b9ff";
                ctx.fillRect(x + 20, y - 10, 15, 10);
                ctx.fillStyle = "#535353";
                ctx.fillRect(x + 5, y + 2, 20, 18);
                return;
            }

            ctx.fillRect(x + 10, y + 10, 18, 16);
            ctx.fillRect(x + 18, y, 14, 14);
            ctx.fillRect(x + 26, y + 6, 6, 6);
            
            if (isCrying) {
                ctx.fillStyle = "#0984e3";
                ctx.fillRect(x + 26, y + 4, 3, 5);
            } else {
                ctx.fillStyle = "#ffffff";
                ctx.fillRect(x + 26, y + 3, 3, 3);
            }

            ctx.fillStyle = "#535353";
            ctx.fillRect(x + 24, y + 13, 4, 3);
            ctx.fillRect(x + 12, y + 26, 4, 10);
            ctx.fillRect(x + 20, y + 26, 4, 10);
            ctx.fillRect(x + 2, y + 14, 10, 4);
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = "#d3d3d3";
            clouds.forEach(c => {
                ctx.fillRect(c.x, c.y, 30, 10);
                ctx.fillRect(c.x + 8, c.y - 5, 15, 6);
            });

            ctx.strokeStyle = "#535353";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(0, 212);
            ctx.lineTo(800, 212);
            ctx.stroke();

            obstacles.forEach(obs => {
                ctx.fillStyle = "#535353";
                ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
            });

            items.forEach(it => {
                ctx.fillStyle = "#0984e3";
                ctx.fillRect(it.x, it.y, it.width, it.height);
                ctx.fillStyle = "#fff";
                ctx.fillRect(it.x + 7, it.y + 5, 8, 12);
            });

            drawTrex(trex.x, trex.y, trex.isFlying, trex.isCrying);

            if (gameState === "START") {
                ctx.fillStyle = "#535353";
                ctx.font = "11px 'Press Start 2P'";
                ctx.textAlign = "center";
                ctx.fillText("NHẤN PHÍM CÁCH HOẶC CHẠM ĐỂ BẮT ĐẦU", canvas.width / 2, canvas.height / 2);
            } else if (gameState === "GAMEOVER") {
                ctx.fillStyle = "#ff4757";
                ctx.font = "13px 'Press Start 2P'";
                ctx.textAlign = "center";
                ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 20);
                ctx.fillStyle = "#535353";
                ctx.font = "8px 'Press Start 2P'";
                ctx.fillText("Nhấn phím Cách để chơi lại", canvas.width / 2, canvas.height / 2 + 10);
            } else if (gameState === "VICTORY") {
                ctx.fillStyle = "#2ed573";
                ctx.font = "13px 'Press Start 2P'";
                ctx.textAlign = "center";
                ctx.fillText("CHIẾN THẮNG BOSS XƯƠNG RỒNG!", canvas.width / 2, canvas.height / 2 - 20);
                ctx.fillStyle = "#535353";
                ctx.font = "8px 'Press Start 2P'";
                ctx.fillText("Bạn đã xuất sắc vượt qua 1000 mét và hạ Boss!", canvas.width / 2, canvas.height / 2 + 5);
                ctx.fillText("Nhấn phím Cách để tiếp tục chơi", canvas.width / 2, canvas.height / 2 + 25);
            }
        }

        function loop() {
            update();
            draw();
            requestAnimationFrame(loop);
        }

        loop();
    </script>
</body>
</html>
"""

st.components.v1.html(game_html, height=350, scrolling=False)
