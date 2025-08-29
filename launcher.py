import pygame
import sys
import subprocess
import os

def run_mario_game():
    """
    Main launcher for Super Mario Bros - Gesture Control Edition
    This script launches the menu system and handles game transitions
    """
    
    # Set the working directory to the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    while True:
        try:
            # Import and run the menu system
            from menu import MarioMenu
            
            # Create and run menu
            menu = MarioMenu()
            result = menu.run()
            
            # Handle menu result
            if result == "START_GAME":
                # Clean up menu resources
                pygame.quit()
                
                # Start the main game (18.py)
                try:
                    subprocess.run([sys.executable, "18.py"], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Game exited with error code: {e.returncode}")
                except FileNotFoundError:
                    print("Error: 18.py not found!")
                    break
                
                # After game ends, reinitialize pygame for menu
                pygame.init()
                
            else:
                # User chose to quit
                break
                
        except ImportError as e:
            print(f"Error importing menu: {e}")
            print("Make sure menu.py is in the same directory")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
    
    # Final cleanup
    try:
        pygame.quit()
    except:
        pass

if __name__ == "__main__":
    run_mario_game()
