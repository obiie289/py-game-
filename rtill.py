import pygame
import random

# --- [1] 초기 설정 및 변수 선언 ---
pygame.init()
pygame.font.init()

display = pygame.display.set_mode((800, 600))
myfont = pygame.font.SysFont("Comic Sans MS", 30)

# 이미지 로드 (경로는 사용자 환경에 맞게 유지)
def load_images():
    imgs = {}
    path = "py game img/" # 경로가 길다면 변수로 뺌 
    
    # 플레이어
    p = pygame.image.load(path + "battleship.png")
    imgs['player'] = pygame.transform.scale(p, (60, 60))
    
    # 미사일
    m = pygame.image.load(path + "missile.png")
    imgs['missile'] = pygame.transform.scale(m, (30, 30))
    
    # 배경
    bg = pygame.image.load(path + "background.png")
    imgs['bg'] = pygame.transform.scale(bg, (800, 600))

    # 적 이미지들
    a1 = pygame.image.load(path + "alien.png")
    imgs['alien'] = pygame.transform.scale(a1, (40, 40))
    
    a2 = pygame.image.load(path + "alien2.jpeg")
    imgs['mid'] = pygame.transform.scale(a2, (60, 60))
    
    a3 = pygame.image.load(path + "alien3.png")
    imgs['mid2'] = pygame.transform.scale(a3, (60, 60))
    
    a4 = pygame.image.load(path + "mid3.png")
    imgs['mid3'] = pygame.transform.scale(a4, (50, 50))
    
    a5 = pygame.image.load(path + "mid4.png")
    imgs['mid4'] = pygame.transform.scale(a5, (50, 50))
    
    return imgs

game_imgs = load_images() # 이미지들 로딩 완료

# --- [2] 유틸리티 함수 (반복되는 계산을 처리) ---

def check_collision(enemy_rect, missile_rect, state):
    """충돌했는지 검사해서 True/False를 알려주는 함수"""
    if state == "fire" and enemy_rect.colliderect(missile_rect):
        return True
    return False

def reset_enemy_pos(idx, enemy_type):
    """적이 죽거나 나갔을 때 위치를 초기화(리스폰) 해주는 함수"""
    if enemy_type == "alien":
        return 20 + idx * 80, 10
    elif enemy_type == "mid":
        return 100 + idx * 150, -100
    elif enemy_type == "mid2":
        return 150 + idx * 300, -150
    elif enemy_type == "mid3": # 왼쪽 -> 오른쪽
        return -150, random.randint(50, 400)
    elif enemy_type == "mid4": # 오른쪽 -> 왼쪽
        return 950, random.randint(50, 400)
    return 0, 0

# --- [3] 게임 데이터 초기화 ---

# 플레이어
playerX, playerY, playerDx = 400, 530, 0

# 미사일
missileX, missileY, missileDx, missileDy = 0, 1000, 0, 10
missileState = "hidden"

# 적 리스트 생성 함수
def create_enemies(num, speed, start_pos_func):
    x, y, dx, dy = [], [], [], []
    for i in range(num):
        sx, sy = start_pos_func(i)
        x.append(sx)
        y.append(sy)
        dx.append(speed)
        dy.append(0.0) # 기본 dy
    return x, y, dx, dy

# 각 적들의 데이터 생성
# (복잡한 append 반복문을 한 줄로 줄일 수 있습니다)
alienX, alienY, alienDx, alienDy = create_enemies(12, 3, lambda i: (20 + i * 80, 10))
midX, midY, midDx, midDy = create_enemies(3, 2, lambda i: (100 + i * 150, -100))
mid2X, mid2Y, mid2Dx, mid2Dy = create_enemies(3, 2, lambda i: (150 + i * 300, -150))
mid3X, mid3Y, mid3Dx, mid3Dy = create_enemies(2, 4, lambda i: (-100, 100 + i * 150))
mid4X, mid4Y, mid4Dx, mid4Dy = create_enemies(2, -4, lambda i: (900, 200 + i * 150))

# 게임 상태 변수
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
        display.blit(game_imgs['bg'], (0, 0))
    else:
        display.fill((0, 0, 0))

    # 2. 키 입력 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT: playerDx = -5
            if event.key == pygame.K_RIGHT: playerDx = 5
            if event.key == pygame.K_SPACE:
                if missileState == "hidden":
                    missileState = "fire"
                    missileX = playerX + 15
                    missileY = playerY
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                playerDx = 0

    # 플레이어 이동
    playerX += playerDx
    if playerX <= 0: playerX = 0
    if playerX >= 740: playerX = 740

    # 3. 적 업데이트 및 충돌 처리
    
    # 공통 미사일 Rect (충돌 검사용)
    missile_rect = pygame.Rect(missileX, missileY, 10, 30)

    # (A) 기본 몹 업데이트
    for i in range(len(alienX)):
        alienX[i] += alienDx[i]
        alienY[i] += 3.0 if alienDx[i] == 0 else 0 # 내려오는 로직 간단화
        
        # 벽 충돌
        if alienX[i] <= 0 or alienX[i] > 750:
            alienDx[i] *= -1
            alienY[i] += 30
            
        display.blit(game_imgs['alien'], (alienX[i], alienY[i]))
        
        # 충돌 체크 함수 사용!
        alien_rect = pygame.Rect(alienX[i], alienY[i], 40, 40)
        if check_collision(alien_rect, missile_rect, missileState):
            score += 1
            missileState = "hidden"
            missileY = 1000
            
            # 스테이지 체크 로직
            if score >= 10 and game_stage == 1:
                game_stage = 2
                stage_change_time = pygame.time.get_ticks()
                print("2 stage")
            elif score >= 60 and game_stage == 2:
                game_stage = 3
                print("3 stage 보스 출몰!")
                
            # 리스폰 함수 사용!
            alienX[i], alienY[i] = reset_enemy_pos(i, "alien")
            alienDx[i] = 3 # 속도 초기화

    # (B) 스테이지 2 이상 - 중간 몹들 업데이트
    if game_stage >= 2:
        
        # Mid 1 (랜덤 이동)
        for i in range(len(midX)):
            midX[i] += midDx[i]
            midY[i] += 4 # dy값 직접 사용
            
            if random.randint(1, 100) <= 60: # 랜덤 움직임
                midY[i] -= 1
                midX[i] += 2
                
            if midX[i] <= 0 or midX[i] > 720: midDx[i] *= -1; midY[i] += 40
            if midY[i] > 100: midY[i] += 1
            
            display.blit(game_imgs['mid'], (midX[i], midY[i]))
            
            if check_collision(pygame.Rect(midX[i], midY[i], 60, 60), missile_rect, missileState):
                score += 5
                missileState = "hidden"
                missileY = 1000
                midX[i], midY[i] = reset_enemy_pos(i, "mid")

        # Mid 2 (다른 랜덤 이동)
        for i in range(len(mid2X)):
            mid2X[i] += mid2Dx[i]
            mid2Y[i] += 4
            
            if random.randint(1, 100) <= 65:
                mid2Y[i] -= 5
                mid2X[i] -= 3
            
            if mid2X[i] <= 0 or mid2X[i] > 729: mid2Dx[i] *= -1; mid2Y[i] += 40
            if mid2Y[i] < 10: mid2Y[i] += 1
            
            display.blit(game_imgs['mid2'], (mid2X[i], mid2Y[i]))
            
            if check_collision(pygame.Rect(mid2X[i], mid2Y[i], 60, 60), missile_rect, missileState):
                score += 4
                missileState = "hidden"
                missileY = 1000
                mid2X[i], mid2Y[i] = reset_enemy_pos(i, "mid2")

        # Mid 3 (왼쪽 -> 오른쪽)
        for i in range(len(mid3X)):
            mid3X[i] += mid3Dx[i]
            if mid3X[i] > 850: # 화면 밖 나가면 리스폰
                mid3X[i], mid3Y[i] = reset_enemy_pos(i, "mid3")
            
            display.blit(game_imgs['mid3'], (mid3X[i], mid3Y[i]))
            
            if check_collision(pygame.Rect(mid3X[i], mid3Y[i], 50, 50), missile_rect, missileState):
                score += 3
                missileState = "hidden"
                missileY = 1000
                mid3X[i], mid3Y[i] = reset_enemy_pos(i, "mid3")

        # Mid 4 (오른쪽 -> 왼쪽)
        for i in range(len(mid4X)):
            mid4X[i] += mid4Dx[i]
            if mid4X[i] < -50: # 화면 밖 나가면 리스폰
                mid4X[i], mid4Y[i] = reset_enemy_pos(i, "mid4")
            
            display.blit(game_imgs['mid4'], (mid4X[i], mid4Y[i]))
            
            if check_collision(pygame.Rect(mid4X[i], mid4Y[i], 50, 50), missile_rect, missileState):
                score += 3
                missileState = "hidden"
                missileY = 1000
                mid4X[i], mid4Y[i] = reset_enemy_pos(i, "mid4")


    # 4. 미사일 이동 및 그리기
    if missileY <= 0:
        missileY = 1000
        missileState = "hidden"
    
    if missileState == "fire":
        missileY -= missileDy
        display.blit(game_imgs['missile'], (missileX, missileY))

    display.blit(game_imgs['player'], (playerX, playerY))
    
    # UI 표시
    text = myfont.render(f'Score: {score}', False, (255, 255, 255))
    display.blit(text, (10, 550))
    
    stage_text = myfont.render(f'Stage: {game_stage}', False, (255, 255, 255))
    display.blit(stage_text, (350, 50))
    
    pygame.display.update()

pygame.quit()