import pygame
import sys
import os

def run_game_with_menu_return():
    """
    Modified version of 18.py that can return to menu
    This preserves your original game logic while adding menu integration
    """
    
    # Import all the game logic from your original file
    import importlib.util
    spec = importlib.util.spec_from_file_location("game_module", "18.py")
    game_module = importlib.util.module_from_spec(spec)
    
    # Add a custom exit handler to the game module
    original_quit = pygame.quit
    
    def custom_quit():
        """Custom quit function that returns to launcher instead of completely exiting"""
        pygame.mixer.quit()  # Clean up audio
        pygame.quit()
        # Don't call sys.exit() here - let the launcher handle the flow
        return
    
    # Replace pygame.quit in the game module
    game_module.pygame.quit = custom_quit
    
    try:
        # Execute the game
        spec.loader.exec_module(game_module)
    except SystemExit:
        # Catch sys.exit() calls and convert them to returns
        pass
    except Exception as e:
        print(f"Game error: {e}")
    
    # Ensure pygame is properly quit
    try:
        pygame.quit()
    except:
        pass

if __name__ == "__main__":
    run_game_with_menu_return()
