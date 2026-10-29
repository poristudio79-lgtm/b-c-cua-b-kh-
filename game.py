import pygame
import random
import sys

# Khởi tạo Pygame
pygame.init()

# Cấu hình kích thước cửa sổ game
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 300
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("T-Rex Dash (Geometry Dash Style)")

# Bảng màu phong cách Neon
PURPLE = (26, 0, 51)
PINK = (255, 0, 119)
CYAN = (0, 255, 204)
WHITE = (255, 255, 255)

clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier New", 16, bold=True)

# Trạng thái và chỉ số game
score = 0
high_score = 0
game_speed = 7
gravity = 0.8

# Khủng long T-Rex
trex_x = 100
trex_y = 200
trex_width = 30
trex_height = 30
trex_vy = 0
jump_power = -12
is_grounded = True

obstacles = []
ground_y = 230
spawn_timer = 0
game_state = "START"  # START, PLAYING, GAMEOVER

def reset_game():
    global score, game_speed, obstacles, trex_y, trex_vy, is_grounded
    score = 0
    game_speed = 7
    obstacles = []
    trex_y = ground_y - trex_height
    trex_vy = 0
    is_grounded = True

# Vòng lặp chính của trò chơi
while True:
    screen.fill(PURPLE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                if game_state == "START":
                    game_state = "PLAYING"
                    reset_game()
                elif game_state == "PLAYING" and is_grounded:
                    trex_vy = jump_power
                    is_grounded = False
                elif game_state == "GAMEOVER":
                    game_state = "PLAYING"
                    reset_game()

    if game_state == "PLAYING":
        score += 1
        game_speed = 7 + int(score / 300)

        # Xử lý trọng lực và nhảy
        trex_vy += gravity
        trex_y += trex_vy

        # Chạm đất
        if trex_y >= ground_y - trex_height:
            trex_y = ground_y - trex_height
            trex_vy = 0
            is_grounded = True

        # Sinh chướng ngại vật (Gai nhọn / Khối vuông)
        spawn_timer += 1
        if spawn_timer > max(35, 90 - int(score / 50)):
            spawn_timer = 0
            if random.random() < 0.6:
                obstacles.append({"x": SCREEN_WIDTH, "y": ground_y - 25, "w": 25, "h": 25, "type": "spike"})
            else:
                obstacles.append({"x": SCREEN_WIDTH, "y": ground_y - 45, "w": 30, "h": 45, "type": "block"})

        # Cập nhật vị trí chướng ngại vật và kiểm tra va chạm
        for obs in obstacles[:]:
            obs["x"] -= game_speed
            if obs["x"] < -50:
                obstacles.remove(obs)

            # Hitbox kiểm tra va chạm
            trex_rect = pygame.Rect(trex_x + 4, trex_y + 4, trex_width - 8, trex_height - 8)
            obs_rect = pygame.Rect(obs["x"] + 4, obs["y"] + 4, obs["w"] - 8, obs["h"] - 8)

            if trex_rect.colliderect(obs_rect):
                game_state = "GAMEOVER"
                if score > high_score:
                    high_score = score

    # --- KHU VỰC VẼ ĐỒ HỌA ---
    # Vẽ đường mặt đất Neon
    pygame.draw.line(screen, CYAN, (0, ground_y), (SCREEN_WIDTH, ground_y), 4)

    # Vẽ chướng ngại vật
    for obs in obstacles:
        if obs["type"] == "spike":
            points = [
                (obs["x"], obs["y"] + obs["h"]),
                (obs["x"] + obs["w"] // 2, obs["y"]),
                (obs["x"] + obs["w"], obs["y"] + obs["h"])
            ]
            pygame.draw.polygon(screen, PINK, points)
        else:
            pygame.draw.rect(screen, (155, 89, 182), (obs["x"], obs["y"], obs["w"], obs["h"]))
            pygame.draw.rect(screen, WHITE, (obs["x"], obs["y"], obs["w"], obs["h"]), 2)

    # Vẽ T-Rex
    if game_state == "PLAYING" or game_state == "GAMEOVER":
        pygame.draw.rect(screen, CYAN, (trex_x, trex_y, trex_width, trex_height))
        pygame.draw.rect(screen, WHITE, (trex_x + 18, trex_y + 6, 5, 5)) # Mắt khủng long

    # Hiển thị điểm số trên màn hình
    score_text = font.render(f"SCORE: {score}   HI: {high_score}", True, CYAN)
    screen.blit(score_text, (20, 20))

    # Thông báo màn hình Start / Game Over
    if game_state == "START":
        start_text = font.render("NHẤN PHÍM CÁCH ĐỂ BẮT ĐẦU", True, WHITE)
        screen.blit(start_text, (SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2 - 10))
    elif game_state == "GAMEOVER":
        over_text = font.render("CRASH! NHẤN PHÍM CÁCH ĐỂ THỬ LẠI", True, PINK)
        screen.blit(over_text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 10))

    pygame.display.flip()
    clock.tick(60)
