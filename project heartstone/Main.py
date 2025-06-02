import pygame

#основной сетап
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("project HeartStone")
running = True

#окно игры
surf = pygame.Surface((100,200))
surf.fill('orange')
x = 100
y = 150

#запуск и ход игры
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    display_surface.fill("darkgray")
    display_surface.blit(surf,(x,y))
    pygame.display.update()

pygame.quit()