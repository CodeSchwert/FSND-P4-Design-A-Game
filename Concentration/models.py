"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game').

Classes modified from reference Udacity project:
User
Game -> GameP1,GameP2
Score -> ScoreP2,ScoreP2

"""

import datetime
import json
import random
from datetime import date
from protorpc import messages
from protorpc import message_types
from google.appengine.ext import ndb


""" Storage Classes """


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()


class GameP1(ndb.Model):
    """Single player game object"""
    user = ndb.KeyProperty(required=True, kind='User')
    size = ndb.IntegerProperty(required=True)
    card_pairs = ndb.IntegerProperty(required=True)
    card_map = ndb.JsonProperty(required=True)
    card_graveyard = ndb.JsonProperty(required=True)
    pairs_won = ndb.IntegerProperty(required=True, default=0)
    turns = ndb.IntegerProperty(required=True, default=0)
    consec_turns = ndb.IntegerProperty(required=True, default=0)
    consec_turns_temp = ndb.IntegerProperty(required=True, default=0)
    game_over = ndb.BooleanProperty(required=True, default=False)

    @classmethod
    def new_game(cls, user, size):
        """Creates and returns a new game"""
        if size not in [2,4,8]:
            raise ValueError('Invalid board size. Valid sizes are 2,4,8.')
        # Build a list of co-ordinate pairs
        card_map = {}
        card_pairs = ((size * size) / 2) # 2,8,32 pairs
        # create coord for all possible cells on board
        coords = [(x, y) for x in range(size) for y in range(size)]
        # shuffle the coords and randomly create matching pair
        random.shuffle(coords)
        for pair in range(card_pairs):
            card_map[str(coords.pop())] = pair
            card_map[str(coords.pop())] = pair
        # save json with an array of coord: value pairs
        card_map_json = json.dumps(card_map)
        card_graveyard_json = json.dumps({})
        # Create the game
        game = GameP1(user=user,
                      size=size,
                      card_pairs=card_pairs,
                      card_map=card_map_json,
                      card_graveyard=card_graveyard_json)
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        card_map_dict = json.loads(self.card_map)
        form = GameFormP1()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.size = self.size
        form.turns = self.turns
        form.game_over = self.game_over
        form.message = message
        form.cards = [
            json.dumps({key: card_map_dict[key]})
            for key in card_map_dict.keys()]
        form.pairs_won = self.pairs_won
        form.consec_turns = self.consec_turns
        return form

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = ScoreP1(user=self.user,
                        date=datetime.datetime.now(),
                        won=won,
                        turns=self.turns,
                        pairs=self.pairs_won,
                        size=self.size)
        consec_turns = ConsecutiveTurns(user=self.user,
                                        turns=self.consec_turns,
                                        size=self.size)
        score.put()
        consec_turns.put()


class GameP2(ndb.Model):
    """Two player game object"""
    # player 1 variables
    user1 = ndb.KeyProperty(required=True, kind='User')
    user1_turns = ndb.IntegerProperty(required=True, default=0)
    user1_pairs = ndb.IntegerProperty(required=True, default=0)
    user1_consec_turns = ndb.IntegerProperty(required=True, default=0)
    user1_consec_temp = ndb.IntegerProperty(required=True, default=0)
    # player 2 variables
    user2 = ndb.KeyProperty(required=True, kind='User')
    user2_turns = ndb.IntegerProperty(required=True, default=0)
    user2_pairs = ndb.IntegerProperty(required=True, default=0)
    user2_consec_turns = ndb.IntegerProperty(required=True, default=0)
    user2_consec_temp = ndb.IntegerProperty(required=True, default=0)
    # game object variables
    turns = ndb.IntegerProperty(required=True, default=0)
    card_pairs = ndb.IntegerProperty(required=True)
    card_map = ndb.JsonProperty(required=True)
    card_graveyard = ndb.JsonProperty(required=True)
    size = ndb.IntegerProperty(required=True)
    current_turn = ndb.IntegerProperty(required=True)
    game_over = ndb.BooleanProperty(required=True, default=False)

    @classmethod
    def new_game(cls, user1, user2, size):
        """Creates and returns a new game"""
        if size not in [2, 4, 8]:
            raise ValueError('Invalid board size. Valid sizes are 2,4,8.')
        # Build a list of co-ordinate pairs
        card_map = {}
        card_pairs = ((size * size) / 2) # 2,8,32 pairs
        # create coord for all possible cells on board
        coords = [(x, y) for x in range(size) for y in range(size)]
        # shuffle the coords and randomly create matching pair
        random.shuffle(coords)
        for pair in range(card_pairs):
            card_map[str(coords.pop())] = pair
            card_map[str(coords.pop())] = pair
        # save json with an array of coord: value pairs
        card_map_json = json.dumps(card_map)
        card_graveyard_json = json.dumps({})
        # Randomly choose which player goes first
        start_player = random.choice([1,2])
        game = GameP2(
            user1=user1,
            user2=user2,
            card_pairs=card_pairs,
            card_map=card_map_json,
            card_graveyard=card_graveyard_json,
            size=size,
            current_turn=start_player)
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        card_map_dict = json.loads(self.card_map)
        form = GameFormP2()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name1 = self.user1.get().name
        form.user_name1_turns = self.user1_turns
        form.user_name1_pairs = self.user1_pairs
        form.user_name1_consec_turns = self.user1_consec_turns
        form.user_name2 = self.user2.get().name
        form.user_name2_turns = self.user2_turns
        form.user_name2_pairs = self.user2_pairs
        form.user_name2_consec_turns = self.user2_consec_turns
        form.turns = self.turns
        form.current_turn = self.current_turn
        form.size = self.size
        form.cards = [
            json.dumps({key: card_map_dict[key]})
            for key in card_map_dict.keys()]
        form.game_over = self.game_over
        form.message = message
        return form

    def end_game(self, winner=0):
        """Ends the game - winner 0 = tied game, otherwise winner = 1 || 2"""
        if winner not in [0, 1, 2]:
            raise ValueError(
                'Invalid player selection number. Valid values are 0,1,2.')
        self.game_over = True
        self.put()
        # Add the game to the score 'board' for each player
        score1 = ScoreP2(user=self.user1,
                         date=datetime.datetime.now(),
                         won=False,
                         turns=self.user1_turns,
                         pairs=self.user1_pairs,
                         tie=False,
                         size=self.size)
        conect_turns1 = ConsecutiveTurns(user=self.user,
                                         turns=self.user1_consec_turns,
                                         size=self.size)
        score2 = ScoreP2(user=self.user2,
                         date=datetime.datetime.now(),
                         won=False,
                         turns=self.user2_turns,
                         pairs=self.user2_pairs,
                         tie=False,
                         size=self.size)
        conect_turns2 = ConsecutiveTurns(user=self.user,
                                         turns=self.user2_consec_turns,
                                         size=self.size)
        # Update the won flag for the winner
        if winner is 0:
            score1.tie = True
            score2.tie = True
        if winner is 1: score1.won = True
        if winner is 2: score2.won = True
        score1.put()
        score2.put()
        conect_turns1.put()
        conect_turns2.put()


class ScoreP1(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateTimeProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    turns = ndb.IntegerProperty(required=True)
    pairs = ndb.IntegerProperty(required=True)
    size = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreFormP1(user_name=self.user.get().name,
                           date=str(self.date),
                           won=self.won,
                           turns=self.turns,
                           pairs=self.pairs,
                           size=self.size)


class ScoreP2(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateTimeProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    turns = ndb.IntegerProperty(required=True)
    pairs = ndb.IntegerProperty(required=True)
    tie = ndb.BooleanProperty(required=True)
    size = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreFormP2(user_name=self.user.get().name,
                           date=str(self.date),
                           won=self.won,
                           turns=self.turns,
                           pairs=self.pairs,
                           tie=self.tie,
                           size=self.size)


class ConsecutiveTurns(ndb.Model):
    """Consecutive turns bonus score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    turns = ndb.IntegerProperty(required=True)
    size = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ConsecutiveTurnsForm(user_name=self.user.get().name,
                                    turns=self.turns,
                                    board_size=self.size)


""" Message Classes """


class NewGameFormP1(messages.Message):
    """Inbound form for creating a new single player game"""
    user_name = messages.StringField(1, required=True)
    size = messages.IntegerField(2, required=True)


class NewGameFormP2(messages.Message):
    """Inbound form for creating a new single player game"""
    user_name1 = messages.StringField(1, required=True)
    user_name2 = messages.StringField(2, required=True)
    size = messages.IntegerField(3, required=True)


class GameFormP1(messages.Message):
    """GameForm for outbound single player game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    user_name = messages.StringField(2, required=True)
    size = messages.IntegerField(3, required=True)
    turns = messages.IntegerField(4, required=True)
    game_over = messages.BooleanField(5, required=True)
    message = messages.StringField(6, required=True)
    cards = messages.StringField(7, repeated=True) # array of json
    pairs_won = messages.IntegerField(8, required=True)
    consec_turns = messages.IntegerField(9, required=True)


class GameFormP2(messages.Message):
    """GameForm for outbound two player game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    user_name1 = messages.StringField(2, required=True)
    user_name1_turns = messages.IntegerField(3, required=True)
    user_name1_pairs = messages.IntegerField(4, required=True)
    user_name1_consec_turns = messages.IntegerField(5, required=True)
    user_name2 = messages.StringField(6, required=True)
    user_name2_turns = messages.IntegerField(7, required=True)
    user_name2_pairs = messages.IntegerField(8, required=True)
    user_name2_consec_turns= messages.IntegerField(9, required=True)
    turns = messages.IntegerField(10 ,required=True)
    current_turn = messages.IntegerField(11, required=True)
    size = messages.IntegerField(12, required=True)
    cards = messages.StringField(13, repeated=True) # array of json
    game_over = messages.BooleanField(14, required=True)
    message = messages.StringField(15, required=True)


class MakeMoveFormP1(messages.Message):
    """Used to make a move in an existing game"""
    x1 = messages.IntegerField(1, required=True)
    y1 = messages.IntegerField(2, required=True)
    x2 = messages.IntegerField(3, required=True)
    y2 = messages.IntegerField(4, required=True)


class MakeMoveFormP2(messages.Message):
    """Used to make a move in an existing game"""
    x1 = messages.IntegerField(1, required=True)
    y1 = messages.IntegerField(2, required=True)
    x2 = messages.IntegerField(3, required=True)
    y2 = messages.IntegerField(4, required=True)
    user_name = messages.StringField(5, required=True)


class ActiveGamesForm(messages.Message):
    """List active games for a user (outbound)"""
    game = messages.StringField(1, repeated=True)


class ScoreFormP1(messages.Message):
    """ScoreForm for single plater outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    turns = messages.IntegerField(4, required=True)
    pairs = messages.IntegerField(5, required=True)
    size = messages.IntegerField(6, required=True)


class ScoreFormP2(messages.Message):
    """ScoreForm for two player outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    turns = messages.IntegerField(4, required=True)
    pairs = messages.IntegerField(5, required=True)
    tie = messages.BooleanField(6, required=True)
    size = messages.IntegerField(7, required=True)


class ScoreFormsP1(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreFormP1, 1, repeated=True)


class ScoreFormsP2(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreFormP2, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage - outbound (single) string message"""
    message = messages.StringField(1, required=True)


class ConsecutiveTurnsForm(messages.Message):
    """Returns Consecutive turn information (outbound)"""
    user_name = messages.StringField(1, required=True)
    turns = messages.IntegerField(2, required=True)
    board_size = messages.IntegerField(3, required=True)


class ConsecutiveTurnsForms(messages.Message):
    """Returns multiple ConsecutiveTurnsForm"""
    items = messages.MessageField(ConsecutiveTurnsForm, 1, repeated=True)


# class UserGameForm(messages.Message):
#     """Returns information about a single active Game"""
#     user_name = messages.StringField(1, required=True)
#     urlsafe_key = messages.StringField(2, required=True)
#     player_turn = messages.IntegerField(3, required=True)
#     turn = messages.IntegerField(4, required=True)
#
#
# class UserGameForms(messages.Message):
#     """Returns multiple UserGameForms"""
#     items = messages.MessageField(UserGameForm, 1, repeated=True)
#
#
# class HighScoresP1Form(messages.Message):
#     """Returns single player high score information (outbound)"""
#     user_name = messages.StringField(1, required=True)
#     turns = messages.IntegerField(2, required=True)
#
#
# class HighScoresP1Forms(messages.Message):
#     """Returns multiple HighScoresP1Form"""
#     items = messages.MessageField(HighScoresP1Form, 1, repeated=True)
#
#
# class HighScoresP2Form(messages.Message):
#     """Returns two player high score information (outbound)"""
#     user_name = messages.StringField(1, required=True)
#     pairs= messages.IntegerField(2, required=True)
#
#
# class HighScoresP2Forms(messages.Message):
#     """Returns multiple HighScoresP2Form"""
#     items = messages.MessageField(HighScoresP2Form, 1, repeated=True)
