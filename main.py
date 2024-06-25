import random
import pygame
from Classes import *

pygame.init()
pygame.font.init()
#background_music = pygame.mixer.music.play(TRANCE_LOOP)
pygame.mixer.music.set_volume(0.055)

def main():
    run = True
    FPS = 60
    level = 0
    invades = 5
    main_font = pygame.font.SysFont("comicsans", 30)
    lost_font = pygame.font.SysFont("comicsans", 60)
    player_vel = 7.2
    player = Player(WIDTH/2 - PLAYER_SHIP.get_width()/2 - 20, HEIGHT - PLAYER_SHIP.get_height() - 80)
    lost = False
    lost_count = 0
    enemies = []
    wave_length = 10
    enemy_vel, package_vel = 1, 1.2
    laser_vel = 8
    packages = []
    boss = None
    level_player_collide_triple_shot = 0
    p_enemy_shoot = 0.005
    clock = pygame.time.Clock()
    def redraw_window():
        WIN.blit(BG, (0, 0))
        # draw text
        lives_label = main_font.render(f"Invades : {invades}", 1, (255, 0, 0))
        level_label = main_font.render(f"Level : {level}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level : {level}", 1, (255, 255, 255))
        score_label = main_font.render(f"Score : {player.score}", 1, (0, 255, 170))
        WIN.blit(score_label, (WIDTH / 2 - score_label.get_width() / 2 - 10, 15))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        for enemy in enemies:
            enemy.draw(WIN)
        for pack in packages:
            pack.draw(WIN)
        player.draw(WIN)
        if lost:
            lost_label = lost_font.render("Game Over !!!", 1, (0, 150, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))
        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if invades <= 0 or player.health <= 0 or lost:
            lost = True
            lost_count += 1

        if lost:
            if lost_count >= FPS * 2:
                run = False
            else:
                continue

        if len(enemies) == 0:   # finished level
            level += 1
            wave_length += 2
            p_enemy_shoot += 0.003
            if level > 1:
                if player.health < 100 and player.health >= 80:
                    player.health = 100
                if player.health < 80:
                    player.health += 20
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(['red', 'blue', 'green']))
                enemies.append(enemy)
            if level > 2 and level % 2 == 1:
                boss = Boss(random.randrange(int(WIDTH * 0.25), int(WIDTH * 0.75)), random.randrange(100, 300),
                            random.choice(['grey']), 400)
                enemies.append(boss)
            if player.pack_flag['triple_shot']:
                player.pack_flag['triple_shot'] = False
            if player.pack_flag['shield']:
                player.pack_flag['shield'] = False
            '''if player.pack_flag['triple_shot']:      # keep the package for 2 levels
                player.pack_duration['triple_shot'] += 1
                if player.pack_duration['triple_shot'] > 1:
                    player.pack_duration['triple_shot'] = 0
                    player.pack_flag['triple_shot'] = False
            if player.pack_flag['shield']:
                player.pack_duration['shield'] += 1
                if player.pack_duration['shield'] > 1:
                    player.pack_duration['shield'] = 0
                    player.pack_flag['shield'] = False'''

        if len(packages) == 0 and level > 2 and level % 2 == 1:
        #if True:
            package = Package(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(['hp', 'triple_laser', 'shield']))
            packages.append(package)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width < WIDTH:  # right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height + 20 < HEIGHT:  # down
            player.y += player_vel
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_SPACE]:
            if player.cooldown_meter < player.ship_img.get_width():
                if player.pack_flag['triple_shot']:
                    player.triple_shot()
                else:
                    player.shoot()
        if not keys[pygame.K_SPACE]:
            if player.cooldown_meter >= 0:
                player.cooldown_meter -= 0.6

        for pack in packages:
            pack.move(package_vel)
            if collide(pack, player):
                if pack.type == 'hp':
                    if player.health < 100:
                        player.health = 100
                        packages.remove(pack)
                if not player.pack_flag['triple_shot']:
                    if pack.type == 'triple_laser':
                        player.pack_flag['triple_shot'] = True
                        packages.remove(pack)
                if not player.pack_flag['shield']:
                    if pack.type == 'shield':
                        player.pack_flag['shield'] = True
                        packages.remove(pack)
            if pack.y + pack.get_height > HEIGHT:
                packages.remove(pack)

        for enemy in enemies[:]:
            if isinstance(enemy, Boss):
                enemy.move()
            else:
                enemy.move(enemy_vel)
            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
            enemy.move_lasers(laser_vel, player)
            if collide(enemy, player):
                if isinstance(enemy, Enemy):
                    player.health -= 15
                    enemies.remove(enemy)
                else: lost = True           # player collided with boss
            if isinstance(enemy, Enemy) and enemy.y + enemy.get_height > HEIGHT:
                invades -= 1
                enemies.remove(enemy)

        player.move_lasers(-(laser_vel + 3), enemies)

def instructions_screen():
    instructions_font = pygame.font.SysFont("comicsans", 30)
    instructions_flag = True
    instruction_1 = instructions_font.render("~ Use Arrows to move the spaceship ~", 1, (255, 255, 255))
    instruction_2 = instructions_font.render("~ Press Spacebar to shoot lasers ~", 1, (255, 255, 255))
    instruction_3 = instructions_font.render("~ Destroy all enemies before they invade your planet ! ~", 1,
                                             (255, 255, 255))
    while instructions_flag:
        WIN.blit(BG, (0, 0))
        WIN.blit(instruction_1, (WIDTH / 2 - instruction_2.get_width() / 2 - 40, 300))
        WIN.blit(instruction_2, (WIDTH / 2 - instruction_1.get_width() / 2, 400))
        WIN.blit(instruction_3, (WIDTH / 2 - instruction_3.get_width() / 2, 500))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                instructions_flag = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.mixer.music.play(-1)
                main()
                return

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 30)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label1 = title_font.render("Welcome to Space Invaders Pro !!!", 1, (255, 255, 255))
        title_label2 = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
        WIN.blit(title_label1, (WIDTH / 2 - title_label1.get_width() / 2 - 20, 300))
        WIN.blit(title_label2, (WIDTH / 2 - title_label1.get_width() / 2 + 30, 500))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                #run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                instructions_screen()
                break

    pygame.quit()

main_menu()
