import cv2
import mediapipe as mp
import pygame
import sys

# Initialize Pygame and screen settings
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Load Mario character and set initial position
mario_img = pygame.image.load('mario.png')
mario_img = pygame.transform.scale(mario_img, (50, 50))
mario_start_x, mario_start_y = 400, 500
mario_x, mario_y = mario_start_x, mario_start_y
mario_speed_x = 5
gravity = 1
jump_force = 15
mario_velocity_y = 0
on_ground = False
scroll_offset = 0

# Load background images for extended map
try:
    background_img = pygame.image.load('j.png')
    background_img = pygame.transform.scale(background_img, (3200, 600))
except:
    background_img = None

# Load background music
pygame.mixer.music.load('background_music.mp3')
pygame.mixer.music.play(-1)

# Define 40 hardcoded platforms with varying distances and heights
platforms = [
    pygame.Rect(300, 450, 200, 20),
    pygame.Rect(800, 400, 200, 20),
    pygame.Rect(1300, 450, 200, 20),
    pygame.Rect(1800, 350, 200, 20),
    pygame.Rect(2300, 500, 200, 20),
    pygame.Rect(2800, 400, 200, 20),
    pygame.Rect(3300, 450, 200, 20),
    pygame.Rect(3800, 300, 200, 20),
    pygame.Rect(4300, 500, 200, 20),
    pygame.Rect(4800, 350, 200, 20),
    pygame.Rect(5300, 450, 200, 20),
    pygame.Rect(5800, 500, 200, 20),
    pygame.Rect(6300, 400, 200, 20),
    pygame.Rect(6800, 450, 200, 20),
    pygame.Rect(7300, 300, 200, 20),
    pygame.Rect(7800, 500, 200, 20),
    pygame.Rect(8300, 350, 200, 20),
    pygame.Rect(8800, 450, 200, 20),
    pygame.Rect(9300, 400, 200, 20),
    pygame.Rect(9800, 500, 200, 20),
    pygame.Rect(10300, 350, 200, 20),
    pygame.Rect(10800, 450, 200, 20),
    pygame.Rect(11300, 500, 200, 20),
    pygame.Rect(11800, 400, 200, 20),
    pygame.Rect(12300, 300, 200, 20),
    pygame.Rect(12800, 450, 200, 20),
    pygame.Rect(13300, 500, 200, 20),
    pygame.Rect(13800, 350, 200, 20),
    pygame.Rect(14300, 450, 200, 20),
    pygame.Rect(14800, 500, 200, 20),
    pygame.Rect(15300, 400, 200, 20),
    pygame.Rect(15800, 450, 200, 20),
    pygame.Rect(16300, 300, 200, 20),
    pygame.Rect(16800, 500, 200, 20),
    pygame.Rect(17300, 350, 200, 20),
    pygame.Rect(17800, 450, 200, 20),
    pygame.Rect(18300, 500, 200, 20),
    pygame.Rect(18800, 400, 200, 20),
    pygame.Rect(19300, 450, 200, 20),
]

# Define obstacles on specific platforms
obstacles = [
    pygame.Rect(900, 370, 30, 30),
    pygame.Rect(1850, 320, 30, 30),
    pygame.Rect(4350, 470, 30, 30),
    pygame.Rect(9800, 470, 30, 30),
    pygame.Rect(15800, 420, 30, 30),
]

# Initialize score and distance tracking
score = 0
distance_traveled = 0

# Ground settings
ground_y = 550
ground_rect = pygame.Rect(0, ground_y, 800, 50)

# Initialize MediaPipe for pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Open camera for capturing player movements
cap = cv2.VideoCapture(0)

def check_platform_collisions(mario_rect, platforms):
    """Check if Mario lands on a platform."""
    for platform in platforms:
        platform_rect = platform.move(scroll_offset, 0)
        if mario_rect.colliderect(platform_rect) and mario_rect.bottom <= platform_rect.bottom:
            return platform.top
    return None

def reset_game():
    """Reset game settings for replay."""
    global mario_x, mario_y, mario_velocity_y, scroll_offset, on_ground, score, distance_traveled
    mario_x, mario_y = mario_start_x, mario_start_y
    mario_velocity_y = 0
    scroll_offset = 0
    on_ground = False
    score = 0
    distance_traveled = 0

# Main game loop
game_over = False
while True:
    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            cap.release()
            sys.exit()
        elif event.type == pygame.KEYDOWN and game_over:
            reset_game()
            game_over = False

    # Read frame from the camera and process with MediaPipe
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb_frame)

    # Set movement variables
    move_right, move_left, jump = False, False, False

    # Gesture recognition for movement and jump
    if result.pose_landmarks:
        landmarks = result.pose_landmarks.landmark
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

        # Detect right/left movement
        if right_wrist.x > right_shoulder.x:
            move_right = True
        elif left_wrist.x < left_shoulder.x:
            move_left = True

        # Detect jump when wrists are raised
        if (left_wrist.y < left_shoulder.y and right_wrist.y < right_shoulder.y) and on_ground:
            jump = True

    # Update Mario's position
    if not game_over:
        if move_right:
            mario_x += mario_speed_x
            distance_traveled += mario_speed_x
        if move_left:
            mario_x -= mario_speed_x
        if jump:
            mario_velocity_y = -jump_force
            on_ground = False

        # Apply gravity
        mario_velocity_y += gravity
        mario_y += mario_velocity_y

        # Platform collision detection
        platform_top = check_platform_collisions(pygame.Rect(mario_x, mario_y, 50, 50), platforms)
        if platform_top is not None:
            mario_y = platform_top - 50
            mario_velocity_y = 0
            on_ground = True
        else:
            on_ground = False

        # Ground collision detection
        if mario_y > ground_y - 50:
            mario_y = ground_y - 50
            mario_velocity_y = 0
            on_ground = True

        # Scroll the background when Mario reaches the middle of the screen
        if mario_x > 400:
            scroll_offset -= mario_speed_x
            mario_x = 400

        # Check collision with obstacles
        mario_rect = pygame.Rect(mario_x, mario_y, 50, 50)
        for obstacle in obstacles:
            obstacle_rect = obstacle.move(scroll_offset, 0)
            if mario_rect.colliderect(obstacle_rect):
                game_over = True

        # Update score based on distance traveled
        score = distance_traveled // 10

    # Draw background (extended)
    if background_img:
        screen.blit(background_img, (scroll_offset % -3200, 0))
        if scroll_offset % -3200 != 0:
            screen.blit(background_img, ((scroll_offset % -3200) + 3200, 0))
    else:
        screen.fill((255, 255, 255))

    # Draw ground
    pygame.draw.rect(screen, (139, 69, 19), ground_rect)

    # Draw platforms and obstacles
    for platform in platforms:
        platform_rect = platform.move(scroll_offset, 0)
        pygame.draw.rect(screen, (100, 100, 255), platform_rect)

   
