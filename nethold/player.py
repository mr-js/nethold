from enum import Enum

PLAYER_START_BALANCE = 100

class Player:
    name = ''
    position = 1
    balance = 0
    voted = False
    folded = False
    allin = False
    won = False
    bet = 0
    score = None

    class Actions(Enum):
        FAILED, NONE, BLIND, CALL, CHECK, RAISE, FOLD, ALLIN = (-1, 0, 1, 2, 3, 4, 5, 6)

    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.balance = PLAYER_START_BALANCE
        self.action = self.Actions.NONE
        self.folded = False
        self.allin = False
        self.voted = False
        self.won = False
        self.bet = 0
        self.score = None

    def showinfo(self):
        print('Player #{} "{}": {} chips balance'.format(self.position, self.name, self.balance))

    def post(self, action_type, *action_args):
        self.voted = True
        self.action = action_type
        bet_round_min = action_args[0]

        if action_type == self.Actions.BLIND:
            bet_player_first = action_args[1]
            if bet_player_first >= bet_round_min:
                self.bet = bet_player_first
                self.balance -= bet_player_first
                if self.balance <= 0:
                    self.balance = 0
                    self.allin = True
                print('Player #{} "{}": posted blind of {} chips, remaining balance: {}'.format(
                    self.position, self.name, bet_player_first, self.balance))
                return self.action, bet_player_first

        if action_type == self.Actions.CHECK:
            if self.bet == bet_round_min:
                print('Player #{} "{}": checked, remaining balance: {}'.format(self.position, self.name, self.balance))
                return self.action, bet_round_min

        if action_type == self.Actions.CALL:
            bet_delta = bet_round_min - self.bet
            if self.balance >= bet_delta and bet_delta >= 0:
                self.balance -= bet_delta
                self.bet += bet_delta
                if self.balance == 0:
                    self.allin = True
                print('Player #{} "{}": called {}, added {} chips, remaining balance: {}'.format(
                    self.position, self.name, bet_round_min, bet_delta, self.balance))
                return self.action, bet_round_min
            elif self.balance > 0 and self.balance < bet_delta:
                return self.post(self.Actions.ALLIN, bet_round_min)

        if action_type == self.Actions.RAISE:
            bet_player_total = action_args[1]
            bet_player_delta = bet_player_total - self.bet
            if self.balance >= bet_player_delta and bet_player_total >= bet_round_min and bet_player_delta > 0:
                self.balance -= bet_player_delta
                self.bet = bet_player_total
                if self.balance == 0:
                    self.allin = True
                print('Player #{} "{}": raised to {}, added {} chips, remaining balance: {}'.format(
                    self.position, self.name, bet_player_total, bet_player_delta, self.balance))
                return self.action, bet_player_total

        if action_type == self.Actions.ALLIN:
            added_chips = self.balance
            self.bet += self.balance
            self.balance = 0
            self.allin = True
            new_min = max(bet_round_min, self.bet)
            print('Player #{} "{}": goes ALL-IN, adding {} chips, total bet is now {}'.format(
                self.position, self.name, added_chips, self.bet))
            return self.action, new_min

        if action_type == self.Actions.FOLD:
            print('Player #{} "{}": folded and left the betting round'.format(self.position, self.name))
            self.folded = True
            return self.action, bet_round_min

        print('Player #{} "{}": failed to execute action {} {}'.format(self.position, self.name, self.action, action_args))
        self.action = self.Actions.FAILED
        return self.action, bet_round_min

class Players:
    def __init__(self, names):
        self.players = []
        counter = 1
        for name in names:
            self.players.append(Player(name, counter))
            counter += 1
        self.active = 1            
        self.dealer = 0

    def __del__(self): del self.players
    def __len__(self): return len(self.players)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.players[key.start:key.stop:key.step]
        else:
            return self.players[key]

    def showinfo(self):        
        for player in self.players:
            print('Player #{} "{}"'.format(player.position, player.name))

    def showstate(self):     
        for player in self.players:
            print('Player #{} "{}": {} chips'.format(player.position, player.name, player.balance))            

    def active_players(self):
         return list(player for player in self.players if not player.folded)

    def bet_min(self):
        active = self.active_players()
        return min((player.bet for player in active), default=0)

    def bet_sum(self):
        return sum(player.bet for player in self.active_players())

    def vote_players(self):
        return list(player for player in self.players if not player.folded and not player.allin)

    def vote_finished(self):
        voting = self.vote_players()
        if not voting:
            return True
        return all(player.voted for player in voting)

    def win_players(self):
         return list(player for player in self.players if player.won)    

    def next_player_move(self):
        if len(self.active_players()) <= 1:
            return None
        current_idx = next((i for i, p in enumerate(self.players) if p.position == self.active), 0)
        for i in range(1, len(self.players) + 1):
            idx = (current_idx + i) % len(self.players)
            p = self.players[idx]
            if not p.folded and not p.allin:
                self.active = p.position
                return p         
        return None   

    def round_states_reset(self):
        for player in self.players:
            player.voted = False
            player.bet = 0           
        self.active = self.players[self.dealer].position if self.players else 1

    def reset(self):
        for player in self.players:
            player.folded = False
            player.allin = False
            player.voted = False
            player.won = False           
            player.bet = 0
            player.score = None
        self.dealer = (self.dealer + 1) % len(self.players)
        self.active = self.players[self.dealer].position

    def player_game_losers(self):
        to_remove = [p for p in self.players if p.balance == 0]
        for player in to_remove:
            print('Player #{} "{}" is out of chips and leaves the game'.format(player.position, player.name))
            self.players.remove(player)

    def check_game_win(self):
        if len(self.players) == 1:
            player = self.players[0]
            print('Player #{} "{}" has WON THE GAME!'.format(player.position, player.name))
            return True
        return False