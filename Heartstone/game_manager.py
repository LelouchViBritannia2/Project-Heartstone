import pygame
import math
from player import Player
from card import CardType
import os

class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        #инциализация аудио
        pygame.mixer.init()
        self.init_background_music()
        
        #инциализация игроков
        self.player1 = Player("Игрок 1", True)
        self.player2 = Player("Игрок 2", True)
        self.current_player = self.player1
        self.other_player = self.player2
        
        #статус игры
        self.game_over = False
        self.winner = None
        self.selected_card_index = -1
        self.selected_minion_index = -1
        self.attack_mode = False
        self.turn_number = 1
        self.show_help = False
        self.show_menu = False
        self.menu_selected_option = 0
        self.menu_options = ["Продолжить", "Настройки", "Выйти"]
        self.show_settings = False
        self.volume = 0.3
        self.volume_dragging = False
        
        #окончание игры
        self.game_over_selected_option = 0
        self.game_over_options = ["Играть ещё раз", "Выйти"]
        
        #отрисовка окна коллекции карт
        self.show_card_collection = False
        self.collection_scroll_offset = 0
        self.collection_card_size = (120, 160)
        self.selected_collection_card = 0
        
        #перетаскивание и использования карт из руки
        self.dragging = False
        self.dragged_card_index = -1
        self.drag_start_pos = (0, 0)
        self.drag_current_pos = (0, 0)
        self.drag_offset = (0, 0)
        
        #флип стола
        self.table_flip_active = False
        self.flip_progress = 0.0
        self.flip_speed = 3.0
        
        #оверлей картинок
        self.show_photo = False
        self.space_pressed_once = False
        
        #бэкграунд картинки
        self.background_image = None
        self.background_loaded = False
        
        #фонт
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def init_background_music(self):
        """Музыка"""
        try:
            # Try to load background music from assets folder
            music_files = "Heartstone/assets/Linkin Park — In the End.mp3"
            
            music_loaded = False
            for music_file in music_files:
                if os.path.exists(music_file):
                    try:
                        pygame.mixer.music.load("Heartstone/assets/Linkin Park — In the End.mp3")
                        pygame.mixer.music.set_volume(0.3)
                        pygame.mixer.music.play(-1)  #бесконечная лупа
                        print(f"Background music loaded: {"Heartstone/assets/Linkin Park — In the End.mp3"}")
                        music_loaded = True
                        break
                    
                    except pygame.error as e:
                        print(f"Could not load {"Heartstone/assets/Linkin Park — In the End.mp3"}: {e}")
                        continue
            
        except pygame.error as e:
            print(f"Could not initialize background music: {e}")

    def load_background_image(self):
        """отрисовка поля"""
        if self.background_loaded:
            return
        
        try:
            background_files = "Heartstone/assets/table/backgrount.jpg"
            
            for bg_file in background_files:
                if os.path.exists("Heartstone/assets/table/backgrount.jpg"):
                    try:
                        self.background_image = pygame.image.load("Heartstone/assets/table/backgrount.jpg")
                        #скейл для приятности глазу
                        self.background_image = pygame.transform.smoothscale(
                            self.background_image, 
                            (self.screen_width, self.screen_height)
                        )
                        print(f"Background image loaded: {"Heartstone/assets/table/backgrount.jpg"}")
                        break
                    
                    except pygame.error as e:
                        print(f"Could not load {"Heartstone/assets/table/backgrount.jpg"}: {e}")
                        continue

        except Exception as e:
            print(f"Could not initialize background image: {e}")
        
        self.background_loaded = True
    
    def toggle_music(self):
        """включение и выключение музыки на кнопку"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
    
    def toggle_card_collection(self):
        """вкл/выкл коллекции карт"""
        self.show_card_collection = not self.show_card_collection
        if self.show_card_collection:
            self.collection_scroll_offset = 0
    
    def toggle_help(self):
        """вкл/выкл таба(окно гайда)"""
        self.show_help = not self.show_help
    
    def handle_menu_selection(self):
        """меню"""
        selected = self.menu_options[self.menu_selected_option]
        
        if selected == "Продолжить":
            self.show_menu = False
        elif selected == "Настройки":
            self.show_settings = True
        elif selected == "Выйти":
            pygame.quit()
            exit()
    
    def handle_menu_mouse_click(self, pos):
        """кнопки в меню нажимаются мышкой"""
        if self.show_settings:
            self.handle_settings_mouse_click(pos)
            return
            
        #меню окна(вид)
        window_width = 400
        window_height = 300
        window_x = (self.screen_width - window_width) // 2
        window_y = (self.screen_height - window_height) // 2
        start_y = window_y + 120
        
        #проверка на клик в меню
        menu_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        if not menu_rect.collidepoint(pos):
            #выключение меню при клике не на него
            self.show_menu = False
            return
        
        #чек что выбрал при клике игрок в меню
        for i, option in enumerate(self.menu_options):
            option_rect = pygame.Rect(window_x + 50, start_y + i * 60 - 15, window_width - 100, 50)
            if option_rect.collidepoint(pos):
                self.menu_selected_option = i
                self.handle_menu_selection()
                break
    
    def handle_menu_mouse_hover(self, pos):
        """настройки"""
        if self.show_settings:
            return
            
        #настройки вид
        window_width = 400
        window_height = 300
        window_x = (self.screen_width - window_width) // 2
        window_y = (self.screen_height - window_height) // 2
        start_y = window_y + 120
        
        for i, option in enumerate(self.menu_options):
            option_rect = pygame.Rect(window_x + 50, start_y + i * 60 - 15, window_width - 100, 50)
            if option_rect.collidepoint(pos):
                self.menu_selected_option = i
                break
    
    def handle_event(self, event):
        if self.game_over:
            self.handle_game_over_event(event)
            return
        if self.table_flip_active:
            return
            
        if event.type == pygame.KEYDOWN:
            #ESC для закрытия любого меню
            if event.key == pygame.K_ESCAPE:
                if self.show_settings:
                    self.show_settings = False
                elif self.show_menu:
                    self.show_menu = False
                elif self.show_help:
                    self.show_help = False
                elif self.show_card_collection:
                    self.show_card_collection = False
                elif self.show_photo:
                    self.show_photo = False
                    self.space_pressed_once = False
                elif self.attack_mode:
                    self.cancel_selection()
                else:
                    self.show_menu = True
                    self.menu_selected_option = 0
            #включение TAB-а
            elif event.key == pygame.K_TAB:
                if self.show_card_collection:
                    self.show_card_collection = False
                elif not self.show_menu and not self.show_settings and not self.show_photo:
                    self.toggle_help()
            #навигация в таб-е
            elif self.show_menu and not self.show_settings:
                if event.key == pygame.K_UP and self.menu_selected_option > 0:
                    self.menu_selected_option -= 1
                elif event.key == pygame.K_DOWN and self.menu_selected_option < len(self.menu_options) - 1:
                    self.menu_selected_option += 1
                elif event.key == pygame.K_RETURN:
                    self.handle_menu_selection()
            #блокировка оверлея при открытом меню
            elif self.show_help or self.show_menu or self.show_settings or self.show_card_collection:
                return
            #SPACE переворот экрана
            elif event.key == pygame.K_SPACE:
                if not self.space_pressed_once:
                    #первое нажатие - переворот фона
                    self.show_photo = True
                    self.space_pressed_once = True
                else:
                    #старт тейбл флипа после 2-го нажатия
                    self.show_photo = False
                    self.space_pressed_once = False
                    self.end_turn()
            #блокировка оверлея при открытом фото
            elif self.show_photo:
                return
            #нормал гейм стейт без открытого оверлея
            elif event.key == pygame.K_a:
                self.toggle_attack_mode()
            elif event.key == pygame.K_m:
                self.toggle_music()
            elif event.key == pygame.K_c:
                self.toggle_card_collection()
            elif not self.attack_mode:
                if event.key == pygame.K_LEFT and self.selected_card_index > 0:
                    self.selected_card_index -= 1
                elif event.key == pygame.K_RIGHT and self.selected_card_index < len(self.current_player.hand) - 1:
                    self.selected_card_index += 1
            else:
                if event.key == pygame.K_LEFT and self.selected_minion_index > 0:
                    self.selected_minion_index -= 1
                elif event.key == pygame.K_RIGHT and self.selected_minion_index < len(self.current_player.board) - 1:
                    self.selected_minion_index += 1
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  #лефтклик
                if self.show_menu:
                    self.handle_menu_mouse_click(event.pos)
                elif self.show_card_collection:
                    self.handle_card_collection_mouse_click(event.pos)
                elif not (self.show_help or self.show_photo):
                    self.handle_mouse_down(event.pos)
                    #проверка на клик коллекции карт
                    self.handle_card_collection_button_click(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.show_settings and self.volume_dragging:
                    self.volume_dragging = False
                elif not (self.show_menu or self.show_help or self.show_photo):
                    self.handle_mouse_up(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            if self.show_menu:
                if self.show_settings and self.volume_dragging:
                    self.handle_volume_drag(event.pos)
                else:
                    self.handle_menu_mouse_hover(event.pos)
            elif self.show_card_collection:
                self.handle_card_collection_mouse_hover(event.pos)
            elif not (self.show_help or self.show_photo):
                self.handle_mouse_motion(event.pos)
        elif event.type == pygame.MOUSEWHEEL:
            if self.show_card_collection:
                self.handle_card_collection_scroll(event.y)
    
    def handle_mouse_down(self, pos):
        """нажатие на мышку"""
        #проверка на нажатие на карту для её перемещения
        hand_y = self.screen_height - 180
        hand_width = len(self.current_player.hand) * 130
        start_x = (self.screen_width - hand_width) // 2
        
        for i, card in enumerate(self.current_player.hand):
            card_x = start_x + i * 130
            card_rect = pygame.Rect(card_x, hand_y, 120, 160)
            if card_rect.collidepoint(pos):
                #начало перемещения карты
                self.dragging = True
                self.dragged_card_index = i
                self.drag_start_pos = pos
                self.drag_current_pos = pos
                self.drag_offset = (pos[0] - card_x, pos[1] - hand_y)
                self.selected_card_index = i
                self.selected_minion_index = -1
                self.attack_mode = False
                return
        
        #если не зажата, прост клик
        self.handle_mouse_click(pos)
    
    def handle_mouse_up(self, pos):
        """отжимание кнопки мыши"""
        if self.dragging:
            self.handle_card_drop(pos)
            self.dragging = False
            self.dragged_card_index = -1
        else:
            #клик если не зажата
            pass
    
    def handle_mouse_motion(self, pos):
        """движение мышки"""
        if self.dragging:
            self.drag_current_pos = pos
    
    def handle_card_drop(self, pos):
        """отпускание перемещающейся карты"""
        if self.dragged_card_index < 0 or self.dragged_card_index >= len(self.current_player.hand):
            return
        
        card = self.current_player.hand[self.dragged_card_index]
        
        #проверка на кого поставлена карта
        current_face_rect = pygame.Rect(10, self.screen_height - 120, 200, 100)
        if current_face_rect.collidepoint(pos):
            if card.card_type == CardType.SPELL:
                if self.current_player.play_card(self.dragged_card_index, self.current_player):
                    self.selected_card_index = -1
                    self.cleanup_dead_minions()
                    self.check_game_over()
            return
        
        #проверка на то, убрал ли карту обратно в круку
        hand_y = self.screen_height - 180
        hand_zone = pygame.Rect(0, hand_y - 20, self.screen_width, 200)
        if hand_zone.collidepoint(pos):
            #отпуск карты обратно в руку
            self.selected_card_index = -1
            return
        
        #проверка на дроп в зону стола
        board_drop_zone = pygame.Rect(0, self.screen_height - 400, self.screen_width, 200)
        if board_drop_zone.collidepoint(pos) and card.card_type == CardType.MINION:
            #сыгрывание карты существа
            if self.current_player.play_card(self.dragged_card_index):
                self.selected_card_index = -1
                self.cleanup_dead_minions()
                self.check_game_over()
            return
        
        #проверка на цель в виде соперника и его существ для атаки заклинаниями и существами
        opponent_face_rect = pygame.Rect(10, 10, 200, 100)
        if opponent_face_rect.collidepoint(pos):
            if card.card_type == CardType.SPELL:
                if self.current_player.play_card(self.dragged_card_index, self.other_player):
                    self.selected_card_index = -1
                    self.cleanup_dead_minions()
                    self.check_game_over()
            elif card.card_type == CardType.MINION:
                #прямая атака на соперника
                if self.current_player.play_card(self.dragged_card_index):
                    self.selected_card_index = -1
                    self.cleanup_dead_minions()
                    self.check_game_over()
            return
        
        #проверка на дроп на существо соперника
        opponent_board_y = 50
        board_width = len(self.other_player.board) * 130
        start_x = (self.screen_width - board_width) // 2
        
        for i, target_card in enumerate(self.other_player.board):
            card_x = start_x + i * 130
            card_rect = pygame.Rect(card_x - 10, opponent_board_y - 10, 140, 180)
            if card_rect.collidepoint(pos):
                if card.card_type == CardType.SPELL:
                    if self.current_player.play_card(self.dragged_card_index, target_card):
                        self.selected_card_index = -1
                        self.cleanup_dead_minions()
                        self.check_game_over()
                elif card.card_type == CardType.MINION:
                    if self.current_player.play_card(self.dragged_card_index):
                        self.selected_card_index = -1
                        self.cleanup_dead_minions()
                        self.check_game_over()
                return
        
        #проверка на цель в виде своих существ
        current_board_y = self.screen_height - 350
        board_width = len(self.current_player.board) * 130
        start_x = (self.screen_width - board_width) // 2
        
        for i, target_card in enumerate(self.current_player.board):
            card_x = start_x + i * 130
            card_rect = pygame.Rect(card_x - 10, current_board_y - 10, 140, 180)
            if card_rect.collidepoint(pos):
                if card.card_type == CardType.SPELL:
                    if self.current_player.play_card(self.dragged_card_index, target_card):
                        self.selected_card_index = -1
                        self.cleanup_dead_minions()
                        self.check_game_over()
                return
        
        #если ничего из вышеперечисленног - отмена действия
        self.selected_card_index = -1
    
    def handle_mouse_click(self, pos):
        """просто клик на карты"""
        
        current_board_y = self.screen_height - 350
        board_width = len(self.current_player.board) * 130
        start_x = (self.screen_width - board_width) // 2
        
        for i, card in enumerate(self.current_player.board):
            card_x = start_x + i * 130
            card_rect = pygame.Rect(card_x, current_board_y, 120, 160)
            if card_rect.collidepoint(pos):
                if self.selected_card_index >= 0:
                    #спелл таргет для дружественных существ
                    self.play_selected_card(target=card)
                    return
                elif card.can_attack_target():
                    #выбор существа для атаки
                    if self.selected_minion_index == i and self.attack_mode:
                        #отмена выбора при нажатии на то же существо
                        self.selected_minion_index = -1
                        self.attack_mode = False
                    else:
                        self.selected_minion_index = i
                        self.attack_mode = True
                        self.selected_card_index = -1
                return
        
        #проверка на клик для доски соперника
        opponent_board_y = 50
        board_width = len(self.other_player.board) * 130
        start_x = (self.screen_width - board_width) // 2
        
        for i, card in enumerate(self.other_player.board):
            card_x = start_x + i * 130
            card_rect = pygame.Rect(card_x, opponent_board_y, 120, 160)
            if card_rect.collidepoint(pos):
                if self.selected_card_index >= 0:
                    #спелл таргет - вражеское существо
                    self.play_selected_card(target=card)
                elif self.attack_mode and self.selected_minion_index >= 0:
                    #атака на существо
                    self.attack_target(card)
                return
        
        #проверка на атаку вражеского игрока
        opponent_face_rect = pygame.Rect(10, 10, 200, 100)
        if opponent_face_rect.collidepoint(pos):
            if self.selected_card_index >= 0:
                #спелл таргет для вражеского игрока
                self.play_selected_card(target=self.other_player)
            elif self.attack_mode and self.selected_minion_index >= 0:
                #атака енеми плеера
                self.attack_target(self.other_player)
            return
        
        #проверка на клик на себя
        current_face_rect = pygame.Rect(10, self.screen_height - 120, 200, 100)
        if current_face_rect.collidepoint(pos):
            if self.selected_card_index >= 0:
                #спелл таргет
                self.play_selected_card(target=self.current_player)
            return
        
        #клик на ничего из вышеперечисленного - десилект
        self.cancel_selection()
    
    def play_selected_card(self, target=None):
        """сыграть выбранной картой"""
        if self.selected_card_index < 0 or self.selected_card_index >= len(self.current_player.hand):
            return
        
        card = self.current_player.hand[self.selected_card_index]
        
        # выбор атаки спелла прямо на оппонента
        if card.card_type == CardType.SPELL and not target and card.spell_damage > 0:
            target = self.other_player
        
        if self.current_player.play_card(self.selected_card_index, target):
            self.selected_card_index = -1
            self.cleanup_dead_minions()
            self.check_game_over()
    
    def attack_target(self, target):
        """атака выбранным существом"""
        if self.selected_minion_index < 0 or self.selected_minion_index >= len(self.current_player.board):
            return
        
        if self.current_player.attack_with_minion(self.selected_minion_index, target):
            self.cleanup_dead_minions()
            self.cancel_selection()
            self.check_game_over()
    
    def toggle_attack_mode(self):
        """режим атаки"""
        if len(self.current_player.board) > 0:
            self.attack_mode = not self.attack_mode
            if self.attack_mode:
                self.selected_card_index = -1
                self.selected_minion_index = 0
            else:
                self.selected_minion_index = -1
    
    def cancel_selection(self):
        """отмена выбора существа в аттак режиме"""
        self.selected_card_index = -1
        self.selected_minion_index = -1
        self.attack_mode = False
    
    def cleanup_dead_minions(self):
        """ремув мёртвых существ"""
        self.current_player.remove_dead_minions()
        self.other_player.remove_dead_minions()
    
    def end_turn(self):
        """окончание хода и начала флип анимации"""
        self.current_player.end_turn()
        self.table_flip_active = True
        self.flip_progress = 0.0
    
    def complete_turn_switch(self):
        """окончание хода игрока после анимации переворота"""
        #смена игрока
        self.current_player, self.other_player = self.other_player, self.current_player
        self.current_player.start_turn()
        self.turn_number += 1
        self.selected_card_index = -1
        
        #ресет анимаций
        self.table_flip_active = False
        self.flip_progress = 0.0
    
    def update(self):
        """обновления состояния игры"""
        if self.table_flip_active:
            self.flip_progress += self.flip_speed * (1/60)
            if self.flip_progress >= 1.0:
                self.complete_turn_switch()
        
        self.check_game_over()
    
    def check_game_over(self):
        """проверка на геймовер"""
        if self.player1.health <= 0:
            self.game_over = True
            self.winner = self.player2
        elif self.player2.health <= 0:
            self.game_over = True
            self.winner = self.player1
    
    def draw(self):
        """отрисовка игры после флипа"""
        if self.table_flip_active:
            self.draw_table_flip()
        else:
            self.draw_normal_game()
    
    def draw_normal_game(self):
        """нормал стейт отрисовка"""
        #отрисовка бэкграунда
        if not self.background_loaded:
            self.load_background_image()
        
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
         #отрисовка оппонента
        self.other_player.draw_board(self.screen, 50)
        self.draw_player_info_with_highlight(self.other_player, 10, 10, False)
        
        #отрисовка нынешнего игрока
        self.draw_player_board_with_selection(self.current_player, self.screen_height - 350)
        self.draw_hand_with_drag(self.current_player, self.screen_height - 180)
        self.draw_player_info_with_highlight(self.current_player, 10, self.screen_height - 120, True)
        #отрисовка взятых карт
        if self.dragging and self.dragged_card_index >= 0:
            self.draw_dragged_card()
        
        #отрисовка коллекции
        self.draw_card_collection_button()
        
        #отрисовка таба(помощи)
        if self.show_help:
            self.draw_help_window()
        
        #отрисовка меню
        if self.show_menu:
            if self.show_settings:
                self.draw_settings()
            else:
                self.draw_menu()
        
        if self.show_card_collection:
            self.draw_card_collection_window()
        
        if self.show_photo:
            self.draw_photo_overlay()
        
        #геймовер скрин
        if self.game_over:
            self.draw_game_over()
    
    def draw_help_window(self):
        """отрисовка окна помощи"""
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        #вид окна
        window_width = 800
        window_height = 500
        window_x = (self.screen_width - window_width) // 2
        window_y = (self.screen_height - window_height) // 2
        
        #бэкграунд
        help_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        pygame.draw.rect(self.screen, (40, 40, 40), help_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), help_rect, 3)
        
        #Названия
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Помощь", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, window_y + 40))
        self.screen.blit(title_text, title_rect)
        
        left_sections = [
            ("Управление:", [
                "TAB - Закрыть окно помощи",
                "SPACE - Закончить ход",
                "ESC - Выйти из режима атаки",
                "A - Войти в режим атаки",
                "M - Вкл/Выкл музыку",
                "Стрелочки для направления в режиме атаки"
            ]),
            ("Геймплей:", [
                "Красные значения - урон, зелёные - здоровье, синие - стоимость",
                "Перетаскивайте карты в цели, которые хотите атаковать",
                "Чтобы призвать существо, переместите его на свою чать стола",
                "Чтобы использовать заклинание, переместите его на существо/игрока",
                "Переместите карту обратно в руку для отмены действия",
                "Нажмите на существо, для его выделения",
                "Атакуйте вражеских существ или игрока с помощью существ и заклинаний",
                "Используйте ману для разыгрывания карт"
            ])
        ]
        
        right_section = ("Правила:", [
            "Вы начинаете игру с 30 здоровья и 1 мана",
            "+1 мана каждый ход(до 10)",
            "Каждый ход даётся карта",
            "Максимум 7 существ на столе",
            "Максимум 7 карт в руке",
            "Для победы убейте соперника"
        ])
        
        current_y = window_y + 80
        
        for section_title, section_items in left_sections:
            section_font = pygame.font.Font(None, 32)
            section_text = section_font.render(section_title, True, (255, 255, 0))
            self.screen.blit(section_text, (window_x + 20, current_y))
            current_y += 35
            
            for item in section_items:
                item_text = self.small_font.render(item, True, (255, 255, 255))
                self.screen.blit(item_text, (window_x + 40, current_y))
                current_y += 22
            
            current_y += 10
        
        right_x = window_x + window_width // 2 + 20
        right_y = window_y + 80
        
        section_font = pygame.font.Font(None, 32)
        section_text = section_font.render(right_section[0], True, (255, 255, 0))
        self.screen.blit(section_text, (right_x, right_y))
        right_y += 35
        
        for item in right_section[1]:
            item_text = self.small_font.render(item, True, (255, 255, 255))
            self.screen.blit(item_text, (right_x, right_y))
            right_y += 22
        
        close_text = self.small_font.render("Нажмите TAB чтобы закрыть", True, (200, 200, 200))
        close_rect = close_text.get_rect(center=(self.screen_width // 2, window_y + window_height + 30))
        self.screen.blit(close_text, close_rect)
    
    def draw_card_collection_button(self):
        """отрисовка кнопки коллекции"""
        button_width = 150
        button_height = 40
        button_x = self.screen_width - button_width - 10
        button_y = self.screen_height - button_height - 10
        
        #бэкграунд
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (60, 60, 60), button_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 2)
        
        #отрисовка текста
        button_text = self.small_font.render("Коллекция карт", True, (255, 255, 255))
        text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, text_rect)
    
    def handle_card_collection_button_click(self, pos):
        """долго нажатие на коллекция"""
        button_width = 150
        button_height = 40
        button_x = self.screen_width - button_width - 10
        button_y = self.screen_height - button_height - 10
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if button_rect.collidepoint(pos):
            self.toggle_card_collection()
    
    def handle_card_collection_mouse_click(self, pos):
        """просто клик на коллекцию"""
        #вид окна коллекции
        window_width = 900
        window_height = 600
        window_x = (self.screen_width - window_width) // 2
        window_y = (self.screen_height - window_height) // 2
        
        #чек на клик вне коллекции
        collection_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        if not collection_rect.collidepoint(pos):
            #закрытие его в этом случае
            self.show_card_collection = False
            return
        
        close_button_rect = pygame.Rect(window_x + window_width - 40, window_y + 10, 30, 30)
        if close_button_rect.collidepoint(pos):
            self.show_card_collection = False
            return
    
    def handle_card_collection_mouse_hover(self, pos):
        """выход мышки за пределы окна"""
        pass
    
    def handle_card_collection_scroll(self, scroll_y):
        """скролл в коллекции"""
        from card import CARD_DATABASE
        
        #скорость скролла
        scroll_speed = 40
        
        #апдейт окна при скролле
        self.collection_scroll_offset -= scroll_y * scroll_speed
        
        #вычисления окна при скролле
        entry_height = 220
        entry_spacing = 30
        total_content_height = len(CARD_DATABASE) * (entry_height + entry_spacing)
        window_height = 600
        visible_height = window_height - 120
        
        max_scroll = max(0, total_content_height - visible_height)
        
        self.collection_scroll_offset = max(0, min(self.collection_scroll_offset, max_scroll))
    
    def draw_card_collection_window(self):
        """отрисовка карт в коллекции"""
        from card import CARD_DATABASE
        
        #прозрачный бэкграунд
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        #вид коллекции
        window_width = 900
        window_height = 600
        window_x = (self.screen_width - window_width) // 2
        window_y = (self.screen_height - window_height) // 2
        
        collection_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        pygame.draw.rect(self.screen, (40, 40, 40), collection_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), collection_rect, 3)
        
        #тайтл
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Коллекция", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, window_y + 40))
        self.screen.blit(title_text, title_rect)
        
        #кнопка закрытия
        close_button_rect = pygame.Rect(window_x + window_width - 40, window_y + 10, 30, 30)
        pygame.draw.rect(self.screen, (80, 80, 80), close_button_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), close_button_rect, 2)
        
        #отрисовка Х
        center_x = close_button_rect.centerx
        center_y = close_button_rect.centery
        offset = 8
        pygame.draw.line(self.screen, (255, 255, 255), 
                        (center_x - offset, center_y - offset), 
                        (center_x + offset, center_y + offset), 3)
        pygame.draw.line(self.screen, (255, 255, 255), 
                        (center_x + offset, center_y - offset), 
                        (center_x - offset, center_y + offset), 3)
        
        #контент для скролла
        content_area_x = window_x + 20
        content_area_y = window_y + 80
        content_area_width = window_width - 40
        content_area_height = window_height - 120
        
        #скролл рект
        content_clip_rect = pygame.Rect(content_area_x, content_area_y, content_area_width, content_area_height)
        
        #зажим кратинок так, чтобы они не вываливались из окна
        original_clip = self.screen.get_clip()
        self.screen.set_clip(content_clip_rect)
        
        #отрисовка карт с описанием
        entry_height = 220 
        entry_spacing = 30
        
        for i, card_template in enumerate(CARD_DATABASE):
            entry_y = content_area_y + i * (entry_height + entry_spacing) - self.collection_scroll_offset
            
            #скип того, что вне экрана
            if entry_y + entry_height < content_area_y - 50 or entry_y > content_area_y + content_area_height + 50:
                continue
            
            #карты для дисплея
            display_card = type(card_template)(
                card_template.name,
                card_template.cost,
                card_template.card_type,
                card_template.description,
                card_template.attack,
                card_template.health,
                card_template.spell_damage,
                card_template.image_path,
                card_template.cost_icon_path,
                card_template.attack_icon_path,
                card_template.health_icon_path,
                card_template.spell_icon_path
            )
            
            #отрисовка карты слева
            card_x = content_area_x + 15
            card_y = entry_y + 10
            
            #отрисовка только если видна
            if card_y >= content_area_y - 160 and card_y <= content_area_y + content_area_height:
                display_card.draw(self.screen, card_x, card_y, False)
            
            #отрисовка описания
            desc_x = card_x + 150 
            desc_y = entry_y + 10 
            desc_width = content_area_width - 180
            
            #отрисовка описания если оно помещается
            if desc_y >= content_area_y - 50 and desc_y <= content_area_y + content_area_height + 50:
                #имя карт
                name_font = pygame.font.Font(None, 28)
                name_text = name_font.render(display_card.name, True, (255, 255, 0))
                self.screen.blit(name_text, (desc_x, desc_y))
                
                current_y = desc_y + 35
                
                #тип карты
                type_cost_text = self.small_font.render(f"Тип: {display_card.card_type.value.title()} | Стоимость: {display_card.cost}", True, (200, 200, 200))
                self.screen.blit(type_cost_text, (desc_x, current_y))
                current_y += 28
                
                #Описание существ
                if display_card.card_type.value == "minion":
                    stats_text = self.small_font.render(f"Урон: {display_card.attack} | Здоровье: {display_card.health}", True, (200, 200, 200))
                    self.screen.blit(stats_text, (desc_x, current_y))
                    current_y += 28
                
                # спелл дмг
                if display_card.spell_damage != 0:
                    if display_card.spell_damage > 0:
                        spell_text = self.small_font.render(f"Урон способностями: {display_card.spell_damage}", True, (200, 100, 200))
                    else:
                        spell_text = self.small_font.render(f"Здоровье: {abs(display_card.spell_damage)}", True, (100, 255, 100))
                    self.screen.blit(spell_text, (desc_x, current_y))
                    current_y += 28
                
                #описание
                if display_card.description:
                    current_y += 15
                    desc_title = self.small_font.render("Описанме:", True, (255, 255, 255))
                    self.screen.blit(desc_title, (desc_x, current_y))
                    current_y += 25
                    
                    words = display_card.description.split()
                    lines = []
                    current_line = ""
                    max_width = desc_width - 20
                    
                    for word in words:
                        test_line = current_line + (" " if current_line else "") + word
                        test_surface = self.small_font.render(test_line, True, (255, 255, 255))
                        if test_surface.get_width() <= max_width:
                            current_line = test_line
                        else:
                            if current_line:
                                lines.append(current_line)
                            current_line = word
                    
                    if current_line:
                        lines.append(current_line)
                    
                    #отрисовка с нужными скейлами
                    for line in lines:
                        if current_y <= entry_y + entry_height - 10:
                            desc_text = self.small_font.render(line, True, (180, 180, 180))
                            if desc_x + desc_text.get_width() <= content_area_x + content_area_width - 15:
                                self.screen.blit(desc_text, (desc_x, current_y))
                        current_y += 22
            
            #отрисовка линий меж контентом
            if i < len(CARD_DATABASE) - 1:
                separator_y = entry_y + entry_height + entry_spacing // 2
                if separator_y >= content_area_y and separator_y <= content_area_y + content_area_height:
                    pygame.draw.line(self.screen, (100, 100, 100), 
                                   (content_area_x + 10, separator_y), 
                                   (content_area_x + content_area_width - 10, separator_y), 1)

        self.screen.set_clip(original_clip)
    
    def draw_menu(self):
        """ескейп оверлей"""
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        #вид меню
        window_width = 400
        window_height = 300
        window_x = (self.screen_width - window_width) // 2
        window_y = (self.screen_height - window_height) // 2
        
        #бэкграунд меню
        menu_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        pygame.draw.rect(self.screen, (40, 40, 40), menu_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), menu_rect, 3)
        
        # Тайтл
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Меню", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, window_y + 50))
        self.screen.blit(title_text, title_rect)
        
        # Опции в менню
        option_font = pygame.font.Font(None, 36)
        start_y = window_y + 120
        
        for i, option in enumerate(self.menu_options):
            #подсветка выбраннного 
            if i == self.menu_selected_option:
                color = (255, 255, 0)
                # бэкграунд выбранного
                option_bg = pygame.Rect(window_x + 50, start_y + i * 60 - 15, window_width - 100, 50)
                pygame.draw.rect(self.screen, (80, 80, 80), option_bg)
            else:
                color = (255, 255, 255)
            
            option_text = option_font.render(option, True, color)
            option_rect = option_text.get_rect(center=(self.screen_width // 2, start_y + i * 60 + 10))
            self.screen.blit(option_text, option_rect)
    
    def handle_settings_mouse_click(self, pos):
        """маус клики в настройках"""
        #Вид настроек
        window_width = 500
        window_height = 400
        window_x = (self.screen_width - window_width) // 2
        window_y = (self.screen_height - window_height) // 2
        
        #чек на клик вне меню
        settings_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        if not settings_rect.collidepoint(pos):
            #закрытие
            self.show_settings = False
            return
        
        #вид настройки звука
        slider_y = window_y + 150
        slider_x = window_x + 150
        slider_width = 200
        slider_rect = pygame.Rect(slider_x, slider_y - 10, slider_width, 20)
        
        if slider_rect.collidepoint(pos):
            #перемещение ползунка звука
            self.volume_dragging = True
            #счисление звука
            relative_x = pos[0] - slider_x
            self.volume = max(0.0, min(1.0, relative_x / slider_width))
            pygame.mixer.music.set_volume(self.volume)
        
        back_button_rect = pygame.Rect(window_x + 50, window_y + window_height - 80, 100, 40)
        if back_button_rect.collidepoint(pos):
            self.show_settings = False
    
    def handle_volume_drag(self, pos):
        """перемещение звука"""
        if not self.volume_dragging:
            return
            
        #вид окна настроек
        window_width = 500
        window_x = (self.screen_width - window_width) // 2
        slider_x = window_x + 150
        slider_width = 200
        
        #счистление звука
        relative_x = pos[0] - slider_x
        self.volume = max(0.0, min(1.0, relative_x / slider_width))
        pygame.mixer.music.set_volume(self.volume)
    
    def handle_game_over_event(self, event):
        """нажатие на геймовер"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and self.game_over_selected_option > 0:
                self.game_over_selected_option -= 1
            elif event.key == pygame.K_DOWN and self.game_over_selected_option < len(self.game_over_options) - 1:
                self.game_over_selected_option += 1
            elif event.key == pygame.K_RETURN:
                self.handle_game_over_selection()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.handle_game_over_mouse_click(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_game_over_mouse_hover(event.pos)
    
    def handle_game_over_selection(self):
        """нажатие на геймовер"""
        selected = self.game_over_options[self.game_over_selected_option]
        
        if selected == "Начать заного":
            self.restart_game()
        elif selected == "Выйти":
            pygame.quit()
            exit()
    
    def handle_game_over_mouse_click(self, pos):
        """клик на геймовер"""
        #отрисовка
        button_width = 200
        button_height = 50
        button_x = (self.screen_width - button_width) // 2
        start_y = self.screen_height // 2 + 50
        
        #чек на что кликнул игрок
        for i, option in enumerate(self.game_over_options):
            button_y = start_y + i * 70
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            if button_rect.collidepoint(pos):
                self.game_over_selected_option = i
                self.handle_game_over_selection()
                break
    
    def handle_game_over_mouse_hover(self, pos):
        """нажатие на геймовер"""
        # вид окна
        button_width = 200
        button_height = 50
        button_x = (self.screen_width - button_width) // 2
        start_y = self.screen_height // 2 + 50
    
        for i, option in enumerate(self.game_over_options):
            button_y = start_y + i * 70
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            if button_rect.collidepoint(pos):
                self.game_over_selected_option = i
                break
    
    def restart_game(self):
        """рестарт"""
        #обновление геймстейта
        self.game_over = False
        self.winner = None
        self.selected_card_index = -1
        self.selected_minion_index = -1
        self.attack_mode = False
        self.turn_number = 1
        self.show_help = False
        self.show_menu = False
        self.show_settings = False
        self.show_card_collection = False
        self.show_photo = False
        self.space_pressed_once = False
        self.table_flip_active = False
        self.flip_progress = 0.0
        self.dragging = False
        self.dragged_card_index = -1
        self.game_over_selected_option = 0
        
        self.player1 = Player("Игрок 1", True)
        self.player2 = Player("Игрок 2", True)
        self.current_player = self.player1
        self.other_player = self.player2
    
    def draw_settings(self):
        """Отрисовка меню"""
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        window_width = 500
        window_height = 400
        window_x = (self.screen_width - window_width) // 2
        window_y = (self.screen_height - window_height) // 2
        
        settings_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        pygame.draw.rect(self.screen, (40, 40, 40), settings_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), settings_rect, 3)
        
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Настройки", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, window_y + 50))
        self.screen.blit(title_text, title_rect)
        
        volume_label = self.font.render("Звук:", True, (255, 255, 255))
        self.screen.blit(volume_label, (window_x + 50, window_y + 140))
        
        slider_y = window_y + 150
        slider_x = window_x + 150
        slider_width = 200
        slider_height = 10
        
        track_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
        pygame.draw.rect(self.screen, (100, 100, 100), track_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), track_rect, 2)
        
        fill_width = int(slider_width * self.volume)
        if fill_width > 0:
            fill_rect = pygame.Rect(slider_x, slider_y, fill_width, slider_height)
            pygame.draw.rect(self.screen, (0, 255, 0), fill_rect)
        
        handle_x = slider_x + int(slider_width * self.volume) - 5
        handle_rect = pygame.Rect(handle_x, slider_y - 5, 10, 20)
        pygame.draw.rect(self.screen, (255, 255, 255), handle_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), handle_rect, 2)
        
        volume_text = self.small_font.render(f"{int(self.volume * 100)}%", True, (255, 255, 255))
        self.screen.blit(volume_text, (slider_x + slider_width + 20, window_y + 145))
        
        back_button_rect = pygame.Rect(window_x + 50, window_y + window_height - 80, 100, 40)
        pygame.draw.rect(self.screen, (80, 80, 80), back_button_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), back_button_rect, 2)
        
        back_text = self.font.render("Назад", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=back_button_rect.center)
        self.screen.blit(back_text, back_text_rect)
        
    
    def draw_hand_with_drag(self, player, y_position):
        """отрисовка руки даже с взятой картой"""
        hand_width = len(player.hand) * 130
        start_x = (self.screen_width - hand_width) // 2
        
        for i, card in enumerate(player.hand):
            #скип карты, что ты тащищь
            if self.dragging and i == self.dragged_card_index:
                continue
                
            x = start_x + i * 130
            selected = (i == self.selected_card_index and not self.dragging)
            card.draw(self.screen, x, y_position, selected)
    
    def draw_dragged_card(self):
        """отрисовка тащющейся карты"""
        if self.dragged_card_index >= 0 and self.dragged_card_index < len(self.current_player.hand):
            card = self.current_player.hand[self.dragged_card_index]
            #отрисовка карты на месте мышки
            draw_x = self.drag_current_pos[0] - self.drag_offset[0]
            draw_y = self.drag_current_pos[1] - self.drag_offset[1]
            
            card_surface = pygame.Surface((120, 160), pygame.SRCALPHA)
            card.draw(card_surface, 0, 0, True)
            card_surface.set_alpha(200)
            
            glow_rect = pygame.Rect(draw_x - 2, draw_y - 2, 124, 164)
            pygame.draw.rect(self.screen, (255, 255, 0), glow_rect, 3)
            
            self.screen.blit(card_surface, (draw_x, draw_y))
    
    def draw_table_flip(self):
        """отрисовка тейбл флипа"""
        angle = self.flip_progress * math.pi
        
        flip_surface = pygame.Surface((self.screen_width, self.screen_height))
        if self.background_image:
            flip_surface.blit(self.background_image, (0, 0))
        else:
            flip_surface.fill((0, 0, 0))
        

        if self.flip_progress < 0.5:
            #отрисовка состояния игры
            self.other_player.draw_board(flip_surface, 50)
            self.other_player.draw_info(flip_surface, 10, 10)
            self.current_player.draw_board(flip_surface, self.screen_height - 350)
            self.current_player.draw_hand(flip_surface, self.screen_height - 180)
            self.current_player.draw_info(flip_surface, 10, self.screen_height - 120)
        else:
            self.current_player.draw_board(flip_surface, 50)
            self.current_player.draw_info(flip_surface, 10, 10)
            self.other_player.draw_board(flip_surface, self.screen_height - 350)
            self.other_player.draw_hand(flip_surface, self.screen_height - 180)
            self.other_player.draw_info(flip_surface, 10, self.screen_height - 120)
        
        #применение флипа
        scale_y = abs(math.cos(angle))
        if scale_y < 0.1:
            scale_y = 0.1
        
        #скейл сёрфейса
        scaled_height = int(self.screen_height * scale_y)
        scaled_surface = pygame.transform.scale(flip_surface, (self.screen_width, scaled_height))
        
        #чёрный бэкграунд
        self.screen.fill((0, 0, 0))
        
        #центрирование
        y_offset = (self.screen_height - scaled_height) // 2
        self.screen.blit(scaled_surface, (0, y_offset))
    
    def draw_game_over(self):
        """геймовер скрин"""
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        #геймовер текст
        game_over_font = pygame.font.Font(None, 72)
        game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        winner_text = self.font.render(f"{self.winner.name} Победил!", True, (255, 255, 0))
        
        #центрирование
        game_over_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 100))
        winner_rect = winner_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(winner_text, winner_rect)
        
        #отрисовка кнопок
        button_width = 200
        button_height = 50
        button_x = (self.screen_width - button_width) // 2
        start_y = self.screen_height // 2 + 50
        
        for i, option in enumerate(self.game_over_options):
            button_y = start_y + i * 70
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            #отсвечивание выбранной кнопки
            if i == self.game_over_selected_option:
                color = (255, 255, 0) 
                pygame.draw.rect(self.screen, (80, 80, 80), button_rect)
            else:
                color = (255, 255, 255)
                pygame.draw.rect(self.screen, (40, 40, 40), button_rect)
        
            pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 2)
            

            button_text = self.font.render(option, True, color)
            text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, text_rect)
    
    def draw_photo_overlay(self):
        """отрисовка картинки переворота"""
        try:
            photo_files = "Heartstone/assets/switch.jpg"
            photo_loaded = False
            for photo_file in photo_files:
                if os.path.exists("Heartstone/assets/switch.jpg"):
                    try:
                        photo = pygame.image.load("Heartstone/assets/switch.jpg")
                    
                        photo_width, photo_height = photo.get_size()
                        
                        scale_x = self.screen_width / photo_width
                        scale_y = self.screen_height / photo_height
                        scale = max(scale_x, scale_y) * 0.56
                        
                        new_width = int(photo_width * scale)
                        new_height = int(photo_height * scale)
                        
                        photo = pygame.transform.scale(photo, (new_width, new_height))
                        
                        #ротейт на 90*
                        photo = pygame.transform.rotate(photo, 90)
                        
                        rotated_width, rotated_height = photo.get_size()
                        
                        #заполнение бэкграунда чёрным
                        self.screen.fill((0, 0, 0))
                        
                        #центрирование
                        photo_x = (self.screen_width - rotated_width) // 2
                        photo_y = (self.screen_height - rotated_height) // 2
                        
                        self.screen.blit(photo, (photo_x, photo_y))
                        photo_loaded = True
                        break
                    except pygame.error:
                        continue

        except Exception:
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
        
        #инструкции
        instruction_font = pygame.font.Font(None, 36)
        instruction_text = instruction_font.render("Нажмите SPACE для продолжения", True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        self.screen.blit(instruction_text, instruction_rect)
    
    def draw_player_board_with_selection(self, player, y_position):
        """хайлайт выбранного существа"""
        board_width = len(player.board) * 130
        start_x = (self.screen_width - board_width) // 2
        
        for i, card in enumerate(player.board):
            x = start_x + i * 130
            selected = (self.attack_mode and i == self.selected_minion_index)
            card.draw(self.screen, x, y_position, selected)
    
    def draw_player_info_with_highlight(self, player, x, y, is_current_player):
        """инфо о таргете"""
        player.draw_info(self.screen, x, y)