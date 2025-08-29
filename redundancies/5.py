import cv2
import mediapipe as mp
import pygame
import random
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

# Initialize platform and obstacle lists
platforms = [pygame.Rect(300, 450, 200, 20)]
obstacles = []

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

def generate_platform():
    """Generate a new platform at a random height and distance to the right."""
    x = 800 + random.randint(100, 300)
    y = random.randint(300, ground_y - 50)
    width = random.randint(150, 250)
    return pygame.Rect(x, y, width, 20)

def generate_obstacle():
    """Generate a new obstacle at a random position on the next platform."""
    x = 800 + random.randint(100, 300)
    y = ground_y - 30  # Place it just above the ground
    return pygame.Rect(x, y, 30, 30)

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
    platforms.clear()
    platforms.append(pygame.Rect(300, 450, 200, 20))
    obstacles.clear()

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
            distance_traveled += mario_speed_x  # Update distance traveled
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

        # Scroll the background and generate new platforms/obstacles as Mario advances
        if mario_x > 400:
            scroll_offset -= mario_speed_x
            mario_x = 400

        # Generate new platforms and obstacles periodically
        if len(platforms) < 5:
            platforms.append(generate_platform())
        if len(obstacles) < 3:
            obstacles.append(generate_obstacle())

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

    for obstacle in obstacles:
        obstacle_rect = obstacle.move(scroll_offset, 0)
        pygame.draw.rect(screen, (255, 0, 0), obstacle_rect)

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
