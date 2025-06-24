import pygame
from enum import Enum

class CardType(Enum):
    MINION = "minion"
    SPELL = "spell"
    WEAPON = "weapon"

class Card:
    def __init__(self, name, cost, card_type, description="", attack=0, health=0, spell_damage=0, image_path=None):
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
        self.summoning_sickness = True  # Can't attack the turn it's played
        self.rect = pygame.Rect(0, 0, 120, 160)
        self.image_path = image_path
        self.image = None
        self.image_loaded = False
        
    def reset_turn(self):
        """Reset card state for new turn"""
        if self.card_type == CardType.MINION:
            self.can_attack = True
            self.has_attacked = False
            self.summoning_sickness = False  # Can attack after first turn
    
    def take_damage(self, damage):
        """Apply damage to the card"""
        if self.card_type == CardType.MINION:
            self.health -= damage
            return self.health <= 0
        return False
    
    def attack_target(self, target):
        """Attack another card or player"""
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
        """Check if this minion can attack"""
        return (self.card_type == CardType.MINION and 
                not self.has_attacked and 
                not self.summoning_sickness and
                self.attack > 0)
    
    def heal(self, amount):
        """Heal the card"""
        if self.card_type == CardType.MINION:
            self.health = min(self.max_health, self.health + amount)
    
    def load_image(self):
        """Load the card image if not already loaded"""
        if self.image_loaded or not self.image_path:
            return
        
        try:
            # Try to load the image
            self.image = pygame.image.load(self.image_path)
            # Scale image to fit full card size
            self.image = pygame.transform.scale(self.image, (120, 160))
            self.image_loaded = True
        except (pygame.error, FileNotFoundError):
            # If image fails to load, set to None and mark as loaded to avoid retrying
            self.image = None
            self.image_loaded = True
    
    def draw(self, surface, x, y, selected=False):
        """Draw the card on the surface"""
        self.rect.x = x
        self.rect.y = y
        
        # Load and draw card image as background if available
        if not self.image_loaded:
            self.load_image()
        
        if self.image:
            # Draw the card image as full background
            surface.blit(self.image, (x, y))
        else:
            # Card background if no image
            color = (255, 255, 255) if not selected else (255, 255, 0)
            pygame.draw.rect(surface, color, self.rect)
        
        # Draw card border
        border_color = (255, 255, 0) if selected else (0, 0, 0)
        pygame.draw.rect(surface, border_color, self.rect, 3 if selected else 2)
        
        # Font setup
        font_small = pygame.font.Font(None, 16)
        font_medium = pygame.font.Font(None, 20)
        
        cost_bg = pygame.Surface((25, 20), pygame.SRCALPHA)
        cost_bg.fill((0, 0, 0, 180))
        surface.blit(cost_bg, (x + 2, y + 2))
        
        name_bg = pygame.Surface((115, 18), pygame.SRCALPHA)
        name_bg.fill((0, 0, 0, 180))
        surface.blit(name_bg, (x + 2, y + 23))
        
        # Draw cost with background
        cost_text = font_medium.render(str(self.cost), True, (100, 150, 255))
        surface.blit(cost_text, (x + 5, y + 5))
        
        # Draw name with background
        name_text = font_small.render(self.name[:12], True, (255, 255, 255))
        surface.blit(name_text, (x + 5, y + 25))
        
        # Draw stats for minions with backgrounds
        if self.card_type == CardType.MINION:
            # Attack background
            attack_bg = pygame.Surface((25, 20), pygame.SRCALPHA)
            attack_bg.fill((0, 0, 0, 180))
            surface.blit(attack_bg, (x + 2, y + 135))
            
            # Health background
            health_bg = pygame.Surface((25, 20), pygame.SRCALPHA)
            health_bg.fill((0, 0, 0, 180))
            surface.blit(health_bg, (x + 93, y + 135))
            
            attack_text = font_medium.render(str(self.attack), True, (255, 100, 100))
            health_text = font_medium.render(str(self.health), True, (100, 255, 100))
            surface.blit(attack_text, (x + 5, y + 135))
            surface.blit(health_text, (x + 95, y + 135))
        
        # Draw spell damage indicator with background
        if self.spell_damage > 0:
            spell_bg = pygame.Surface((80, 16), pygame.SRCALPHA)
            spell_bg.fill((0, 0, 0, 180))
            surface.blit(spell_bg, (x + 2, y + 128))
            
            spell_text = font_small.render(f"Spell +{self.spell_damage}", True, (200, 100, 200))
            surface.blit(spell_text, (x + 5, y + 130))
        
        # Draw attack indicator for minions that can attack
        if self.card_type == CardType.MINION and self.can_attack_target():
            pygame.draw.circle(surface, (255, 255, 0), (x + 110, y + 10), 5)
        
        # Draw summoning sickness indicator
        if self.card_type == CardType.MINION and self.summoning_sickness:
            pygame.draw.rect(surface, (128, 128, 128), self.rect, 3)

#сами карты
CARD_DATABASE = [
    #Существа
    Card("Канеки", 10, CardType.MINION, "", 10, 10, 0, "OPD/Heartstone/карты/миноны/Пробуждённый_кен.jpg"),
    Card("Татаро", 2, CardType.MINION, "", 3, 2, 0, "OPD/Heartstone/карты/миноны/Татаро.jpg"),
    Card("Йошимура", 1, CardType.MINION, "", 1, 2, 0, "OPD/Heartstone/карты/миноны/Это_Йошимура.jpg"),
    Card("Урие", 3, CardType.MINION, "", 5, 3, 0, "OPD/Heartstone/карты/миноны/Урие.jpg"),
    Card("Тоука", 5, CardType.MINION, "", 4, 7, 0, "OPD/Heartstone/карты/миноны/Тоука.jpg"),
    Card("Кукла", 6, CardType.MINION, "", 5, 8, 0, "OPD/Heartstone/карты/миноны/Кукла.jpg"),
    Card("Жрица", 4, CardType.MINION, "", 4, 6, 0, "OPD/Heartstone/карты/миноны/Жрец_кровавой_луны.jpg"),
    Card("Белка!", 7, CardType.MINION, "", 8, 5, 0, "OPD/Heartstone/карты/миноны/Белка.jpg"),
    
    #Заклинания
    Card("жатва", 6, CardType.SPELL, "Наносит 9 урона", 0, 0, 9, "OPD/Heartstone/карты/спелы/кровавая_жатва.jpg"),
    Card("Арата", 5, CardType.SPELL, "Даёт +3/+2", 0, 0, 0, "OPD/Heartstone/карты/спелы/Арата.jpg"),
    Card("Сахар", 2, CardType.SPELL, "Восстанавливает 4 здоровья", 0, 0, -4, "OPD/Heartstone/карты/спелы/Сахар.jpg"),
    Card("Кофе", 1, CardType.SPELL, "Восстанавливает 2 здоровья", 0, 0, -2, "OPD/Heartstone/карты/спелы/Кофе.jpg"),
    Card("Пакт",3, CardType.SPELL, "Наносит 4 урона", 0,0,5,"OPD/Heartstone/карты/спелы/Демонический_пакт.jpg")
]

def create_random_deck():
    """Create a random deck of 30 cards"""
    import random
    deck = []
    for _ in range(30):
        card_template = random.choice(CARD_DATABASE)
        # Create a copy of the card
        new_card = Card(
            card_template.name,
            card_template.cost,
            card_template.card_type,
            card_template.description,
            card_template.attack,
            card_template.health,
            card_template.spell_damage,
            card_template.image_path
        )
        deck.append(new_card)
    return deck