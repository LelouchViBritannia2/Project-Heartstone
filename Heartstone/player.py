import pygame
from card import create_random_deck, CardType

class Player:
    def __init__(self, name, is_human=True):
        self.name = name
        self.is_human = is_human
        self.health = 30
        self.max_health = 30
        self.mana = 1
        self.max_mana = 1
        self.deck = create_random_deck()
        self.hand = []
        self.board = []
        self.selected_card = None
        
        #Начальная Рука
        for _ in range(3):
            self.draw_card()
    
    def draw_card(self):
        """Draw a card from deck to hand"""
        if self.deck and len(self.hand) < 10:
            card = self.deck.pop(0)
            self.hand.append(card)
            return card
        return None
    
    def play_card(self, card_index, target=None):
        """Play a card from hand"""
        if card_index >= len(self.hand):
            return False
            
        card = self.hand[card_index]
        
        # Check if player has enough mana
        if card.cost > self.mana:
            return False
        
        # Check board space for minions
        if card.card_type == CardType.MINION and len(self.board) >= 7:
            return False  # Board is full
        
        # Spend mana
        self.mana -= card.cost
        
        # Remove card from hand
        self.hand.pop(card_index)
        
        # Handle different card types
        if card.card_type == CardType.MINION:
            # Place minion on board
            card.summoning_sickness = True  # Can't attack this turn
            self.board.append(card)
            return True
        elif card.card_type == CardType.SPELL:
            # Cast spell using unified spell system
            if target:
                self.cast_spell(card, target)
            return True
        
        return False
    
    def start_turn(self):
        """Start a new turn"""
        # Increase max mana (up to 10)
        if self.max_mana < 10:
            self.max_mana += 1
        
        # Restore mana
        self.mana = self.max_mana
        
        # Draw a card
        self.draw_card()
        
        # Reset minions and remove dead ones
        self.board = [minion for minion in self.board if minion.health > 0]
        for minion in self.board:
            minion.reset_turn()
    
    def end_turn(self):
        """End the current turn"""
        pass
    
    def take_damage(self, damage):
        """Take damage to health"""
        self.health -= damage
        return self.health <= 0
    
    def heal(self, amount):
        """Heal health"""
        self.health = min(self.max_health, self.health + amount)
    
    def cast_spell(self, spell_card, target):
        """Cast a spell based on its spell_damage value and name"""
        spell_damage = spell_card.spell_damage
        spell_name = spell_card.name
        
        # Positive spell_damage = damage spells
        if spell_damage > 0:
            if hasattr(target, 'take_damage'):
                target.take_damage(spell_damage)
        
        # Negative spell_damage = healing spells
        elif spell_damage < 0:
            heal_amount = abs(spell_damage)
            if hasattr(target, 'heal'):
                target.heal(heal_amount)
        
        # Zero spell_damage = buff/utility spells (check by name)
        elif spell_damage == 0:
            # Attack buff spells
            if "Арата" in spell_name and hasattr(target, 'attack'):
                target.attack += 3
                target.health +=2
    
    def draw_hand(self, surface, y_position, selected_index=-1):
        """Draw the player's hand"""
        hand_width = len(self.hand) * 130
        start_x = (surface.get_width() - hand_width) // 2
        
        for i, card in enumerate(self.hand):
            x = start_x + i * 130
            selected = (i == selected_index)
            card.draw(surface, x, y_position, selected)
    
    def draw_board(self, surface, y_position):
        """Draw the player's board"""
        board_width = len(self.board) * 130
        start_x = (surface.get_width() - board_width) // 2
        
        for i, card in enumerate(self.board):
            x = start_x + i * 130
            card.draw(surface, x, y_position)
    
    def attack_with_minion(self, minion_index, target):
        """Attack with a minion"""
        if minion_index >= len(self.board):
            return False
        
        minion = self.board[minion_index]
        if minion.attack_target(target):
            # Remove dead minions after combat
            self.board = [m for m in self.board if m.health > 0]
            return True
        return False
    
    def remove_dead_minions(self):
        """Remove minions with 0 or less health"""
        self.board = [minion for minion in self.board if minion.health > 0]
    
    def draw_health_bar(self, surface, x, y, width=150, height=20):
        """Draw a health bar for the player"""
        # Calculate health percentage
        health_percentage = self.health / self.max_health if self.max_health > 0 else 0
        
        # Draw background (empty health bar)
        background_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (100, 100, 100), background_rect)
        
        # Draw health fill
        if health_percentage > 0:
            fill_width = int(width * health_percentage)
            fill_rect = pygame.Rect(x, y, fill_width, height)
            
            # Color based on health percentage
            if health_percentage > 0.6:
                color = (0, 255, 0)  # Green
            elif health_percentage > 0.3:
                color = (255, 255, 0)  # Yellow
            else:
                color = (255, 0, 0)  # Red
            
            pygame.draw.rect(surface, color, fill_rect)
        
        # Draw health text on top of bar
        font = pygame.font.Font(None, 18)
        health_text = font.render(f"{self.health}/{self.max_health}", True, (255, 255, 255))
        text_rect = health_text.get_rect(center=(x + width // 2, y + height // 2))
        surface.blit(health_text, text_rect)
        
        # Draw black border on top
        pygame.draw.rect(surface, (0, 0, 0), background_rect, 2)

    def draw_mana_bar(self, surface, x, y, width=150, height=20):
        """Draw a mana bar for the player"""
        # Calculate mana percentage
        mana_percentage = self.mana / self.max_mana if self.max_mana > 0 else 0
        
        # Draw background (empty mana bar)
        background_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (100, 100, 100), background_rect)
        
        # Draw mana fill
        if mana_percentage > 0:
            fill_width = int(width * mana_percentage)
            fill_rect = pygame.Rect(x, y, fill_width, height)
            
            # Blue color for mana
            color = (0, 100, 255)  # Blue
            pygame.draw.rect(surface, color, fill_rect)
        
        # Draw mana text on top of bar
        font = pygame.font.Font(None, 18)
        mana_text = font.render(f"{self.mana}/{self.max_mana}", True, (255, 255, 255))
        text_rect = mana_text.get_rect(center=(x + width // 2, y + height // 2))
        surface.blit(mana_text, text_rect)
        
        # Draw black border on top
        pygame.draw.rect(surface, (0, 0, 0), background_rect, 2)

    def draw_info(self, surface, x, y):
        """Draw player info (health, mana)"""
        font = pygame.font.Font(None, 24)
        
        # Draw name
        name_text = font.render(self.name, True, (0, 0, 0))
        surface.blit(name_text, (x, y))
        
        # Draw health bar
        self.draw_health_bar(surface, x, y + 25, 150, 20)
        
        # Draw mana bar
        self.draw_mana_bar(surface, x, y + 50, 150, 20)
        
        # Draw deck size
        deck_text = font.render(f"Колода: {len(self.deck)}", True, (0, 0, 0))
        surface.blit(deck_text, (x, y + 80))