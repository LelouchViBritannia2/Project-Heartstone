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
        """Получение карты из колоды в руку"""
        if self.deck and len(self.hand) < 7:
            card = self.deck.pop(0)
            self.hand.append(card)
            return card
        return None
    
    def play_card(self, card_index, target=None):
        """Сыграть карту из руки"""
        if card_index >= len(self.hand):
            return False
            
        card = self.hand[card_index]
        
        #Проверка на наличие достаточного кол-ва маны
        if card.cost > self.mana:
            return False
        
        #Проверка на свободное место
        if card.card_type == CardType.MINION and len(self.board) >= 7:
            return False  # Board is full
        
        #Трата маны
        self.mana -= card.cost
        
        #Убирание карты из руки
        self.hand.pop(card_index)
        
        #свойства разных тип карт
        if card.card_type == CardType.MINION:
            #Размещение существа
            card.summoning_sickness = True  #не может атаковать в этот ход
            self.board.append(card)
            return True
        elif card.card_type == CardType.SPELL:
            #Использование заклинаний
            if target:
                self.cast_spell(card, target)
            return True
        
        return False
    
    def start_turn(self):
        """начало хода"""
        if self.max_mana < 10:
            self.max_mana += 1
        
        self.mana = self.max_mana
        
        #взятие карты
        self.draw_card()
        
        #чистка мёртвых существа
        self.board = [minion for minion in self.board if minion.health > 0]
        for minion in self.board:
            minion.reset_turn()
    
    def end_turn(self):
        """конец хода"""
        pass
    
    def take_damage(self, damage):
        """получение урона"""
        self.health -= damage
        return self.health <= 0
    
    def heal(self, amount):
        """восстановление здоровья"""
        self.health = min(self.max_health, self.health + amount)
    
    def cast_spell(self, spell_card, target):
        """Свойства заклинаний"""
        spell_damage = spell_card.spell_damage
        spell_name = spell_card.name
        
        if spell_damage > 0:
            if hasattr(target, 'take_damage'):
                target.take_damage(spell_damage)
        
        elif spell_damage < 0:
            heal_amount = abs(spell_damage)
            if hasattr(target, 'heal'):
                target.heal(heal_amount)
        
        elif spell_damage == 0:
            if "Арата" in spell_name and hasattr(target, 'attack'):
                target.attack += 3
                target.health +=2
            if "Голод" in spell_name and hasattr(target, 'attack'):
                target.attack += 5
                target.health -=2
    
    def draw_hand(self, surface, y_position, selected_index=-1):
        """Отрисовка руки"""
        hand_width = len(self.hand) * 130
        start_x = (surface.get_width() - hand_width) // 2
        
        for i, card in enumerate(self.hand):
            x = start_x + i * 130
            selected = (i == selected_index)
            card.draw(surface, x, y_position, selected)
    
    def draw_board(self, surface, y_position):
        """отрисовка своего стола"""
        board_width = len(self.board) * 130
        start_x = (surface.get_width() - board_width) // 2
        
        for i, card in enumerate(self.board):
            x = start_x + i * 130
            card.draw(surface, x, y_position)
    
    def attack_with_minion(self, minion_index, target):
        """Атака существом"""
        if minion_index >= len(self.board):
            return False
        
        minion = self.board[minion_index]
        if minion.attack_target(target):
            #чистка существа с доски
            self.board = [m for m in self.board if m.health > 0]
            return True
        return False
    
    def remove_dead_minions(self):
        """""чистка существа с доски"""
        self.board = [minion for minion in self.board if minion.health > 0]
    
    def draw_health_bar(self, surface, x, y, width=150, height=20):
        """Отрисовка здоровья игрока"""
        #счёт здоровья в %
        health_percentage = self.health / self.max_health if self.max_health > 0 else 0
        
        #пустые очки здоровья
        background_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (100, 100, 100), background_rect)
        
        #восстановление здоровья
        if health_percentage > 0:
            fill_width = int(width * health_percentage)
            fill_rect = pygame.Rect(x, y, fill_width, height)
            
            #цвета для разного кол-ва здоровья
            if health_percentage > 0.6:
                color = (0, 255, 0) 
            elif health_percentage > 0.3:
                color = (255, 255, 0)
            else:
                color = (255, 0, 0)
            
            pygame.draw.rect(surface, color, fill_rect)
        
        #Текст на шкале здоровья
        font = pygame.font.Font(None, 18)
        health_text = font.render(f"{self.health}/{self.max_health}", True, (0, 0, 0))
        text_rect = health_text.get_rect(center=(x + width // 2, y + height // 2))
        surface.blit(health_text, text_rect)
        
        #отрисовка
        pygame.draw.rect(surface, (0, 0, 0), background_rect, 2)

    def draw_mana_bar(self, surface, x, y, width=150, height=20):
        """Отрисовка мана-бара"""
        #мана %
        mana_percentage = self.mana / self.max_mana if self.max_mana > 0 else 0
        
        #бэкграунд
        background_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (100, 100, 100), background_rect)
        
        #восстановление маны
        if mana_percentage > 0:
            fill_width = int(width * mana_percentage)
            fill_rect = pygame.Rect(x, y, fill_width, height)
            
            #цвет маны
            color = (100, 150, 255)
            pygame.draw.rect(surface, color, fill_rect)
        
        #мана текс
        font = pygame.font.Font(None, 18)
        mana_text = font.render(f"{self.mana}/{self.max_mana}", True, (0, 0, 0))
        text_rect = mana_text.get_rect(center=(x + width // 2, y + height // 2))
        surface.blit(mana_text, text_rect)
        
        #отрисовка
        pygame.draw.rect(surface, (0, 0, 0), background_rect, 2)

    def draw_info(self, surface, x, y):
        """инфа о игроке"""
        font = pygame.font.Font(None, 24)
        
        #имя
        name_text = font.render(self.name, True, (0, 0, 0))
        surface.blit(name_text, (x, y))
        
        #хп бар
        self.draw_health_bar(surface, x, y + 25, 150, 20)
        
        #мана бар
        self.draw_mana_bar(surface, x, y + 50, 150, 20)
        
        #кол-во карт на доске
        deck_text = font.render(f"Колода: {len(self.deck)}", True, (255, 255, 255))
        deck_text_width = deck_text.get_width()
        deck_text_height = deck_text.get_height()
        
        #прозрычный бэкграунд для доски
        deck_bg = pygame.Surface((deck_text_width + 8, deck_text_height + 4), pygame.SRCALPHA)
        deck_bg.fill((0, 0, 0, 180))
        surface.blit(deck_bg, (x - 2, y + 78))
        
        surface.blit(deck_text, (x, y + 80))