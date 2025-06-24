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
        
        # Initialize audio
        pygame.mixer.init()
        self.init_background_music()
        
        # Initialize players
        self.player1 = Player("Игрок 1", True)
        self.player2 = Player("Игрок 2", True)
        self.current_player = self.player1
        self.other_player = self.player2
        
        # Game state
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
        self.volume = 0.3  # Current volume (0.0 to 1.0)
        self.volume_dragging = False
        
        # Game over state
        self.game_over_selected_option = 0
        self.game_over_options = ["Играть ещё раз", "Выйти"]
        
        # Drag and drop state
        self.dragging = False
        self.dragged_card_index = -1
        self.drag_start_pos = (0, 0)
        self.drag_current_pos = (0, 0)
        self.drag_offset = (0, 0)
        
        # Table flip animation
        self.table_flip_active = False
        self.flip_progress = 0.0
        self.flip_speed = 3.0
        
        # Photo overlay state
        self.show_photo = False
        self.space_pressed_once = False
        
        # Background image
        self.background_image = None
        self.background_loaded = False
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def init_background_music(self):
        """Initialize and start background music"""
        try:
            # Try to load background music from assets folder
            music_files = "OPD/Heartstone/assets/background_music.mp3"
            
            music_loaded = False
            for music_file in music_files:
                if os.path.exists(music_file):
                    try:
                        pygame.mixer.music.load("OPD/Heartstone/assets/background_music.mp3")
                        pygame.mixer.music.set_volume(0.3)  # Set volume to 30%
                        pygame.mixer.music.play(-1)  # Loop indefinitely
                        print(f"Background music loaded: {"OPD/Heartstone/assets/background_music.mp3"}")
                        music_loaded = True
                        break
                    
                    except pygame.error as e:
                        print(f"Could not load {"OPD/Heartstone/assets/background_music.mp3"}: {e}")
                        continue
            
            if not music_loaded:
                print("No background music file found. Place a music file in assets/ folder.")
                print("Supported formats: .mp3, .ogg")
                print("Suggested filename: assets/background_music.mp3")
                
        except pygame.error as e:
            print(f"Could not initialize background music: {e}")

    def load_background_image(self):
        """Load the background image if not already loaded"""
        if self.background_loaded:
            return
        
        try:
            # Try to load background image from assets folder
            background_files = "OPD/Heartstone/поле/бэкграунд_поле.jpg"
            
            for bg_file in background_files:
                if os.path.exists("OPD/Heartstone/поле/бэкграунд_поле.jpg"):
                    try:
                        self.background_image = pygame.image.load("OPD/Heartstone/поле/бэкграунд_поле.jpg")
                        # Scale background to fill entire screen using smoothscale for better quality
                        self.background_image = pygame.transform.smoothscale(
                            self.background_image, 
                            (self.screen_width, self.screen_height)
                        )
                        print(f"Background image loaded: {"OPD/Heartstone/поле/бэкграунд_поле.jpg"}")
                        break
                    
                    except pygame.error as e:
                        print(f"Could not load {"OPD/Heartstone/поле/бэкграунд_поле.jpg"}: {e}")
                        continue

        except Exception as e:
            print(f"Could not initialize background image: {e}")
        
        self.background_loaded = True
    
    def toggle_music(self):
        """Toggle background music on/off"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
    
    def toggle_help(self):
        """Toggle help window on/off"""
        self.show_help = not self.show_help
    
    def handle_menu_selection(self):
        """Handle menu option selection"""
        selected = self.menu_options[self.menu_selected_option]
        
        if selected == "Продолжить":
            self.show_menu = False
        elif selected == "Настройки":
            self.show_settings = True
        elif selected == "Выйти":
            pygame.quit()
            exit()
    
    def handle_menu_mouse_click(self, pos):
        """Handle mouse clicks in the menu"""
        if self.show_settings:
            self.handle_settings_mouse_click(pos)
            return
            
        # Menu window dimensions
        window_width = 400
        window_height = 300
        window_x = (self.screen_width - window_width) // 2
        window_y = (self.screen_height - window_height) // 2
        start_y = window_y + 120
        
        # Check if click is within menu bounds
        menu_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        if not menu_rect.collidepoint(pos):
            # Click outside menu - close it
            self.show_menu = False
            return
        
        # Check which menu option was clicked
        for i, option in enumerate(self.menu_options):
            option_rect = pygame.Rect(window_x + 50, start_y + i * 60 - 15, window_width - 100, 50)
            if option_rect.collidepoint(pos):
                self.menu_selected_option = i
                self.handle_menu_selection()
                break
    
    def handle_menu_mouse_hover(self, pos):
        """Handle mouse hover in the menu"""
        if self.show_settings:
            return
            
        # Menu window dimensions
        window_width = 400
        window_height = 300
        window_x = (self.screen_width - window_width) // 2
        window_y = (self.screen_height - window_height) // 2
        start_y = window_y + 120
        
        # Check which menu option is being hovered
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
            # Handle ESC key first (always available to close overlays)
            if event.key == pygame.K_ESCAPE:
                if self.show_settings:
                    self.show_settings = False
                elif self.show_menu:
                    self.show_menu = False
                elif self.show_help:
                    self.show_help = False
                elif self.show_photo:
                    self.show_photo = False
                    self.space_pressed_once = False
                elif self.attack_mode:
                    self.cancel_selection()
                else:
                    self.show_menu = True
                    self.menu_selected_option = 0
            # Handle TAB key (always available to toggle help)
            elif event.key == pygame.K_TAB:
                if not self.show_menu and not self.show_settings and not self.show_photo:
                    self.toggle_help()
            # Handle menu navigation when menu is open
            elif self.show_menu and not self.show_settings:
                if event.key == pygame.K_UP and self.menu_selected_option > 0:
                    self.menu_selected_option -= 1
                elif event.key == pygame.K_DOWN and self.menu_selected_option < len(self.menu_options) - 1:
                    self.menu_selected_option += 1
                elif event.key == pygame.K_RETURN:
                    self.handle_menu_selection()
            # Block all other inputs when any overlay is open (except photo overlay for SPACE)
            elif self.show_help or self.show_menu or self.show_settings:
                return  # Block all other inputs
            # Handle SPACE key (special case - works when photo overlay is open, blocked by other overlays)
            elif event.key == pygame.K_SPACE:
                if not self.space_pressed_once:
                    # First press - show photo
                    self.show_photo = True
                    self.space_pressed_once = True
                else:
                    # Second press - hide photo and start table flip
                    self.show_photo = False
                    self.space_pressed_once = False
                    self.end_turn()
            # Block remaining inputs when photo overlay is open
            elif self.show_photo:
                return  # Block all other inputs when photo is showing
            # Normal game inputs (only when no overlays are open)
            elif event.key == pygame.K_a:
                self.toggle_attack_mode()
            elif event.key == pygame.K_m:
                self.toggle_music()
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
            if event.button == 1:  # Left click
                if self.show_menu:
                    self.handle_menu_mouse_click(event.pos)
                elif not (self.show_help or self.show_photo):
                    # Only handle mouse down if no overlays are blocking
                    self.handle_mouse_down(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                if self.show_settings and self.volume_dragging:
                    self.volume_dragging = False
                elif not (self.show_menu or self.show_help or self.show_photo):
                    # Only handle mouse up if no overlays are blocking
                    self.handle_mouse_up(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            if self.show_menu:
                if self.show_settings and self.volume_dragging:
                    self.handle_volume_drag(event.pos)
                else:
                    self.handle_menu_mouse_hover(event.pos)
            elif not (self.show_help or self.show_photo):
                # Only handle mouse motion if no overlays are blocking
                self.handle_mouse_motion(event.pos)
    
    def handle_mouse_down(self, pos):
        """Handle mouse button down events"""
        # Check if clicking on current player's hand to start dragging
        hand_y = self.screen_height - 180
        hand_width = len(self.current_player.hand) * 130
        start_x = (self.screen_width - hand_width) // 2
        
        for i, card in enumerate(self.current_player.hand):
            card_x = start_x + i * 130
            card_rect = pygame.Rect(card_x, hand_y, 120, 160)
            if card_rect.collidepoint(pos):
                # Start dragging this card
                self.dragging = True
                self.dragged_card_index = i
                self.drag_start_pos = pos
                self.drag_current_pos = pos
                self.drag_offset = (pos[0] - card_x, pos[1] - hand_y)
                self.selected_card_index = i
                self.selected_minion_index = -1
                self.attack_mode = False
                return
        
        # If not dragging, handle regular clicks
        self.handle_mouse_click(pos)
    
    def handle_mouse_up(self, pos):
        """Handle mouse button up events"""
        if self.dragging:
            self.handle_card_drop(pos)
            self.dragging = False
            self.dragged_card_index = -1
        else:
            # Handle regular click if not dragging
            pass
    
    def handle_mouse_motion(self, pos):
        """Handle mouse motion events"""
        if self.dragging:
            self.drag_current_pos = pos
    
    def handle_card_drop(self, pos):
        """Handle dropping a dragged card"""
        if self.dragged_card_index < 0 or self.dragged_card_index >= len(self.current_player.hand):
            return
        
        card = self.current_player.hand[self.dragged_card_index]
        
        # Check if dropped on current player (for self-targeting spells) - PRIORITY ZONE
        current_face_rect = pygame.Rect(10, self.screen_height - 120, 200, 100)
        if current_face_rect.collidepoint(pos):
            if card.card_type == CardType.SPELL:
                if self.current_player.play_card(self.dragged_card_index, self.current_player):
                    self.selected_card_index = -1
                    self.cleanup_dead_minions()
                    self.check_game_over()
            return
        
        # Check if dropped back in hand area (cancel action)
        hand_y = self.screen_height - 180
        hand_zone = pygame.Rect(0, hand_y - 20, self.screen_width, 200)
        if hand_zone.collidepoint(pos):
            # Cancel - card stays in hand, just reset selection
            self.selected_card_index = -1
            return
        
        # Check if dropped on board area (play zone for minions)
        board_drop_zone = pygame.Rect(0, self.screen_height - 400, self.screen_width, 200)
        if board_drop_zone.collidepoint(pos) and card.card_type == CardType.MINION:
            # Play the minion card
            if self.current_player.play_card(self.dragged_card_index):
                self.selected_card_index = -1
                self.cleanup_dead_minions()
                self.check_game_over()
            return
        
        # Check if dropped on opponent (for spells and minion attacks)
        opponent_face_rect = pygame.Rect(10, 10, 200, 100)
        if opponent_face_rect.collidepoint(pos):
            if card.card_type == CardType.SPELL:
                if self.current_player.play_card(self.dragged_card_index, self.other_player):
                    self.selected_card_index = -1
                    self.cleanup_dead_minions()
                    self.check_game_over()
            elif card.card_type == CardType.MINION:
                # Direct attack on opponent - play minion first if not on board
                if self.current_player.play_card(self.dragged_card_index):
                    self.selected_card_index = -1
                    self.cleanup_dead_minions()
                    self.check_game_over()
            return
        
        # Check if dropped on opponent's minions
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
                    # Play minion to board first
                    if self.current_player.play_card(self.dragged_card_index):
                        self.selected_card_index = -1
                        self.cleanup_dead_minions()
                        self.check_game_over()
                return
        
        # Check if dropped on own minions (for beneficial spells)
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
        
        # If dropped nowhere valid, cancel the action (card returns to hand)
        self.selected_card_index = -1
    
    def handle_mouse_click(self, pos):
        """Handle mouse clicks on cards (fallback for non-drag interactions)"""
        
        # Check if clicking on current player's board
        current_board_y = self.screen_height - 350
        board_width = len(self.current_player.board) * 130
        start_x = (self.screen_width - board_width) // 2
        
        for i, card in enumerate(self.current_player.board):
            card_x = start_x + i * 130
            card_rect = pygame.Rect(card_x, current_board_y, 120, 160)
            if card_rect.collidepoint(pos):
                if self.selected_card_index >= 0:
                    # Spell targeting friendly minion
                    self.play_selected_card(target=card)
                    return
                elif card.can_attack_target():
                    # Select minion for attack
                    if self.selected_minion_index == i and self.attack_mode:
                        # Deselect if clicking same minion
                        self.selected_minion_index = -1
                        self.attack_mode = False
                    else:
                        self.selected_minion_index = i
                        self.attack_mode = True
                        self.selected_card_index = -1
                return
        
        # Check if clicking on opponent's board
        opponent_board_y = 50
        board_width = len(self.other_player.board) * 130
        start_x = (self.screen_width - board_width) // 2
        
        for i, card in enumerate(self.other_player.board):
            card_x = start_x + i * 130
            card_rect = pygame.Rect(card_x, opponent_board_y, 120, 160)
            if card_rect.collidepoint(pos):
                if self.selected_card_index >= 0:
                    # Spell targeting enemy minion
                    self.play_selected_card(target=card)
                elif self.attack_mode and self.selected_minion_index >= 0:
                    # Attack enemy minion
                    self.attack_target(card)
                return
        
        # Check if clicking on opponent's face (player info area)
        opponent_face_rect = pygame.Rect(10, 10, 200, 100)
        if opponent_face_rect.collidepoint(pos):
            if self.selected_card_index >= 0:
                # Spell targeting enemy player
                self.play_selected_card(target=self.other_player)
            elif self.attack_mode and self.selected_minion_index >= 0:
                # Attack enemy player
                self.attack_target(self.other_player)
            return
        
        # Check if clicking on current player's face (self-targeting)
        current_face_rect = pygame.Rect(10, self.screen_height - 120, 200, 100)
        if current_face_rect.collidepoint(pos):
            if self.selected_card_index >= 0:
                # Spell targeting self
                self.play_selected_card(target=self.current_player)
            return
        
        # Click on empty space - deselect everything
        self.cancel_selection()
    
    def play_selected_card(self, target=None):
        """Play the currently selected card"""
        if self.selected_card_index < 0 or self.selected_card_index >= len(self.current_player.hand):
            return
        
        card = self.current_player.hand[self.selected_card_index]
        
        # For spells targeting opponent directly
        if card.card_type == CardType.SPELL and not target and card.spell_damage > 0:
            target = self.other_player
        
        if self.current_player.play_card(self.selected_card_index, target):
            self.selected_card_index = -1
            self.cleanup_dead_minions()
            self.check_game_over()
    
    def attack_target(self, target):
        """Attack with selected minion"""
        if self.selected_minion_index < 0 or self.selected_minion_index >= len(self.current_player.board):
            return
        
        if self.current_player.attack_with_minion(self.selected_minion_index, target):
            self.cleanup_dead_minions()
            self.cancel_selection()
            self.check_game_over()
    
    def toggle_attack_mode(self):
        """Toggle attack mode"""
        if len(self.current_player.board) > 0:
            self.attack_mode = not self.attack_mode
            if self.attack_mode:
                self.selected_card_index = -1
                self.selected_minion_index = 0
            else:
                self.selected_minion_index = -1
    
    def cancel_selection(self):
        """Cancel current selection"""
        self.selected_card_index = -1
        self.selected_minion_index = -1
        self.attack_mode = False
    
    def cleanup_dead_minions(self):
        """Remove dead minions from both players"""
        self.current_player.remove_dead_minions()
        self.other_player.remove_dead_minions()
    
    def end_turn(self):
        """End current turn and switch players with table flip animation"""
        self.current_player.end_turn()
        self.table_flip_active = True
        self.flip_progress = 0.0
    
    def complete_turn_switch(self):
        """Complete the turn switch after animation"""
        # Switch players
        self.current_player, self.other_player = self.other_player, self.current_player
        self.current_player.start_turn()
        self.turn_number += 1
        self.selected_card_index = -1
        
        # Reset animation
        self.table_flip_active = False
        self.flip_progress = 0.0
    
    def update(self):
        """Update game state"""
        if self.table_flip_active:
            self.flip_progress += self.flip_speed * (1/60)  # Assuming 60 FPS
            if self.flip_progress >= 1.0:
                self.complete_turn_switch()
        
        self.check_game_over()
    
    def check_game_over(self):
        """Check if game is over"""
        if self.player1.health <= 0:
            self.game_over = True
            self.winner = self.player2
        elif self.player2.health <= 0:
            self.game_over = True
            self.winner = self.player1
    
    def draw(self):
        """Draw the entire game"""
        if self.table_flip_active:
            self.draw_table_flip()
        else:
            self.draw_normal_game()
    
    def draw_normal_game(self):
        """Draw the game in normal state"""
        # Load and draw background image if available
        if not self.background_loaded:
            self.load_background_image()
        
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
         # Draw opponent (top)
        self.other_player.draw_board(self.screen, 50)
        self.draw_player_info_with_highlight(self.other_player, 10, 10, False)
        
        # Draw current player (bottom)
        self.draw_player_board_with_selection(self.current_player, self.screen_height - 350)
        self.draw_hand_with_drag(self.current_player, self.screen_height - 180)
        self.draw_player_info_with_highlight(self.current_player, 10, self.screen_height - 120, True)
        # Draw dragged card on top
        if self.dragging and self.dragged_card_index >= 0:
            self.draw_dragged_card()
        # Draw turn info
        turn_text = self.font.render(f"Turn {self.turn_number} - {self.current_player.name}'s Turn", True, (255, 255, 255))
        text_rect = turn_text.get_rect(center=(self.screen_width // 2, 30))
        self.screen.blit(turn_text, text_rect)
        
        # Draw help hint in corner
        help_hint = self.small_font.render("Нажмите TAB для помощи", True, (255, 255, 255))
        self.screen.blit(help_hint, (self.screen_width - 150, 10))
        
        # Draw help window if active
        if self.show_help:
            self.draw_help_window()
        
        # Draw menu if active
        if self.show_menu:
            if self.show_settings:
                self.draw_settings()
            else:
                self.draw_menu()
        
        # Draw photo overlay if active
        if self.show_photo:
            self.draw_photo_overlay()
        
        # Draw game over screen
        if self.game_over:
            self.draw_game_over()
    
    def draw_help_window(self):
        """Draw the help window overlay"""
        # Create semi-transparent background
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Help window dimensions
        window_width = 800
        window_height = 500
        window_x = (self.screen_width - window_width) // 2
        window_y = (self.screen_height - window_height) // 2
        
        # Draw help window background
        help_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        pygame.draw.rect(self.screen, (40, 40, 40), help_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), help_rect, 3)
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Помощь", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, window_y + 40))
        self.screen.blit(title_text, title_rect)
        
        # Left side sections
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
        
        # Right side section
        right_section = ("Правила:", [
            "Вы начинаете игру с 30 здоровья и 1 мана",
            "+1 мана каждый ход(до 10)",
            "Каждый ход даётся карта",
            "Максимум 7 существ на столе",
            "Максимум 10 карт в руке",
            "Для победы убейте соперника"
        ])
        
        # Draw left side sections
        current_y = window_y + 80
        
        for section_title, section_items in left_sections:
            # Section title
            section_font = pygame.font.Font(None, 32)
            section_text = section_font.render(section_title, True, (255, 255, 0))
            self.screen.blit(section_text, (window_x + 20, current_y))
            current_y += 35
            
            # Section items
            for item in section_items:
                item_text = self.small_font.render(item, True, (255, 255, 255))
                self.screen.blit(item_text, (window_x + 40, current_y))
                current_y += 22
            
            current_y += 10  # Extra space between sections
        
        # Draw right side section
        right_x = window_x + window_width // 2 + 20
        right_y = window_y + 80
        
        # Section title
        section_font = pygame.font.Font(None, 32)
        section_text = section_font.render(right_section[0], True, (255, 255, 0))
        self.screen.blit(section_text, (right_x, right_y))
        right_y += 35
        
        # Section items
        for item in right_section[1]:
            item_text = self.small_font.render(item, True, (255, 255, 255))
            self.screen.blit(item_text, (right_x, right_y))
            right_y += 22
        
        # Close instruction
        close_text = self.small_font.render("Нажмите TAB чтобы закрыть", True, (200, 200, 200))
        close_rect = close_text.get_rect(center=(self.screen_width // 2, window_y + window_height + 30))
        self.screen.blit(close_text, close_rect)
    
    def draw_menu(self):
        """Draw the ESC menu overlay"""
        # Create semi-transparent background
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Menu window dimensions
        window_width = 400
        window_height = 300
        window_x = (self.screen_width - window_width) // 2
        window_y = (self.screen_height - window_height) // 2
        
        # Draw menu window background
        menu_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        pygame.draw.rect(self.screen, (40, 40, 40), menu_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), menu_rect, 3)
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Меню", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, window_y + 50))
        self.screen.blit(title_text, title_rect)
        
        # Menu options
        option_font = pygame.font.Font(None, 36)
        start_y = window_y + 120
        
        for i, option in enumerate(self.menu_options):
            # Highlight selected option
            if i == self.menu_selected_option:
                color = (255, 255, 0)  # Yellow for selected
                # Draw selection background
                option_bg = pygame.Rect(window_x + 50, start_y + i * 60 - 15, window_width - 100, 50)
                pygame.draw.rect(self.screen, (80, 80, 80), option_bg)
            else:
                color = (255, 255, 255)  # White for unselected
            
            option_text = option_font.render(option, True, color)
            option_rect = option_text.get_rect(center=(self.screen_width // 2, start_y + i * 60 + 10))
            self.screen.blit(option_text, option_rect)
    
    def handle_settings_mouse_click(self, pos):
        """Handle mouse clicks in the settings menu"""
        # Settings window dimensions
        window_width = 500
        window_height = 400
        window_x = (self.screen_width - window_width) // 2
        window_y = (self.screen_height - window_height) // 2
        
        # Check if click is within settings bounds
        settings_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        if not settings_rect.collidepoint(pos):
            # Click outside settings - close it
            self.show_settings = False
            return
        
        # Volume slider area
        slider_y = window_y + 150
        slider_x = window_x + 150
        slider_width = 200
        slider_rect = pygame.Rect(slider_x, slider_y - 10, slider_width, 20)
        
        if slider_rect.collidepoint(pos):
            # Start dragging volume slider
            self.volume_dragging = True
            # Calculate new volume based on click position
            relative_x = pos[0] - slider_x
            self.volume = max(0.0, min(1.0, relative_x / slider_width))
            pygame.mixer.music.set_volume(self.volume)
        
        # Back button
        back_button_rect = pygame.Rect(window_x + 50, window_y + window_height - 80, 100, 40)
        if back_button_rect.collidepoint(pos):
            self.show_settings = False
    
    def handle_volume_drag(self, pos):
        """Handle dragging the volume slider"""
        if not self.volume_dragging:
            return
            
        # Settings window dimensions
        window_width = 500
        window_x = (self.screen_width - window_width) // 2
        slider_x = window_x + 150
        slider_width = 200
        
        # Calculate new volume based on mouse position
        relative_x = pos[0] - slider_x
        self.volume = max(0.0, min(1.0, relative_x / slider_width))
        pygame.mixer.music.set_volume(self.volume)
    
    def handle_game_over_event(self, event):
        """Handle events during game over screen"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and self.game_over_selected_option > 0:
                self.game_over_selected_option -= 1
            elif event.key == pygame.K_DOWN and self.game_over_selected_option < len(self.game_over_options) - 1:
                self.game_over_selected_option += 1
            elif event.key == pygame.K_RETURN:
                self.handle_game_over_selection()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.handle_game_over_mouse_click(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_game_over_mouse_hover(event.pos)
    
    def handle_game_over_selection(self):
        """Handle game over option selection"""
        selected = self.game_over_options[self.game_over_selected_option]
        
        if selected == "Начать заного":
            self.restart_game()
        elif selected == "Выйти":
            pygame.quit()
            exit()
    
    def handle_game_over_mouse_click(self, pos):
        """Handle mouse clicks on game over screen"""
        # Button dimensions
        button_width = 200
        button_height = 50
        button_x = (self.screen_width - button_width) // 2
        start_y = self.screen_height // 2 + 50
        
        # Check which button was clicked
        for i, option in enumerate(self.game_over_options):
            button_y = start_y + i * 70
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            if button_rect.collidepoint(pos):
                self.game_over_selected_option = i
                self.handle_game_over_selection()
                break
    
    def handle_game_over_mouse_hover(self, pos):
        """Handle mouse hover on game over screen"""
        # Button dimensions
        button_width = 200
        button_height = 50
        button_x = (self.screen_width - button_width) // 2
        start_y = self.screen_height // 2 + 50
        
        # Check which button is being hovered
        for i, option in enumerate(self.game_over_options):
            button_y = start_y + i * 70
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            if button_rect.collidepoint(pos):
                self.game_over_selected_option = i
                break
    
    def restart_game(self):
        """Restart the game"""
        # Reset game state
        self.game_over = False
        self.winner = None
        self.selected_card_index = -1
        self.selected_minion_index = -1
        self.attack_mode = False
        self.turn_number = 1
        self.show_help = False
        self.show_menu = False
        self.show_settings = False
        self.show_photo = False
        self.space_pressed_once = False
        self.table_flip_active = False
        self.flip_progress = 0.0
        self.dragging = False
        self.dragged_card_index = -1
        self.game_over_selected_option = 0
        
        # Reset players
        self.player1 = Player("Player 1", True)
        self.player2 = Player("Player 2", True)
        self.current_player = self.player1
        self.other_player = self.player2
    
    def draw_settings(self):
        """Draw the settings menu overlay"""
        # Create semi-transparent background
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Settings window dimensions
        window_width = 500
        window_height = 400
        window_x = (self.screen_width - window_width) // 2
        window_y = (self.screen_height - window_height) // 2
        
        # Draw settings window background
        settings_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        pygame.draw.rect(self.screen, (40, 40, 40), settings_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), settings_rect, 3)
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Настройки", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, window_y + 50))
        self.screen.blit(title_text, title_rect)
        
        # Volume label
        volume_label = self.font.render("Звук:", True, (255, 255, 255))
        self.screen.blit(volume_label, (window_x + 50, window_y + 140))
        
        # Volume slider
        slider_y = window_y + 150
        slider_x = window_x + 150
        slider_width = 200
        slider_height = 10
        
        # Draw slider track
        track_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
        pygame.draw.rect(self.screen, (100, 100, 100), track_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), track_rect, 2)
        
        # Draw slider fill
        fill_width = int(slider_width * self.volume)
        if fill_width > 0:
            fill_rect = pygame.Rect(slider_x, slider_y, fill_width, slider_height)
            pygame.draw.rect(self.screen, (0, 255, 0), fill_rect)
        
        # Draw slider handle
        handle_x = slider_x + int(slider_width * self.volume) - 5
        handle_rect = pygame.Rect(handle_x, slider_y - 5, 10, 20)
        pygame.draw.rect(self.screen, (255, 255, 255), handle_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), handle_rect, 2)
        
        # Volume percentage text
        volume_text = self.small_font.render(f"{int(self.volume * 100)}%", True, (255, 255, 255))
        self.screen.blit(volume_text, (slider_x + slider_width + 20, window_y + 145))
        
        # Back button
        back_button_rect = pygame.Rect(window_x + 50, window_y + window_height - 80, 100, 40)
        pygame.draw.rect(self.screen, (80, 80, 80), back_button_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), back_button_rect, 2)
        
        back_text = self.font.render("Назад", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=back_button_rect.center)
        self.screen.blit(back_text, back_text_rect)
        
    
    def draw_hand_with_drag(self, player, y_position):
        """Draw player's hand, excluding dragged card"""
        hand_width = len(player.hand) * 130
        start_x = (self.screen_width - hand_width) // 2
        
        for i, card in enumerate(player.hand):
            # Skip drawing the card that's being dragged
            if self.dragging and i == self.dragged_card_index:
                continue
                
            x = start_x + i * 130
            selected = (i == self.selected_card_index and not self.dragging)
            card.draw(self.screen, x, y_position, selected)
    
    def draw_dragged_card(self):
        """Draw the card being dragged"""
        if self.dragged_card_index >= 0 and self.dragged_card_index < len(self.current_player.hand):
            card = self.current_player.hand[self.dragged_card_index]
            # Draw card at mouse position minus offset
            draw_x = self.drag_current_pos[0] - self.drag_offset[0]
            draw_y = self.drag_current_pos[1] - self.drag_offset[1]
            
            # Add slight transparency and glow effect
            card_surface = pygame.Surface((120, 160), pygame.SRCALPHA)
            card.draw(card_surface, 0, 0, True)  # Draw as selected
            card_surface.set_alpha(200)  # Make slightly transparent
            
            # Draw glow effect
            glow_rect = pygame.Rect(draw_x - 2, draw_y - 2, 124, 164)
            pygame.draw.rect(self.screen, (255, 255, 0), glow_rect, 3)
            
            self.screen.blit(card_surface, (draw_x, draw_y))
    
    def draw_table_flip(self):
        """Draw the table flip animation"""
        # Calculate flip angle (0 to π)
        angle = self.flip_progress * math.pi
        
        # Create a surface for the flipped content
        flip_surface = pygame.Surface((self.screen_width, self.screen_height))
        if self.background_image:
            flip_surface.blit(self.background_image, (0, 0))
        else:
            flip_surface.fill((0, 0, 0))
        
        # Draw the game state on the flip surface
        # During first half of flip, show current state
        # During second half, show switched state
        if self.flip_progress < 0.5:
            # Show current state
            self.other_player.draw_board(flip_surface, 50)
            self.other_player.draw_info(flip_surface, 10, 10)
            self.current_player.draw_board(flip_surface, self.screen_height - 350)
            self.current_player.draw_hand(flip_surface, self.screen_height - 180)
            self.current_player.draw_info(flip_surface, 10, self.screen_height - 120)
        else:
            # Show switched state (preview)
            self.current_player.draw_board(flip_surface, 50)
            self.current_player.draw_info(flip_surface, 10, 10)
            self.other_player.draw_board(flip_surface, self.screen_height - 350)
            self.other_player.draw_hand(flip_surface, self.screen_height - 180)
            self.other_player.draw_info(flip_surface, 10, self.screen_height - 120)
        
        # Apply flip transformation
        scale_y = abs(math.cos(angle))
        if scale_y < 0.1:
            scale_y = 0.1
        
        # Scale the surface
        scaled_height = int(self.screen_height * scale_y)
        scaled_surface = pygame.transform.scale(flip_surface, (self.screen_width, scaled_height))
        
        # Draw black background
        self.screen.fill((0, 0, 0))
        
        # Center the scaled surface
        y_offset = (self.screen_height - scaled_height) // 2
        self.screen.blit(scaled_surface, (0, y_offset))
    
    def draw_game_over(self):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_font = pygame.font.Font(None, 72)
        game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        winner_text = self.font.render(f"{self.winner.name} Победил!", True, (255, 255, 0))
        
        # Center the text
        game_over_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 100))
        winner_rect = winner_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(winner_text, winner_rect)
        
        # Draw buttons
        button_width = 200
        button_height = 50
        button_x = (self.screen_width - button_width) // 2
        start_y = self.screen_height // 2 + 50
        
        for i, option in enumerate(self.game_over_options):
            button_y = start_y + i * 70
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Highlight selected button
            if i == self.game_over_selected_option:
                color = (255, 255, 0)  # Yellow for selected
                # Draw selection background
                pygame.draw.rect(self.screen, (80, 80, 80), button_rect)
            else:
                color = (255, 255, 255)  # White for unselected
                # Draw button background
                pygame.draw.rect(self.screen, (40, 40, 40), button_rect)
            
            # Draw button border
            pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 2)
            
            # Draw button text
            button_text = self.font.render(option, True, color)
            text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, text_rect)
    
    def draw_photo_overlay(self):
        """Draw photo overlay that covers the entire screen"""
        # Try to load and display a photo
        try:
            # Try to load photo from assets folder
            photo_files = "OPD/Heartstone/assets/переворот_экрана.jpg"
            photo_loaded = False
            for photo_file in photo_files:
                if os.path.exists("OPD/Heartstone/assets/переворот_экрана.jpg"):
                    try:
                        photo = pygame.image.load("OPD/Heartstone/assets/переворот_экрана.jpg")
                        
                        # Get original photo dimensions
                        photo_width, photo_height = photo.get_size()
                        
                        # Calculate scaling to fit screen while maintaining aspect ratio
                        scale_x = self.screen_width / photo_width
                        scale_y = self.screen_height / photo_height
                        scale = max(scale_x, scale_y) * 0.56  # Use larger  scale to fit entirely
                        
                        # Calculate new dimensions
                        new_width = int(photo_width * scale)
                        new_height = int(photo_height * scale)
                        
                        # Scale photo maintaining aspect ratio
                        photo = pygame.transform.scale(photo, (new_width, new_height))
                        
                        # Rotate photo 90 degrees counterclockwise (left)
                        photo = pygame.transform.rotate(photo, 90)
                        
                        # Get new dimensions after rotation
                        rotated_width, rotated_height = photo.get_size()
                        
                        # Fill screen with black background first
                        self.screen.fill((0, 0, 0))
                        
                        # Center the rotated photo on screen
                        photo_x = (self.screen_width - rotated_width) // 2
                        photo_y = (self.screen_height - rotated_height) // 2
                        
                        self.screen.blit(photo, (photo_x, photo_y))
                        photo_loaded = True
                        break
                    except pygame.error:
                        continue

        except Exception:
            # Fallback to black screen
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
        
        # Show instruction text
        instruction_font = pygame.font.Font(None, 36)
        instruction_text = instruction_font.render("Нажмите SPACE для продолжения", True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        self.screen.blit(instruction_text, instruction_rect)
    
    def draw_player_board_with_selection(self, player, y_position):
        """Draw player's board with attack selection highlighting"""
        board_width = len(player.board) * 130
        start_x = (self.screen_width - board_width) // 2
        
        for i, card in enumerate(player.board):
            x = start_x + i * 130
            selected = (self.attack_mode and i == self.selected_minion_index)
            card.draw(self.screen, x, y_position, selected)
    
    def draw_player_info_with_highlight(self, player, x, y, is_current_player):
        """Draw player info with targeting highlight"""
        player.draw_info(self.screen, x, y)