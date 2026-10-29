<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>T-Rex Dash: Chrome Dino x Geometry Dash</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        * {
            box-sizing: border-box;
            user-select: none;
        }
        body {
            margin: 0;
            padding: 0;
            background: #111;
            font-family: 'Press Start 2P', monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            overflow: hidden;
            color: #fff;
        }
        h1 {
            font-size: 14px;
            color: #00ffcc;
            margin-bottom: 10px;
            text-align: center;
            text-shadow: 0 0 10px #00ffcc;
        }
        .game-container {
            position: relative;
            width: 800px;
            height: 300px;
            background: #1a0033;
            border: 3px solid #ff007f;
            box-shadow: 0 0 20px #ff007f;
            overflow: hidden;
        }
        canvas {
            display: block;
            background: linear-gradient(to bottom, #110022, #220044);
        }
        .ui-panel {
            width: 800px;
            display: flex;
            justify-content: space-between;
            padding: 8px 10px;
            font-size: 10px;
            color: #00ffcc;
        }
    </style>
</head>
<body>

    <h1>T-REX DASH: CHROME DINO x GEOMETRY DASH</h1>
    <div class="game-container">
        <canvas id="gameCanvas" width="800" height="300"></canvas>
    </div>
    
    <div class="ui-panel">
        <div>HI: <span id="highScore">00000</span></div>
        <div>ATTEMPT: <span id="attemptCount">1</span></div>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const highScoreEl = document.getElementById("highScore");
        const attemptCountEl = document.getElementById("attemptCount");

        let gameState = "START"; // START, PLAYING, GAMEOVER
        let score = 0;
        let highScore = localStorage.getItem("trex_dash_highscore") || 0;
        let attempts = 1;
        highScoreEl.innerText = String(highScore).padStart(5, '0');

        let gameSpeed = 7; // Tốc độ phi mã phong cách Dash
        let gravity = 0.75;

        // Nhân vật T-Rex Neon
        let trex = {
            x: 100,
            y: 200,
            width: 32,
            height: 32,
            vy: 0,
            jumpPower: -12,
            grounded: true,
            rotation: 0
        };

        let obstacles = []; // Gai nhọn và khối vuông Dash
        let particles = []; // Hiệu ứng đuôi neon
        let groundY = 232;

        // Bắt sự kiện nhảy (Giữ phím hoặc nhấp liên tục để bay nhảy phong cách Dash)
        window.addEventListener("keydown", (e) => {
            if (e.code === "Space" || e.code === "ArrowUp") {
                triggerJump();
            }
        });

        canvas.addEventListener("click", () => {
            triggerJump();
        });

        function triggerJump() {
            if (gameState === "START") {
                startGame();
            } else if (gameState === "PLAYING" && trex.grounded) {
                trex.vy = trex.jumpPower;
                trex.grounded = false;
            } else if (gameState === "GAMEOVER") {
                resetGame();
                startGame();
            }
        }

        function startGame() {
            gameState = "PLAYING";
            score = 0;
            gameSpeed = 7;
            obstacles = [];
            particles = [];
        }

        function resetGame() {
            trex.y = groundY - trex.height;
            trex.vy = 0;
            trex.grounded = true;
            trex.rotation = 0;
            attempts++;
            attemptCountEl.innerText = attempts;
        }

        // Sinh chướng ngại vật phong cách Geometry Dash (Gai nhọn, tường vuông)
        let spawnTimer = 0;
        function handleSpawns() {
            spawnTimer++;
            if (spawnTimer > Math.max(35, 90 - Math.floor(score / 50))) {
                spawnTimer = 0;
                let type = Math.random();
                
                if (type < 0.6) {
                    // Cụm gai nhọn đặc trưng của Geometry Dash
                    let spikeCount = Math.random() > 0.5 ? 2 : 1;
                    for (let i = 0; i < spikeCount; i++) {
                        obstacles.push({
                            x: 800 + (i * 25),
                            y: groundY - 26,
                            width: 26,
                            height: 26,
                            type: 'spike'
                        });
                    }
                } else {
                    // Khối trụ/bục nhảy cao
                    obstacles.push({
                        x: 800,
                        y: groundY - 50,
                        width: 35,
                        height: 50,
                        type: 'block'
                    });
                }
            }
        }

        function update() {
            if (gameState === "PLAYING") {
                score += 1;
                highScoreEl.innerText = String(Math.floor(score)).padStart(5, '0');
                
                // Tăng tốc độ dần theo điểm số
                gameSpeed = 7 + Math.floor(score / 300);

                // Trọng lực và nhảy
                trex.vy += gravity;
                trex.y += trex.vy;

                // Xoay nhẹ T-Rex khi đang bay (chuẩn vibe Dash)
                if (!trex.grounded) {
                    trex.rotation += 12;
                } else {
                    trex.rotation = 0;
                }

                // Xử lý chạm đất
                if (trex.y >= groundY - trex.height) {
                    trex.y = groundY - trex.height;
                    trex.vy = 0;
                    trex.grounded = true;
                }

                // Tạo hiệu ứng hạt neon phía sau T-Rex
                if (Math.random() > 0.3) {
                    particles.push({
                        x: trex.x,
                        y: trex.y + trex.height / 2,
                        size: Math.random() * 6 + 2,
                        alpha: 1,
                        color: score % 200 > 100 ? '#00ffcc' : '#ff007f'
                    });
                }

                particles.forEach((p, index) => {
                    p.x -= gameSpeed;
                    p.alpha -= 0.05;
                    if (p.alpha <= 0) particles.splice(index, 1);
                });

                handleSpawns();

                // Cập nhật chướng ngại vật & Kiểm tra va chạm (AABB)
                for (let i = obstacles.length - 1; i >= 0; i--) {
                    obstacles[i].x -= gameSpeed;

                    let obs = obstacles[i];
                    // Thu hẹp hitbox một chút cho cảm giác công bằng khi lướt qua gai
                    let hitBoxMargin = 6;
                    if (
                        trex.x + hitBoxMargin < obs.x + obs.width - hitBoxMargin &&
                        trex.x + trex.width - hitBoxMargin > obs.x + hitBoxMargin &&
                        trex.y + hitBoxMargin < obs.y + obs.height - hitBoxMargin &&
                        trex.y + trex.height - hitBoxMargin > obs.y + hitBoxMargin
                    ) {
                        gameState = "GAMEOVER";
                        if (score > highScore) {
                            highScore = Math.floor(score);
                            localStorage.setItem("trex_dash_highscore", highScore);
                            highScoreEl.innerText = String(highScore).padStart(5, '0');
                        }
                    }

                    if (obs.x < -50) {
                        obstacles.splice(i, 1);
                    }
                }
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Vẽ lưới điện tử nền phong cách Dash
            ctx.strokeStyle = "rgba(255, 0, 127, 0.08)";
            ctx.lineWidth = 1;
            for (let i = 0; i < canvas.width; i += 40) {
                ctx.beginPath();
                ctx.moveTo(i, 0);
                ctx.lineTo(i, canvas.height);
                ctx.stroke();
            }

            // Vẽ vệt hạt Neon phía sau
            particles.forEach(p => {
                ctx.fillStyle = p.color;
                ctx.globalAlpha = p.alpha;
                ctx.fillRect(p.x, p.y, p.size, p.size);
            });
            ctx.globalAlpha = 1.0;

            // Vẽ đường mặt đất phát sáng Neon
            ctx.strokeStyle = "#00ffcc";
            ctx.lineWidth = 4;
            ctx.shadowBlur = 15;
            ctx.shadowColor = "#00ffcc";
            ctx.beginPath();
            ctx.moveTo(0, groundY);
            ctx.lineTo(canvas.width, groundY);
            ctx.stroke();
            ctx.shadowBlur = 0; // Reset shadow

            // Vẽ chướng ngại vật (Gai nhọn & Khối màu rực rỡ)
            obstacles.forEach(obs => {
                if (obs.type === 'spike') {
                    // Vẽ Gai nhọn phong cách Geometry Dash
                    ctx.fillStyle = "#ff0055";
                    ctx.shadowBlur = 10;
                    ctx.shadowColor = "#ff0055";
                    ctx.beginPath();
                    ctx.moveTo(obs.x, obs.y + obs.height);
                    ctx.lineTo(obs.x + obs.width / 2, obs.y);
                    ctx.lineTo(obs.x + obs.width, obs.y + obs.height);
                    ctx.closePath();
                    ctx.fill();
                    ctx.shadowBlur = 0;
                } else {
                    // Vẽ Khối vuông neon
                    ctx.fillStyle = "#9b59b6";
                    ctx.shadowBlur = 10;
                    ctx.shadowColor = "#9b59b6";
                    ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
                    ctx.strokeStyle = "#fff";
                    ctx.strokeRect(obs.x, obs.y, obs.width, obs.height);
                    ctx.shadowBlur = 0;
                }
            });

            // Vẽ T-Rex Neon xoay vòng
            ctx.save();
            ctx.translate(trex.x + trex.width / 2, trex.y + trex.height / 2);
            ctx.rotate((trex.rotation * Math.PI) / 180);
            
            ctx.fillStyle = "#00ffcc";
            ctx.shadowBlur = 12;
            ctx.shadowColor = "#00ffcc";
            // Thân T-Rex pixel
            ctx.fillRect(-12, -8, 24, 20);
            ctx.fillRect(4, -16, 14, 14); // Đầu
            ctx.fillStyle = "#ffffff";
            ctx.fillRect(10, -12, 4, 4);   // Mắt
            
            ctx.restore();
            ctx.shadowBlur = 0;

            // Giao diện Màn hình Bắt đầu & Thua
            if (gameState === "START") {
                ctx.fillStyle = "#00ffcc";
                ctx.font = "11px 'Press Start 2P'";
                ctx.textAlign = "center";
                ctx.shadowBlur = 10;
                ctx.shadowColor = "#00ffcc";
                ctx.fillText("NHẤN PHÍM CÁCH ĐỂ BẮT ĐẦU DASH", canvas.width / 2, canvas.height / 2);
                ctx.shadowBlur = 0;
            } else if (gameState === "GAMEOVER") {
                ctx.fillStyle = "#ff0055";
                ctx.font = "14px 'Press Start 2P'";
                ctx.textAlign = "center";
                ctx.shadowBlur = 15;
                ctx.shadowColor = "#ff0055";
                ctx.fillText("CRASH!", canvas.width / 2, canvas.height / 2 - 20);
                
                ctx.fillStyle = "#fff";
                ctx.font = "8px 'Press Start 2P'";
                ctx.fillText("Nhấn phím Cách để thử lại", canvas.width / 2, canvas.height / 2 + 10);
                ctx.shadowBlur = 0;
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
