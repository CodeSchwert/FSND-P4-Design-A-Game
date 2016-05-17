# -*- coding: utf-8 -*-`
"""messages.py - This file contains essage class definitions."""


from protorpc import messages


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
    cards = messages.StringField(7, repeated=True)  # array of json
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
    user_name2_consec_turns = messages.IntegerField(9, required=True)
    turns = messages.IntegerField(10, required=True)
    current_turn = messages.IntegerField(11, required=True)
    size = messages.IntegerField(12, required=True)
    cards = messages.StringField(13, repeated=True)  # array of json
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


class UserRanking(messages.Message):
    """User ranking information"""
    user_name = messages.StringField(1, required=True)
    user_ranking = messages.FloatField(2, required=True)


class UserRankings(messages.Message):
    """A list of user rankings"""
    rankings = messages.MessageField(UserRanking, 1, repeated=True)


class GameHistoryForm(messages.Message):
    """Game move - (turn, player, coord1, coord2, result)"""
    turn = messages.IntegerField(1, required=True)
    player = messages.IntegerField(2, required=True)
    coord1 = messages.StringField(3, required=True)
    coord2 = messages.StringField(4, required=True)
    result = messages.StringField(5, required=True)


class GameHistoryForms(messages.Message):
    history = messages.MessageField(GameHistoryForm, 1, repeated=True)
