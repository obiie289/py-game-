import pygame

import random
# 페이지 2. 만듬 
# 1. 점수에 따른 스테이지 변화 (1->2->3)
# 2. 스테이지 2에서 중간 몹 2종 추가
# 3. 중간 몹은 랜덤으로 움직임
# 4. 스테이지 변화시 배경화면 잠깐 보여주기 
pygame.init()
pygame.font.init()

display = pygame.display.set_mode((800, 600))
myfont = pygame.font.SysFont("Comic Sans MS", 30)
score = 0 

game_stage = 1 
stage_change_time = 0

#------ 외계인 ------
player = pygame.image.load("/Users/Obiie/workspace/1학년/2학기/python3/무제 폴더/game/battleship.png")
player = pygame.transform.scale(player, (60, 60)) 
playerX, playerY, playerDx, playerDy = 400, 530, 0, 0


alien_img = pygame.image.load("/Users/Obiie/workspace/1학년/2학기/python3/무제 폴더/game/alien.png")
alien_img = pygame.transform.scale(alien_img, (40, 40))

mid_alien_img = pygame.image.load("/Users/Obiie/workspace/1학년/2학기/python3/무제 폴더/game/alien2.jpeg")
mid_alien_img = pygame.transform.scale(mid_alien_img, (60, 60))

mid2_alien_img = pygame.image.load("/Users/Obiie/workspace/1학년/2학기/python3/무제 폴더/game/alien3.png")
mid2_alien_img = pygame.transform.scale(mid2_alien_img, (60, 60))

#--------------------

#-------- 배경 ------

background_img = pygame.image.load("/Users/Obiie/workspace/1학년/2학기/python3/무제 폴더/game/background.png")
background_img = pygame.transform.scale(background_img,(800,600))


#--------------------


alienX = []
alienY = []
alienDx = [] #속도 x 
alienDy = [] #속도 y
alienNumber = 12 

midX = [ ]
midY = [ ]
midDx = [ ]
midDy = [ ]
midnumber = 3 

mid2X = [ ]
mid2Y = [ ]
mid2Dx = [ ]
mid2Dy = [ ]
mid2number = 3 



for i in range(alienNumber):
    alienX.append(20 + i * 80) 
    alienY.append(10)
    alienDx.append(3) 
    alienDy.append(0.0)


for i in range(midnumber):
    midX.append(100 + i * 150) #간격
    midY.append(-100) # 윗쪽 (나중에 내려오게)
    midDx.append(2)
    midDy.append(4) 

for i in range(mid2number):
    mid2X.append(150 + i * 300)
    mid2Y.append(-150)
    mid2Dx.append(2)
    mid2Dy.append(4)


missile = pygame.image.load("/Users/Obiie/workspace/1학년/2학기/python3/무제 폴더/game/missile.PNG")
missile = pygame.transform.scale(missile, (30, 30)) 
missileX, missileY, missileDx, missileDy = 0, 1000, 0, 10 
missileState = "hidden"

running = True
clock = pygame.time.Clock() 

while running:
    clock.tick(60) 


    current_time = pygame.time.get_ticks()

    if game_stage == 2 and (current_time - stage_change_time < 5000):
        display.blit(background_img,(0,0))
    else:
        display.fill((0,0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:  playerDx = -5 
            if event.key == pygame.K_RIGHT: playerDx = 5
            if event.key == pygame.K_SPACE:
                if missileState == "hidden":
                    missileState = "fire"
                    missileX = playerX + 15  # 미사일 위치 중앙 보정
                    missileY = playerY
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                playerDx = 0

    playerX += playerDx
    if playerX <= 0: playerX = 0
    if playerX >= 740: playerX = 740


    # ------------------ 기본 몹 ------------------
    for i in range(alienNumber):
        alienX[i] += alienDx[i]
        alienY[i] += alienDy[i]
        
        if alienX[i] <= 0 or alienX[i] > 750:
            alienDx[i] *= -1
            alienY[i] += 30 
        
        alien_rect = pygame.Rect(alienX[i], alienY[i], 40, 40) 
        missile_rect = pygame.Rect(missileX, missileY, 10, 20) 

        if missileState == "fire" and alien_rect.colliderect(missile_rect):
            score += 1
            if score >= 10 and game_stage == 1:
                game_stage = 2 
                stage_change_time = pygame.time.get_ticks()
                print("2 stage")

            if score >= 60 and game_stage == 2 :
                game_stage = 3 
                print("3 stage 보스 출몰 !")
            
            missileState = "hidden"
            missileY = 1000
            
            alienX[i] = 20 + i * 80
            alienY[i] = 10
            alienDx[i] = 3 

        display.blit(alien_img, (alienX[i], alienY[i]))

    # ------------------  첫번째 중간 몹  ------------------
    if game_stage >= 2:
        for i in range(midnumber):
            midX[i] += midDx[i]
            midY[i] += midDy[i]

            # 랜던 이동
            if random.randint(1,100) <= 60:
                midY[i] += -1 # 위로  반대 이동
                midX[i] += 2
            #

            # 벽 충돌
            if midX[i] <= 0 or midX[i] > 720:
                midDx[i] *= -1 
                midY[i] += 40 
            
            if midY[i] > 100:
                midY[i] += 1
            
            if missileState == "fire" and alien_rect.colliderect(missile_rect):
                score += 1


            # ---------- 두번째 중간 몹 

            mid2X[i] += mid2Dx[i]
            mid2Y[i] += mid2Dy[i]
            #랜덤 이동
            if random.randint(1,100) <= 65:
                mid2Y[i] += -5 
                mid2X[i] += -3

            #

            if mid2X[i] <= 0 or mid2X[i] >729 :
                mid2Dx[i] *= -1 
                mid2Y[i] += 40

            if mid2Y[i] < 10 :
                mid2Y[i] += 1
            #--------------------------
            #1
            display.blit(mid_alien_img, (midX[i], midY[i]))
            #2
            display.blit( mid2_alien_img,(mid2X[i], mid2Y[i]))
            # --------------------------

            # 충돌 처리
            missile_rect = pygame.Rect(missileX, missileY, 10 , 30)

            #1 번째 중간 몹
            mid_rect = pygame.Rect(midX[i], midY[i], 60, 60)
            if missileState == "fire" and mid_rect.colliderect(missile_rect):
                score += 5 
                missileState = "hidden"
                missileY = 1000
                midX[i] = 100 + i * 150
                midY[i] = -100

            #2 번째 중간 몹
            mid2_rect = pygame.Rect(mid2X[i], mid2Y[i], 60,60)
            if missileState == "fire" and mid2_rect.colliderect(missile_rect):
                score += 4
                missileState = "hidden"
                missileY = 3000
                mid2X[i] = 150 + i * 300 
                mid2Y[i] = -100 
    # -------------------------------------------------------------

    if missileY <= 0: 
        missileY = 1000
        missileState = "hidden"

    if missileState == "fire": 
        missileY -= missileDy 

    display.blit(player, (playerX, playerY))
    
    if missileState == "fire":
        display.blit(missile, (missileX, missileY))
    
    text = myfont.render(f'Score: {score}', False, (255, 255, 255))
    display.blit(text, (10, 550))

    stage_text = myfont.render(f'Stage: {game_stage}', False, (255,255,255))
    display.blit(stage_text, (350, 100)) 
    
    pygame.display.update()

pygame.quit()