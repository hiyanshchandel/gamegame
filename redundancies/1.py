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
mario_start_x, mario_start_y = 400, 500
mario_x, mario_y = mario_start_x, mario_start_y
mario_speed_x = 5
gravity = 1
jump_force = 15
mario_velocity_y = 0
on_ground = False
scroll_offset = 0  # Used for scrolling effect

# Load background images for extended map and colorful scenery
try:
    background_img = pygame.image.load('1.png')
    background_img = pygame.transform.scale(background_img, (3200, 600))  # Extended width for map
except:
    background_img = None

# Load background music
pygame.mixer.music.load('background_music.mp3')
pygame.mixer.music.play(-1)  # Loop background music indefinitely

# Define platforms and obstacles (extended map)
platforms = [
    pygame.Rect(2700, 450, 200, 20),
    pygame.Rect(2900, 400, 200, 20),
    pygame.Rect(3100, 350, 200, 20),
    pygame.Rect(3300, 450, 200, 20),
    pygame.Rect(3500, 300, 200, 20),
    pygame.Rect(3700, 350, 200, 20),
    pygame.Rect(3900, 400, 200, 20),
    pygame.Rect(4100, 450, 200, 20),
    pygame.Rect(4300, 350, 200, 20),
    pygame.Rect(4500, 300, 200, 20),
    pygame.Rect(4700, 400, 200, 20),
    pygame.Rect(4900, 350, 200, 20),
    pygame.Rect(5100, 300, 200, 20),
    pygame.Rect(5300, 450, 200, 20),
    pygame.Rect(5500, 400, 200, 20),
    pygame.Rect(5700, 350, 200, 20),
    pygame.Rect(5900, 450, 200, 20),
    pygame.Rect(6100, 300, 200, 20),
    pygame.Rect(6300, 350, 200, 20),
    pygame.Rect(6500, 400, 200, 20),
    pygame.Rect(6700, 450, 200, 20),
    pygame.Rect(6900, 300, 200, 20),
    pygame.Rect(7100, 350, 200, 20),
    pygame.Rect(7300, 400, 200, 20),
    pygame.Rect(7500, 450, 200, 20),
    pygame.Rect(7700, 300, 200, 20),
    pygame.Rect(7900, 350, 200, 20),
    pygame.Rect(8100, 400, 200, 20),
    pygame.Rect(8300, 450, 200, 20)
    # Add remaining platforms here
]

# Define additional obstacles
obstacles = [
    pygame.Rect(2800, 520, 30, 30),
    pygame.Rect(3000, 520, 30, 30),
    pygame.Rect(3200, 520, 30, 30),
    pygame.Rect(3400, 520, 30, 30),
    pygame.Rect(3600, 520, 30, 30),
    pygame.Rect(3800, 520, 30, 30),
    pygame.Rect(4000, 520, 30, 30),
    pygame.Rect(4200, 520, 30, 30),
    pygame.Rect(4400, 520, 30, 30),
    pygame.Rect(4600, 520, 30, 30),
    pygame.Rect(4800, 520, 30, 30),
    pygame.Rect(5000, 520, 30, 30),
    pygame.Rect(5200, 520, 30, 30),
    pygame.Rect(5400, 520, 30, 30),
    pygame.Rect(5600, 520, 30, 30),
    pygame.Rect(5800, 520, 30, 30),
    pygame.Rect(6000, 520, 30, 30),
    pygame.Rect(6200, 520, 30, 30),
    pygame.Rect(6400, 520, 30, 30),
    pygame.Rect(6600, 520, 30, 30),
    pygame.Rect(6800, 520, 30, 30),
    pygame.Rect(7000, 520, 30, 30),
    pygame.Rect(7200, 520, 30, 30),
    pygame.Rect(7400, 520, 30, 30),
    pygame.Rect(7600, 520, 30, 30),
    pygame.Rect(7800, 520, 30, 30),
    pygame.Rect(8000, 520, 30, 30),
    pygame.Rect(8200, 520, 30, 30),
    pygame.Rect(8400, 520, 30, 30)
    # Add remaining obstacles here
]

# Initialize obstacle movement settings for obstacles
obstacle_speeds = [2, -3, 1, -2, 3, -1, 4, -2, -1, 2, 3, -1, -2, 1, -3, 2, 4, -2, -1, 2, 3, -2, 4, -1, 1, 2, -3, -1, 4, -2]
obstacle_directions = [1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, 1, -1, 1, -1, 1, 1, -1, 1, -1]

# Initialize score
score = 0

# Initialize MediaPipe for pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Open camera for capturing player movements
cap = cv2.VideoCapture(0)

def check_platform_collisions(mario_rect, platforms):
    """Check if Mario lands on a platform."""
    for platform in platforms:
        if mario_rect.colliderect(platform.move(scroll_offset, 0)) and mario_rect.bottom <= platform.bottom:
            return platform.top
    return None

def reset_game():
    """Reset game settings for replay."""
    global mario_x, mario_y, mario_velocity_y, scroll_offset, on_ground, score
    mario_x, mario_y = mario_start_x, mario_start_y
    mario_velocity_y = 0
    scroll_offset = 0
    on_ground = False
    score = 0

# Main game loop
game_over = False
while True:
    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            cap.release()
            sys.exit()
        elif event.type == pygame.KEYDOWN and game_over:  # Restart on any key press if game over
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

        # Scroll the background when Mario reaches the middle of the screen
        if mario_x > 400:
            scroll_offset -= mario_speed_x
            mario_x = 400

        # Check collision with obstacles
        mario_rect = pygame.Rect(mario_x, mario_y, 50, 50)
        for i, obstacle in enumerate(obstacles):
            if mario_rect.colliderect(obstacle.move(scroll_offset, 0)):
                game_over = True
            else:
                # Move obstacles
                obstacles[i] = obstacle.move(obstacle_speeds[i] * obstacle_directions[i], 0)
                if obstacle.left <= 0 or obstacle.right >= 800:
                    obstacle_directions[i] *= -1

        # Update score
        score += 1

    # Draw background (extended)
    if background_img:
        screen.blit(background_img, (scroll_offset % -3200, 0))
        if scroll_offset % -3200 != 0:
            screen.blit(background_img, ((scroll_offset % -3200) + 3200, 0))
    else:
        screen.fill((255, 255, 255))

    # Draw platforms and obstacles
    for platform in platforms:
        pygame.draw.rect(screen, (100, 100, 100), platform.move(scroll_offset, 0))
    for obstacle in obstacles:
        pygame.draw.rect(screen, (255, 0, 0), obstacle.move(scroll_offset, 0))  # Red obstacles

    # Draw Mario character
    screen.blit(mario_img, (mario_x, mario_y))

    # Display camera feed with landmarks
    annotated_frame = frame.copy()
    mp.solutions.drawing_utils.draw_landmarks(annotated_frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    camera_feed = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
    camera_feed = pygame.surfarray.make_surface(camera_feed)
    camera_feed = pygame.transform.scale(camera_feed, (200, 150))
    screen.blit(camera_feed, (0, 0))

    # Display score
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    # Show Game Over message if game over
    if game_over:
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over!", True, (255, 0, 0))
        screen.blit(text, (250, 200))
        font = pygame.font.Font(None, 36)
        text = font.render("Press any key to replay", True, (255, 255, 255))
        screen.blit(text, (250, 300))

    # Update display
    pygame.display.flip()
    clock.tick(30)

# Release resources
cap.release()
cv2.destroyAllWindows()
