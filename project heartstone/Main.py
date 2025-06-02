import pygame

#основной сетап
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("project HeartStone")
running = True
clock =  pygame.time.Clock()
#окно карт
cadr_sufr = pygame.Surface((120,200))
card_rect = cadr_sufr.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT - 100))
cadr_sufr.fill('orange')

#запуск и ход игры
while running:
    clock.tick()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    display_surface.fill("darkgray")
    display_surface.blit(cadr_sufr,card_rect)
    pygame.display.update()

pygame.quit()