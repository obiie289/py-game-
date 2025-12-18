import pygame
import random
import math # 추가함 수학 계산 ((조준 사격)

# 1 설정 & 변수 
pygame.init()
pygame.font.init()

boss_anim_index = 0

display = pygame.display.set_mode((800, 600))
myfont = pygame.font.SysFont("Comic Sans MS", 30)

# 경고 문구용 폰트
warn_font = pygame.font.SysFont("Comic Sans MS", 50, True)

# 게임 오버용 폰트
game_over_font = pygame.font.SysFont("Comic Sans MS", 80, True)

# 이미지 로드
def load_images():
    imgs = {}
    path = "py game img/" 
    
    try:
        p = pygame.image.load(path + "battleship.png")
        imgs['player'] = pygame.transform.scale(p, (60, 60))
        
        m = pygame.image.load(path + "missile.png")
        imgs['missile'] = pygame.transform.scale(m, (30, 30))
        
        bg = pygame.image.load(path + "background.png")
        imgs['bg'] = pygame.transform.scale(bg, (800, 600))

        try:
            bg_def = pygame.image.load(path + "back.png")
            imgs['bg_default'] = pygame.transform.scale(bg_def, (800, 600))
        except:
            print("기본 배경(back.png)이 없어 흰색 배경을 사용합니다.")

        a1 = pygame.image.load(path + "alien.png")
        imgs['alien'] = pygame.transform.scale(a1, (40, 40))
        
        a2 = pygame.image.load(path + "alien2.jpeg")
        imgs['mid'] = pygame.transform.scale(a2, (60, 60))
        
        a3 = pygame.image.load(path + "Six seven kid.jpeg")
        imgs['mid2'] = pygame.transform.scale(a3, (60, 60))
        
        a4 = pygame.image.load(path + "mid3.png")
        imgs['mid3'] = pygame.transform.scale(a4, (50, 50))
        
        a5 = pygame.image.load(path + "mid4.png")
        imgs['mid4'] = pygame.transform.scale(a5, (50, 50))

        boss_imgs = []
        for i in range(34): 
            filename = path + "groove_battle/5b6f042a0a094533dd8019b7488908a6Dwi7s4QNLfseiVdI-" + str(i) + ".png"
            img = pygame.image.load(filename)
            img = pygame.transform.scale(img, (300, 350))
            img.set_colorkey((255, 255, 255))
            boss_imgs.append(img)

        imgs['last_boss'] = boss_imgs 

    except Exception as e:
        print(f"이미지 로드 중 오류 발생: {e}")
    
    return imgs

game_imgs = load_images() 

# --- [2] 함수 ---

def check_collision(enemy_rect, missile_rect, state):
    if state == "fire" and enemy_rect.colliderect(missile_rect):
        return True
    return False

def reset_enemy_pos(idx, enemy_type):
    if enemy_type == "alien":
        return 20 + idx * 80, 10
    elif enemy_type == "mid":
        return 100 + idx * 150, -100
    elif enemy_type == "mid2":
        return 150 + idx * 300, -150
    elif enemy_type == "mid3": 
        return -150, random.randint(50, 400)
    elif enemy_type == "mid4": 
        return 950, random.randint(50, 400)
    return 0, 0

def draw_boss(surface, x, y, current_hp, max_hp):
    block_width = 8 
    block_height = 15 
    spacing = 2 
    hp_per_block = 5 

    num_blocks = int(current_hp / hp_per_block)
    max_block = int(max_hp / hp_per_block)

    startX = x 
    for i in range(max_block):
        bx = startX + i * (block_width + spacing)
        by = y 
        pygame.draw.rect(surface, (50, 0, 0), (bx, by, block_width, block_height))  
    for i in range(num_blocks):
        bx = startX + i * (block_width + spacing)
        by = y 
        pygame.draw.rect(surface, (255, 50, 50), (bx, by, block_width, block_height))

# --- [3] 게임 데이터 초기화 ---

playerX, playerY, playerDx = 400, 530, 0
missileX, missileY, missileDx, missileDy = 0, 1000, 0, 10
missileState = "hidden" 

player_hp = 3 
last_hit_time = 0 
game_over = False

def create_enemies(num, speed, start_pos_func):
    x, y, dx, dy = [], [], [], []
    for i in range(num):
        sx, sy = start_pos_func(i)
        x.append(sx)
        y.append(sy)
        dx.append(speed)
        dy.append(0.0) 
    return x, y, dx, dy

alienX, alienY, alienDx, alienDy = create_enemies(12, 3, lambda i: (20 + i * 80, 10))
midX, midY, midDx, midDy = create_enemies(3, 2, lambda i: (100 + i * 150, -100))
mid2X, mid2Y, mid2Dx, mid2Dy = create_enemies(3, 2, lambda i: (150 + i * 300, -150))
mid3X, mid3Y, mid3Dx, mid3Dy = create_enemies(2, 4, lambda i: (-100, 100 + i * 150))
mid4X, mid4Y, mid4Dx, mid4Dy = create_enemies(2, -4, lambda i: (900, 200 + i * 150))

bossX = 325 
bossY = 50 
bossDx = 2 
bossmaxHP = 100
bosscurrentHP = 100
boss_spawned = False
warning_time = 0 

# [추가] 보스 총알 관련 변수 (변수명 유지하며 추가)
boss_bullets = []   
boss_fire_time = 0  

score = 0
game_stage = 1
stage_change_time = 0
running = True
clock = pygame.time.Clock()

# --- [4] 메인 루프 ---

while running: 
    clock.tick(60)
    
    # 1. 배경 처리
    current_time = pygame.time.get_ticks()

    if game_stage == 2 and (current_time - stage_change_time < 5000):
        if 'bg' in game_imgs: 
            display.blit(game_imgs['bg'], (0, 0))
    else:
        if 'bg_default' in game_imgs:
            display.blit(game_imgs['bg_default'], (0, 0))
        else:
            display.fill((255, 255, 255))

    missile_rect = pygame.Rect(missileX, missileY, 10, 30) 

    # ---------------- 보스 (Stage 3) 로직 ----------------
    if game_stage == 3: 
        if not boss_spawned: 
            if warning_time == 0: 
                warning_time = pygame.time.get_ticks()

            if pygame.time.get_ticks() - warning_time < 3000:
                if (pygame.time.get_ticks() // 500) % 2 == 0 :
                    warn_text_surface = warn_font.render("!!!6 7!!", True, (255,0,0))
                    display.blit(warn_text_surface, (200, 250))
            else:
                boss_spawned = True
        
        else: 
            # 1. 보스 움직임
            bossX += bossDx 
            if bossX <= 0 or bossX > 500:
                bossDx *= -1 

            boss_anim_index += 0.2
            boss_frames = game_imgs['last_boss']
            current_frame_num = int(boss_anim_index) % len(boss_frames)
            
            # 2 보스 그리기
            display.blit(boss_frames[current_frame_num], (bossX, bossY))
            draw_boss(display, bossX + 10, bossY - 25, bosscurrentHP, bossmaxHP)

            # -------------- 보스 공격 패턴 원거리  ----------------
            if not game_over:
                # 0.8초(800ms)마다 발사
                if current_time - boss_fire_time > 800:
                    boss_fire_time = current_time
                    
                    # 총알 시작 위치 (보스 가슴 쯤)
                    bx = bossX + 150 
                    by = bossY + 150
                    
                    # 플레이어 쪽으로 각도 계산 (조준)
                    diff_x = (playerX + 30) - bx
                    diff_y = (playerY + 30) - by
                    distance = math.sqrt(diff_x**2 + diff_y**2)
                    
                    if distance != 0:
                        b_dx = (diff_x / distance) * 7
                        b_dy = (diff_y / distance) * 7
                        boss_bullets.append([bx, by, b_dx, b_dy])
            
            # 총알 이동 및 그리기
            for b in boss_bullets[:]: 
                b[0] += b[2] # x 이동
                b[1] += b[3] # y 이동
                
                # 화면 밖 삭제
                if b[1] > 600 or b[0] < 0 or b[0] > 800:
                    boss_bullets.remove(b)
                    continue

                # 총알 그리기 (노란색 원)
                pygame.draw.circle(display, (180, 85, 0), (int(b[0]), int(b[1])), 10)
                pygame.draw.circle(display, (128,0,128), (int(b[0]), int(b[1])), 10, 2)
                
                # 플레이어와 총알 충돌 검사
                if not game_over:
                    bullet_rect = pygame.Rect(b[0]-10, b[1]-10, 20, 20)
                    player_rect = pygame.Rect(playerX, playerY, 60, 60)
                    
                    if bullet_rect.colliderect(player_rect):
                        if current_time - last_hit_time > 1000:
                            player_hp -= 1
                            last_hit_time = current_time
                            print("보스 총알 맞음!")
                            if player_hp <= 0: game_over = True
            # ------------------------------------------------------------------

            # 3. 보스 피격 및 충돌 처리
            boss_rect = pygame.Rect(bossX, bossY, 300, 350)
            
            # 미사일 맞았을 때
            if check_collision(boss_rect, missile_rect, missileState):
                bosscurrentHP -= 2
                missileState = "hidden"
                missileY = 1000
                score += 67
                if bosscurrentHP <= 0 :
                    print("보스 다운")
                    running = False 

            # 플레이어와 몸통 박치기
            if not game_over:
                player_rect = pygame.Rect(playerX, playerY, 60, 60)
                if boss_rect.colliderect(player_rect):
                    if current_time - last_hit_time > 1000:
                        player_hp -= 3 
                        last_hit_time = current_time
                        game_over = True
                        print("보스와 충돌! 게임 오버")

    # ----------------------------------------------------

    # 2. 키 입력 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT: playerDx = -5
            if event.key == pygame.K_RIGHT: playerDx = 5

            if event.key == pygame.K_r and game_over: 
                score = 0 
                player_hp = 3
                game_stage = 1
                game_over = False
                boss_spawned = False
                bosscurrentHP = bossmaxHP
                boss_bullets = [] # [수정] 재시작시 총알도 없애기
                print("게임 재시작")
                
            if event.key == pygame.K_SPACE:
                if missileState == "hidden":
                    missileState = "fire"
                    missileX = playerX + 15
                    missileY = playerY
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                playerDx = 0

    # 3. 플레이어 이동
    playerX += playerDx
    if playerX <= 0: playerX = 0
    if playerX >= 740: playerX = 740

    # 4. 쫄병 업데이트 및 그리기 (보스 위에 그려짐)

    # (A) 기본 몹
    for i in range(len(alienX)):
        alienX[i] += alienDx[i]
        alienY[i] += 3.0 if alienDx[i] == 0 else 0 
        
        if alienX[i] <= 0 or alienX[i] > 750:
            alienDx[i] *= -1
            alienY[i] += 30
            
        display.blit(game_imgs['alien'], (alienX[i], alienY[i]))
        
        alien_rect = pygame.Rect(alienX[i], alienY[i], 40, 40)
        
        # 1. 미사일 충돌
        if check_collision(alien_rect, missile_rect, missileState):
            score += 1
            missileState = "hidden"
            missileY = 1000
            
            if score >= 10 and game_stage == 1:
                game_stage = 2
                stage_change_time = pygame.time.get_ticks()
                print("2 stage")
            elif score >= 60 and game_stage == 2:
                game_stage = 3
                print("3 stage 보스 출몰!")
                
            alienX[i], alienY[i] = reset_enemy_pos(i, "alien")
            
        # 2. 플레이어 충돌
        if not game_over:
            player_rect = pygame.Rect(playerX, playerY, 60, 60)
            if alien_rect.colliderect(player_rect):
                if current_time - last_hit_time > 1000:
                    player_hp -= 1
                    last_hit_time = current_time 
                    print(f"충돌! 남은 체력: {player_hp}")
                    if player_hp <= 0:
                        game_over = True

    # (B) 중간 몹들
    if game_stage >= 2:
        
        # Mid 1
        for i in range(len(midX)):
            midX[i] += midDx[i]
            midY[i] += 4 
            if random.randint(1, 100) <= 60: 
                midY[i] -= 1
                midX[i] += 2
            if midX[i] <= 0 or midX[i] > 720: midDx[i] *= -1; midY[i] += 40
            if midY[i] > 100: midY[i] += 1
            
            display.blit(game_imgs['mid'], (midX[i], midY[i]))
            mid_rect = pygame.Rect(midX[i], midY[i], 60, 60)
            
            if check_collision(mid_rect, missile_rect, missileState):
                score += 5
                missileState = "hidden"
                missileY = 1000
                midX[i], midY[i] = reset_enemy_pos(i, "mid")

            if not game_over:
                player_rect = pygame.Rect(playerX, playerY, 60, 60)
                if mid_rect.colliderect(player_rect):
                    if current_time - last_hit_time > 1000:
                        player_hp -= 1
                        last_hit_time = current_time 
                        if player_hp <= 0: game_over = True

        # Mid 2
        for i in range(len(mid2X)):
            mid2X[i] += mid2Dx[i]
            mid2Y[i] += 4
            if random.randint(1, 100) <= 65:
                mid2Y[i] -= 5
                mid2X[i] -= 3
            if mid2X[i] <= 0 or mid2X[i] > 729: mid2Dx[i] *= -1; mid2Y[i] += 40
            if mid2Y[i] < 10: mid2Y[i] += 1
            
            display.blit(game_imgs['mid2'], (mid2X[i], mid2Y[i]))
            mid2_rect = pygame.Rect(mid2X[i], mid2Y[i], 60, 60)
            
            if check_collision(mid2_rect, missile_rect, missileState):
                score += 4
                missileState = "hidden"
                missileY = 1000
                mid2X[i], mid2Y[i] = reset_enemy_pos(i, "mid2")
            
            if not game_over:
                player_rect = pygame.Rect(playerX, playerY, 60, 60)
                if mid2_rect.colliderect(player_rect):
                    if current_time - last_hit_time > 1000:
                        player_hp -= 1
                        last_hit_time = current_time 
                        if player_hp <= 0: game_over = True

        # Mid 3
        for i in range(len(mid3X)):
            mid3X[i] += mid3Dx[i]
            if mid3X[i] > 850: 
                mid3X[i], mid3Y[i] = reset_enemy_pos(i, "mid3")
            display.blit(game_imgs['mid3'], (mid3X[i], mid3Y[i]))
            
            mid3_rect = pygame.Rect(mid3X[i], mid3Y[i], 50, 50)
            
            if check_collision(mid3_rect, missile_rect, missileState):
                score += 3
                missileState = "hidden"
                missileY = 1000
                mid3X[i], mid3Y[i] = reset_enemy_pos(i, "mid3")
            
            if not game_over:
                player_rect = pygame.Rect(playerX, playerY, 60, 60)
                if mid3_rect.colliderect(player_rect):
                    if current_time - last_hit_time > 1000:
                        player_hp -= 1
                        last_hit_time = current_time 
                        if player_hp <= 0: game_over = True

        # Mid 4
        for i in range(len(mid4X)):
            mid4X[i] += mid4Dx[i]
            if mid4X[i] < -50: 
                mid4X[i], mid4Y[i] = reset_enemy_pos(i, "mid4")
            display.blit(game_imgs['mid4'], (mid4X[i], mid4Y[i]))
            mid4_rect = pygame.Rect(mid4X[i], mid4Y[i], 50, 50)
            
            if check_collision(mid4_rect, missile_rect, missileState):
                score += 3
                missileState = "hidden"
                missileY = 1000
                mid4X[i], mid4Y[i] = reset_enemy_pos(i, "mid4")
            
            if not game_over:
                player_rect = pygame.Rect(playerX, playerY, 60, 60)
                if mid4_rect.colliderect(player_rect):
                    if current_time - last_hit_time > 1000:
                        player_hp -= 1
                        last_hit_time = current_time 
                        if player_hp <= 0: game_over = True

    # 5. 미사일 및 플레이어 그리기 (맨 앞)
    if missileY <= 0:
        missileY = 1000
        missileState = "hidden"
    
    if missileState == "fire":
        missileY -= missileDy
        display.blit(game_imgs['missile'], (missileX, missileY))

    display.blit(game_imgs['player'], (playerX, playerY))
    
    # UI 표시 (검은색)
    text = myfont.render(f'Score: {score}', False, (0, 0, 0))
    display.blit(text, (10, 550))
    
    stage_text = myfont.render(f'Stage: {game_stage}', False, (0, 0, 0))
    display.blit(stage_text, (350, 50))

    # [수정] 체력 및 게임오버 화면 추가
    hp_text = myfont.render(f'HP: {player_hp}', False, (255, 0, 0))
    display.blit(hp_text, (650, 550))

    if game_over:
        over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        display.blit(over_text, (180, 250))
        
        restart_text = myfont.render("Press 'R' to Restart", True, (0, 0, 0))
        display.blit(restart_text, (280, 350))
    
    pygame.display.update()

pygame.quit()