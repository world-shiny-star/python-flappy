import pygame
import sys
import os
import random

pygame.init()
pygame.display.set_caption("Dragon Flappy Game")

window_width, window_height = 800, 600
window = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE, vsync=1)

main_font = pygame.font.SysFont("arial", 32, bold=True, italic=True)
small_font = pygame.font.SysFont("arial", 24, bold=True, italic=True)

clock = pygame.time.Clock()
fps = 60

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_BLUE = (50, 150, 255)
COLOR_GRAY = (180, 180, 180)
COLOR_RED = (255, 0, 0)

STATE_MENU = "menu"
STATE_INTRO = "intro"
STATE_PLAY = "play"

current_state = STATE_MENU

def load_image(name, size=None):
    if not os.path.isfile(name):
        print(f"Warning: '{name}' not found, using red box instead.")
        surf = pygame.Surface(size if size else (50, 50))
        surf.fill(COLOR_RED)
        return surf
    img = pygame.image.load(name).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img

background_img = load_image("download.png", (window_width, window_height))
dragon_img = load_image("dragon.png", (60, 40))
obstacle_img = load_image("obstacle.png", (70, 300))

def draw_text(text, font, color, x, y, center=True):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    window.blit(surf, rect)

def draw_button(rect, text, base_color, hover_color, mouse_pos):
    color = hover_color if rect.collidepoint(mouse_pos) else base_color
    pygame.draw.rect(window, color, rect, border_radius=8)
    draw_text(text, main_font, COLOR_WHITE, rect.centerx, rect.centery)

def resize_background(new_w, new_h):
    global background_img
    if background_img:
        background_img = pygame.transform.scale(background_img, (new_w, new_h))

def gameplay_loop():
    global window_width, window_height, window, background_img

    dragon_x = window_width // 6
    dragon_y = window_height // 2
    velocity = 0
    gravity = 0.5
    jump_strength = -9
    score = 0

    # store obstacles as dicts with a 'passed' flag
    obstacles = []
    obstacle_speed = 4
    gap_size = 170
    spawn_delay = 1500  # milliseconds
    last_spawn = pygame.time.get_ticks()

    font_score = pygame.font.SysFont("arial", 28, bold=True)
    running = True

    while running:
        dt = clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    velocity = jump_strength
            if event.type == pygame.VIDEORESIZE:
                window_width, window_height = event.w, event.h
                window = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
                resize_background(window_width, window_height)

        velocity += gravity
        dragon_y += velocity

        now = pygame.time.get_ticks()
        if now - last_spawn > spawn_delay:
            last_spawn = now
            gap_y = random.randint(150 + gap_size, window_height - 150)
            top_rect = pygame.Rect(window_width, gap_y - gap_size - obstacle_img.get_height(), obstacle_img.get_width(), obstacle_img.get_height())
            bottom_rect = pygame.Rect(window_width, gap_y, obstacle_img.get_width(), obstacle_img.get_height())
            obstacles.append({'top': top_rect, 'bottom': bottom_rect, 'passed': False})

        # Move obstacles left
        for ob in obstacles:
            ob['top'].x -= obstacle_speed
            ob['bottom'].x -= obstacle_speed

        dragon_rect = pygame.Rect(dragon_x, dragon_y, dragon_img.get_width(), dragon_img.get_height())

        # Score update: increment once per obstacle using the passed flag
        for ob in obstacles:
            if not ob['passed'] and ob['top'].right < dragon_x:
                score += 1
                ob['passed'] = True

        # Remove off-screen obstacles
        obstacles = [ob for ob in obstacles if ob['top'].right > 0]

        # Collision detection
        for ob in obstacles:
            if dragon_rect.colliderect(ob['top']) or dragon_rect.colliderect(ob['bottom']):
                running = False
        if dragon_y < 0 or dragon_y + dragon_img.get_height() > window_height:
            running = False

        # Draw everything
        if background_img:
            window.blit(background_img, (0, 0))
        else:
            window.fill(COLOR_BLACK)

        window.blit(dragon_img, (dragon_x, dragon_y))

        for ob in obstacles:
            window.blit(obstacle_img, ob['top'].topleft)
            window.blit(obstacle_img, ob['bottom'].topleft)

        draw_text(f"Score: {score}", font_score, COLOR_WHITE, 10, 10, center=False)

        pygame.display.flip()

    pygame.time.delay(1500)

def main_loop():
    global current_state, window_width, window_height, window
    running = True

    while running:
        clock.tick(fps)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.VIDEORESIZE:
                window_width, window_height = event.w, event.h
                window = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
                resize_background(window_width, window_height)

            if event.type == pygame.MOUSEBUTTONDOWN:
                click_x, click_y = event.pos
                if current_state == STATE_MENU:
                    play_btn = pygame.Rect(0, 0, window_width // 3, window_height // 10)
                    intro_btn = pygame.Rect(0, 0, window_width // 3, window_height // 10)
                    quit_btn = pygame.Rect(0, 0, window_width // 3, window_height // 10)
                    play_btn.center = (window_width // 2, window_height // 2 - window_height // 8)
                    intro_btn.center = (window_width // 2, window_height // 2)
                    quit_btn.center = (window_width // 2, window_height // 2 + window_height // 8)

                    if play_btn.collidepoint(click_x, click_y):
                        current_state = STATE_PLAY
                    elif intro_btn.collidepoint(click_x, click_y):
                        current_state = STATE_INTRO
                    elif quit_btn.collidepoint(click_x, click_y):
                        running = False

                elif current_state == STATE_INTRO:
                    back_btn = pygame.Rect(window_width // 50, window_height - window_height // 8, window_width // 6, window_height // 12)
                    if back_btn.collidepoint(click_x, click_y):
                        current_state = STATE_MENU

        if background_img:
            window.blit(background_img, (0, 0))
        else:
            window.fill(COLOR_BLACK)

        if current_state == STATE_MENU:
            draw_text("Main Menu", main_font, COLOR_WHITE, window_width // 2, window_height // 6)
            play_btn = pygame.Rect(0, 0, window_width // 3, window_height // 10)
            intro_btn = pygame.Rect(0, 0, window_width // 3, window_height // 10)
            quit_btn = pygame.Rect(0, 0, window_width // 3, window_height // 10)

            play_btn.center = (window_width // 2, window_height // 2 - window_height // 8)
            intro_btn.center = (window_width // 2, window_height // 2)
            quit_btn.center = (window_width // 2, window_height // 2 + window_height // 8)

            draw_button(play_btn, "Play", COLOR_BLUE, COLOR_GRAY, mouse_pos)
            draw_button(intro_btn, "Intro", COLOR_BLUE, COLOR_GRAY, mouse_pos)
            draw_button(quit_btn, "Quit", COLOR_BLUE, COLOR_GRAY, mouse_pos)

        elif current_state == STATE_INTRO:
            draw_text("Intro Screen", main_font, COLOR_WHITE, window_width // 2, window_height // 8)
            intro_lines = [
                "Welcome to the Dragon Flappy Game!",
                "Press Space to jump during gameplay.",
                "Avoid the obstacles to survive.",
                "Press ESC to quit gameplay.",
                "Click Back to return to menu."
            ]
            for i, line in enumerate(intro_lines):
                draw_text(line, small_font, COLOR_WHITE, window_width // 2, window_height // 4 + i * 30)

            back_btn = pygame.Rect(window_width // 50, window_height - window_height // 8, window_width // 6, window_height // 12)
            draw_button(back_btn, "Back", COLOR_BLUE, COLOR_GRAY, mouse_pos)

        elif current_state == STATE_PLAY:
            gameplay_loop()
            current_state = STATE_MENU

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_loop()
