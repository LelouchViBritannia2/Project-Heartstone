import pygame
from enum import Enum

class CardType(Enum):
    MINION = "minion"
    SPELL = "spell"
    WEAPON = "weapon"

class Card:
    def __init__(self, name, cost, card_type, description="", attack=0, health=0, spell_damage=0):
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
    
    def draw(self, surface, x, y, selected=False):
        """Draw the card on the surface"""
        self.rect.x = x
        self.rect.y = y
        
        # Card background
        color = (255, 255, 255) if not selected else (255, 255, 0)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        
        # Font setup
        font_small = pygame.font.Font(None, 16)
        font_medium = pygame.font.Font(None, 20)
        
        # Draw cost
        cost_text = font_medium.render(str(self.cost), True, (0, 0, 255))
        surface.blit(cost_text, (x + 5, y + 5))
        
        # Draw name
        name_text = font_small.render(self.name[:12], True, (0, 0, 0))
        surface.blit(name_text, (x + 5, y + 25))
        
        # Draw stats for minions
        if self.card_type == CardType.MINION:
            attack_text = font_medium.render(str(self.attack), True, (255, 0, 0))
            health_text = font_medium.render(str(self.health), True, (0, 255, 0))
            surface.blit(attack_text, (x + 5, y + 135))
            surface.blit(health_text, (x + 95, y + 135))
        
        # Draw spell damage indicator
        if self.spell_damage > 0:
            spell_text = font_small.render(f"Spell +{self.spell_damage}", True, (128, 0, 128))
            surface.blit(spell_text, (x + 5, y + 45))
        
        # Draw attack indicator for minions that can attack
        if self.card_type == CardType.MINION and self.can_attack_target():
            pygame.draw.circle(surface, (255, 255, 0), (x + 110, y + 10), 5)
        
        # Draw summoning sickness indicator
        if self.card_type == CardType.MINION and self.summoning_sickness:
            pygame.draw.rect(surface, (128, 128, 128), self.rect, 3)

# Card database with 20 different card types
CARD_DATABASE = [
    # Minions
    Card("Fire Elemental", 6, CardType.MINION, "Battlecry: Deal 3 damage", 6, 5),
    Card("Water Elemental", 4, CardType.MINION, "Freeze any character damaged", 3, 6),
    Card("Earth Golem", 7, CardType.MINION, "Taunt", 7, 7),
    Card("Wind Rider", 3, CardType.MINION, "Charge", 3, 2),
    Card("Lightning Drake", 5, CardType.MINION, "Spell Damage +1", 4, 4, 1),
    Card("Ice Wizard", 3, CardType.MINION, "Spell Damage +1", 2, 4, 1),
    Card("Forest Guardian", 8, CardType.MINION, "Taunt, Heal 2 each turn", 6, 8),
    Card("Shadow Assassin", 2, CardType.MINION, "Stealth", 2, 1),
    Card("Crystal Mage", 4, CardType.MINION, "Draw a card", 2, 5),
    Card("Stone Warrior", 5, CardType.MINION, "Taunt", 4, 6),
    Card("Flame Imp", 1, CardType.MINION, "Deal 3 damage to yourself", 3, 2),
    Card("Healing Priest", 2, CardType.MINION, "Restore 3 Health", 1, 3),
    Card("Ken Kaneki",1,CardType.MINION,"nothing", 1,1),
    
    # Spells
    Card("Fireball", 4, CardType.SPELL, "Deal 6 damage", spell_damage=6),
    Card("Lightning Bolt", 1, CardType.SPELL, "Deal 3 damage", spell_damage=3),
    Card("Heal", 1, CardType.SPELL, "Restore 5 health", spell_damage=-5),
    Card("Frost Nova", 3, CardType.SPELL, "Freeze all enemies"),
    Card("Meteor", 6, CardType.SPELL, "Deal 15 damage", spell_damage=15),
    Card("Shield", 2, CardType.SPELL, "Give +0/+5 health"),
    Card("Power Up", 2, CardType.SPELL, "Give +3/+0 attack"),
    Card("Mass Heal", 4, CardType.SPELL, "Restore 3 health to all", spell_damage=-3),
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
            card_template.spell_damage
        )
        deck.append(new_card)
    return deck