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
scroll_offset = 0  # Used for scrolling effect

# Load background images for extended map
try:
    background_img = pygame.image.load('j.png')
    background_img = pygame.transform.scale(background_img, (3200, 600))  # Extended width for map
except:
    background_img = None

# Load background music
pygame.mixer.music.load('background_music.mp3')
pygame.mixer.music.play(-1)  # Loop background music indefinitely

# Define platforms and obstacles (extended map)
platforms = [
    pygame.Rect(500, 450, 200, 20),
    pygame.Rect(1000, 425, 200, 20),  # Slightly higher
    pygame.Rect(1500, 400, 200, 20),  # Higher again
    pygame.Rect(2000, 450, 200, 20),  # Back to lower height for variation
    pygame.Rect(2500, 425, 200, 20),  # Slightly higher
]

# Additional platforms with reachable heights
additional_platforms = [
    pygame.Rect(3000, 400, 200, 20), 
    pygame.Rect(3500, 450, 200, 20), 
    pygame.Rect(4000, 425, 200, 20),
    pygame.Rect(4500, 400, 200, 20),
    pygame.Rect(5000, 425, 200, 20),
    pygame.Rect(5500, 450, 200, 20),
    pygame.Rect(6000, 420, 200, 20),
    pygame.Rect(6500, 430, 200, 20),
    pygame.Rect(7000, 440, 200, 20),
    pygame.Rect(7500, 450, 200, 20),
    pygame.Rect(8000, 430, 200, 20),
    pygame.Rect(8500, 420, 200, 20),
    pygame.Rect(9000, 400, 200, 20),
    pygame.Rect(9500, 410, 200, 20),
    pygame.Rect(10000, 415, 200, 20),
    pygame.Rect(10500, 420, 200, 20),
    pygame.Rect(11000, 425, 200, 20),
    pygame.Rect(11500, 430, 200, 20),
    pygame.Rect(12000, 440, 200, 20),
    pygame.Rect(12500, 450, 200, 20),
    pygame.Rect(13000, 420, 200, 20),
    pygame.Rect(13500, 415, 200, 20),
    pygame.Rect(14000, 410, 200, 20),
    pygame.Rect(14500, 400, 200, 20),
    pygame.Rect(15000, 425, 200, 20),
    pygame.Rect(15500, 430, 200, 20),
    pygame.Rect(16000, 440, 200, 20),
    pygame.Rect(16500, 450, 200, 20),
    pygame.Rect(17000, 430, 200, 20),
    pygame.Rect(17500, 420, 200, 20),
    pygame.Rect(18000, 415, 200, 20),
    pygame.Rect(18500, 410, 200, 20),
    pygame.Rect(19000, 400, 200, 20),
    pygame.Rect(19500, 425, 200, 20),
    pygame.Rect(20000, 430, 200, 20),
]

# Add these to the main platform list
platforms += additional_platforms
obstacles = [
    pygame.Rect(800, 520, 30, 30),
    pygame.Rect(1200, 520, 30, 30),
    pygame.Rect(1600, 520, 30, 30),
]

obstacle_gap = 400
additional_obstacles = []
for i in range(20):
    # Reduce the gap slightly with each obstacle to make it progressively harder
    additional_obstacles.append(pygame.Rect(3000 + i * obstacle_gap, 520, 30, 30))
    obstacle_gap = max(100, obstacle_gap - 15)  # Ensure a minimum gap of 100 pixels

# Combine the original obstacles with the newly defined ones
obstacles = [
    pygame.Rect(800, 520, 30, 30),
    pygame.Rect(1200, 520, 30, 30),
    pygame.Rect(1600, 520, 30, 30),
] + additional_obstacles

# Initialize obstacle movement settings
# Expand obstacle speeds and directions for all obstacles
# Updated obstacle speeds and directions with 23 entries (for 23 obstacles in total)
obstacle_speeds = [2, -3, 1, 2, -2, 1, 3, -1, 2, -3, 2, -1, 1, -2, 2, 3, -1, 1, -3, 2, 1, -2, 3]
obstacle_directions = [1, -1, 1, -1, 1, -1, 1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1]


# Initialize score and track Mario's total distance traveled
score = 0
total_distance = 0  # Track total distance traveled for scoring

# Ground settings
ground_y = 550  # Adjust the ground level as needed
ground_rect = pygame.Rect(0, ground_y, 800, 50)  # Create a ground rectangle

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
    global mario_x, mario_y, mario_velocity_y, scroll_offset, on_ground, score, total_distance
    mario_x, mario_y = mario_start_x, mario_start_y
    mario_velocity_y = 0
    scroll_offset = 0
    on_ground = False
    score = 0
    total_distance = 0

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
            total_distance += mario_speed_x  # Increment total distance when moving right only
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
        if mario_y > ground_y - 50:  # Adjust for Mario's height
            mario_y = ground_y - 50
            mario_velocity_y = 0
            on_ground = True

        # Scroll the background when Mario reaches the middle of the screen
        if mario_x > 400:
            scroll_offset -= mario_speed_x
            mario_x = 400

        # Check collision with obstacles
        mario_rect = pygame.Rect(mario_x, mario_y, 50, 50)
        for i, obstacle in enumerate(obstacles):
            obstacle_rect = obstacle.move(scroll_offset, 0)
            if mario_rect.colliderect(obstacle_rect):
                game_over = True
            else:
                # Move obstacles
                obstacles[i] = obstacle.move(obstacle_speeds[i] * obstacle_directions[i], 0)
                if obstacle.left <= 0 or obstacle.right >= 800:
                    obstacle_directions[i] *= -1

        # Update score based on total distance traveled
        score = total_distance // 10  # Adjust the divisor for score scaling

    # Draw background (extended)
    if background_img:
        screen.blit(background_img, (scroll_offset % -3200, 0))
        if scroll_offset % -3200 != 0:
            screen.blit(background_img, ((scroll_offset % -3200) + 3200, 0))
    else:
        screen.fill((255, 255, 255))

    # Draw ground
    pygame.draw.rect(screen, (139, 69, 19), ground_rect)  # Brown color for ground

    # Draw platforms and obstacles
    for platform in platforms:
        platform_rect = platform.move(scroll_offset, 0)
        pygame.draw.rect(screen, (100, 100, 255), platform_rect)  # Blue color for platforms

    for obstacle in obstacles:
        obstacle_rect = obstacle.move(scroll_offset, 0)
        pygame.draw.rect(screen, (255, 0, 0), obstacle_rect)  # Red color for obstacles

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
