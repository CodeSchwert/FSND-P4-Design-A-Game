# -*- coding: utf-8 -*-`
"""api.py - Concentration Game API exposing the endpoint resources.
The API contains both game logic and communication to/from the API."""

import datetime
import logging
import endpoints
import json
from protorpc import remote, messages
from protorpc import message_types
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
# import ndb (storage) models
from models import User, GameP1, GameP2, ScoreP1, ScoreP2, ConsecutiveTurns
# import message classes
from messages import (
    NewGameFormP1,
    NewGameFormP2,
    GameFormP1,
    GameFormP2,
    MakeMoveFormP1,
    MakeMoveFormP2,
    ActiveGamesForm,
    ScoreFormP1,
    ScoreFormsP1,
    ScoreFormP2,
    ScoreFormsP2,
    StringMessage,
    ConsecutiveTurnsForm,
    ConsecutiveTurnsForms,
    UserRanking,
    UserRankings,
    GameHistoryForm,
    GameHistoryForms
)
from utils import get_by_urlsafe

USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))
NEW_GAME_REQUEST_P1 = endpoints.ResourceContainer(NewGameFormP1)
NEW_GAME_REQUEST_P2 = endpoints.ResourceContainer(NewGameFormP2)
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST_P1 = endpoints.ResourceContainer(
    MakeMoveFormP1,
    urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST_P2 = endpoints.ResourceContainer(
    MakeMoveFormP2,
    urlsafe_game_key=messages.StringField(1),)
USER_RESOURCE_REQUEST = endpoints.ResourceContainer(
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
        """Create a User. Requires a unique username.
        Args:
            user_name: A user name string.
            email: Optional, valid email. Not validated.
        Returns:
            StringMessage with a welcome message!
        Raises:
            ConflictException: when user already exists."""
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
        """Creates new single player game.
        Args:
            user_name: Player user name.
            size: Size of the game board, valid values [2, 4, 8].
        Returns:
            GameP1 form representation of the game state.
        Raises:
            NotFoundException: when user doesn't exist.
            BadRequestException on invalid size."""
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

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameFormP1,
                      path='gamep1/{urlsafe_game_key}',
                      name='get_game_p1',
                      http_method='GET')
    def get_game_p1(self, request):
        """Return the current single player game state.
        Args:
            urlsafe_game_key: A urlsafe key string.
        Returns:
            GameP1 form representation of the game state.
        Raises:
            NotFoundException: if the game doesn't exist."""
        game = get_by_urlsafe(request.urlsafe_game_key, GameP1)
        if game:
            if game.game_over:
                return game.to_form('Game already over!')
            else:
                return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=USER_RESOURCE_REQUEST,
                      response_message=ActiveGamesForm,
                      path='activegamesp1',
                      name='active_games_p1',
                      http_method='GET')
    def active_games_p1(self, request):
        """List all active single player games for a user.
        Args:
            user_name: User name string.
        Returns:
            A list of urlsafe_game_key.
        Raises:
            NotFoundException: if user doesn't exist."""
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
        """Makes a move. Returns a game state with message.
        Args:
            x1: First co-ordinate x position
            x2: Second co-ordinate x position
            y1: First co-ordinate y position
            y2: Second co-ordinate y position
        Returns:
            GameP1 form representation of the game state."""
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
            msg = "The pair doesn't match ..."
            game.consec_turns_temp = 0
        # update game state
        game.turns += 1
        game.card_map = json.dumps(card_map_dict)
        game.card_graveyard = json.dumps(graveyard_dict)
        game.update_game_history(1, selection1, selection2, msg)
        game.put()
        # check the game isn't finished
        if len(card_map_dict) is 0:
            msg = "Congratulations you found the last pair - Game Over!!"
            game.end_game(won=True)
        # return game form
        return game.to_form(msg)

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameFormP1,
                      path='gamep1/cancel/{urlsafe_game_key}',
                      name='cancel_game_p1',
                      http_method='PUT')
    def cancel_game_p1(self, request):
        """Cancel a single player game.
        Args:
            urlsafe: A urlsafe key string.
        Returns:
            GameP1 form representation of the game state.
        Raises:
            NotFoundException: if game doesn't exist."""
        game = get_by_urlsafe(request.urlsafe_game_key, GameP1)
        if game:
            if game.game_over:
                return game.to_form('Game already over!')
            else:
                game.end_game()
                return game.to_form('Game cancelled!!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(response_message=ScoreFormsP1,
                      path='scoresp1',
                      name='get_high_scores_p1',
                      http_method='GET')
    def get_high_scores_p1(self, request):
        """Get single player game high scores (turns taken). Only includes
        games which were won.
        Args:
            None.
        Returns:
            List of ScoreP1 - ordered by turns ascending."""
        scores = ScoreP1.query(ScoreP1.won == True).order(ScoreP1.turns)
        return ScoreFormsP1(items=[s.to_form() for s in scores])

    @endpoints.method(request_message=USER_RESOURCE_REQUEST,
                      response_message=ScoreFormsP1,
                      path='scoresp1/user/{user_name}',
                      name='get_user_scores_p1',
                      http_method='GET')
    def get_user_scores_p1(self, request):
        """Returns all single player game scores for a user - ordered by turns
        taken.
        Args:
            user_name: User name string.
        Returns:
            List of ScoreP1 - all scores for given user.
        Raises:
            NotFoundException: if user doesn't exist."""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = ScoreP1.query(ScoreP1.user == user.key).order(ScoreP1.turns)
        return ScoreFormsP1(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=NEW_GAME_REQUEST_P2,
                      response_message=GameFormP2,
                      path='newgamep2',
                      name='new_game_p2',
                      http_method='POST')
    def new_game_p2(self, request):
        """Create a new two player game.
        Args:
            user_name1: Player 1 user name.
            user_name2: Player 2 user name.
            size: Size of the game board, valid values [2, 4, 8].
        Returns:
            GameP2 form representation of the game state.
        Raises:
            NotFoundException: if either of the players doesn't exist.
            BadRequestException: when invalid size passed."""
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

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameFormP2,
                      path='gamep2/{urlsafe_game_key}',
                      name='get_game_p2',
                      http_method='GET')
    def get_game_p2(self, request):
        """Get two player game state information.
        Args:
            urlsafe_game_key: A urlsafe key string.
        Returns:
            GameP2 form representation of the game state.
        Raises:
            NotFoundException: if the game doesn't exist."""
        game = get_by_urlsafe(request.urlsafe_game_key, GameP2)
        if game:
            if game.game_over:
                return game.to_form('Game already over!')
            else:
                return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=USER_RESOURCE_REQUEST,
                      response_message=ActiveGamesForm,
                      path='activegamesp2',
                      name='active_games_p2',
                      http_method='GET')
    def active_games_p2(self, request):
        """List all active two player games for a user.
        Args:
            user_name: User name string.
        Returns:
            A list of urlsafe_game_key.
        Raises:
            NotFoundException: if user doesn't exist."""
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
        """Make move in two player game. Returns game state with message.
        Args:
            x1: First co-ordinate x position.
            x2: Second co-ordinate x position.
            y1: First co-ordinate y position.
            y2: Second co-ordinate y position.
            user_name: User name string.
        Returns:
            GameP2 form representation of the game state.
        Raises:
            NotFoundException: if user doesn't exist."""
        game = get_by_urlsafe(request.urlsafe_game_key, GameP2)
        if game.game_over:
            return game.to_form('Game already over!')
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        # determine the player making the move
        player = (1 if user.key == game.user1 else 2)
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
        game.update_game_history(player, selection1, selection2, msg)
        game.put()
        # end the game if all cards are removed from play
        if len(card_map_dict) is 0:
            user1 = User.query(User.key == game.user1).get()
            user2 = User.query(User.key == game.user2).get()
            if not user1 or not user2:
                raise endpoints.NotFoundException(
                        'A User with that name does not exist!')
            msg = "Congratulations you found the last pair - Game Over!!"
            # determine winning player - most pairs
            if game.user1_pairs == game.user2_pairs:
                winner = 0
                user1.update_user_ranking_info(0)
                user2.update_user_ranking_info(0)
            else:
                winner = (1 if game.user1_pairs > game.user2_pairs else 2)
            # update user stats
            if winner == 1:
                user1.update_user_ranking_info(1)
                user2.update_user_ranking_info(-1)
            elif winner == 2:
                user1.update_user_ranking_info(-1)
                user2.update_user_ranking_info(1)
            # end game ...
            game.end_game(winner=winner)
        # return game form
        return game.to_form(msg)

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameFormP2,
                      path='gamep2/cancel/{urlsafe_game_key}',
                      name='cancel_game_p2',
                      http_method='PUT')
    def cancel_game_p2(self, request):
        """Cancel a two player game.
        Args:
            urlsafe: A urlsafe key string.
        Returns:
            GameP2 form representation of the game state.
        Raises:
            NotFoundException: if game doesn't exist."""
        game = get_by_urlsafe(request.urlsafe_game_key, GameP2)
        if game:
            if game.game_over:
                return game.to_form('Game already over!')
            else:
                game.end_game()
                return game.to_form('Game cancelled!!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(response_message=ScoreFormsP2,
                      path='scoresp2',
                      name='get_high_scores_p2',
                      http_method='GET')
    def get_high_scores_p2(self, request):
        """Get two player game high scores (pairs won).
        Args:
            None.
        Returns:
            List of ScoreP2 - ordered by pairs descending then by date
            descending."""
        scores = ScoreP2.query().order(-ScoreP2.pairs).order(-ScoreP2.date)
        return ScoreFormsP2(items=[s.to_form() for s in scores])

    @endpoints.method(request_message=USER_RESOURCE_REQUEST,
                      response_message=ScoreFormsP2,
                      path='scoresp2/user/{user_name}',
                      name='get_user_scores_p2',
                      http_method='GET')
    def get_user_scores_p2(self, request):
        """Returns all two player game scores for a user - ordered by pairs
        won.
        Args:
            user_name: User name string.
        Returns:
            List of ScoreP2 - all scores for given user.
        Raises:
            NotFoundException: if user doesn't exist."""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = ScoreP2.query(ScoreP2.user == user.key).order(ScoreP2.pairs)
        return ScoreFormsP2(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameHistoryForms,
                      path='historyp1/{urlsafe_game_key}',
                      name='get_game_history_p1',
                      http_method='GET')
    def get_game_history_p1(self, request):
        """Game history - get a list of game moves (single player games).
        Args:
            urlsafe: A urlsafe key string.
        Returns:
            A list of GameHistoryForm -
                (turns, player, coord1, coord2, move_result)
        Raises:
            NotFoundException: if the game doesn't exist."""
        game = get_by_urlsafe(request.urlsafe_game_key, GameP1)
        if not game:
            raise endpoints.NotFoundException('Game not found!')
        return GameHistoryForms(
            history=[GameHistoryForm(turn=h[0],
                                     player=h[1],
                                     coord1=h[2],
                                     coord2=h[3],
                                     result=h[4]) for h in game.game_history])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameHistoryForms,
                      path='historyp2/{urlsafe_game_key}',
                      name='get_game_history_p2',
                      http_method='GET')
    def get_game_history_p2(self, request):
        """Game history - get a list of game moves (two player games).
        Args:
            urlsafe: A urlsafe key string.
        Returns:
            A list of GameHistoryForm -
                (turns, player, coord1, coord2, move_result)
        Raises:
            NotFoundException: if the game doesn't exist."""
        # each move is recorded as:
        #     (turn, player: 1||2, coord1: (x, y), coord2: (x, y), result: msg)
        game = get_by_urlsafe(request.urlsafe_game_key, GameP2)
        if not game:
            raise endpoints.NotFoundException('Game not found!')
        return GameHistoryForms(
            history=[GameHistoryForm(turn=h[0],
                                     player=h[1],
                                     coord1=h[2],
                                     coord2=h[3],
                                     result=h[4]) for h in game.game_history])

    @endpoints.method(response_message=ConsecutiveTurnsForms,
                      path='consecutiveturns',
                      name='get_consecutive_turn_scores',
                      http_method='GET')
    def get_consecutive_turn_scores(self, request):
        """Get a list of all consecutive turn scores.
        Args:
            None.
        Returns:
            A list of ConsecutiveTurns (forms) - ordered by turns descending
            then by size descending."""
        consec_turns = ConsecutiveTurns.query()\
            .order(-ConsecutiveTurns.turns)\
            .order(-ConsecutiveTurns.size)
        return ConsecutiveTurnsForms(
            items=[ct.to_form() for ct in consec_turns])

    @endpoints.method(response_message=UserRankings,
                      path='rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Two player user ranking - determined by pairs won / turns taken.
        This method just lists the rankings. Ranking information is updated at
        the end of each game turn.
        Args:
            None.
        Returns:
            A list of UserRanking (form) ordered by user_ranking descending."""
        user_rankings = User.query().order(-User.user_ranking)
        return UserRankings(
            rankings=[ur.to_user_ranking_form() for ur in user_rankings])

api = endpoints.api_server([ConcentrationGameApi])
