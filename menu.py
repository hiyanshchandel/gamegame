import pygame
import sys
import math
import random
from enum import Enum

class MenuState(Enum):
    MAIN_MENU = 1
    SETTINGS = 2
    CREDITS = 3
    GAME = 4

class MarioMenu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Super Mario Bros - Gesture Control")
        self.clock = pygame.time.Clock()
        
        # Menu state
        self.current_state = MenuState.MAIN_MENU
        self.selected_option = 0
        
        # Colors - Mario themed
        self.RED = (220, 20, 20)
        self.BLUE = (20, 20, 220)
        self.GREEN = (20, 220, 20)
        self.YELLOW = (255, 255, 0)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BROWN = (139, 69, 19)
        self.ORANGE = (255, 165, 0)
        self.GRAY = (128, 128, 128)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 120)
        self.menu_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        
        # Menu options
        self.main_menu_options = ["PLAY", "SETTINGS", "CREDITS", "QUIT"]
        self.settings_options = ["MUSIC: ON", "SFX: ON", "DIFFICULTY: NORMAL", "BACK"]
        
        # Animation variables
        self.title_bounce = 0
        self.option_glow = {}
        self.particle_system = []
        
        # Settings
        self.music_enabled = True
        self.sfx_enabled = True
        self.difficulty = "NORMAL"  # EASY, NORMAL, HARD
        
        # Load images (with fallbacks)
        try:
            self.mario_img = pygame.image.load('mario.png')
            self.mario_img = pygame.transform.scale(self.mario_img, (80, 80))
        except:
            self.mario_img = None
            
        try:
            self.background_img = pygame.image.load('im1.png')
            self.background_img = pygame.transform.scale(self.background_img, (800, 600))
        except:
            self.background_img = None
            
        # Load and play menu music
        try:
            pygame.mixer.music.load('background_music.mp3')
            if self.music_enabled:
                pygame.mixer.music.play(-1, 0.0, 1000)  # Fade in over 1 second
        except:
            print("Menu music not found")
            
        # Initialize particles
        self.init_particles()
        
    def init_particles(self):
        """Initialize enhanced floating particles for background effect"""
        self.particle_system = []
        for _ in range(25):  # More particles for richer effect
            particle = {
                'x': random.randint(0, 800),
                'y': random.randint(0, 600),
                'speed': random.uniform(0.3, 1.8),
                'size': random.randint(2, 8),
                'color': random.choice([
                    (255, 255, 200),  # Bright yellow
                    (255, 255, 255),  # White
                    (255, 200, 100),  # Orange
                    (200, 255, 255),  # Light blue
                    (255, 150, 255)   # Pink
                ]),
                'alpha': random.randint(120, 200),  # Higher alpha for better visibility
                'pulse': random.uniform(0, math.pi * 2)  # For pulsing effect
            }
            self.particle_system.append(particle)
    
    def update_particles(self):
        """Update particle positions and create enhanced floating effect"""
        for particle in self.particle_system:
            particle['y'] -= particle['speed']
            particle['x'] += math.sin(particle['y'] * 0.01 + particle['pulse']) * 0.8
            particle['pulse'] += 0.02  # For pulsing animation
            
            # Add some random horizontal drift
            particle['x'] += random.uniform(-0.2, 0.2)
            
            # Reset particle when it goes off screen
            if particle['y'] < -10:
                particle['y'] = 610
                particle['x'] = random.randint(0, 800)
                particle['pulse'] = random.uniform(0, math.pi * 2)
                
            # Keep particles within screen bounds horizontally
            if particle['x'] < -10:
                particle['x'] = 810
            elif particle['x'] > 810:
                particle['x'] = -10
                
    def draw_particles(self):
        """Draw enhanced floating particles with better visibility"""
        for particle in self.particle_system:
            # Create enhanced particle with glow effect
            particle_size = particle['size']
            glow_size = particle_size + 4
            
            # Outer glow
            glow_surf = pygame.Surface((glow_size * 3, glow_size * 3))
            glow_surf.set_alpha(particle['alpha'] // 3)
            pygame.draw.circle(glow_surf, (255, 255, 200), 
                             (glow_size * 1.5, glow_size * 1.5), glow_size)
            self.screen.blit(glow_surf, (int(particle['x'] - glow_size), int(particle['y'] - glow_size)))
            
            # Main particle with enhanced colors
            particle_surf = pygame.Surface((particle_size * 2, particle_size * 2))
            particle_surf.set_alpha(particle['alpha'])
            enhanced_color = (
                min(255, particle['color'][0] + 50),
                min(255, particle['color'][1] + 50), 
                min(255, particle['color'][2] + 100)
            )
            pygame.draw.circle(particle_surf, enhanced_color, 
                             (particle_size, particle_size), particle_size)
            self.screen.blit(particle_surf, (int(particle['x']), int(particle['y'])))
    
    def draw_background(self):
        """Draw animated background with enhanced visibility"""
        if self.background_img:
            # Create a scrolling background effect
            scroll_offset = (pygame.time.get_ticks() * 0.02) % self.background_img.get_width()
            self.screen.blit(self.background_img, (-scroll_offset, 0))
            if scroll_offset > 0:
                self.screen.blit(self.background_img, 
                               (self.background_img.get_width() - scroll_offset, 0))
        else:
            # Enhanced gradient background as fallback
            for y in range(600):
                color_ratio = y / 600
                r = int(25 * (1 - color_ratio) + 5 * color_ratio)
                g = int(50 * (1 - color_ratio) + 15 * color_ratio)
                b = int(100 * (1 - color_ratio) + 40 * color_ratio)
                pygame.draw.line(self.screen, (r, g, b), (0, y), (800, y))
                
        # Add stronger overlay for much better text visibility
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(180)  # Increased opacity for better contrast
        overlay.fill((0, 0, 30))  # Dark blue tint instead of pure black
        self.screen.blit(overlay, (0, 0))
        
        # Add subtle vignette effect
        vignette = pygame.Surface((800, 600))
        pygame.draw.circle(vignette, (0, 0, 0), (400, 300), 500)
        vignette.set_alpha(80)
        self.screen.blit(vignette, (0, 0), special_flags=pygame.BLEND_MULT)
    
    def draw_title(self):
        """Draw enhanced animated title with better visibility"""
        self.title_bounce += 0.1
        bounce_offset = math.sin(self.title_bounce) * 12
        
        # Enhanced shadow with multiple layers for depth
        for i in range(3):
            shadow_alpha = 150 - (i * 40)
            shadow_offset = 4 + (i * 2)
            shadow_surf = pygame.Surface((600, 120))
            shadow_surf.set_alpha(shadow_alpha)
            shadow_text = self.title_font.render("SUPER MARIO", True, self.BLACK)
            shadow_surf.blit(shadow_text, (0, 0))
            shadow_rect = shadow_surf.get_rect(center=(400 + shadow_offset, 100 + bounce_offset + shadow_offset))
            self.screen.blit(shadow_surf, shadow_rect)
        
        # Outer glow effect
        glow_surf = pygame.Surface((650, 150))
        glow_surf.set_alpha(80)
        glow_text = self.title_font.render("SUPER MARIO", True, (255, 255, 100))
        glow_rect = glow_text.get_rect(center=(325, 75))
        glow_surf.blit(glow_text, glow_rect)
        glow_main_rect = glow_surf.get_rect(center=(400, 100 + bounce_offset))
        self.screen.blit(glow_surf, glow_main_rect)
        
        # Main title with enhanced colors and outline
        # Create outline effect
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    outline_text = self.title_font.render("SUPER MARIO", True, (150, 0, 0))
                    outline_rect = outline_text.get_rect(center=(400 + dx, 100 + bounce_offset + dy))
                    self.screen.blit(outline_text, outline_rect)
        
        # Main title
        title_text = self.title_font.render("SUPER MARIO", True, (255, 50, 50))
        title_rect = title_text.get_rect(center=(400, 100 + bounce_offset))
        self.screen.blit(title_text, title_rect)
        
        # Enhanced subtitle with background
        subtitle_bg = pygame.Surface((400, 40))
        subtitle_bg.set_alpha(120)
        subtitle_bg.fill((0, 0, 50))
        subtitle_bg_rect = subtitle_bg.get_rect(center=(400, 160 + bounce_offset * 0.5))
        self.screen.blit(subtitle_bg, subtitle_bg_rect)
        
        subtitle_text = self.menu_font.render("Gesture Control Edition", True, (255, 255, 150))
        subtitle_rect = subtitle_text.get_rect(center=(400, 160 + bounce_offset * 0.5))
        self.screen.blit(subtitle_text, subtitle_rect)
    
    def draw_mario_character(self):
        """Draw Mario character with enhanced animation and effects"""
        if self.mario_img:
            bob_offset = math.sin(pygame.time.get_ticks() * 0.003) * 8
            mario_x = 60 + math.sin(pygame.time.get_ticks() * 0.001) * 25
            mario_y = 430 + bob_offset
            
            # Add Mario's glow effect
            glow_surf = pygame.Surface((120, 120))
            glow_surf.set_alpha(60)
            glow_surf.fill((255, 200, 100))
            glow_rect = glow_surf.get_rect(center=(mario_x + 40, mario_y + 40))
            self.screen.blit(glow_surf, glow_rect)
            
            # Add Mario's enhanced shadow
            shadow_surf = pygame.Surface((90, 25))
            shadow_surf.set_alpha(100)
            shadow_surf.fill((0, 0, 30))
            pygame.draw.ellipse(shadow_surf, (0, 0, 30), shadow_surf.get_rect())
            self.screen.blit(shadow_surf, (mario_x - 5, mario_y + 80))
            
            # Main Mario sprite
            self.screen.blit(self.mario_img, (mario_x, mario_y))
            
            # Add sparkle effects around Mario
            sparkle_time = pygame.time.get_ticks() * 0.01
            for i in range(3):
                sparkle_x = mario_x + 40 + math.sin(sparkle_time + i * 2) * 60
                sparkle_y = mario_y + 40 + math.cos(sparkle_time + i * 1.5) * 40
                sparkle_size = 3 + math.sin(sparkle_time * 2 + i) * 2
                
                sparkle_surf = pygame.Surface((int(sparkle_size * 2), int(sparkle_size * 2)))
                sparkle_surf.set_alpha(150 + int(math.sin(sparkle_time * 3 + i) * 50))
                pygame.draw.circle(sparkle_surf, (255, 255, 200), 
                                 (int(sparkle_size), int(sparkle_size)), int(sparkle_size))
                self.screen.blit(sparkle_surf, (int(sparkle_x), int(sparkle_y)))
    
    def draw_menu_options(self, options):
        """Draw enhanced menu options with better visibility and effects"""
        start_y = 280
        spacing = 70
        
        for i, option in enumerate(options):
            # Calculate glow effect
            if i not in self.option_glow:
                self.option_glow[i] = 0
                
            if i == self.selected_option:
                self.option_glow[i] = min(self.option_glow[i] + 8, 255)
            else:
                self.option_glow[i] = max(self.option_glow[i] - 12, 0)
            
            y_pos = start_y + i * spacing
            
            # Enhanced selection background with multiple layers
            if i == self.selected_option:
                # Outer glow
                glow_alpha = 60 + math.sin(pygame.time.get_ticks() * 0.008) * 30
                outer_glow = pygame.Surface((500, 60))
                outer_glow.set_alpha(int(glow_alpha))
                outer_glow.fill((100, 150, 255))
                outer_rect = pygame.Rect(150, y_pos - 10, 500, 60)
                self.screen.blit(outer_glow, outer_rect)
                
                # Main selection background
                selection_alpha = 120 + math.sin(pygame.time.get_ticks() * 0.01) * 40
                selection_surf = pygame.Surface((450, 50))
                selection_surf.set_alpha(int(selection_alpha))
                selection_surf.fill((50, 100, 200))
                selection_rect = pygame.Rect(175, y_pos - 5, 450, 50)
                self.screen.blit(selection_surf, selection_rect)
                
                # Animated border with multiple colors
                border_color_shift = math.sin(pygame.time.get_ticks() * 0.005) * 50
                border_color = (255, 200 + int(border_color_shift), 100)
                pygame.draw.rect(self.screen, border_color, selection_rect, 4)
                pygame.draw.rect(self.screen, (255, 255, 255), selection_rect, 2)
            
            # Create text with enhanced visibility
            # Text shadow for better readability
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    if dx != 0 or dy != 0:
                        shadow_text = self.menu_font.render(option, True, (0, 0, 0))
                        shadow_rect = shadow_text.get_rect(center=(400 + dx, y_pos + 20 + dy))
                        shadow_alpha_surf = pygame.Surface(shadow_text.get_size())
                        shadow_alpha_surf.set_alpha(150)
                        shadow_alpha_surf.blit(shadow_text, (0, 0))
                        self.screen.blit(shadow_alpha_surf, shadow_rect)
            
            # Main option text with enhanced colors
            if i == self.selected_option:
                color = (255, 255, 255)  # Pure white for selected
            else:
                color = (220, 220, 220)  # Light gray for unselected
                
            text = self.menu_font.render(option, True, color)
            text_rect = text.get_rect(center=(400, y_pos + 20))
            self.screen.blit(text, text_rect)
            
        # Enhanced controller hint with background
        if hasattr(self, 'selected_option'):
            hint_bg = pygame.Surface((600, 30))
            hint_bg.set_alpha(140)
            hint_bg.fill((20, 20, 60))
            hint_bg_rect = hint_bg.get_rect(center=(400, 535))
            self.screen.blit(hint_bg, hint_bg_rect)
            
            hint_text = self.small_font.render("← → to navigate, SPACE/ENTER to select", True, (255, 255, 150))
            hint_rect = hint_text.get_rect(center=(400, 535))
            self.screen.blit(hint_text, hint_rect)
    
    def draw_credits(self):
        """Draw enhanced credits screen with better visibility"""
        self.draw_background()
        self.draw_particles()
        
        # Add central background panel for better readability
        panel_surf = pygame.Surface((700, 500))
        panel_surf.set_alpha(180)
        panel_surf.fill((10, 15, 40))
        panel_rect = panel_surf.get_rect(center=(400, 300))
        self.screen.blit(panel_surf, panel_rect)
        
        # Add panel border
        pygame.draw.rect(self.screen, (100, 150, 255), panel_rect, 3)
        
        credits = [
            "SUPER MARIO - GESTURE CONTROL",
            "",
            "Developed with:",
            "• Python & Pygame",
            "• MediaPipe for Gesture Recognition",
            "• OpenCV for Computer Vision",
            "",
            "Features:",
            "• Hand Gesture Controls",
            "• Dynamic Platform Generation",
            "• Real-time Motion Detection",
            "• Infinite Scrolling World",
            "",
            "Controls:",
            "Right Hand → Move Right",
            "Left Hand → Move Left", 
            "Both Hands Up → Jump",
            "",
            "Press ESC to return to menu"
        ]
        
        start_y = 80
        for i, line in enumerate(credits):
            if line == "":
                continue
            elif line.startswith("•"):
                color = (255, 255, 150)
                font = self.small_font
            elif ":" in line and not line.startswith("Press"):
                color = (255, 200, 100)
                font = self.menu_font
            elif line == credits[0]:
                color = (255, 100, 100)
                font = self.title_font
            else:
                color = (255, 255, 255)
                font = self.small_font
                
            # Add text shadow for better visibility
            shadow_text = font.render(line, True, (0, 0, 0))
            shadow_rect = shadow_text.get_rect(center=(402, start_y + i * 25 + 2))
            self.screen.blit(shadow_text, shadow_rect)
            
            text = font.render(line, True, color)
            text_rect = text.get_rect(center=(400, start_y + i * 25))
            self.screen.blit(text, text_rect)
    
    def draw_settings(self):
        """Draw enhanced settings screen with better visibility"""
        self.draw_background()
        self.draw_particles()
        
        # Add settings panel background
        panel_surf = pygame.Surface((600, 400))
        panel_surf.set_alpha(170)
        panel_surf.fill((15, 20, 50))
        panel_rect = panel_surf.get_rect(center=(400, 330))
        self.screen.blit(panel_surf, panel_rect)
        
        # Add panel border with glow
        pygame.draw.rect(self.screen, (150, 200, 255), panel_rect, 4)
        pygame.draw.rect(self.screen, (255, 255, 255), panel_rect, 2)
        
        # Enhanced settings title with effects
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    shadow_text = self.title_font.render("SETTINGS", True, (0, 0, 0))
                    shadow_rect = shadow_text.get_rect(center=(400 + dx, 100 + dy))
                    shadow_surf = pygame.Surface(shadow_text.get_size())
                    shadow_surf.set_alpha(120)
                    shadow_surf.blit(shadow_text, (0, 0))
                    self.screen.blit(shadow_surf, shadow_rect)
        
        title_text = self.title_font.render("SETTINGS", True, (255, 100, 100))
        title_rect = title_text.get_rect(center=(400, 100))
        self.screen.blit(title_text, title_rect)
        
        # Update settings options based on current values
        self.settings_options = [
            f"MUSIC: {'ON' if self.music_enabled else 'OFF'}",
            f"SFX: {'ON' if self.sfx_enabled else 'OFF'}",
            f"DIFFICULTY: {self.difficulty}",
            "BACK"
        ]
        
        self.draw_menu_options(self.settings_options)
    
    def handle_input(self):
        """Handle keyboard input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if self.current_state == MenuState.MAIN_MENU:
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        self.selected_option = (self.selected_option - 1) % len(self.main_menu_options)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.selected_option = (self.selected_option + 1) % len(self.main_menu_options)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return self.handle_menu_selection()
                        
                elif self.current_state == MenuState.SETTINGS:
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        self.selected_option = (self.selected_option - 1) % len(self.settings_options)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.selected_option = (self.selected_option + 1) % len(self.settings_options)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return self.handle_settings_selection()
                    elif event.key == pygame.K_ESCAPE:
                        self.current_state = MenuState.MAIN_MENU
                        self.selected_option = 0
                        
                elif self.current_state == MenuState.CREDITS:
                    if event.key == pygame.K_ESCAPE:
                        self.current_state = MenuState.MAIN_MENU
                        self.selected_option = 0
                        
        return True
    
    def handle_menu_selection(self):
        """Handle main menu selection"""
        option = self.main_menu_options[self.selected_option]
        
        if option == "PLAY":
            self.current_state = MenuState.GAME
            pygame.mixer.music.fadeout(1000)  # Fade out menu music
            return "START_GAME"
        elif option == "SETTINGS":
            self.current_state = MenuState.SETTINGS
            self.selected_option = 0
        elif option == "CREDITS":
            self.current_state = MenuState.CREDITS
        elif option == "QUIT":
            return False
            
        return True
    
    def handle_settings_selection(self):
        """Handle settings menu selection"""
        option = self.settings_options[self.selected_option]
        
        if "MUSIC:" in option:
            self.music_enabled = not self.music_enabled
            if self.music_enabled:
                try:
                    pygame.mixer.music.play(-1, 0.0, 1000)
                except:
                    pass
            else:
                pygame.mixer.music.fadeout(500)
                
        elif "SFX:" in option:
            self.sfx_enabled = not self.sfx_enabled
            
        elif "DIFFICULTY:" in option:
            difficulties = ["EASY", "NORMAL", "HARD"]
            current_index = difficulties.index(self.difficulty)
            self.difficulty = difficulties[(current_index + 1) % len(difficulties)]
            
        elif option == "BACK":
            self.current_state = MenuState.MAIN_MENU
            self.selected_option = 0
            
        return True
    
    def run(self):
        """Main menu loop"""
        running = True
        
        while running:
            # Handle input
            result = self.handle_input()
            if result == "START_GAME":
                return "START_GAME"
            elif result == False:
                return False
            
            # Update animations
            self.update_particles()
            
            # Draw everything
            if self.current_state == MenuState.MAIN_MENU:
                self.draw_background()
                self.draw_particles()
                self.draw_title()
                self.draw_mario_character()
                self.draw_menu_options(self.main_menu_options)
                
            elif self.current_state == MenuState.SETTINGS:
                self.draw_settings()
                
            elif self.current_state == MenuState.CREDITS:
                self.draw_credits()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return False

def main():
    """Main function to run the menu system"""
    menu = MarioMenu()
    result = menu.run()
    
    if result == "START_GAME":
        # Import and run the main game
        pygame.quit()
        import subprocess
        subprocess.run([sys.executable, "18.py"])
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
