# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue
# import ndb models
from models import User, GameP1, ScoreP1#, GameP2,  ScoreP2
# omport message classes
from models import StringMessage, NewGameFormP1, GameFormP1
# from models import GameFormP2, NewGameForm, ScoreFormP1, \
#     ScoreFormP2, ConsecutiveTurnsForm, UserGameForm, HighScoresP1Form, \
#     HighScoresP2Form, StringMessage
from utils import get_by_urlsafe

USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))
NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameFormP1)
GET_GAME_P1_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)
GET_GAME_P2_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)

# MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
#     MakeMoveForm,
#     urlsafe_game_key=messages.StringField(1),)


#MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

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

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameFormP1,
                      path='game_p1',
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
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')


    """TODO - List all active single player games for a user"""


    # @endpoints.method(request_message=MAKE_MOVE_REQUEST,
    #                   response_message=GameForm,
    #                   path='game/{urlsafe_game_key}',
    #                   name='make_move',
    #                   http_method='PUT')
    # def make_move(self, request):
    #     """Makes a move. Returns a game state with message"""
    #     game = get_by_urlsafe(request.urlsafe_game_key, Game)
    #     if game.game_over:
    #         return game.to_form('Game already over!')
    #
    #     game.attempts_remaining -= 1
    #     if request.guess == game.target:
    #         game.end_game(True)
    #         return game.to_form('You win!')
    #
    #     if request.guess < game.target:
    #         msg = 'Too low!'
    #     else:
    #         msg = 'Too high!'
    #
    #     if game.attempts_remaining < 1:
    #         game.end_game(False)
    #         return game.to_form(msg + ' Game over!')
    #     else:
    #         game.put()
    #         return game.to_form(msg)
    #
    # @endpoints.method(response_message=ScoreForms,
    #                   path='scores',
    #                   name='get_scores',
    #                   http_method='GET')
    # def get_scores(self, request):
    #     """Return all scores"""
    #     return ScoreForms(items=[score.to_form() for score in Score.query()])
    #
    # @endpoints.method(request_message=USER_REQUEST,
    #                   response_message=ScoreForms,
    #                   path='scores/user/{user_name}',
    #                   name='get_user_scores',
    #                   http_method='GET')
    # def get_user_scores(self, request):
    #     """Returns all of an individual User's scores"""
    #     user = User.query(User.name == request.user_name).get()
    #     if not user:
    #         raise endpoints.NotFoundException(
    #                 'A User with that name does not exist!')
    #     scores = Score.query(Score.user == user.key)
    #     return ScoreForms(items=[score.to_form() for score in scores])
    #
    # @endpoints.method(response_message=StringMessage,
    #                   path='games/average_attempts',
    #                   name='get_average_attempts_remaining',
    #                   http_method='GET')
    # def get_average_attempts(self, request):
    #     """Get the cached average moves remaining"""
    #     return StringMessage(message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')
    #
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
