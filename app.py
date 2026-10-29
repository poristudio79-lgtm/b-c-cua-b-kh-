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
            font-size: 16px;
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
        /* Màn hình Boss / Trắc nghiệm */
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
            font-size: 14px;
            margin-bottom: 10px;
        }
        .boss-status {
            font-size: 10px;
            margin-bottom: 15px;
            color: #ffa502;
        }
        #question-box {
            font-size: 11px;
            margin-bottom: 15px;
            line-height: 1.5;
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
            font-size: 9px;
            cursor: pointer;
            border-radius: 4px;
            transition: 0.2s;
        }
        .answer-btn:hover {
            background: #26af5f;
        }
        /* Thông báo trạng thái máy bay */
        #notification {
            position: absolute;
            top: 15px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(53, 53, 53, 0.9);
            color: #fff;
            padding: 8px 15px;
            font-size: 9px;
            border-radius: 20px;
            display: none;
            z-index: 5;
        }
    </style>
</head>
<body>

    <h1>CHROME T-REX: BOSS XƯƠNG RỒNG & MÁY BAY</h1>
    <div class="game-container">
        <div id="notification">ĐÃ LỤM REMOTE! MÁY BAY XUẤT PHÁT (10s)!</div>
        
        <!-- Modal đánh boss / Trả lời câu hỏi -->
        <div id="boss-modal">
            <h2>ĐẤU BOSS XƯƠNG RỒNG!</h2>
            <div class="boss-status" id="boss-hp-text">Máu Boss Xương Rồng: 3 / 3</div>
            <div id="question-box">Đang tải câu hỏi...</div>
            <div class="answers-grid" id="answers-container"></div>
        </div>

        <canvas id="gameCanvas" width="800" height="250"></canvas>
    </div>
    
    <div class="ui-panel">
        <div>HI: <span id="highScore">00000</span></div>
        <div>SC: <span id="currentScore">00000</span></div>
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

        // Trạng thái Game
        let gameState = "START"; // START, PLAYING, BOSS_FIGHT, GAMEOVER
        let score = 0;
        let highScore = localStorage.getItem("trex_highscore") || 0;
        highScoreEl.innerText = String(highScore).padStart(5, '0');

        let gameSpeed = 5;
        let gravity = 0.6;

        // Nhân vật T-Rex
        let trex = {
            x: 50,
            y: 180,
            width: 30,
            height: 40,
            vy: 0,
            jumpPower: -11,
            grounded: true,
            isFlying: false,
            flyTimer: 0
        };

        let obstacles = [];
        let items = []; // Remote
        let clouds = [];
        let groundX = 0;

        // Câu hỏi đấu Boss
        const questions = [
        {
            q: "Thủ đô của Việt Nam là gì?",
            answers: ["TP. Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Hải Phòng"],
            correct: 1
        },
        {
            q: "Kết quả của phép tính: 15 + 25 * 2 là bao nhiêu?",
            answers: ["80", "55", "65", "90"],
            correct: 2
        },
        {
            q: "Hành tinh nào gần mặt trời nhất trong hệ Mặt Trời?",
            answers: ["Sao Kim", "Sao Hỏa", "Sao Thủy", "Trái Đất"],
            correct: 2
        },
        {
            q: "Ngôn ngữ lập trình nào phổ biến nhất cho web trên trình duyệt?",
            answers: ["Python", "C++", "JavaScript", "Java"],
            correct: 2
        },
        {
            q: "Nước nào có diện tích lớn nhất thế giới?",
            answers: ["Trung Quốc", "Mỹ", "Canada", "Nga"],
            correct: 3
        }
        ];
        let bossHp = 3;
        let currentQuestion = null;

        // Khởi tạo mây phong cảnh
        for (let i = 0; i < 3; i++) {
            clouds.push({ x: Math.random() * 800, y: Math.random() * 80 + 20, speed: 1 });
        }

        // Bắt sự kiện bàn phím
        window.addEventListener("keydown", (e) => {
            if (e.code === "Space" || e.code === "ArrowUp") {
                if (gameState === "START") {
                    startGame();
                } else if (gameState === "PLAYING" && trex.grounded && !trex.isFlying) {
                    trex.vy = trex.jumpPower;
                    trex.grounded = false;
                } else if (gameState === "GAMEOVER") {
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
            } else if (gameState === "GAMEOVER") {
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
        }

        function resetGame() {
            trex.y = 180;
            trex.vy = 0;
            trex.grounded = true;
            trex.isFlying = false;
            bossHp = 3;
        }

        // Spawn chướng ngại vật hoặc remote
        let spawnTimer = 0;
        function handleSpawns() {
            spawnTimer++;
            if (spawnTimer > Math.max(50, 120 - Math.floor(score / 100))) {
                spawnTimer = 0;
                let typeRand = Math.random();
                
                // Xác suất xuất hiện Remote (20%)
                if (typeRand < 0.2 && score < 950) {
                    items.push({
                        x: 800,
                        y: 150,
                        width: 25,
                        height: 25,
                        type: 'remote'
                    });
                } else {
                    // Xương rồng hoặc chim
                    let isBird = Math.random() > 0.7 && score > 300;
                    obstacles.push({
                        x: 800,
                        y: isBird ? 140 : 185,
                        width: isBird ? 30 : 20,
                        height: isBird ? 25 : 35,
                        isBird: isBird
                    });
                }
            }
        }

        // Kích hoạt chế độ máy bay khi nhặt remote
        function triggerAirplane() {
            trex.isFlying = true;
            trex.flyTimer = 10 * 60; // 10 giây (60fps)
            notificationEl.style.display = "block";
            setTimeout(() => {
                notificationEl.style.display = "none";
            }, 3000);
        }

        // Bắt đầu đấu Boss
        function startBossFight() {
            gameState = "BOSS_FIGHT";
            bossHp = 3;
            bossModal.style.display = "flex";
            loadNewQuestion();
        }

        function loadNewQuestion() {
            bossHpText.innerText = `Máu Boss Xương Rồng: ${bossHp} / 3`;
            if (bossHp <= 0) {
                // Thắng Boss
                bossModal.style.display = "none";
                gameState = "PLAYING";
                score += 200; // Thưởng điểm vượt boss
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
                alert("Trả lời sai! Mất 1 máu hoặc chơi lại từ đầu tùy bạn, hãy thử lại câu hỏi tiếp theo!");
                loadNewQuestion();
            }
        }

        // Vòng lặp game chính
        function update() {
            if (gameState === "PLAYING") {
                score += 0.1;
                currentScoreEl.innerText = String(Math.floor(score)).padStart(5, '0');

                // Kiểm tra kích hoạt Boss Xương Rồng tại 1000 điểm
                if (Math.floor(score) >= 1000 && score < 1005) {
                    startBossFight();
                    return;
                }

                // Tăng tốc dần theo điểm
                gameSpeed = 5 + Math.floor(score / 200);

                // Quản lý máy bay (10 giây)
                if (trex.isFlying) {
                    trex.flyTimer--;
                    trex.y = 80; // Trex bay lơ lửng trên cao
                    trex.vy = 0;
                    if (trex.flyTimer <= 0) {
                        trex.isFlying = false;
                    }
                } else {
                    // Trọng lực cho T-Rex chạy mặt đất
                    trex.vy += gravity;
                    trex.y += trex.vy;
                    if (trex.y > 180) {
                        trex.y = 180;
                        trex.vy = 0;
                        trex.grounded = true;
                    }
                }

                // Chuyển động mặt đất & mây
                groundX = (groundX + gameSpeed) % 800;
                clouds.forEach(c => {
                    c.x -= c.speed;
                    if (c.x < -50) c.x = 850;
                });

                handleSpawns();

                // Cập nhật chướng ngại vật
                for (let i = obstacles.length - 1; i >= 0; i--) {
                    obstacles[i].x -= gameSpeed;

                    // Va chạm (Nếu đang bay máy bay thì né hoàn toàn chướng ngại vật dưới đất)
                    if (!trex.isFlying &&
                        trex.x < obstacles[i].x + obstacles[i].width &&
                        trex.x + trex.width > obstacles[i].x &&
                        trex.y < obstacles[i].y + obstacles[i].height &&
                        trex.y + trex.height > obstacles[i].y) {
                        gameState = "GAMEOVER";
                        if (score > highScore) {
                            highScore = Math.floor(score);
                            localStorage.setItem("trex_highscore", highScore);
                            highScoreEl.innerText = String(highScore).padStart(5, '0');
                        }
                    }

                    // Xóa chướng ngại vật ra khỏi mảng khi đi qua màn hình
                    if (obstacles[i].x < -50) {
                        obstacles.splice(i, 1);
                    }
                }

                // Cập nhật vật phẩm (Remote)
                for (let i = items.length - 1; i >= 0; i--) {
                    items[i].x -= gameSpeed;

                    // Nhặt remote
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

                    if (items[i] && items[i].x < -50) {
                        items.splice(i, 1);
                    }
                }
            }
        }

        // Vẽ đồ họa game phong cách Pixel Retro
        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Vẽ mây
            ctx.fillStyle = "#d3d3d3";
            clouds.forEach(c => {
                ctx.fillRect(c.x, c.y, 30, 10);
                ctx.fillRect(c.x + 8, c.y - 5, 15, 6);
            });

            // Vẽ mặt đất
            ctx.strokeStyle = "#535353";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(0, 220);
            ctx.lineTo(800, 220);
            ctx.stroke();

            // Vẽ chướng ngại vật (Xương rồng / Chim)
            obstacles.forEach(obs => {
                ctx.fillStyle = "#535353";
                if (obs.isBird) {
                    ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
                } else {
                    ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
                }
            });

            // Vẽ vật phẩm Remote
            items.forEach(it => {
                ctx.fillStyle = "#0984e3";
                ctx.fillRect(it.x, it.y, it.width, it.height);
                ctx.fillStyle = "#fff";
                ctx.fillRect(it.x + 8, it.y + 6, 8, 12); // Nút bấm remote
            });

            // Vẽ T-Rex hoặc Máy bay
            if (trex.isFlying) {
                // Vẽ Máy bay
                ctx.fillStyle = "#e17055";
                ctx.fillRect(trex.x - 10, trex.y - 5, 55, 20); // Thân máy bay
                ctx.fillStyle = "#74b9ff";
                ctx.fillRect(trex.x + 20, trex.y - 10, 15, 10); // Buồng lái
                // Vẽ T-rex ngồi bên trong
                ctx.fillStyle = "#535353";
                ctx.fillRect(trex.x + 5, trex.y + 2, 20, 20);
            } else {
                // Vẽ T-Rex thường
                ctx.fillStyle = "#535353";
                ctx.fillRect(trex.x, trex.y, trex.width, trex.height);
                // Mắt dino
                ctx.fillStyle = "#ffffff";
                ctx.fillRect(trex.x + 20, trex.y + 6, 4, 4);
            }

            // Hiển thị trạng thái khi ở màn hình Bắt đầu hoặc Game Over
            if (gameState === "START") {
                ctx.fillStyle = "#535353";
                ctx.font = "12px 'Press Start 2P'";
                ctx.textAlign = "center";
                ctx.fillText("NHẤN PHÍM CÁCH HOẶC CHẠM ĐỂ BẮT ĐẦU", canvas.width / 2, canvas.height / 2);
            } else if (gameState === "GAMEOVER") {
                ctx.fillStyle = "#ff4757";
                ctx.font = "14px 'Press Start 2P'";
                ctx.textAlign = "center";
                ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 15);
                ctx.fillStyle = "#535353";
                ctx.font = "9px 'Press Start 2P'";
                ctx.fillText("Nhấn phím Cách để chơi lại", canvas.width / 2, canvas.height / 2 + 15);
            }
        }

        // Vòng lặp yêu cầu khung hình
        function loop() {
            update();
            draw();
            requestAnimationFrame(loop);
        }

        loop();
    </script>
</body>
</html>
