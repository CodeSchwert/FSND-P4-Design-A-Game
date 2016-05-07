"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game').

Classes modified from reference Udacity project:
User
Game -> GameP1,GameP2
Score -> ScoreP2,ScoreP2

"""

import random
from datetime import date
from protorpc import messages
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
    turns = ndb.IntegerProperty(required=True, default=0)
    game_over = ndb.BooleanProperty(required=True, default=False)

    @classmethod
    def new_game(cls, user, size):
        """Creates and returns a new game"""
        if size not in [2,4,8]:
            raise ValueError('Invalid board size. Valid sizes are 2,4,8.')
        game = GameP1(user=user, size=size) #, turns=turns, game_over=game_over
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameFormP1()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.size = self.size
        form.turns = self.turns
        form.game_over = self.game_over
        form.message = message
        return form

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = ScoreP1(user=self.user,
                        date=date.today(),
                        won=won,
                        turns=self.turns)
        score.put()


# class GameP2(ndb.Model):
#     """Two player game object"""
#     user1 = ndb.KeyProperty(required=True, kind='User')
#     user1_turns = ndb.IntegerProperty(required=True)
#     user1_pairs = ndb.IntegerProperty(required=True)
#     user2 = ndb.KeyProperty(required=True, kind='User')
#     user2_turns = ndb.IntegerProperty(required=True)
#     user2_pairs = ndb.IntegerProperty(required=True)
#     size = ndb.IntegerProperty(required=True)
#     game_over = ndb.BooleanProperty(required=True, default=False)
#
#     @classmethod
#     def new_game(cls, user1, user2, size):
#         """Creates and returns a new game"""
#         if size not in [2, 4, 8]:
#             raise ValueError('Invalid board size. Valid sizes are 2,4,8.')
#         game = GameP1(
#             user1=user1,
#             user1_turns=0,
#             user1_pairs=0,
#             user2=user2,
#             user2_turns=0,
#             user2_pairs=0,
#             size=size,
#             game_over=False)
#         game.put()
#         return game
#
#     def to_form(self, message):
#         """Returns a GameForm representation of the Game"""
#         form = GameFormP2()
#         form.urlsafe_key = self.key.urlsafe()
#         form.user_name1 = self.user1.get().name
#         form.user_name1_turns = self.user1_turns
#         form.user_name1_pairs = self.user1_pairs
#         form.user_name2 = self.user2.get().name
#         form.user_name2_turns = self.user2_turns
#         form.user_name2_pairs = self.user2_pairs
#         form.size = self.size
#         form.game_over = self.game_over
#         form.message = message
#         return form
#
#     def end_game(self, winner=0):
#         """Ends the game - if won is True, the player won. - if won is False,
#         the player lost."""
#         if winner not in [0, 1, 2]:
#             raise ValueError(
#                 'Invalid player selection number. Valid values are 0,1,2.')
#         self.game_over = True
#         self.put()
#         # Add the game to the score 'board' for each player
#         score1 = ScoreP2(user=self.user1, date=date.today(), won=False,
#                          turns=self.user1_turns, pairs=self.user1_pairs,
#                          tie=False)
#         score2 = ScoreP2(user=self.user2, date=date.today(), won=False,
#                          turns=self.user2_turns, pairs=self.user2_pairs,
#                          tie=False)
#         # Update the won flag for the winner
#         if winner is 0:
#             score1.tie = True
#             score2.tie = True
#         if winner is 1: score1.won = True
#         if winner is 2: score2.won = True
#         score1.put()
#         score2.put()


class ScoreP1(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    turns = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreFormP1(user_name=self.user.get().name, date=str(self.date),
                           won=self.won, turns=self.turns)

#
# class ScoreP2(ndb.Model):
#     """Score object"""
#     user = ndb.KeyProperty(required=True, kind='User')
#     date = ndb.DateProperty(required=True)
#     won = ndb.BooleanProperty(required=True)
#     turns = ndb.IntegerProperty(required=True)
#     pairs = ndb.IntegerProperty(required=True)
#     tie = ndb.BooleanProperty(required=True)
#
#     def to_form(self):
#         return ScoreFormP2(user_name=self.user.get().name, date=str(self.date),
#                            won=self.won, turns=self.turns, pairs=self.pairs,
#                            tie=self.tie)
#

""" Message Classes """


class NewGameFormP1(messages.Message):
    """Inbound form for creating a new single player game"""
    user_name = messages.StringField(1, required=True)
    size = messages.IntegerField(2, required=True)


class GameFormP1(messages.Message):
    """GameForm for outbound single player game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    user_name = messages.StringField(2, required=True)
    size = messages.IntegerField(3, required=True)
    turns = messages.IntegerField(4, required=True)
    game_over = messages.BooleanField(5, required=True)
    message = messages.StringField(6, required=True)
#
#
# class GameFormP2(messages.Message):
#     """GameForm for outbound two player game state information"""
#     urlsafe_key = messages.StringField(1, required=True)
#     user_name1 = messages.StringField(2, required=True)
#     user_name1_turns = messages.IntegerField(3, required=True)
#     user_name1_pairs = messages.IntegerField(4, required=True)
#     user_name2 = messages.StringField(5, required=True)
#     user_name2_turns = messages.IntegerField(6, required=True)
#     user_name2_pairs = messages.IntegerField(7, required=True)
#     size = messages.IntegerField(8, required=True)
#     game_over = messages.BooleanField(9, required=True)
#     message = messages.StringField(10, required=True)
#

# class MakeMoveForm(messages.Message):
#     """Used to make a move in an existing game"""
#     x = messages.IntegerField(1, required=True)
#     y = messages.IntegerField(2, required=True)


class ScoreFormP1(messages.Message):
    """ScoreForm for single plater outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    turns = messages.IntegerField(4, required=True)


# class ScoreFormP2(messages.Message):
#     """ScoreForm for two player outbound Score information"""
#     user_name = messages.StringField(1, required=True)
#     date = messages.StringField(2, required=True)
#     won = messages.BooleanField(3, required=True)
#     turns = messages.IntegerField(4, required=True)
#     pairs = messages.IntegerField(5, required=True)
#     tie = messages.BooleanField(6, required=True)
#
#
# class ScoreFormsP1(messages.Message):
#     """Return multiple ScoreForms"""
#     items = messages.MessageField(ScoreFormP1, 1, repeated=True)
#
#
# class ScoreFormsP2(messages.Message):
#     """Return multiple ScoreForms"""
#     items = messages.MessageField(ScoreFormP2, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage - outbound (single) string message"""
    message = messages.StringField(1, required=True)


# class ConsecutiveTurnsForm(messages.Message):
#     """Returns Consecutive turn information (outbound)"""
#     user_name = messages.StringField(1, required=True)
#     turns = messages.IntegerField(2, required=True)
#     board_size = messages.IntegerField(3, required=True)
#
#
# class ConsecutiveTurnsForms(messages.Message):
#     """Returns multiple ConsecutiveTurnsForm"""
#     items = messages.MessageField(ConsecutiveTurnsForm, 1, repeated=True)
#
#
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
