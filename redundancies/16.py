import cv2
import mediapipe as mp
import pygame
import sys
import random
from pygame import mixer

# Initialize Pygame, mixer, and screen settings
pygame.init()
mixer.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)

# Game states
class GameState:
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    LEVEL_COMPLETE = "level_complete"

# Power-up types
class PowerUpType:
    SPEED_BOOST = "speed"
    INVINCIBILITY = "invincible"
    DOUBLE_JUMP = "double_jump"

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type):
        super().__init__()
        self.type = power_type
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW if power_type == PowerUpType.SPEED_BOOST else
                       RED if power_type == PowerUpType.INVINCIBILITY else GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        try:
            self.image = pygame.image.load('mario.png')
            self.image = pygame.transform.scale(self.image, (50, 50))
        except:
            self.image = pygame.Surface((50, 50))
            self.image.fill(GREEN)
        self.velocity_y = 0
        self.speed_x = 5
        self.lives = 3
        self.score = 0
        self.on_ground = False
        self.can_double_jump = False
        self.has_double_jumped = False
        self.is_invincible = False
        self.power_up_timer = 0
        self.current_power_up = None
        self.coins_collected = 0
        self.rect = pygame.Rect(x, y, 50, 50)

    def apply_power_up(self, power_up_type):
        self.current_power_up = power_up_type
        self.power_up_timer = pygame.time.get_ticks()
        
        if power_up_type == PowerUpType.SPEED_BOOST:
            self.speed_x = 8
        elif power_up_type == PowerUpType.INVINCIBILITY:
            self.is_invincible = True
        elif power_up_type == PowerUpType.DOUBLE_JUMP:
            self.can_double_jump = True
            self.has_double_jumped = False
        try:
            powerup_sound.play()
        except:
            pass

    def update_power_up_status(self):
        if self.current_power_up and pygame.time.get_ticks() - self.power_up_timer > 10000:
            self.speed_x = 5
            self.is_invincible = False
            self.can_double_jump = False
            self.current_power_up = None

class Game:
    def __init__(self):
        # Load sounds
        try:
            global jump_sound, coin_sound, powerup_sound, death_sound
            jump_sound = mixer.Sound('jump.wav')
            coin_sound = mixer.Sound('coin.wav')
            powerup_sound = mixer.Sound('powerup.wav')
            death_sound = mixer.Sound('death.wav')
        except:
            print("Some sound files not found")

        # Load background
        try:
            self.background_img = pygame.image.load('j.png')
            self.background_img = pygame.transform.scale(self.background_img, (3200, 600))
        except:
            self.background_img = None

        # Initialize game state
        self.state = GameState.PLAYING
        self.scroll_offset = 0
        self.player = Player(400, 500)
        self.gravity = 1
        self.jump_force = 15
        
        # Initialize sprite groups
        self.platforms = []
        self.obstacles = []
        self.power_ups = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        
        # Generate level content
        self.generate_level()
        
        # Initialize MediaPipe
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.cap = cv2.VideoCapture(0)

    def generate_level(self):
        # Generate platforms
        platform_positions = [
            (500, 450), (800, 400), (1100, 450),
            (1400, 400), (1700, 450), (2000, 400)
        ]
        
        for x, y in platform_positions:
            self.platforms.append(pygame.Rect(x, y, 200, 20))

        # Generate obstacles
        for i in range(10):
            x = random.randint(800, 2500)
            self.obstacles.append(pygame.Rect(x, 520, 30, 30))

        # Generate power-ups
        power_up_types = [PowerUpType.SPEED_BOOST, PowerUpType.INVINCIBILITY, PowerUpType.DOUBLE_JUMP]
        for _ in range(5):
            x = random.randint(800, 2000)
            y = random.randint(200, 400)
            self.power_ups.add(PowerUp(x, y, random.choice(power_up_types)))

        # Generate coins
        for _ in range(20):
            coin = pygame.sprite.Sprite()
            coin.image = pygame.Surface((15, 15))
            coin.image.fill(YELLOW)
            coin.rect = coin.image.get_rect()
            coin.rect.x = random.randint(500, 2500)
            coin.rect.y = random.randint(200, 500)
            self.coins.add(coin)

    def handle_input(self):
        ret, frame = self.cap.read()
        if not ret:
            return False, False, False

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.pose.process(rgb_frame)

        move_right, move_left, jump = False, False, False

        if result.pose_landmarks:
            landmarks = result.pose_landmarks.landmark
            left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]

            if right_wrist.x > right_shoulder.x:
                move_right = True
            elif left_wrist.x < left_shoulder.x:
                move_left = True

            if (left_wrist.y < left_shoulder.y and right_wrist.y < right_shoulder.y):
                jump = True

        return move_right, move_left, jump, frame, result

    def update(self):
        if self.state != GameState.PLAYING:
            return

        move_right, move_left, jump, frame, result = self.handle_input()

        # Update player position
        if move_right:
            self.player.x += self.player.speed_x
        if move_left:
            self.player.x -= self.player.speed_x
        if jump and (self.player.on_ground or (self.player.can_double_jump and not self.player.has_double_jumped)):
            self.player.velocity_y = -self.jump_force
            self.player.on_ground = False
            if not self.player.on_ground:
                self.player.has_double_jumped = True
            try:
                jump_sound.play()
            except:
                pass

        # Apply gravity
        self.player.velocity_y += self.gravity
        self.player.y += self.player.velocity_y

        # Update player rect
        self.player.rect.x = self.player.x
        self.player.rect.y = self.player.y

        # Check collisions
        self.check_collisions()

        # Update power-up status
        self.player.update_power_up_status()

        # Scroll the background
        if self.player.x > 400:
            self.scroll_offset -= self.player.speed_x
            self.player.x = 400

        return frame, result

    def check_collisions(self):
        # Ground collision
        if self.player.y > SCREEN_HEIGHT - 100:
            self.player.y = SCREEN_HEIGHT - 100
            self.player.velocity_y = 0
            self.player.on_ground = True
            self.player.has_double_jumped = False

        # Platform collisions
        self.player.on_ground = False
        for platform in self.platforms:
            platform_rect = platform.move(self.scroll_offset, 0)
            if self.player.rect.colliderect(platform_rect):
                if self.player.velocity_y > 0:
                    self.player.y = platform_rect.top - self.player.rect.height
                    self.player.velocity_y = 0
                    self.player.on_ground = True
                    self.player.has_double_jumped = False

        # Obstacle collisions
        if not self.player.is_invincible:
            for obstacle in self.obstacles:
                obstacle_rect = obstacle.move(self.scroll_offset, 0)
                if self.player.rect.colliderect(obstacle_rect):
                    self.player.lives -= 1
                    try:
                        death_sound.play()
                    except:
                        pass
                    if self.player.lives <= 0:
                        self.state = GameState.GAME_OVER
                    self.player.x = 400
                    self.player.y = 500
                    self.player.velocity_y = 0

        # Power-up collisions
        for power_up in self.power_ups:
            power_up.rect.x += self.scroll_offset
            if self.player.rect.colliderect(power_up.rect):
                self.player.apply_power_up(power_up.type)
                power_up.kill()

        # Coin collisions
        for coin in self.coins:
            coin.rect.x += self.scroll_offset
            if self.player.rect.colliderect(coin.rect):
                self.player.score += 10
                self.player.coins_collected += 1
                coin.kill()
                try:
                    coin_sound.play()
                except:
                    pass

    def draw(self, frame, result):
        # Draw background
        if self.background_img:
            screen.blit(self.background_img, (self.scroll_offset % -3200, 0))
            if self.scroll_offset % -3200 != 0:
                screen.blit(self.background_img, ((self.scroll_offset % -3200) + 3200, 0))
        else:
            screen.fill(WHITE)

        # Draw ground
        pygame.draw.rect(screen, BROWN, pygame.Rect(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))

        # Draw platforms
        for platform in self.platforms:
            platform_rect = platform.move(self.scroll_offset, 0)
            pygame.draw.rect(screen, BLUE, platform_rect)

        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle_rect = obstacle.move(self.scroll_offset, 0)
            pygame.draw.rect(screen, RED, obstacle_rect)

        # Draw power-ups and coins
        self.power_ups.draw(screen)
        self.coins.draw(screen)

        # Draw player
        screen.blit(self.player.image, (self.player.x, self.player.y))

        # Draw camera feed with landmarks
        if frame is not None and result.pose_landmarks:
            annotated_frame = frame.copy()
            mp.solutions.drawing_utils.draw_landmarks(
                annotated_frame, result.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            camera_feed = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            camera_feed = pygame.surfarray.make_surface(camera_feed)
            camera_feed = pygame.transform.scale(camera_feed, (200, 150))
            screen.blit(camera_feed, (0, 0))

        # Draw HUD
        self.draw_hud()

        # Draw game over screen
        if self.state == GameState.GAME_OVER:
            font = pygame.font.Font(None, 74)
            text = font.render("Game Over!", True, RED)
            screen.blit(text, (250, 200))
            font = pygame.font.Font(None, 36)
            text = font.render("Press any key to replay", True, WHITE)
            screen.blit(text, (250, 300))

    def draw_hud(self):
        font = pygame.font.Font(None, 36)
        texts = [
            (f"Lives: {self.player.lives}", RED, (10, 10)),
            (f"Score: {self.player.score}", WHITE, (10, 50)),
            (f"Coins: {self.player.coins_collected}", YELLOW, (10, 90))
        ]
        
        if self.player.current_power_up:
            texts.append((f"Power-up: {self.player.current_power_up}", GREEN, (10, 130)))
            
        for text, color, pos in texts:
            surface = font.render(text, True, color)
            screen.blit(surface, pos)

    def reset(self):
        self.__init__()

def main():
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and game.state == GameState.GAME_OVER:
                game.reset()

        if game.state == GameState.PLAYING:
            frame, result = game.update()
            game.draw(frame, result)
        
        pygame.display.flip()
        clock.tick(60)

    game.cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()