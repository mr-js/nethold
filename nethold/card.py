from itertools import combinations
from random import randint, shuffle

class Card:
    rank = ''
    suit = ''
    name = ''
    
    NAMES = (
        '2♣', '3♣', '4♣', '5♣', '6♣', '7♣', '8♣', '9♣', 'T♣', 'J♣', 'Q♣', 'K♣', 'A♣',
        '2♦', '3♦', '4♦', '5♦', '6♦', '7♦', '8♦', '9♦', 'T♦', 'J♦', 'Q♦', 'K♦', 'A♦',
        '2♥', '3♥', '4♥', '5♥', '6♥', '7♥', '8♥', '9♥', 'T♥', 'J♥', 'Q♥', 'K♥', 'A♥',
        '2♠', '3♠', '4♠', '5♠', '6♠', '7♠', '8♠', '9♠', 'T♠', 'J♠', 'Q♠', 'K♠', 'A♠'
    )
    
    RANKS = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 
             'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    SUITS = {'♣': 1, '♦': 2, '♥': 3, '♠': 4}
    owner = 1000

    def __init__(self, name=None):
        if name is None:
            name = self.NAMES[randint(0, 51)]
        if name not in self.NAMES:
            raise ValueError('Card {} does not exist in the deck'.format(name))
        self.name = name
        self.rank = self.name[:-1]
        self.suit = self.name[-1]
        self.rank_value = self.RANKS[self.rank]
        self.owner = 1000

    def __ne__(self, other): return self.suit != other.suit
    def __eq__(self, other): return self.rank_value == other.rank_value
    def __gt__(self, other): return self.rank_value > other.rank_value
    def __lt__(self, other): return self.rank_value < other.rank_value
    def __le__(self, other): return self.rank_value <= other.rank_value
    def __ge__(self, other): return self.rank_value >= other.rank_value
    def __add__(self, other): return [self, other]

    def showinfo(self):
        print('Card {}: rank {}, suit {}'.format(self.name, self.rank, self.suit))

    def owning(self, owner=None):
        if owner is not None and self.owner != owner:
            self.owner = owner
        text = 'Card {} '.format(self.name)
        if self.owner > 0:
            if self.owner == 100:
                text += 'on the board'
            elif self.owner != 1000:
                text += 'held by player #: {}'.format(self.owner)
        else:
            text += 'in deck or discarded'
        print(text)

class Deck:
    cards = []
    point = 0    
    
    def __init__(self, cards=None):
        self.cards = []
        if cards is not None:
            for card in cards:
                self.cards.append(card)
        else:
            for name in Card.NAMES:
                self.cards.append(Card(name))
            shuffle(self.cards)
        self.point = 0

    def __getitem__(self, key):
        if isinstance(key, slice):
            return Deck(self.cards[key.start:key.stop:key.step])
        else:
            return self.cards[key]

    def __setitem__(self, key, value):
        self.cards[key].owner = value

    def distribution(self, target, amount):
        for card_index in range(self.point, self.point + amount):
             self.cards[card_index].owner = target
        self.point += amount

    def showinfo(self):
        print('{}'.format(' '.join(card.name for card in self.cards)))

    def evaluate(self):
        if len(self.cards) < 5:
            return ((0, []), "Not enough cards")

        best_score = (-1, [])
        best_name = ""

        for comb in combinations(self.cards, 5):
            ranks = sorted([c.rank_value for c in comb], reverse=True)
            is_flush = len(set(c.suit for c in comb)) == 1

            is_straight = False
            if len(set(ranks)) == 5 and ranks[0] - ranks[4] == 4:
                is_straight = True
            elif ranks == [14, 5, 4, 3, 2]:
                is_straight = True
                ranks = [5, 4, 3, 2, 1] 

            counts = {r: ranks.count(r) for r in set(ranks)}
            counts_sorted = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)

            if is_flush and is_straight:
                if ranks[0] == 14 and ranks[1] == 13:
                    score = (9, ranks)
                    name = "9. ROYAL FLUSH"
                else:
                    score = (8, ranks)
                    name = "8. STRAIGHT FLUSH"
            elif counts_sorted[0][1] == 4:
                score = (7, [counts_sorted[0][0], counts_sorted[1][0]])
                name = "7. FOUR OF A KIND"
            elif counts_sorted[0][1] == 3 and counts_sorted[1][1] == 2:
                score = (6, [counts_sorted[0][0], counts_sorted[1][0]])
                name = "6. FULL HOUSE"
            elif is_flush:
                score = (5, ranks)
                name = "5. FLUSH"
            elif is_straight:
                score = (4, ranks)
                name = "4. STRAIGHT"
            elif counts_sorted[0][1] == 3:
                score = (3, [counts_sorted[0][0]] + [r for r, c in counts_sorted[1:]])
                name = "3. THREE OF A KIND"
            elif counts_sorted[0][1] == 2 and counts_sorted[1][1] == 2:
                score = (2, [counts_sorted[0][0], counts_sorted[1][0], counts_sorted[2][0]])
                name = "2. TWO PAIR"
            elif counts_sorted[0][1] == 2:
                score = (1, [counts_sorted[0][0]] + [r for r, c in counts_sorted[1:]])
                name = "1. ONE PAIR"
            else:
                score = (0, ranks)
                name = "0. HIGH CARD"

            if score > best_score:
                best_score = score
                best_name = name

        return best_score, best_name

    def reset(self):
        for card in self.cards:
            card.owner = 1000
        shuffle(self.cards)
        self.point = 0