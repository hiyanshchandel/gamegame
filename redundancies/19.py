import cv2
import mediapipe as mp
import pygame
import sys
import random

# Initialize Pygame and screen settings
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Load Mario character and set initial position
mario_img = pygame.image.load('mario.png')
mario_img = pygame.transform.scale(mario_img, (50, 50))
obstacle_img = pygame.image.load('obstacle.png')

# Background image
try:
    background_img = pygame.image.load('im1.png')
    background_img = pygame.transform.scale(background_img, (1600, 600))
except:
    background_img = None

# Load background music
try:
    pygame.mixer.music.load('background_music.mp3')
    pygame.mixer.music.play(-1)
except:
    print("Background music file not found")

# Mario physics variables
mario_start_x, mario_start_y = 400, 500
mario_x, mario_y = mario_start_x, mario_start_y
mario_speed_x = 5
gravity = 1
jump_force = 15
mario_velocity_y = 0
on_ground = False
scroll_offset = 0

# Platforms & obstacles
platforms = [pygame.Rect(500, 450, 200, 20), pygame.Rect(1000, 425, 200, 20), pygame.Rect(1500, 400, 200, 20)]
obstacles = [pygame.Rect(800, 520, 30, 30), pygame.Rect(1200, 520, 30, 30), pygame.Rect(1600, 520, 30, 30)]

obstacle_gap = 400
platform_gap = 500
obstacle_speeds, obstacle_directions, obstacle_movement_ranges = [], [], []
for obs in obstacles:
    speed = random.uniform(2, 4)
    direction = random.choice([-1, 1])
    range_limit = random.randint(100, 300)
    obstacle_speeds.append(speed)
    obstacle_directions.append(direction)
    obstacle_movement_ranges.append({'start': obs.x - range_limit, 'end': obs.x + range_limit, 'initial_x': obs.x})

# Ground
ground_y = 550
ground_rect = pygame.Rect(0, ground_y, 800, 50)

# MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
cap = cv2.VideoCapture(0)

# Score
score = 0
total_distance = 0

# Game states
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
game_state = STATE_MENU


def check_platform_collisions(mario_rect, platforms):
    for platform in platforms:
        platform_rect = platform.move(scroll_offset, 0)
        if mario_rect.colliderect(platform_rect) and mario_rect.bottom <= platform_rect.bottom:
            return platform.top
    return None


def reset_game():
    global mario_x, mario_y, mario_velocity_y, scroll_offset, on_ground, score, total_distance, platforms, obstacles, obstacle_speeds, obstacle_directions, obstacle_movement_ranges
    mario_x, mario_y = mario_start_x, mario_start_y
    mario_velocity_y = 0
    scroll_offset = 0
    on_ground = False
    score = 0
    total_distance = 0
    platforms = [pygame.Rect(500, 450, 200, 20), pygame.Rect(1000, 425, 200, 20), pygame.Rect(1500, 400, 200, 20)]
    obstacles = [pygame.Rect(800, 520, 30, 30), pygame.Rect(1200, 520, 30, 30), pygame.Rect(1600, 520, 30, 30)]
    obstacle_speeds, obstacle_directions, obstacle_movement_ranges = [], [], []
    for obs in obstacles:
        speed = random.uniform(2, 4)
        direction = random.choice([-1, 1])
        range_limit = random.randint(100, 300)
        obstacle_speeds.append(speed)
        obstacle_directions.append(direction)
        obstacle_movement_ranges.append({'start': obs.x - range_limit, 'end': obs.x + range_limit, 'initial_x': obs.x})

def draw_text(surface, text, font, color, x, y, outline_color=(0,0,0)):
    # Render outline
    text_surface = font.render(text, True, outline_color)
    for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
        surface.blit(text_surface, (x+dx, y+dy))
    # Render main text
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))


# --- Menu Screen ---
def draw_menu():
    screen.fill((0, 0, 0))
    if background_img:
        screen.blit(background_img, (0, 0))

    title_font = pygame.font.Font(pygame.font.match_font('couriernew'), 100)
    option_font = pygame.font.Font(pygame.font.match_font('couriernew'), 40)

    title = title_font.render("Mario Runner", True, (255, 215, 0))
    screen.blit(title, (150, 150))

    draw_text(screen, "Press ENTER to Start", option_font, (255,255,0), 200, 300)  # yellow with black outline
    draw_text(screen, "Move with Hands or Arrow Keys", option_font, (0,0,255), 100, 380)  # blue
    draw_text(screen, "Jump: Raise Both Hands / SPACE", option_font, (255,0,0), 100, 430)  # red



# Main game loop
game_over = False
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            cap.release()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if game_state == STATE_MENU and event.key == pygame.K_RETURN:
                reset_game()
                game_state = STATE_PLAYING
            elif game_state == STATE_GAME_OVER:
                reset_game()
                game_state = STATE_PLAYING

    if game_state == STATE_MENU:
        draw_menu()
        pygame.display.flip()
        clock.tick(30)
        continue

    # Camera input
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb_frame)

    move_right, move_left, jump = False, False, False

    if result.pose_landmarks:
        landmarks = result.pose_landmarks.landmark
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

        if right_wrist.x > right_shoulder.x:
            move_right = True
        elif left_wrist.x < left_shoulder.x:
            move_left = True

        if (left_wrist.y < left_shoulder.y and right_wrist.y < right_shoulder.y) and on_ground:
            jump = True

    # Keyboard fallback
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        move_right = True
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        move_left = True
    if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and on_ground:
        jump = True

    if game_state == STATE_PLAYING:
        if move_right:
            mario_x += mario_speed_x
            total_distance += mario_speed_x
        if move_left:
            mario_x -= mario_speed_x
        if jump:
            mario_velocity_y = -jump_force
            on_ground = False

        mario_velocity_y += gravity
        mario_y += mario_velocity_y

        mario_rect = pygame.Rect(mario_x, mario_y, 50, 50)
        platform_top = check_platform_collisions(mario_rect, platforms)
        if platform_top is not None:
            mario_y = platform_top - 50
            mario_velocity_y = 0
            on_ground = True

        if mario_y > ground_y - 50:
            mario_y = ground_y - 50
            mario_velocity_y = 0
            on_ground = True

        if mario_x > 400:
            scroll_offset -= mario_speed_x
            mario_x = 400

        # Spawn new obstacles dynamically
        if obstacles:
            last_obstacle_x = obstacles[-1].x
            if mario_x - scroll_offset > last_obstacle_x - 2000:
                new_x = last_obstacle_x + obstacle_gap
                new_obstacle = pygame.Rect(new_x, 520, 30, 30)
                obstacles.append(new_obstacle)

                speed = random.uniform(2, 4)
                direction = random.choice([-1, 1])
                range_limit = random.randint(100, 300)
                obstacle_speeds.append(speed)
                obstacle_directions.append(direction)
                obstacle_movement_ranges.append({'start': new_obstacle.x - range_limit, 'end': new_obstacle.x + range_limit, 'initial_x': new_obstacle.x})

        # Spawn new platforms dynamically
        if platforms:
            last_platform_x = platforms[-1].x
            if mario_x - scroll_offset > last_platform_x - 2000:
                new_x = last_platform_x + platform_gap
                new_y = random.randint(350, 500)
                new_platform = pygame.Rect(new_x, new_y, 200, 20)
                platforms.append(new_platform)

        # Move obstacles & check collision
        for i, obstacle in enumerate(obstacles):
            obstacle_rect = obstacle.move(scroll_offset, 0)
            if mario_rect.colliderect(obstacle_rect):
                game_state = STATE_GAME_OVER

            current_x = obstacles[i].x
            movement = obstacle_speeds[i] * obstacle_directions[i]
            new_x = current_x + movement

            if new_x <= obstacle_movement_ranges[i]['start']:
                obstacle_directions[i] = 1
                new_x = obstacle_movement_ranges[i]['start']
            elif new_x >= obstacle_movement_ranges[i]['end']:
                obstacle_directions[i] = -1
                new_x = obstacle_movement_ranges[i]['end']

            obstacles[i].x = new_x

        score = total_distance // 10

    # --- Drawing ---
    if background_img:
        x_position = scroll_offset % -background_img.get_width()
        screen.blit(background_img, (x_position, 0))
        if x_position + background_img.get_width() < 800:
            screen.blit(background_img, (x_position + background_img.get_width(), 0))
    else:
        screen.fill((255, 255, 255))

    pygame.draw.rect(screen, (139, 69, 19), ground_rect)

    for platform in platforms:
        platform_rect = platform.move(scroll_offset, 0)
        pygame.draw.rect(screen, (100, 100, 255), platform_rect)

    for obstacle in obstacles:
        obstacle_rect = obstacle.move(scroll_offset, 0)
        screen.blit(obstacle_img, (obstacle_rect.x, obstacle_rect.y))

    screen.blit(mario_img, (mario_x, mario_y))

    font = pygame.font.Font(pygame.font.match_font('couriernew'), 60)
    text = font.render(f"Score: {score}", True, (128, 0, 128))
    screen.blit(text, (screen.get_width() - 250, 10))

    # Camera overlay
    annotated_frame = frame.copy()
    mp.solutions.drawing_utils.draw_landmarks(annotated_frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    camera_feed = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
    camera_feed = pygame.surfarray.make_surface(camera_feed)
    camera_feed = pygame.transform.rotate(camera_feed, -90)
    camera_feed = pygame.transform.flip(camera_feed, True, False)
    camera_feed = pygame.transform.scale(camera_feed, (200, 150))
    screen.blit(camera_feed, (0, 0))

    if game_state == STATE_GAME_OVER:
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over!", True, (255, 0, 0))
        screen.blit(text, (250, 200))
        font = pygame.font.Font(None, 36)
        text = font.render("Press any key to restart", True, (255, 255, 255))
        screen.blit(text, (250, 300))

    pygame.display.flip()
    clock.tick(30)
