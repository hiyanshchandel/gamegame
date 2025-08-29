# Load sad meow sound effect for player death
try:
    sad_meow = pygame.mixer.Sound('sad-meow-song.mp3')
except:
    print("Sad meow sound file not found")
    sad_meow = None
import cv2
import mediapipe as mp
import pygame
import sys
import random
import math

# Initialize Pygame and screen settings
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
SCREEN_WIDTH = screen.get_width()
SCREEN_HEIGHT = screen.get_height()
pygame.display.set_caption("Mario Game - Gesture Controlled")

# Texture generation functions for Jump King style blocks
def create_stone_texture(width, height, base_color=(120, 100, 80)):
    """Create a stone texture similar to Jump King with better seamless tiling"""
    texture = pygame.Surface((width, height))
    
    # Base color fill
    texture.fill(base_color)
    
    # Add noise and variation with position-based smoothing for seamless tiling
    for y in range(height):
        for x in range(width):
            # Create stone-like variation with smoother transitions
            position_noise = math.sin(x * 0.4) * math.cos(y * 0.3) * 12
            random_noise_r = random.randint(-15, 15)
            random_noise_g = random.randint(-12, 12)  
            random_noise_b = random.randint(-10, 10)
            
            total_noise_r = int(position_noise + random_noise_r)
            total_noise_g = int(position_noise * 0.8 + random_noise_g)
            total_noise_b = int(position_noise * 0.6 + random_noise_b)
            
            r = max(0, min(255, base_color[0] + total_noise_r))
            g = max(0, min(255, base_color[1] + total_noise_g))
            b = max(0, min(255, base_color[2] + total_noise_b))
            
            # Add some stone patterns (less frequent for subtlety)
            if random.random() < 0.08:  # Stone grain
                r = max(0, r - 25)
                g = max(0, g - 20)
                b = max(0, b - 15)
            elif random.random() < 0.06:  # Lighter spots
                r = min(255, r + 30)
                g = min(255, g + 25)
                b = min(255, b + 20)
                
            texture.set_at((x, y), (r, g, b))
    
    # Add fewer, more subtle crack lines
    for _ in range(random.randint(1, 3)):
        start_x = random.randint(0, width-1)
        start_y = random.randint(0, height-1)
        end_x = start_x + random.randint(-15, 15)
        end_y = start_y + random.randint(-8, 8)
        end_x = max(0, min(width-1, end_x))
        end_y = max(0, min(height-1, end_y))
        
        crack_color = (max(0, base_color[0] - 25), max(0, base_color[1] - 20), max(0, base_color[2] - 15))
        pygame.draw.line(texture, crack_color, (start_x, start_y), (end_x, end_y), 1)
    
    return texture

def create_grass_ground_texture(width, height):
    """Create grass-topped ground texture with better seamless tiling"""
    texture = pygame.Surface((width, height))
    
    # Dirt base with more natural variation
    dirt_color = (101, 67, 33)
    texture.fill(dirt_color)
    
    # Add dirt variation with smoother transitions
    for y in range(height):
        for x in range(width):
            if y > 4:  # Below grass line
                # Create smoother noise using position-based variation
                noise_factor = (math.sin(x * 0.3) + math.cos(y * 0.2)) * 8
                base_noise = random.randint(-8, 8)
                total_noise = int(noise_factor + base_noise)
                
                r = max(0, min(255, dirt_color[0] + total_noise))
                g = max(0, min(255, dirt_color[1] + total_noise))
                b = max(0, min(255, dirt_color[2] + total_noise))
                texture.set_at((x, y), (r, g, b))
    
    # Create more natural grass top layer
    grass_height = 6
    for y in range(min(grass_height, height)):
        for x in range(width):
            # Use position-based variation for seamless tiling
            grass_variation = math.sin(x * 0.2) * math.cos(y * 0.4) * 15
            
            if y < 2:  # Top grass layer
                base_green = (45 + int(grass_variation), 120 + int(grass_variation * 0.8), 35 + int(grass_variation * 0.5))
            elif y < 4:  # Mid grass layer  
                base_green = (40 + int(grass_variation * 0.7), 100 + int(grass_variation * 0.6), 30 + int(grass_variation * 0.4))
            else:  # Grass/dirt transition
                base_green = (60 + int(grass_variation * 0.5), 80 + int(grass_variation * 0.4), 35 + int(grass_variation * 0.3))
                
            # Add subtle random variation
            noise_r = random.randint(-5, 5)
            noise_g = random.randint(-8, 12)
            noise_b = random.randint(-5, 5)
            
            r = max(0, min(255, base_green[0] + noise_r))
            g = max(0, min(255, base_green[1] + noise_g))
            b = max(0, min(255, base_green[2] + noise_b))
            
            # Add occasional grass blade highlights (less frequent for subtlety)
            if random.random() < 0.1:
                g = min(255, g + 20)
                r = max(0, r - 5)
                
            texture.set_at((x, y), (r, g, b))
    
    # Add some small dirt spots for realism
    for _ in range(random.randint(3, 7)):
        spot_x = random.randint(0, width-3)
        spot_y = random.randint(grass_height-2, height-1)
        spot_size = random.randint(1, 2)
        
        dirt_spot_color = (dirt_color[0] + random.randint(-10, 10),
                          dirt_color[1] + random.randint(-10, 10), 
                          dirt_color[2] + random.randint(-10, 10))
        
        for dy in range(spot_size):
            for dx in range(spot_size):
                if (spot_x + dx < width and spot_y + dy < height):
                    texture.set_at((spot_x + dx, spot_y + dy), dirt_spot_color)
    
    return texture

def draw_textured_rect(surface, texture, rect, offset_x=0):
    """Draw a rectangle with tiled texture, with optional horizontal offset for scrolling"""
    if texture:
        texture_width = texture.get_width()
        texture_height = texture.get_height()
        
        # Fix the offset calculation to handle negative values properly
        # This ensures seamless tiling when scrolling in both directions
        offset_mod = offset_x % texture_width
        start_x = rect.x - texture_width + offset_mod
        
        # Tile the texture across the rectangle with extra coverage
        for x in range(start_x, rect.x + rect.width + texture_width, texture_width):
            for y in range(rect.y, rect.y + rect.height, texture_height):
                # Calculate how much of the texture to draw
                draw_x = max(rect.x, x)
                draw_y = max(rect.y, y)
                
                # Only draw if the tile overlaps with the target rectangle
                if draw_x < rect.x + rect.width and draw_y < rect.y + rect.height:
                    clip_width = min(texture_width - (draw_x - x), rect.x + rect.width - draw_x)
                    clip_height = min(texture_height - (draw_y - y), rect.y + rect.height - draw_y)
                    
                    if clip_width > 0 and clip_height > 0:
                        # Calculate texture clip area
                        tex_clip_x = max(0, draw_x - x)
                        tex_clip_y = max(0, draw_y - y)
                        texture_clip = pygame.Rect(tex_clip_x, tex_clip_y, clip_width, clip_height)
                        surface.blit(texture, (draw_x, draw_y), texture_clip)

# Generate textures with better sizes for seamless tiling
stone_texture = create_stone_texture(32, 32, (120, 100, 80))
platform_texture = create_stone_texture(32, 32, (90, 90, 120))  # Bluer platforms  

# Create variety of platform textures for visual interest
platform_textures = [
    create_stone_texture(32, 32, (90, 90, 120)),   # Blue stone
    create_stone_texture(32, 32, (100, 80, 120)),  # Purple stone  
    create_stone_texture(32, 32, (80, 100, 90)),   # Green stone
    create_stone_texture(32, 32, (120, 90, 80)),   # Brown stone
]


clock = pygame.time.Clock()

# Load Mario character and set initial position
mario_img = pygame.image.load('mario.png').convert_alpha()
mario_img = pygame.transform.scale(mario_img, (100, 100))  # Double the size
obstacle_img = pygame.image.load('obstacle.png').convert_alpha()  # Replace with your image file name
obstacle_img = pygame.transform.scale(obstacle_img, (45, 45))  # 1.5x the original size (halfway between original and tripled)
# Load Boss image (single frame) and scale
try:
    boss_img_raw = pygame.image.load('boss_image.png').convert_alpha()
    # Scale boss to thrice the current size
    boss_img = pygame.transform.scale(boss_img_raw, (540, 540))  # Tripled from 180
except Exception:
    boss_img = pygame.Surface((540, 540), pygame.SRCALPHA)
    boss_img.fill((200,0,0))

    boss_x = SCREEN_WIDTH - boss_img.get_width()   # Update boss spawn position
    boss_y = 50

# Load bullet image
try:
    bullet_img_raw = pygame.image.load('bullet.png').convert_alpha()
    bullet_img = pygame.transform.scale(bullet_img_raw, (40, 40))  # Much bigger bullets
except Exception:
    bullet_img = pygame.Surface((40, 40), pygame.SRCALPHA)
    bullet_img.fill((255, 255, 0))  # Yellow fallback

# Load boss face images (placeholders for now)
try:
    boss_face_neutral_raw = pygame.image.load('boss_face_neutral.png').convert_alpha()
    boss_face_neutral = pygame.transform.scale(boss_face_neutral_raw, (180, 180))  # Tripled size
except Exception:
    # Placeholder: calm blue face (tripled size)
    boss_face_neutral = pygame.Surface((180, 180), pygame.SRCALPHA)
    pygame.draw.circle(boss_face_neutral, (100, 150, 255), (90, 90), 75)  # Tripled
    pygame.draw.circle(boss_face_neutral, (50, 50, 50), (66, 75), 9)  # Left eye (tripled)
    pygame.draw.circle(boss_face_neutral, (50, 50, 50), (114, 75), 9)  # Right eye (tripled)
    pygame.draw.arc(boss_face_neutral, (50, 50, 50), (60, 105, 60, 30), 0, 3.14, 6)  # Smile (tripled)

try:
    boss_face_angry_raw = pygame.image.load('boss_face_angry.png').convert_alpha()
    boss_face_angry = pygame.transform.scale(boss_face_angry_raw, (180, 180))  # Tripled size
except Exception:
    # Placeholder: angry red face (tripled size)
    boss_face_angry = pygame.Surface((180, 180), pygame.SRCALPHA)
    pygame.draw.circle(boss_face_angry, (255, 100, 100), (90, 90), 75)  # Tripled
    pygame.draw.circle(boss_face_angry, (200, 0, 0), (66, 75), 9)  # Left eye (tripled)
    pygame.draw.circle(boss_face_angry, (200, 0, 0), (114, 75), 9)  # Right eye (tripled)
    pygame.draw.arc(boss_face_angry, (200, 0, 0), (60, 120, 60, 24), 3.14, 6.28, 6)  # Frown (tripled)
# Mario settings
mario_start_x, mario_start_y = 100, SCREEN_HEIGHT - 200  # Start higher to accommodate larger Mario
mario_x, mario_y = mario_start_x, mario_start_y
mario_speed_x = 5 
gravity = 1.5  # Increased gravity for less floaty feeling
jump_force = 30  # Increased by 35% from 22 (22 * 1.35 ≈ 30)
mario_velocity_y = 0
on_ground = False
scroll_offset = 0

# Load background image for extended map
try:
    background_img = pygame.image.load('im2.png').convert()
    background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH * 2, SCREEN_HEIGHT))
except:
    background_img = None

# Load background music
try:
    pygame.mixer.music.load('background_music.mp3')
    pygame.mixer.music.play(-1)
except:
    print("Background music file not found")

# Load boss spawn sound effect
try:
    angry_sound = pygame.mixer.Sound('angry_sound.mp3')
except:
    print("Angry sound file not found")
    angry_sound = None

# Load boss death sound effect
try:
    luigi_scream = pygame.mixer.Sound('luigi-woaaahh-scream.mp3')
except:
    print("Luigi scream sound file not found")
    luigi_scream = None

# Initialize platforms list with more random variety
def generate_random_platforms():
    """Generate random initial platforms relative to ground"""
    initial_platforms = []
    x_positions = [500, 1000, 1500]  # Base positions
    for i, base_x in enumerate(x_positions):
        # Add some randomness to position and size
        x = base_x + random.randint(-100, 100)
        # Platform Y positions relative to ground (150-300 pixels above ground for higher Mario jump)
        y = (SCREEN_HEIGHT - 50) - random.randint(150, 300)  # Higher platforms for bigger Mario
        width = random.choice([200, 250, 300, 350, 400])  # Larger platform widths
        height = random.choice([20, 25, 30])  # Slightly thicker platforms
        texture_id = random.randint(0, len(platform_textures) - 1)
        
        platform = {'rect': pygame.Rect(x, y, width, height), 'texture_id': texture_id}
        initial_platforms.append(platform)
        
        # Sometimes add an extra platform nearby
        if random.random() < 0.4:  # 40% chance
            extra_x = x + random.randint(200, 400)
            extra_y = y + random.randint(-80, 80)  # More vertical variation
            # Keep platforms reasonable distance from ground
            extra_y = max(SCREEN_HEIGHT - 350, min(SCREEN_HEIGHT - 120, extra_y))  # Adjusted bounds
            extra_width = random.choice([180, 220, 250])  # Larger extra platforms
            extra_platform = {'rect': pygame.Rect(extra_x, extra_y, extra_width, 20), 
                            'texture_id': random.randint(0, len(platform_textures) - 1)}
            initial_platforms.append(extra_platform)
    
    return initial_platforms

# Ground settings (define after screen is initialized)
ground_y = SCREEN_HEIGHT - 50
ground_rect = pygame.Rect(0, ground_y, SCREEN_WIDTH, 50)

# Generate platforms after screen dimensions are available
platforms = generate_random_platforms()

# Initialize obstacles (after ground_y is defined) - 1.5x size
obstacles = [
    pygame.Rect(SCREEN_WIDTH + 200, ground_y - 45, 45, 45),    # First obstacle off-screen to the right (1.5x size)
    pygame.Rect(SCREEN_WIDTH + 600, ground_y - 45, 45, 45),    # Second obstacle further right (1.5x size)
    pygame.Rect(SCREEN_WIDTH + 1000, ground_y - 45, 45, 45)    # Third obstacle even further (1.5x size)
]

# Infinite spawning settings
obstacle_gap = 400
platform_gap = 500

obstacle_speeds = []
obstacle_directions = []
obstacle_movement_ranges = []

# Setup initial obstacle movement
for obs in obstacles:
    speed = random.uniform(2, 4)
    direction = random.choice([-1, 1])
    range_limit = random.randint(100, 300)
    obstacle_speeds.append(speed)
    obstacle_directions.append(direction)
    obstacle_movement_ranges.append({
        'start': obs.x - range_limit,
        'end': obs.x + range_limit,
        'initial_x': obs.x
    })

# Initialize MediaPipe for pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
cap = cv2.VideoCapture(0)

# Initialize score and distance tracking
score = 0
total_distance = 0
next_boss_spawn_score = 200
last_bullet_time = 0  # Track last bullet shot time
BULLET_COOLDOWN = 700  # Minimum milliseconds between shots
last_score = 0  # Track score changes for visual effects

# Boss warning system
boss_warning_active = False
boss_warning_start_time = 0
BOSS_WARNING_DURATION = 3000  # 3 seconds warning
BOSS_WARNING_THRESHOLD = 20  # Show warning 20 points before boss spawn

# Boss & fireball containers
bosses = []  # Each: {'rect':Rect,'spawn_time':ms,'bob_phase':float,'last_fire_time':ms,'fire_interval':int,'health':int,'max_health':int,'burst_count':int,'burst_cooldown_end':ms,'face_angry_until':ms}
fireballs = []  # Each: {'rect':Rect,'vx':float,'vy':float}
bullets = []  # Each: {'rect':Rect,'vx':float,'vy':float}
BOSS_SPAWN_AHEAD = 600  # how far ahead of player to place new boss (reduced for better visibility)
BOSS_BURST_SHOTS = 5  # Number of shots in each burst
BOSS_SHOT_INTERVAL = 200  # ms between shots within a burst
BOSS_BURST_COOLDOWN = 2500  # ms cooldown between bursts (2 seconds)
BOSS_ANGRY_DURATION = 400  # ms to show angry face after shooting
BOSS_MAX_HEALTH = 10  # Number of bullet hits needed to kill a boss
BULLET_SPEED = 12  # Speed of Mario's bullets

def spawn_boss(world_x):
    """Spawn a boss slightly above ground level ahead of player world position."""
    h = boss_img.get_height()
    w = boss_img.get_width()
    rect = pygame.Rect(world_x, ground_y - h, w, h)
    now = pygame.time.get_ticks()
    bosses.append({
        'rect': rect,
        'spawn_time': now,
        'bob_phase': random.uniform(0, math.tau),
        'last_fire_time': now - BOSS_BURST_COOLDOWN,  # Ready to start burst immediately
        'burst_count': 0,  # Number of shots fired in current burst
        'burst_cooldown_end': 0,  # When current burst cooldown ends
        'face_angry_until': 0,  # When to stop showing angry face
        'health': BOSS_MAX_HEALTH,
        'max_health': BOSS_MAX_HEALTH
    })
    
    # Play angry sound when boss spawns
    if angry_sound:
        angry_sound.play()
    
    print(f"Boss spawned with rect: {rect}, world_x: {world_x}")  # Debug output

def shoot_bullet(mario_world_rect):
    """Shoot a bullet from Mario's position in the direction he's facing"""
    # Spawn bullet from Mario's upper chest area (higher up on his body)
    bullet_x = mario_world_rect.centerx - 20  # Slightly left of center so it looks like it's coming from his body
    bullet_y = mario_world_rect.centery - 15  # Higher up, around chest level
    bullet_rect = pygame.Rect(bullet_x, bullet_y, 40, 40)  # Match bigger bullet size
    bullets.append({'rect': bullet_rect, 'vx': BULLET_SPEED, 'vy': 0})
    print("Mario shot a bullet!")

def update_bosses_fireballs_and_bullets(mario_world_rect):
    global game_over, score
    now = pygame.time.get_ticks()
    
    # Update bosses (bobbing + burst shooting)
    for b in bosses[:]:
        bob = math.sin((now/700.0) + b['bob_phase']) * 10
        b['rect'].y = ground_y - b['rect'].height + int(bob)
        
        # Check collision with Mario (boss collision) - both in world coordinates
        if b['rect'].colliderect(mario_world_rect):
            game_over = True
            pygame.mixer.music.pause()
            if sad_meow:
                sad_meow.play()
        
        distance_to_player = abs(mario_world_rect.centerx - b['rect'].centerx)
        
        # Burst firing system
        if distance_to_player < 800:
            # Check if we're in cooldown between bursts
            if now < b['burst_cooldown_end']:
                continue  # Still in cooldown, can't fire
            
            # Check if we can fire the next shot in the burst
            if b['burst_count'] < BOSS_BURST_SHOTS and now - b['last_fire_time'] >= BOSS_SHOT_INTERVAL:
                # Fire a shot!
                direction = 1 if mario_world_rect.centerx > b['rect'].centerx else -1
                speed = 9
                vy = (mario_world_rect.centery - b['rect'].centery) / 80.0
                fire_rect = pygame.Rect(b['rect'].centerx, b['rect'].centery, 20, 20)
                fireballs.append({'rect': fire_rect, 'vx': speed * direction, 'vy': vy})
                
                # Update boss state
                b['last_fire_time'] = now
                b['burst_count'] += 1
                b['face_angry_until'] = now + BOSS_ANGRY_DURATION  # Show angry face
                
                print(f"Boss fired shot {b['burst_count']}/{BOSS_BURST_SHOTS}! Distance: {distance_to_player}")
                
                # If burst is complete, start cooldown
                if b['burst_count'] >= BOSS_BURST_SHOTS:
                    b['burst_cooldown_end'] = now + BOSS_BURST_COOLDOWN
                    b['burst_count'] = 0  # Reset for next burst
                    print("Boss burst complete, entering cooldown...")
    
    # Update bullets and check boss collisions
    for bullet in bullets[:]:
        bullet['rect'].x += int(bullet['vx'])
        bullet['rect'].y += int(bullet['vy'])
        
        # Check collision with bosses
        for b in bosses[:]:
            if bullet['rect'].colliderect(b['rect']):
                # Damage the boss
                b['health'] -= 1
                bullets.remove(bullet)
                print(f"Boss hit! Health: {b['health']}/{b['max_health']}")
                
                # Remove boss if health reaches 0
                if b['health'] <= 0:
                    bosses.remove(b)
                    score += 100  # Bonus points for killing boss
                    
                    # Play Luigi scream when boss dies
                    if luigi_scream:
                        luigi_scream.play()
                    
                    print("Boss defeated!")
                break
        
        # Remove bullets that are off screen
        if bullet['rect'].x > mario_world_rect.x + 1000 or bullet['rect'].x < mario_world_rect.x - 200:
            if bullet in bullets:
                bullets.remove(bullet)
    
    # Update fireballs
    gravity_fire = 0.3
    for f in fireballs[:]:
        f['rect'].x += int(f['vx'])
        f['vy'] += gravity_fire
        f['rect'].y += int(f['vy'])
        
        # Collision with player - both in world coordinates
        if f['rect'].colliderect(mario_world_rect):
            game_over = True
            pygame.mixer.music.pause()
            if sad_meow:
                sad_meow.play()
            print("Fireball hit Mario!")  # Debug output
            
        # Remove if far off screen or hits ground (doubled horizontal range)
        if f['rect'].y > ground_y + 200 or f['rect'].right < (mario_world_rect.x - 2400) or f['rect'].left > (mario_world_rect.x + 12000):
            fireballs.remove(f)

def draw_bosses_fireballs_and_bullets():
    now = pygame.time.get_ticks()
    
    # Draw bosses with health bars and face expressions
    for b in bosses:
        draw_pos = b['rect'].move(scroll_offset, 0)
        
        # Draw boss body
        screen.blit(boss_img, (draw_pos.x, draw_pos.y))
        
        # Draw boss face based on state (angry vs neutral)
        face_img = boss_face_angry if now < b['face_angry_until'] else boss_face_neutral
        face_x = draw_pos.x + draw_pos.width // 4  # Position face on boss body
        face_y = draw_pos.y + 10
        screen.blit(face_img, (face_x, face_y))
        
        # Draw health bar above boss
        health_bar_width = 60
        health_bar_height = 8
        health_bar_x = draw_pos.x + (draw_pos.width - health_bar_width) // 2
        health_bar_y = draw_pos.y - health_bar_height - 5
        
        # Health bar background (red)
        pygame.draw.rect(screen, (255, 0, 0), 
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Health bar foreground (green)
        health_percentage = b['health'] / b['max_health']
        health_fill_width = int(health_bar_width * health_percentage)
        pygame.draw.rect(screen, (0, 255, 0), 
                        (health_bar_x, health_bar_y, health_fill_width, health_bar_height))
        
        # Health bar border
        pygame.draw.rect(screen, (255, 255, 255), 
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 1)
    
    # Draw fireballs with debug info
    for f in fireballs:
        draw_pos = f['rect'].move(scroll_offset, 0)
        # Only draw if on screen
        if -50 < draw_pos.x < SCREEN_WIDTH + 50 and -50 < draw_pos.y < SCREEN_HEIGHT + 50:
            # Draw larger, more visible fireballs with glow effect
            pygame.draw.circle(screen, (255,200,50), (draw_pos.centerx, draw_pos.centery), 12)  # yellow glow
            pygame.draw.circle(screen, (255,100,0), (draw_pos.centerx, draw_pos.centery), 8)   # orange center
            pygame.draw.circle(screen, (255,50,0), (draw_pos.centerx, draw_pos.centery), 4)    # red hot center
    
    # Draw bullets
    for bullet in bullets:
        draw_pos = bullet['rect'].move(scroll_offset, 0)
        # Only draw if on screen
        if -50 < draw_pos.x < SCREEN_WIDTH + 50 and -50 < draw_pos.y < SCREEN_HEIGHT + 50:
            screen.blit(bullet_img, (draw_pos.x, draw_pos.y))
    
    # Debug: Show number of active bosses, fireballs, and bullets (reduce frequency)
    if (len(bosses) > 0 or len(fireballs) > 0 or len(bullets) > 0) and pygame.time.get_ticks() % 1000 < 50:
        print(f"Active bosses: {len(bosses)}, Active fireballs: {len(fireballs)}, Active bullets: {len(bullets)}")  # Debug


def check_platform_collisions(mario_rect, platforms):
    for platform_data in platforms:
        platform = platform_data['rect']
        platform_rect = platform.move(scroll_offset, 0)
        if mario_rect.colliderect(platform_rect) and mario_rect.bottom <= platform_rect.bottom:
            return platform.top
    return None


def reset_game():
    global mario_x, mario_y, mario_velocity_y, scroll_offset, on_ground, score, total_distance, platforms, obstacles, next_boss_spawn_score, bosses, fireballs, bullets, last_bullet_time, last_score, boss_warning_active, boss_warning_start_time
    mario_x, mario_y = mario_start_x, mario_start_y
    mario_velocity_y = 0
    scroll_offset = 0
    on_ground = False
    score = 0
    total_distance = 0
    next_boss_spawn_score = 200
    last_bullet_time = 0
    last_score = 0
    boss_warning_active = False
    boss_warning_start_time = 0
    bosses.clear()
    fireballs.clear()
    bullets.clear()
    platforms = generate_random_platforms()  # Use random platforms on reset too
    obstacles = [
        pygame.Rect(SCREEN_WIDTH + 200, ground_y - 45, 45, 45),    # First obstacle off-screen to the right (1.5x size)
        pygame.Rect(SCREEN_WIDTH + 600, ground_y - 45, 45, 45),    # Second obstacle further right (1.5x size)
        pygame.Rect(SCREEN_WIDTH + 1000, ground_y - 45, 45, 45)    # Third obstacle even further (1.5x size)
    ]

def draw_boss_warning():
    """Draw dramatic boss warning with screen effects"""
    global boss_warning_active, boss_warning_start_time
    
    if not boss_warning_active:
        return
        
    now = pygame.time.get_ticks()
    warning_elapsed = now - boss_warning_start_time
    
    # End warning after duration
    if warning_elapsed >= BOSS_WARNING_DURATION:
        boss_warning_active = False
        return
    
    # Calculate warning intensity (starts strong, fades out)
    progress = warning_elapsed / BOSS_WARNING_DURATION
    intensity = 1.0 - progress  # 1.0 to 0.0
    
    # Screen shake effect
    shake_intensity = int(intensity * 15)  # Max 15 pixel shake
    if shake_intensity > 0:
        shake_x = random.randint(-shake_intensity, shake_intensity)
        shake_y = random.randint(-shake_intensity, shake_intensity)
        # Apply shake by temporarily moving all drawing positions
        screen.scroll(shake_x, shake_y)
    
    # Dark overlay with pulsing effect
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pulse = math.sin(warning_elapsed * 0.01) * 0.2 + 0.3  # Pulsing between 0.1 and 0.5
    overlay_alpha = int(intensity * pulse * 255)
    overlay.fill((200, 0, 0, overlay_alpha))  # Red tint
    screen.blit(overlay, (0, 0))
    
    # Warning text with dramatic effects
    warning_font = pygame.font.Font(pygame.font.match_font('arial', bold=True), 64)
    warning_text = "3RD YEAR BOSS INCOMING"
    
    # Text pulsing size effect
    text_pulse = math.sin(warning_elapsed * 0.008) * 0.3 + 1.0  # Scale between 0.7 and 1.3
    scaled_font_size = int(64 * text_pulse * intensity)
    if scaled_font_size > 0:
        scaled_font = pygame.font.Font(pygame.font.match_font('arial', bold=True), scaled_font_size)
        
        # Multiple colored text layers for dramatic effect
        # Red shadow (biggest)
        shadow_text = scaled_font.render(warning_text, True, (150, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH//2 + 4, SCREEN_HEIGHT//3 + 4))
        screen.blit(shadow_text, shadow_rect)
        
        # Dark outline
        outline_text = scaled_font.render(warning_text, True, (50, 0, 0))
        outline_rect = outline_text.get_rect(center=(SCREEN_WIDTH//2 + 2, SCREEN_HEIGHT//3 + 2))
        screen.blit(outline_text, outline_rect)
        
        # Main bright red text
        main_text = scaled_font.render(warning_text, True, (255, 50, 50))
        main_rect = main_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        screen.blit(main_text, main_rect)
        
        # Bright white highlight (center)
        highlight_text = scaled_font.render(warning_text, True, (255, 255, 255))
        highlight_rect = highlight_text.get_rect(center=(SCREEN_WIDTH//2 - 1, SCREEN_HEIGHT//3 - 1))
        # Only show highlight at peak intensity
        if intensity > 0.7:
            screen.blit(highlight_text, highlight_rect)
    
    # Countdown bars at bottom (dramatic progress indicator)
    bar_width = SCREEN_WIDTH - 100
    bar_height = 20
    bar_x = 50
    bar_y = SCREEN_HEIGHT - 100
    
    # Background bar
    pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
    
    # Progress bar (empties as warning progresses)
    progress_width = int(bar_width * intensity)
    if progress_width > 0:
        pygame.draw.rect(screen, (255, 100, 100), (bar_x, bar_y, progress_width, bar_height))
    
    # Bar border
    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 3)
    
    # Reset screen position after shake
    if shake_intensity > 0:
        screen.scroll(-shake_x, -shake_y)


# Main game loop
game_over = False
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            cap.release()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                cap.release()
                sys.exit()
            elif game_over:
                reset_game()
                game_over = False

    # Camera input
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb_frame)

    move_right, move_left, jump, shoot = False, False, False, False

    if result.pose_landmarks:
        landmarks = result.pose_landmarks.landmark
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
        right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]

        if right_wrist.x > right_shoulder.x:
            move_right = True
        elif left_wrist.x < left_shoulder.x:
            move_left = True

        if (left_wrist.y < left_shoulder.y and right_wrist.y < right_shoulder.y) and on_ground:
            jump = True
            
        # Shooting gesture: Point forward with right hand (wrist forward of elbow, elbow forward of shoulder)
        if (right_wrist.z < right_elbow.z and right_elbow.z < right_shoulder.z and 
            abs(right_wrist.y - right_shoulder.y) < 0.15):  # Hand pointing forward at shoulder height
            shoot = True

    # Keyboard fallback
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        move_right = True
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        move_left = True
    if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and on_ground:
        jump = True
    if keys[pygame.K_x] or keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
        shoot = True

    if not game_over:
        now = pygame.time.get_ticks()  # Get current time for shooting cooldown
        
        if move_right:
            mario_x += mario_speed_x
            total_distance += mario_speed_x
        if move_left:
            mario_x -= mario_speed_x
        if jump:
            mario_velocity_y = -jump_force
            on_ground = False
        if shoot and now - last_bullet_time >= BULLET_COOLDOWN:
            mario_world_rect = pygame.Rect(mario_x - scroll_offset, mario_y, 100, 100)
            shoot_bullet(mario_world_rect)
            last_bullet_time = now

        mario_velocity_y += gravity
        mario_y += mario_velocity_y

        mario_rect = pygame.Rect(mario_x, mario_y, 100, 100)
        platform_top = check_platform_collisions(mario_rect, platforms)
        if platform_top is not None:
            mario_y = platform_top - 100  # Updated for larger Mario
            mario_velocity_y = 0
            on_ground = True

        if mario_y > ground_y - 100:  # Updated for larger Mario
            mario_y = ground_y - 100  # Updated for larger Mario
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
                new_obstacle = pygame.Rect(new_x, ground_y - 45, 45, 45)  # Updated size and position
                obstacles.append(new_obstacle)

                speed = random.uniform(2, 4)
                direction = random.choice([-1, 1])
                range_limit = random.randint(100, 300)
                obstacle_speeds.append(speed)
                obstacle_directions.append(direction)
                obstacle_movement_ranges.append({
                    'start': new_obstacle.x - range_limit,
                    'end': new_obstacle.x + range_limit,
                    'initial_x': new_obstacle.x
                })

        # Spawn new platforms dynamically with much more randomization
        if platforms:
            last_platform_data = platforms[-1]
            last_platform_x = last_platform_data['rect'].x
            if mario_x - scroll_offset > last_platform_x - 2000:
                # Randomize horizontal spacing (much more varied gaps)
                random_gap = random.randint(250, 800)  # Much more varied spacing
                new_x = last_platform_x + random_gap
                
                # More varied vertical positioning (relative to ground) - higher for bigger Mario
                new_y = random.randint(SCREEN_HEIGHT - 350, SCREEN_HEIGHT - 120)
                
                # Randomize platform width and height - larger for bigger Mario
                platform_width = random.choice([180, 220, 250, 300, 350, 400])  # Larger widths
                platform_height = random.choice([20, 25, 30])  # Thicker platforms
                
                new_platform_rect = pygame.Rect(new_x, new_y, platform_width, platform_height)
                new_texture_id = random.randint(0, len(platform_textures) - 1)
                new_platform = {'rect': new_platform_rect, 'texture_id': new_texture_id}
                platforms.append(new_platform)
                
                # Sometimes add a second platform nearby for interesting jumps
                if random.random() < 0.3:  # 30% chance
                    bonus_x = new_x + random.randint(150, 300)
                    bonus_y = new_y + random.randint(-100, 100)  # More vertical variation
                    bonus_y = max(SCREEN_HEIGHT - 400, min(SCREEN_HEIGHT - 120, bonus_y))  # Better bounds for higher platforms
                    bonus_width = random.choice([150, 180, 220])  # Larger bonus platforms
                    bonus_rect = pygame.Rect(bonus_x, bonus_y, bonus_width, 20)
                    bonus_texture = random.randint(0, len(platform_textures) - 1)
                    bonus_platform = {'rect': bonus_rect, 'texture_id': bonus_texture}
                    platforms.append(bonus_platform)

        # Move obstacles & check collision
        for i, obstacle in enumerate(obstacles):
            obstacle_rect = obstacle.move(scroll_offset, 0)

            if mario_rect.colliderect(obstacle_rect):
                game_over = True

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
        
        # Track score changes for visual effects
        if score != last_score:
            score_change_time = pygame.time.get_ticks()
            last_score = score

        # Boss warning system
        if not boss_warning_active and score >= next_boss_spawn_score - BOSS_WARNING_THRESHOLD:
            boss_warning_active = True
            boss_warning_start_time = pygame.time.get_ticks()
            print(f"Boss warning activated! Score: {score}, Threshold: {next_boss_spawn_score}")

        # Boss spawning at score thresholds (only after warning period)
        if score >= next_boss_spawn_score and (not boss_warning_active or pygame.time.get_ticks() - boss_warning_start_time >= BOSS_WARNING_DURATION):
            spawn_world_x = (mario_x - scroll_offset) + BOSS_SPAWN_AHEAD
            spawn_boss(spawn_world_x)
            print(f"Boss spawned at world position {spawn_world_x}, Mario at {mario_x - scroll_offset}, Score: {score}")
            next_boss_spawn_score += 200
            boss_warning_active = False  # Reset warning for next boss

        # Create mario world rect for boss/fireball system
        mario_world_rect = pygame.Rect(mario_x - scroll_offset, mario_y, 100, 100)
        
        # Update bosses, fireballs & bullets
        update_bosses_fireballs_and_bullets(mario_world_rect)

    # Draw background
    if background_img:
        x_position = scroll_offset % -background_img.get_width()
        screen.blit(background_img, (x_position, 0))
        if x_position + background_img.get_width() < SCREEN_WIDTH:
            screen.blit(background_img, (x_position + background_img.get_width(), 0))
    else:
        screen.fill((255, 255, 255))

    # Draw textured platforms
    for platform_data in platforms:
        platform = platform_data['rect']
        platform_rect = platform.move(scroll_offset, 0)
        texture_id = platform_data['texture_id']
        
        # Use the appropriate texture
        current_texture = platform_textures[texture_id] if texture_id < len(platform_textures) else platform_textures[0]
        draw_textured_rect(screen, current_texture, platform_rect)
        
        # Add platform borders for Jump King style with texture-appropriate colors
        border_colors = [
            (60, 60, 100),   # Blue border
            (80, 60, 100),   # Purple border
            (60, 80, 70),    # Green border
            (100, 70, 60),   # Brown border
        ]
        highlight_colors = [
            (140, 140, 180),  # Blue highlight
            (160, 140, 180),  # Purple highlight
            (140, 160, 150),  # Green highlight
            (180, 150, 140),  # Brown highlight
        ]
        
        border_color = border_colors[texture_id] if texture_id < len(border_colors) else border_colors[0]
        highlight_color = highlight_colors[texture_id] if texture_id < len(highlight_colors) else highlight_colors[0]
        
        pygame.draw.rect(screen, border_color, platform_rect, 2)
        # Add highlight on top edge
        pygame.draw.line(screen, highlight_color, 
                        (platform_rect.left, platform_rect.top), 
                        (platform_rect.right, platform_rect.top), 2)

    for obstacle in obstacles:
        obstacle_rect = obstacle.move(scroll_offset, 0)
        screen.blit(obstacle_img, (obstacle_rect.x, obstacle_rect.y))

    # Draw bosses, fireballs & bullets
    draw_bosses_fireballs_and_bullets()

    screen.blit(mario_img, (mario_x, mario_y))

    # Draw boss warning (must be after everything else for screen shake effect)
    draw_boss_warning()

    # Elegant Score HUD
    # Clean, modern score display with subtle effects
    score_font = pygame.font.Font(pygame.font.match_font('arial'), 32)
    
    # Subtle shadow for depth
    shadow_text = score_font.render(f"Score: {score:,}", True, (30, 30, 30))
    shadow_rect = shadow_text.get_rect()
    shadow_rect.topright = (screen.get_width() - 18, 22)
    screen.blit(shadow_text, shadow_rect)
    
    # Main score text in clean white
    score_text = score_font.render(f"Score: {score:,}", True, (255, 255, 255))
    score_rect = score_text.get_rect()
    score_rect.topright = (screen.get_width() - 20, 20)
    screen.blit(score_text, score_rect)
    
    # Subtle background panel
    panel_rect = pygame.Rect(score_rect.left - 10, score_rect.top - 5, 
                           score_rect.width + 20, score_rect.height + 10)
    panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    panel_surface.fill((0, 0, 0, 80))  # Semi-transparent black
    screen.blit(panel_surface, panel_rect)
    
    # Controls HUD
    small_font = pygame.font.Font(pygame.font.match_font('arial'), 20)
    white = (255, 255, 255)
    controls_text = small_font.render("Controls: Gestures (Move hands, Raise arms=Jump, Point forward=Shoot) | Keys: WASD/Arrows, X/Ctrl", True, white)
    screen.blit(controls_text, (10, screen.get_height() - 25))

    # Camera overlay
    annotated_frame = frame.copy()
    mp.solutions.drawing_utils.draw_landmarks(annotated_frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    camera_feed = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
    camera_feed = pygame.surfarray.make_surface(camera_feed)
    camera_feed = pygame.transform.rotate(camera_feed, -90)
    camera_feed = pygame.transform.flip(camera_feed, True, False)
    camera_feed = pygame.transform.scale(camera_feed, (200, 150))
    screen.blit(camera_feed, (0, 0))

    if game_over:
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over!", True, (255, 0, 0))
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(text, text_rect)
        font = pygame.font.Font(None, 36)
        text = font.render("Press any key to restart", True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        screen.blit(text, text_rect)

    pygame.display.flip()
    clock.tick(120)  # Increased from 30 to 120 FPS for smoother gameplay
