import pygame
import sys
import random
import cv2
import mediapipe as mp

# Initialize Pygame first
pygame.init()

from game_v20.settings import *
from game_v20.player import Player
from game_v20.entities import Obstacle, Platform
from game_v20.ui import draw_menu, draw_game_over, draw_text

class Game:
    def __init__(self):
        # Pygame is already initialized
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Mario Runner")
        self.clock = pygame.time.Clock()
        self.game_state = STATE_MENU
        self.load_assets()
        self.init_camera()
        self.scroll_offset = 0
        self.total_distance = 0
        self.score = 0

    def load_assets(self):
        try:
            self.mario_img = pygame.image.load(MARIO_IMG_PATH).convert_alpha()
            self.obstacle_img = pygame.image.load(OBSTACLE_IMG_PATH).convert_alpha()
            self.background_img = pygame.image.load(BACKGROUND_IMG_PATH).convert()
            self.background_img = pygame.transform.scale(self.background_img, (self.background_img.get_width(), SCREEN_HEIGHT))
        except pygame.error as e:
            print(f"Error loading image: {e}")
            # Create placeholder surfaces if images are missing
            self.mario_img = pygame.Surface((50, 50)); self.mario_img.fill(RED)
            self.obstacle_img = pygame.Surface((30, 30)); self.obstacle_img.fill(BLUE)
            self.background_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); self.background_img.fill(WHITE)

        try:
            pygame.mixer.music.load(BACKGROUND_MUSIC_PATH)
            pygame.mixer.music.play(-1)
        except pygame.error:
            print("Background music file not found or could not be played.")

    def init_camera(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Cannot open camera")
            self.cap = None

    def reset_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()

        self.player = Player()
        self.all_sprites.add(self.player)

        # Initial platforms and obstacles
        for i in range(5):
            p = Platform(SCREEN_WIDTH + i * PLATFORM_GAP, random.randint(SCREEN_HEIGHT - 250, SCREEN_HEIGHT - 100), 200, 20)
            self.platforms.add(p)
            self.all_sprites.add(p)
        
        for i in range(3):
            o = Obstacle(SCREEN_WIDTH + 400 + i * OBSTACLE_GAP, GROUND_Y - 30)
            self.obstacles.add(o)
            self.all_sprites.add(o)

        self.scroll_offset = 0
        self.total_distance = 0
        self.score = 0
        self.game_state = STATE_PLAYING

    def process_camera_input(self):
        move_right, move_left, jump = False, False, False
        frame = None
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = self.pose.process(rgb_frame)

                if result.pose_landmarks:
                    landmarks = result.pose_landmarks.landmark
                    left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST]
                    right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]
                    left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
                    right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]

                    if right_wrist.x > right_shoulder.x + 0.05:
                        move_right = True
                    elif left_wrist.x < left_shoulder.x - 0.05:
                        move_left = True

                    if (left_wrist.y < left_shoulder.y and right_wrist.y < right_shoulder.y) and self.player.on_ground:
                        jump = True
                
                # Draw landmarks for camera feed
                mp.solutions.drawing_utils.draw_landmarks(frame, result.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

        return move_left, move_right, jump, frame

    def run(self):
        while True:
            if self.game_state == STATE_MENU:
                self.run_menu()
            elif self.game_state == STATE_PLAYING:
                self.run_playing()
            elif self.game_state == STATE_GAME_OVER:
                self.run_game_over()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit_game()
                if self.game_state == STATE_MENU and event.key == pygame.K_RETURN:
                    self.reset_game()
                elif self.game_state == STATE_GAME_OVER and event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    self.reset_game()

    def run_menu(self):
        self.handle_events()
        draw_menu(self.screen, self.background_img)
        pygame.display.flip()
        self.clock.tick(30)

    def run_game_over(self):
        self.handle_events()
        draw_game_over(self.screen)
        pygame.display.flip()
        self.clock.tick(30)

    def run_playing(self):
        self.handle_events()

        # --- Input ---
        move_left_cam, move_right_cam, jump_cam, camera_frame = self.process_camera_input()
        
        keys = pygame.key.get_pressed()
        move_left_key = keys[pygame.K_LEFT] or keys[pygame.K_a]
        move_right_key = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        jump_key = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]

        move_left = move_left_cam or move_left_key
        move_right = move_right_cam or move_right_key
        jump = jump_cam or jump_key

        # --- Update ---
        self.player.update(move_left, move_right, jump)
        
        # Scrolling
        if self.player.rect.x > SCREEN_WIDTH * 0.6:
            scroll = self.player.rect.x - SCREEN_WIDTH * 0.6
            self.player.rect.x = SCREEN_WIDTH * 0.6
            self.scroll_offset = -scroll
            self.total_distance += scroll
        else:
            self.scroll_offset = 0

        for sprite in self.all_sprites:
            if sprite != self.player:
                sprite.rect.x += self.scroll_offset

        # Update platforms and obstacles based on scroll
        self.platforms.update(self.scroll_offset)
        self.obstacles.update(0) # Obstacles have their own movement logic

        # Collisions
        self.player.check_platform_collisions(self.platforms)
        if pygame.sprite.spritecollide(self.player, self.obstacles, False):
            self.game_state = STATE_GAME_OVER

        # Dynamic content generation
        last_obstacle = self.obstacles.sprites()[-1] if self.obstacles.sprites() else None
        if not last_obstacle or last_obstacle.rect.right < SCREEN_WIDTH + 200:
            o = Obstacle(SCREEN_WIDTH + random.randint(100, 300), GROUND_Y - 30)
            self.obstacles.add(o)
            self.all_sprites.add(o)

        last_platform = self.platforms.sprites()[-1] if self.platforms.sprites() else None
        if not last_platform or last_platform.rect.right < SCREEN_WIDTH + 200:
            p = Platform(SCREEN_WIDTH + random.randint(100, 300), random.randint(SCREEN_HEIGHT - 250, SCREEN_HEIGHT - 100), 200, 20)
            self.platforms.add(p)
            self.all_sprites.add(p)

        self.score = self.total_distance // 10

        # --- Draw ---
        # Draw background
        bg_x = (self.total_distance * 0.5) % self.background_img.get_width()
        self.screen.blit(self.background_img, (-bg_x, 0))
        self.screen.blit(self.background_img, (self.background_img.get_width() - bg_x, 0))

        # Draw ground
        pygame.draw.rect(self.screen, BROWN, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))

        self.all_sprites.draw(self.screen)
        
        # Draw Score
        draw_text(self.screen, f"Score: {self.score}", FONT_NAME, 40, PURPLE, SCREEN_WIDTH - 300, 20)

        # Draw camera feed
        if camera_frame is not None:
            camera_surf = pygame.surfarray.make_surface(cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB))
            camera_surf = pygame.transform.rotate(camera_surf, -90)
            camera_surf = pygame.transform.flip(camera_surf, True, False)
            camera_surf = pygame.transform.scale(camera_surf, (200, 150))
            self.screen.blit(camera_surf, (10, 10))

        pygame.display.flip()
        self.clock.tick(60)

    def quit_game(self):
        if self.cap:
            self.cap.release()
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()
