import random
from typing import List

class Deck:
    def __init__(self):
        self.cards: List[Card] = []
        self.discard_pile: List[Card] = []
        self.hand: List[Card] = []

    def shuffle(self):
        """洗牌，将抽牌堆和弃牌堆混合"""
        if not self.cards:
            self.cards = self.discard_pile[:]
            self.discard_pile.clear()
        random.shuffle(self.cards)

    def draw(self, num=1):
        """从抽牌堆抽指定数量的牌到手上"""
        drawn = []
        for _ in range(num):
            if not self.cards:
                self.shuffle()
            if self.cards:
                drawn.append(self.cards.pop())
        self.hand.extend(drawn)
        return drawn