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
        self.board = []  # Cards played on the board
        self.selected_card = None
        
        # Draw initial hand
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
            # Cast spell
            if target:
                if card.spell_damage > 0:
                    target.take_damage(card.spell_damage)
                elif card.name == "Heal" or card.name == "Mass Heal":
                    if hasattr(target, 'heal'):
                        target.heal(5 if card.name == "Heal" else 3)
                elif card.name == "Shield" and hasattr(target, 'health'):
                    target.health += 5
                    target.max_health += 5
                elif card.name == "Power Up" and hasattr(target, 'attack'):
                    target.attack += 3
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
    
    def draw_info(self, surface, x, y):
        """Draw player info (health, mana)"""
        font = pygame.font.Font(None, 24)
        
        # Draw name
        name_text = font.render(self.name, True, (0, 0, 0))
        surface.blit(name_text, (x, y))
        
        # Draw health
        health_text = font.render(f"Health: {self.health}/{self.max_health}", True, (255, 0, 0))
        surface.blit(health_text, (x, y + 25))
        
        # Draw mana
        mana_text = font.render(f"Mana: {self.mana}/{self.max_mana}", True, (0, 0, 255))
        surface.blit(mana_text, (x, y + 50))
        
        # Draw deck size
        deck_text = font.render(f"Deck: {len(self.deck)}", True, (0, 0, 0))
        surface.blit(deck_text, (x, y + 75))