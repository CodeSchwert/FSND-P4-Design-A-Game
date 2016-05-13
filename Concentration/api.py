# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

import datetime
import logging
import endpoints
import json
from protorpc import remote, messages
from protorpc import message_types
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
# import ndb models
from models import User, GameP1, GameP2, ScoreP1, ScoreP2, ConsecutiveTurns
# import message classes
from models import StringMessage, NewGameFormP1, NewGameFormP2, GameFormP1, \
    GameFormP2, MakeMoveFormP1, MakeMoveFormP2, ActiveGamesForm, \
    ConsecutiveTurnsForm, ConsecutiveTurnsForms, ScoreFormP1, ScoreFormsP1, \
    ScoreFormP2, ScoreFormsP2
from utils import get_by_urlsafe

USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))
NEW_GAME_REQUEST_P1 = endpoints.ResourceContainer(NewGameFormP1)
NEW_GAME_REQUEST_P2 = endpoints.ResourceContainer(NewGameFormP2)
GET_GAME_P1_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)
GET_GAME_P2_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST_P1 = endpoints.ResourceContainer(
    MakeMoveFormP1,
    urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST_P2 = endpoints.ResourceContainer(
    MakeMoveFormP2,
    urlsafe_game_key=messages.StringField(1),)
ACTIVE_GAMES_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1))
USER_SCORE_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1))


@endpoints.api(name='concentration', version='v1')
class ConcentrationGameApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST_P1,
                      response_message=GameFormP1,
                      path='newgamep1',
                      name='new_game_p1',
                      http_method='POST')
    def new_game_p1(self, request):
        """Creates new single player game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        try:
            game = GameP1.new_game(user.key, request.size)
        except ValueError:
            raise endpoints.BadRequestException('Invalid board size. Valid '
                                                'sizes are 2,4,8.')
        return game.to_form('Good luck playing Concentration!')

    @endpoints.method(request_message=GET_GAME_P1_REQUEST,
                      response_message=GameFormP1,
                      path='gamep1/{urlsafe_game_key}',
                      name='get_game_p1',
                      http_method='GET')
    def get_game_p1(self, request):
        """Return the current single player game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, GameP1)
        if game:
            if game.game_over:
                return game.to_form('Game already over!')
            else:
                return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=ACTIVE_GAMES_REQUEST,
                      response_message=ActiveGamesForm,
                      path='activegamesp1',
                      name='active_games_p1',
                      http_method='GET')
    def active_games_p1(self, request):
        """List all active single player games for a user"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        games = GameP1.query(GameP1.user == user.key)
        return ActiveGamesForm(
            game=[(g.key).urlsafe() for g in games if g.game_over is False])

    @endpoints.method(request_message=MAKE_MOVE_REQUEST_P1,
                      response_message=GameFormP1,
                      path='gamep1/{urlsafe_game_key}',
                      name='make_move_p1',
                      http_method='PUT')
    def make_move_p1(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, GameP1)
        if game.game_over:
            return game.to_form('Game already over!')
        # convert card_map from json to dict
        card_map_dict = json.loads(game.card_map)
        graveyard_dict = json.loads(game.card_graveyard)
        # convert coord tuple to string
        selection1 = str((request.x1, request.y1))
        selection2 = str((request.x2, request.y2))
        # check coords are valid / still in play - the two sanity check blocks
        # shouldn't be triggered in normal circumstances, so doesn't increment
        # the turn counter or penalize the player
        if selection1 == selection2:
            msg = "Invalid selection - choose 2 different pairs!!"
            return game.to_form(msg)
        if selection1 not in card_map_dict or selection2 not in card_map_dict:
            msg = "Invalid selection: {0}, {1}".format(selection1, selection2)
            return game.to_form(msg)
        # check coord associated values match
        if card_map_dict[selection1] == card_map_dict[selection2]:
            msg = "Found a pair!!"
            game.pairs_won += 1
            game.consec_turns_temp += 1
            if game.consec_turns_temp > game.consec_turns:
                game.consec_turns = game.consec_turns_temp
            # move the pair of coords to the 'graveyard'
            for selection in [selection1, selection2]:
                graveyard_dict[selection] = card_map_dict[selection]
                del card_map_dict[selection]
        else:
            msg = "The pair don't match ..."
            game.consec_turns_temp = 0
        # update game state
        game.turns += 1
        game.card_map = json.dumps(card_map_dict)
        game.card_graveyard = json.dumps(graveyard_dict)
        game.put()
        # check the game isn't finished
        if len(card_map_dict) is 0:
            msg = "Congratulations you found the last pair - Game Over!!"
            game.end_game(won=True)
        # return game form
        return game.to_form(msg)

    @endpoints.method(response_message=ScoreFormsP1,
                      path='scoresp1',
                      name='get_scores_p1',
                      http_method='GET')
    def get_scores_p1(self, request):
        """Return all single player scores"""
        return ScoreFormsP1(items=[s.to_form() for s in ScoreP1.query()])

    @endpoints.method(request_message=USER_SCORE_REQUEST,
                      response_message=ScoreFormsP1,
                      path='scoresp1/user/{user_name}',
                      name='get_user_scores_p1',
                      http_method='GET')
    def get_user_scores_p1(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = ScoreP1.query(ScoreP1.user == user.key)
        return ScoreFormsP1(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=NEW_GAME_REQUEST_P2,
                      response_message=GameFormP2,
                      path='newgamep2',
                      name='new_game_p2',
                      http_method='POST')
    def new_game_p2(self, request):
        """Create a new two player game"""
        user1 = User.query(User.name == request.user_name1).get()
        user2 = User.query(User.name == request.user_name2).get()
        if not user1 or not user2:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        try:
            game = GameP2.new_game(user1.key, user2.key, request.size)
        except ValueError:
            raise endpoints.BadRequestException('Invalid board size. Valid '
                                                'sizes are 2,4,8.')
        return game.to_form('Good luck playing Concentration!')

    @endpoints.method(request_message=GET_GAME_P2_REQUEST,
                      response_message=GameFormP2,
                      path='gamep2/{urlsafe_game_key}',
                      name='get_game_p2',
                      http_method='GET')
    def get_game_p2(self, request):
        """Get two player game state information"""
        game = get_by_urlsafe(request.urlsafe_game_key, GameP2)
        if game:
            if game.game_over:
                return game.to_form('Game already over!')
            else:
                return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=ACTIVE_GAMES_REQUEST,
                      response_message=ActiveGamesForm,
                      path='activegamesp2',
                      name='active_games_p2',
                      http_method='GET')
    def active_games_p2(self, request):
        """List all active two player games for a user"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        games = GameP2.query(
            ndb.OR(GameP2.user1 == user.key, GameP2.user2 == user.key))
        return ActiveGamesForm(
            game=[(g.key).urlsafe() for g in games if g.game_over is False])

    @endpoints.method(request_message=MAKE_MOVE_REQUEST_P2,
                      response_message=GameFormP2,
                      path='gamep2/{urlsafe_game_key}',
                      name='make_move_p2',
                      http_method='PUT')
    def make_move_p2(self, request):
        """Make move in two player game. Returns game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, GameP2)
        if game.game_over:
            return game.to_form('Game already over!')
        user = User.query(User.name == request.user_name).get().key
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        # determine the player making the move
        player = (1 if user == game.user1 else 2)
        # check the player is allowed to make a move
        if player != game.current_turn:
            return game.to_form('Not your turn yet!!')
        # convert card_map from json to dict
        card_map_dict = json.loads(game.card_map)
        graveyard_dict = json.loads(game.card_graveyard)
        # convert coord tuple to string
        selection1 = str((request.x1, request.y1))
        selection2 = str((request.x2, request.y2))
        # check coords are valid / still in play - the two sanity check blocks
        # shouldn't be triggered in normal circumstances, so doesn't increment
        # the turn counter or penalize the player
        if selection1 == selection2:
            msg = "Invalid selection - choose 2 different pairs!!"
            return game.to_form(msg)
        if selection1 not in card_map_dict or selection2 not in card_map_dict:
            msg = "Invalid selection: {0}, {1}".format(selection1, selection2)
            return game.to_form(msg)
        # player attributes
        player_pairs = 'user{0}_pairs'.format(player)
        player_turns = 'user{0}_turns'.format(player)
        player_con_temp = 'user{0}_consec_temp'.format(player)
        player_con_turns = 'user{0}_consec_turns'.format(player)
        # check coord associated values match
        if card_map_dict[selection1] == card_map_dict[selection2]:
            # move the pair of coords to the 'graveyard'
            for selection in [selection1, selection2]:
                graveyard_dict[selection] = card_map_dict[selection]
                del card_map_dict[selection]
            msg = "Found a pair!!"
            # increment pair count for player
            setattr(game, player_pairs, (getattr(game, player_pairs) + 1))
            # increment turn count for player
            setattr(game, player_turns, (getattr(game, player_turns) + 1))
            # increment consecutive turns counter for player
            setattr(game, player_con_temp, getattr(game, player_con_temp) + 1)
            # update player consec turns if needed
            if (getattr(game, player_con_temp) >
                    getattr(game, player_con_turns)):
                setattr(game, player_con_turns, getattr(game, player_con_temp))
            # update next players turn (current_turn) - take another turn
            setattr(game, 'current_turn', player)
        else:
            msg = "The pair doesn't match ..."
            setattr(game, player_turns, (getattr(game, player_turns) + 1))
            setattr(game, player_con_temp, 0)
            # update next players turn (current_turn) - next players turn
            setattr(game, 'current_turn', (1 if player == 2 else 2))
        # update game "global" variables
        game.turns += 1
        game.card_map = json.dumps(card_map_dict)
        game.card_graveyard = json.dumps(graveyard_dict)
        game.put()
        # end the game if all cards are removed from play
        if len(card_map_dict) is 0:
            msg = "Congratulations you found the last pair - Game Over!!"
            # determine winning player - most pairs
            if game.user1_pairs == game.user2_pairs:
                winner = 0
            else:
                winner = (1 if game.user1_pairs > game.user2_pairs else 2)
            # end game ...
            game.end_game(winner=winner)
        # return game form
        return game.to_form(msg)

    """TODO - Get scores P2 game"""

    @endpoints.method(response_message=ConsecutiveTurnsForms,
                      path='consecutiveturns',
                      name='get_consecutive_turn_scores',
                      http_method='GET')
    def get_consecutive_turn_scores(self, request):
        """Get a list of all consecutive turn scores"""
        consec_turns = ConsecutiveTurns.query()\
            .order(ConsecutiveTurns.turns)\
            .order(-ConsecutiveTurns.size)
        return ConsecutiveTurnsForms(
            items=[ct.to_form() for ct in ConsecutiveTurns.query()])

    # @endpoints.method(response_message=StringMessage,
    #                   path='games/average_attempts',
    #                   name='get_average_attempts_remaining',
    #                   http_method='GET')
    # def get_average_attempts(self, request):
    #     """Get the cached average moves remaining"""
    #     return StringMessage(message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')

    # @staticmethod
    # def _cache_average_attempts():
    #     """Populates memcache with the average moves remaining of Games"""
    #     games = Game.query(Game.game_over == False).fetch()
    #     if games:
    #         count = len(games)
    #         total_attempts_remaining = sum([game.attempts_remaining
    #                                     for game in games])
    #         average = float(total_attempts_remaining)/count
    #         memcache.set(MEMCACHE_MOVES_REMAINING,
    #                      'The average moves remaining is {:.2f}'.format(average))
    #

api = endpoints.api_server([ConcentrationGameApi])
