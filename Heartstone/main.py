import pygame
import sys
from game_manager import GameManager

def main():
    pygame.init()
    
    # Screen dimensions
    SCREEN_WIDTH = 1280 
    SCREEN_HEIGHT = 720
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("project_HeartStone")
    
    clock = pygame.time.Clock()
    game_manager = GameManager(screen)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game_manager.handle_event(event)
        
        game_manager.update()
        game_manager.draw()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()