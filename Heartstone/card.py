import pygame
from enum import Enum

class CardType(Enum):
    MINION = "minion"
    SPELL = "spell"
    WEAPON = "weapon"

class Card:
    def __init__(self, name, cost, card_type, description="", attack=0, health=0, spell_damage=0, image_path=None, cost_icon_path=None, attack_icon_path=None, health_icon_path=None, spell_icon_path=None):
        self.name = name
        self.cost = cost
        self.card_type = card_type
        self.description = description
        self.attack = attack
        self.health = health
        self.max_health = health
        self.spell_damage = spell_damage
        self.can_attack = False
        self.has_attacked = False
        self.summoning_sickness = True
        self.rect = pygame.Rect(0, 0, 120, 160)
        self.image_path = image_path
        self.image = None
        self.image_loaded = False
        
        #путь иконок
        self.cost_icon_path = cost_icon_path
        self.attack_icon_path = attack_icon_path
        self.health_icon_path = health_icon_path
        self.spell_icon_path = spell_icon_path
        
        #картинки иконок
        self.cost_icon = None
        self.attack_icon = None
        self.health_icon = None
        self.spell_icon = None
        self.icons_loaded = False
        
    def reset_turn(self):
        """новый карт стейт после хода"""
        if self.card_type == CardType.MINION:
            self.can_attack = True
            self.has_attacked = False
            self.summoning_sickness = False
    
    def take_damage(self, damage):
        """нанесение существу урона"""
        if self.card_type == CardType.MINION:
            self.health -= damage
            return self.health <= 0
        return False
    
    def attack_target(self, target):
        """атака игрока или существа"""
        if self.card_type != CardType.MINION or self.has_attacked or self.summoning_sickness:
            return False
        
        if hasattr(target, 'take_damage'):
            target.take_damage(self.attack)
            # If attacking a minion, this minion also takes damage
            if hasattr(target, 'attack') and target.attack > 0:
                self.take_damage(target.attack)
            
            self.has_attacked = True
            return True
        return False
    
    def can_attack_target(self):
        """проверка на возможность атаки"""
        return (self.card_type == CardType.MINION and 
                not self.has_attacked and 
                not self.summoning_sickness and
                self.attack > 0)
    
    def heal(self, amount):
        """исцеление карты"""
        if self.card_type == CardType.MINION:
            self.health = min(self.max_health, self.health + amount)
    
    def load_image(self):
        """загрузка карты если нет картинки"""
        if self.image_loaded or not self.image_path:
            return
        
        try:
            self.image = pygame.image.load(self.image_path)
            #скейл картинки
            self.image = pygame.transform.scale(self.image, (120, 160))
            self.image_loaded = True
        except (pygame.error, FileNotFoundError):
            self.image = None
            self.image_loaded = True
    
    def load_icons(self):
        """загрузка иконок"""
        if self.icons_loaded:
            return
        
        #иконка стоимости
        if self.cost_icon_path:
            try:
                self.cost_icon = pygame.image.load(self.cost_icon_path)
                self.cost_icon = pygame.transform.scale(self.cost_icon, (28, 28))
            except (pygame.error, FileNotFoundError):
                self.cost_icon = None
        
        #атаки
        if self.attack_icon_path:
            try:
                self.attack_icon = pygame.image.load(self.attack_icon_path)
                self.attack_icon = pygame.transform.scale(self.attack_icon, (24, 24))
            except (pygame.error, FileNotFoundError):
                self.attack_icon = None
        
        #здоровья
        if self.health_icon_path:
            try:
                self.health_icon = pygame.image.load(self.health_icon_path)
                self.health_icon = pygame.transform.scale(self.health_icon, (24, 24))
            except (pygame.error, FileNotFoundError):
                self.health_icon = None
        
        #спелл дмг
        if self.spell_icon_path:
            try:
                self.spell_icon = pygame.image.load(self.spell_icon_path)
                self.spell_icon = pygame.transform.scale(self.spell_icon, (24, 24))
            except (pygame.error, FileNotFoundError):
                self.spell_icon = None
        
        self.icons_loaded = True
    
    def draw(self, surface, x, y, selected=False):
        """отрисовка карты"""
        self.rect.x = x
        self.rect.y = y
        
        #загрузка бэкграунда для картинки
        if not self.image_loaded:
            self.load_image()
        
        #загрузка иконки
        if not self.icons_loaded:
            self.load_icons()
        
        if self.image:
            #отрисовка картинки
            surface.blit(self.image, (x, y))
        else:
            #бэкграунд для безкартиночных карт
            color = (255, 255, 255) if not selected else (255, 255, 0)
            pygame.draw.rect(surface, color, self.rect)
        
        #стейт карты
        if selected:
            border_color = (255, 255, 0)
            pygame.draw.rect(surface, border_color, self.rect, 3)
        elif self.card_type == CardType.MINION and self.can_attack_target():
            border_color = (255, 0, 0)
            pygame.draw.rect(surface, border_color, self.rect, 2)
        else:
            border_color = (128, 128, 128)
            pygame.draw.rect(surface, border_color, self.rect, 2)
        
        #фонт сетапик
        font_small = pygame.font.Font(None, 16)
        font_medium = pygame.font.Font(None, 20)
        
        #отрисовка имен карты
        words = self.name.split()
        line_height = 16
        start_y = y + 8
        
        for i, word in enumerate(words):
            #бэкграунд для линий текста
            word_surface = font_small.render(word, True, (255, 255, 255))
            word_width = word_surface.get_width()
            
            #позиция имени
            word_x = x + 120 - word_width - 10
            word_y = start_y + i * line_height
            
            #бэкграунд для слов
            word_bg = pygame.Surface((word_width + 4, 16), pygame.SRCALPHA)
            word_bg.fill((0, 0, 0, 180))
            surface.blit(word_bg, (word_x - 2, word_y))
            
            #отрисовка слов
            surface.blit(word_surface, (word_x, word_y + 1))
        
        #отрисовка иконок
        if self.cost_icon:
            surface.blit(self.cost_icon, (x + 3, y + 3))
        
        #иконка стоимости
        cost_text = font_medium.render(str(self.cost), True, (255, 255, 255))
        cost_rect = cost_text.get_rect(center=(x + 16, y + 17))
        surface.blit(cost_text, cost_rect)
        
        if self.card_type == CardType.MINION:
            #бэкграунд атаки
            attack_bg = pygame.Surface((40, 20), pygame.SRCALPHA)
            attack_bg.fill((0, 0, 0, 180))
            surface.blit(attack_bg, (x + 8, y + 135))
            
            #иконка атаки
            if self.attack_icon:
                surface.blit(self.attack_icon, (x + 9, y + 133))
            
            #здоровья
            if self.health_icon:
                surface.blit(self.health_icon, (x + 88, y + 133))
            
            attack_text = font_medium.render(str(self.attack), True, (255, 255, 255))
            health_text = font_medium.render(str(self.health), True, (255, 255, 255))
            attack_rect = attack_text.get_rect(center=(x + 36, y + 145))
            health_rect = health_text.get_rect(center=(x + 100, y + 145))
            surface.blit(attack_text, attack_rect)
            surface.blit(health_text, health_rect)
        
        #спелл дмг
        if self.spell_damage > 0:
            #иконка спелл дмг
            if self.spell_icon:
                surface.blit(self.spell_icon, (x + 50, y + 120))
            
            spell_text = font_small.render(f"+{self.spell_damage}", True, (255, 255, 255))
            spell_rect = spell_text.get_rect(center=(x + 62, y + 125))
            surface.blit(spell_text, spell_rect)
        

#сами карты
CARD_DATABASE = [
    #Существа
    Card("Канеки", 10, CardType.MINION, "", 10, 10, 0, "Heartstone/assets/cards/minions/Пробуждённый_кен.jpg", 
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         attack_icon_path="Heartstone/assets/icons/sword_icon.png", 
         health_icon_path="Heartstone/assets/icons/heart_icon.png"),
         Card("Арима Кишо", 9, CardType.MINION, "", 10, 8, 0, "Heartstone/assets/cards/minions/Арима Кишо.jpg", 
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         attack_icon_path="Heartstone/assets/icons/sword_icon.png", 
         health_icon_path="Heartstone/assets/icons/heart_icon.png"),
    Card("Татаро", 2, CardType.MINION, "", 3, 2, 0, "Heartstone/assets/cards/minions/Татаро.jpg", 
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         attack_icon_path="Heartstone/assets/icons/sword_icon.png", 
         health_icon_path="Heartstone/assets/icons/heart_icon.png"),
    Card("Йошимура", 1, CardType.MINION, "", 1, 2, 0, "Heartstone/assets/cards/minions/Это_Йошимура.jpg", 
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         attack_icon_path="Heartstone/assets/icons/sword_icon.png", 
         health_icon_path="Heartstone/assets/icons/heart_icon.png"),
    Card("Урие", 3, CardType.MINION, "", 4, 3, 0, "Heartstone/assets/cards/minions/Урие.jpg", 
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         attack_icon_path="Heartstone/assets/icons/sword_icon.png", 
         health_icon_path="Heartstone/assets/icons/heart_icon.png"),
    Card("Киришима Тоука", 5, CardType.MINION, "", 4, 7, 0, "Heartstone/assets/cards/minions/Тоука.jpg", 
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         attack_icon_path="Heartstone/assets/icons/sword_icon.png", 
         health_icon_path="Heartstone/assets/icons/heart_icon.png"),
    Card("Кукла", 6, CardType.MINION, "", 5, 8, 0, "Heartstone/assets/cards/minions/Кукла.jpg", 
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         attack_icon_path="Heartstone/assets/icons/sword_icon.png", 
         health_icon_path="Heartstone/assets/icons/heart_icon.png"),
    Card("Кровавая жрица", 4, CardType.MINION, "", 4, 6, 0, "Heartstone/assets/cards/minions/Жрец_кровавой_луны.jpg", 
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         attack_icon_path="Heartstone/assets/icons/sword_icon.png", 
         health_icon_path="Heartstone/assets/icons/heart_icon.png"),
    Card("Белка!", 7, CardType.MINION, "", 8, 4, 0, "Heartstone/assets/cards/minions/Белка.jpg", 
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         attack_icon_path="Heartstone/assets/icons/sword_icon.png", 
         health_icon_path="Heartstone/assets/icons/heart_icon.png"),
    Card("Сузую Джузо" , 7, CardType.MINION, "", 7, 7, 0, "Heartstone/assets/cards/minions/Джузо.jpg", 
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         attack_icon_path="Heartstone/assets/icons/sword_icon.png", 
         health_icon_path="Heartstone/assets/icons/heart_icon.png"),
    Card("Сколопендра" , 3, CardType.MINION, "", 5, 1, 0, "Heartstone/assets/cards/minions/Сколопендра.jpg", 
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         attack_icon_path="Heartstone/assets/icons/sword_icon.png", 
         health_icon_path="Heartstone/assets/icons/heart_icon.png"),
    #Заклинания
    Card("Кровавая жатва", 6, CardType.SPELL, "Наносит 9 урона", 0, 0, 9, "Heartstone/assets/cards/spells/кровавая_жатва.jpg",
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         spell_icon_path="Heartstone/assets/icons/fire.png"),
    Card("Арата", 5, CardType.SPELL, "Даёт +3/+2", 0, 0, 0, "Heartstone/assets/cards/spells/Арата.jpg",
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         spell_icon_path="Heartstone/assets/icons/fire.png"),
    Card("Сахар", 2, CardType.SPELL, "Восстанавливает 4 здоровья", 0, 0, -4, "Heartstone/assets/cards/spells/Сахар.jpg",
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         spell_icon_path="Heartstone/assets/icons/fire.png"),
    Card("Кофе", 1, CardType.SPELL, "Восстанавливает 2 здоровья", 0, 0, -2, "Heartstone/assets/cards/spells/Кофе.jpg",
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         spell_icon_path="Heartstone/assets/icons/fire.png"),
    Card("Пакт",3, CardType.SPELL, "Наносит 4 урона", 0,0,5,"Heartstone/assets/cards/spells/Демонический_пакт.jpg",
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         spell_icon_path="Heartstone/assets/icons/fire.png"),
    Card("Голод",4, CardType.SPELL, "Даёт +5/-2", 0,0,0,"Heartstone/assets/cards/spells/Голод.jpg",
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         spell_icon_path="Heartstone/assets/icons/fire.png"),
    Card("Свирепый натиск",1, CardType.SPELL, "Наносит 2 урона", 0,0,2,"Heartstone/assets/cards/spells/Свирепый натиск.jpg",
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         spell_icon_path="Heartstone/assets/icons/fire.png"),
    Card("Неиссякаемые пытки",10, CardType.SPELL, "наносит 12 урона", 0,0,12,"Heartstone/assets/cards/spells/Неиссякаемые пытки.jpg",
         cost_icon_path="Heartstone/assets/icons/Crystal.png", 
         spell_icon_path="Heartstone/assets/icons/fire.png"),
        ]

def create_random_deck():
    """создание колоды"""
    import random
    deck = []
    card_counts = {}
    
    for _ in range(30):
        #проверка на кол-во появлений карты
        available_cards = []
        for card_template in CARD_DATABASE:
            current_count = card_counts.get(card_template.name, 0)
            if current_count < 2:
                available_cards.append(card_template)

        #рандомная карта из доступных
        card_template = random.choice(available_cards)
        
        #обновление счётчика
        card_counts[card_template.name] = card_counts.get(card_template.name, 0) + 1
        
        #появление новых карт
        new_card = Card(
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
        deck.append(new_card)
    
    return deck