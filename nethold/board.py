from card import Card, Deck
from player import Player, Players
from enum import Enum

BLIND_SMALL = 5

class Board:
    class Stages(Enum):
        PRE_FLOP, FLOP, TURN, RIVER = (0, 1, 2, 3)
        def __int__(self):
            return int(self.value)
            
    def __init__(self, player_names):
        self.stage = self.Stages.PRE_FLOP
        self.bet = 0
        self.pot = 0        
        self.deck = Deck()
        self.players = Players(player_names)
        
    def __del__(self):
        del self.deck, self.players
        
    def reset(self):
        self.stage = self.Stages.PRE_FLOP
        self.bet = 0
        self.pot = 0        
        self.deck.reset()
        
    def view(self):
        print('Stage: {}'.format(self.stage.name))
        print('Pot: {} chips'.format(self.pot))
        
    def player_input(self):
        val = 0
        print('1 - Call, 2 - Check, 3 - Raise, 4 - Fold, 5 - All-In')
        try:
            act = Player.Actions(int(input("> ")) + 1)
        except ValueError:
            act = Player.Actions.FAILED
            
        if act == Player.Actions.RAISE:
            try:
                print('Total amount to bet?')
                val = int(input("> "))
            except ValueError:
                act = Player.Actions.FAILED
        return act, val
        
    def player_cards_output(self, player):
        print('Player #{}'.format(player.position), end=': ')
        print(' '.join(card.name for card in self.deck.cards if card.owner == player.position))
        
    def board_cards_output(self):
        print('Board', end=': ')
        print(' '.join(card.name for card in self.deck.cards if card.owner == 100))
        
    def round_cards(self, stage):
        self.stage = stage
        if self.stage == self.Stages.PRE_FLOP:
            for player in self.players.players:
                self.deck.distribution(player.position, 2)
        elif self.stage == self.Stages.FLOP:
            self.deck.distribution(100, 3)
        elif self.stage == self.Stages.TURN:
            self.deck.distribution(100, 1)
        elif self.stage == self.Stages.RIVER:
            self.deck.distribution(100, 1)
            
        self.board_cards_output()
        for player in self.players.active_players():
            self.player_cards_output(player)
            
    def round_trades(self, stage):
        self.players.round_states_reset()
        self.bet = 0
        
        if self.stage == self.Stages.PRE_FLOP:
            p1 = self.players.next_player_move()
            if p1: p1.post(Player.Actions.BLIND, BLIND_SMALL, BLIND_SMALL)
            p2 = self.players.next_player_move()
            if p2: p2.post(Player.Actions.BLIND, BLIND_SMALL * 2, BLIND_SMALL * 2)
            self.bet = BLIND_SMALL * 2
            
        while True:
            active = self.players.active_players()
            voting = self.players.vote_players()

            if len(active) == 1:
                return 1
            if len(voting) == 0:
                break 
                
            if self.players.vote_finished():
                if all(p.bet == self.bet for p in voting):
                    break

            player = self.players.next_player_move()
            if not player:
                break
                
            print('\nCurrent Round Bet: {} chips'.format(self.bet))
            print('++ Player #{}\'s turn "{}" (Balance: {}, Current Bet: {})'.format(
                player.position, player.name, player.balance, player.bet))
                
            while True:
                act, val = self.player_input()
                result = player.post(act, self.bet, val)
                if result[0] == Player.Actions.FAILED:
                    print('Invalid input, please try again.')
                    continue
                else:
                    if result[0] != Player.Actions.FOLD:
                        if player.bet > self.bet:
                            self.bet = player.bet
                    break
                    
        self.pot += self.players.bet_sum()
        print('++ End of betting round. Total Pot: {} chips'.format(self.pot))
        return 0
        
    def round_final(self):
        print('Total Pot: {} chips'.format(self.pot))
        active_players = self.players.active_players()
        
        if len(active_players) == 1:
            active_players[0].won = True
        else:
            print('++ Combinations:')
            for player in active_players:
                print('Player #{} "{}"'.format(player.position, player.name))
                player_cards = [c for c in self.deck.cards if c.owner == player.position or c.owner == 100]
                hand_deck = Deck(player_cards)
                score_tuple, score_name = hand_deck.evaluate()
                player.score = score_tuple
                print(f"   {score_name}")
                
            best_score = max(player.score for player in active_players)
            for player in active_players:
                if player.score == best_score:
                    player.won = True
                    
        winners = self.players.win_players()
        print('++ Winner(s):')
        award = self.pot // len(winners)
        for player in winners:
            player.balance += award
            print('Player #{} "{}" wins {} chips!'.format(player.position, player.name, award))
        return winners
        
    def hand(self):
        self.reset()
        self.players.reset()
        self.deck.reset()
        
        stages = [
            (self.Stages.PRE_FLOP, 'ROUND 1/4 PRE-FLOP'),
            (self.Stages.FLOP, 'ROUND 2/4 FLOP'),
            (self.Stages.TURN, 'ROUND 3/4 TURN'),
            (self.Stages.RIVER, 'ROUND 4/4 RIVER')
        ]
        
        for stage, title in stages:
            print('\n{}\n{}\n{}'.format('*' * 40, title, '*' * 40))
            self.round_cards(stage)
            if self.round_trades(stage) > 0:
                break
                
        print('\n{}\n{}\n{}'.format('*' * 40, 'SHOWDOWN', '*' * 40))
        self.round_final()
        
        print('-' * 40)
        self.players.player_game_losers()
        self.players.showstate()
        return self.players.check_game_win()