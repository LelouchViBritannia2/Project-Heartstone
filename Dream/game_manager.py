import pygame
import math
from player import Player
from card import CardType

class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Initialize players
        self.player1 = Player("Player 1", True)
        self.player2 = Player("Player 2", True)
        self.current_player = self.player1
        self.other_player = self.player2
        
         # Game state
        self.game_over = False
        self.winner = None
        self.selected_card_index = -1
        self.selected_minion_index = -1
        self.attack_mode = False
        self.turn_number = 1
        
        # Table flip animation
        self.table_flip_active = False
        self.flip_progress = 0.0
        self.flip_speed = 3.0
        
        # Colors
        self.bg_color = (50, 150, 50)  # Green table
        self.text_color = (255, 255, 255)
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def handle_event(self, event):
        if self.game_over or self.table_flip_active:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.end_turn()
            elif event.key == pygame.K_ESCAPE:
                self.cancel_selection()
            elif event.key == pygame.K_a:
                self.toggle_attack_mode()
            elif not self.attack_mode:
                if event.key == pygame.K_LEFT and self.selected_card_index > 0:
                    self.selected_card_index -= 1
                elif event.key == pygame.K_RIGHT and self.selected_card_index < len(self.current_player.hand) - 1:
                    self.selected_card_index += 1
                elif event.key == pygame.K_RETURN and self.selected_card_index >= 0:
                    self.play_selected_card()
            else:
                if event.key == pygame.K_LEFT and self.selected_minion_index > 0:
                    self.selected_minion_index -= 1
                elif event.key == pygame.K_RIGHT and self.selected_minion_index < len(self.current_player.board) - 1:
                    self.selected_minion_index += 1
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.handle_mouse_click(event.pos)
    
    def handle_mouse_click(self, pos):
        """Handle mouse clicks on cards"""
        # Check if clicking on current player's hand
        hand_y = self.screen_height - 180
        hand_width = len(self.current_player.hand) * 130
        start_x = (self.screen_width - hand_width) // 2
        
        for i, card in enumerate(self.current_player.hand):
            card_x = start_x + i * 130
            card_rect = pygame.Rect(card_x, hand_y, 120, 160)
            if card_rect.collidepoint(pos):
                if self.selected_card_index == i:
                    # Deselect if clicking same card
                    self.selected_card_index = -1
                else:
                    self.selected_card_index = i
                    self.selected_minion_index = -1
                    self.attack_mode = False
                return
        
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
        self.screen.fill(self.bg_color)
        
         # Draw opponent (top)
        self.other_player.draw_board(self.screen, 50)
        self.draw_player_info_with_highlight(self.other_player, 10, 10, False)
        
        # Draw current player (bottom)
        self.draw_player_board_with_selection(self.current_player, self.screen_height - 350)
        self.current_player.draw_hand(self.screen, self.screen_height - 180, self.selected_card_index)
        self.draw_player_info_with_highlight(self.current_player, 10, self.screen_height - 120, True)
        # Draw turn info
        turn_text = self.font.render(f"Turn {self.turn_number} - {self.current_player.name}'s Turn", True, self.text_color)
        text_rect = turn_text.get_rect(center=(self.screen_width // 2, 30))
        self.screen.blit(turn_text, text_rect)
        
       # Draw instructions
        if self.attack_mode and self.selected_minion_index >= 0:
            instructions = [
                "Attack Mode Active",
                f"Selected: {self.current_player.board[self.selected_minion_index].name}",
                "Click target to attack",
                "Click minion again to deselect",
                "Esc: Cancel attack"
            ]
        elif self.selected_card_index >= 0:
            card = self.current_player.hand[self.selected_card_index]
            instructions = [
                f"Selected: {card.name}",
                "Click target to cast/play",
                "Click card again to deselect",
                "Enter: Play without target",
                "Space: End turn"
            ]
        else:
            instructions = [
                "Click: Select card/minion",
                "Enter: Play selected card",
                "A: Attack mode",
                "Space: End turn",
                "Esc: Cancel selection"
            ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, self.text_color)
            self.screen.blit(text, (self.screen_width - 250, 10 + i * 25))
        
        # Draw board status
        board_status = f"Board: {len(self.current_player.board)}/7"
        status_text = self.small_font.render(board_status, True, self.text_color)
        self.screen.blit(status_text, (self.screen_width - 250, 150))
        
        # Draw game over screen
        if self.game_over:
            self.draw_game_over()
    
    def draw_table_flip(self):
        """Draw the table flip animation"""
        # Calculate flip angle (0 to π)
        angle = self.flip_progress * math.pi
        
        # Create a surface for the flipped content
        flip_surface = pygame.Surface((self.screen_width, self.screen_height))
        flip_surface.fill(self.bg_color)
        
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
        
        # Draw "Switching turns..." text
        switch_text = self.font.render("Switching turns...", True, (255, 255, 255))
        text_rect = switch_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(switch_text, text_rect)
    
    def draw_game_over(self):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
        winner_text = self.font.render(f"{self.winner.name} Wins!", True, (255, 255, 0))
        
        # Center the text
        game_over_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        winner_rect = winner_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(winner_text, winner_rect)
    
    def draw_player_board_with_selection(self, player, y_position):
        """Draw player's board with attack selection highlighting"""
        board_width = len(player.board) * 110
        start_x = (self.screen_width - board_width) // 2
        
        for i, card in enumerate(player.board):
            x = start_x + i * 110
            selected = (self.attack_mode and i == self.selected_minion_index)
            card.draw(self.screen, x, y_position, selected)
    
    def draw_player_info_with_highlight(self, player, x, y, is_current_player):
        """Draw player info with targeting highlight"""
        # Check if this player can be targeted
        can_target = (self.selected_card_index >= 0 and 
                     len(self.current_player.hand) > self.selected_card_index and
                     self.current_player.hand[self.selected_card_index].card_type == CardType.SPELL)
        
        # Draw highlight box if targetable
        if can_target:
            highlight_rect = pygame.Rect(x - 5, y - 5, 210, 110)
            pygame.draw.rect(self.screen, (255, 255, 0), highlight_rect, 3)
        
        player.draw_info(self.screen, x, y)