import pygame
import sys
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("project HeartStone")
running = True
dragging = False
clock = pygame.time.Clock()

class GameBoard:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width * 0.9
        self.height = screen_height * 0.6
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2

        # Создаем слоты для карт (5 слотов на каждую сторону)
        self.player_slots = self.create_slots(is_player=True)
        self.opponent_slots = self.create_slots(is_player=False)

    def create_slots(self, is_player):
        slots = []
        slot_width = self.width // 6
        slot_height = self.height * 0.4
        slot_margin = slot_width * 0.1

        # Определение Y-позиции: нижняя часть для игрока, верхняя для противника
        y_position = self.y + (self.height * 0.55 if is_player else self.height * 0.05)

        # Создание 5 слотов
        for i in range(5):
            x_position = self.x + (slot_width * i) + slot_margin
            slot_rect = pygame.Rect(
                x_position,
                y_position,
                slot_width - slot_margin * 2,
                slot_height
            )
            slots.append({
                'rect': slot_rect,
                'occupied': False,
                'card': None
            })
        return slots

    def draw(self, screen):
        # Основное поле и разделительная линия
        pygame.draw.rect(screen, (40, 100, 40), (self.x, self.y, self.width, self.height), border_radius=12)
        pygame.draw.rect(screen, (180, 160, 120), (self.x, self.y, self.width, self.height), 4, border_radius=12)
        
        pygame.draw.line(
            screen, (180, 160, 120),
            (self.x, self.y + self.height // 2),
            (self.x + self.width, self.y + self.height // 2),
            3
        )

        # Отрисовка слотов для карт
        for slot in self.player_slots + self.opponent_slots:
            color = (70, 140, 70) if not slot['occupied'] else (30, 80, 30)
            pygame.draw.rect(screen, color, slot['rect'], border_radius=8)
            pygame.draw.rect(screen, (180, 160, 120), slot['rect'], 2, border_radius=8)

game_board = GameBoard(WINDOW_WIDTH, WINDOW_HEIGHT)
card_surface = pygame.Surface((120, 200))
card_rect = card_surface.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 100))
card_surface.fill('orange')

while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Начало перетаскивания карты
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if card_rect.collidepoint(event.pos):
                    dragging = True
                    offset_x = card_rect.x - event.pos[0]
                    offset_y = card_rect.y - event.pos[1]

        # Перетаскивание карты
        if event.type == pygame.MOUSEMOTION:
            if dragging:
                card_rect.x = event.pos[0] + offset_x
                card_rect.y = event.pos[1] + offset_y

        # Завершение перетаскивания карты
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False
                # Проверка на попадание в слот
                for slot in game_board.player_slots:
                    if slot['rect'].colliderect(card_rect) and not slot['occupied']:
                        slot['occupied'] = True
                        slot['card'] = card_rect.copy()  # Сохраняем позицию карты в слоте
                        card_rect.center = (-100, -100)  # Убираем карту с экрана

    display_surface.fill("darkgray")
    game_board.draw(display_surface)
    if card_rect.x > -100:  # Проверяем, что карта не "убрана"
        display_surface.blit(card_surface, card_rect)
    pygame.display.update()
pygame.quit()
sys.exit()