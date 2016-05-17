# FSND-Design-A-Game
Udacity Full Stack Nano Degree - Project: Design a Game

## Set-Up Instructions:
1. Update the value of application in app.yaml to the app ID you have registered
in the App Engine admin console and would like to use to host your instance of
this sample.
2. Run the app with the devserver using dev_appserver.py DIR, and ensure it's
running by visiting the API Explorer
    - by default localhost:8080/_ah/api/explorer.
3. (Optional) Generate your client library(ies) with the endpoints tool. Deploy
your application.

##Game Description - Concentration
This game is based on the popular card game, Concentration! Players start by
creating a game with a grid of 2x2, 4x4 or 8x8 cards. The cards (or items
depending on the front end client) start face down. Players take turns by
picking two cards from the grid. If two cards (or items) "match", the player
"wins" the "pair", and the cards are taken out of play from the grid. If the
cards don't match they are placed back in the grid face down. The game
continues with players taking turns, picking pairs until there are no more
cards left in play. At that point scores are tallied and the game ends.

###Game modes:
-	Single player: The player plays against herself with the high score being the
least turns taken to "win" all the "pairs" in play.
-	Two player: Two players take turns to "match" all the "pairs" in play. If a
player matches a pair they are given another turn until they fail to select a
matching pair of cards. The high score in two player mode is the number of
pairs won.

###Bonus Score - Consecutive Turns:
During games, the number of consecutive turns where a pair was won are tracked.
This bonus score is kept for single and two player games and for both players
in two player games. There is a separate score board with the player scoring
the most consecutive pairs in a game.

###Bonus Score - User Ranking:
A user ranking system is kept for user that participate in two player games.
The score is worked out as a win : loss ratio.

###Rules:
-	Player who creates the game selects board size of 2,4,8 squares.
-	Each turn a player flips 2 cards, if the 2 cards match they “win” / “keep”
  the pair of cards and take another turn. If two cards have been flipped
  that don’t match, the turn is over. The player can keep taking consecutive
  turns as long as they can flip 2 cards that match.
- Once all cards have been removed from play the game is over.
-	The player with the most pairs wins the game. The game can be tied if both
  players have the same amount of pairs.

##Files Included:
- api.py: Contains endpoints and game playing logic.
- app.yaml: App configuration.
- cron.yaml: Cronjob configuration.
- main.py: Handler for taskqueue handler.
- messages.py: Message definitions.
- models.py: Entity definitions including helper methods.
- utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will
      raise a ConflictException if a User with that user_name already exists.

 - **new_game_p1**
    - Path: 'newgamep1'
    - Method: POST
    - Parameters: user_name, size
    - Returns: GameFormP1 with initial game state.
    - Description: Creates a new single player game. user_name provided must
      correspond to an existing user - will raise a NotFoundException if not.
      Size must be 2, 4, 8.

 - **get_game_p1**
    - Path: 'gamep1/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameFormP1 with current game state.
    - Description: Returns the current state of a single player game. Raises a
      NotFoundException if a game can't be found using the urlsafe_game_key.

 - **active_games_p1**
    - Path: 'activegamesp1'
    - Method: GET
    - Parameters: user_name
    - Returns: A list of urlsafe_game_key's of active single player games.
    - Description: The list of urlsafe_game_key are for single player games
      where the user is the player, and the game game_over field set to False.

 - **make_move_p1**
    - Path: 'gamep1/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, x1, x2, y1, y2
    - Returns: GameFormP1 with new game state.
    - Description: Accepts two co-ordinate pair (x1, y1), (x2, y2) and checks
      if the cards at the co-ordinates are a matching pair.

 - **cancel_game_p1**
    - Path: 'gamep1/cancel/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key
    - Returns: GameFormP1 with game_over set to True.
    - Description: Cancels an active game. Won't do anything meaningful if the
      game has already ended. Will raise a NotFoundException error if an
      invalid urlsafe_game_key is passed.

 - **get_high_scores_p1**
    - Path: 'scoresp1'
    - Method: GET
    - Parameters: None
    - Returns: ScoreFormsP1.
    - Description: Returns all ScoreP1 (single player) high scores in the
      database ordered by players with the least turns taken. The scores do not
      count games that haven't been finished by matching all cards on the grid.

 - **get_user_scores_p1**
    - Path: 'scoresp1/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreFormsP1 ordered by turns ascending.
    - Description: returns all ScoreP1 scores for a given user. Raises a
      NotFoundException if the User does not exist.

 - **new_game_p2**
    - Path: 'newgamep2'
    - Method: POST
    - Parameters: user_name1, user_name2, size
    - Returns: GameFormP2 with initial game state.
    - Description: Creates a new two player game. user_name_n provided must
      correspond to an existing user - will raise a NotFoundException if not.
      Size must be 2, 4, 8.

 - **get_game_p2**
    - Path: 'gamep2/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameFormP2 with current game state.
    - Description: Returns the current state of a two player game. Raises a
      NotFoundException if a game can't be found using the urlsafe_game_key.

 - **active_games_p2**
    - Path: 'activegamesp2'
    - Method: GET
    - Parameters: user_name
    - Returns: A list of urlsafe_game_key's of active two player games.
    - Description: The list of urlsafe_game_key are for two player games
      where the user is a player, and the games game_over field set to False.

 - **make_move_p2**
    - Path: 'gamep1/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, x1, x2, y1, y2
    - Returns: GameFormP2 with new game state.
    - Description: Accepts two co-ordinate pair (x1, y1), (x2, y2) and checks
      if the cards at the co-ordinates are a matching pair. Players will not be
      allowed to make a move if it isn't their turn.

 - **cancel_game_p2**
    - Path: 'gamep1/cancel/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key
    - Returns: GameFormP2 with game_over set to True.
    - Description: Cancels an active game. Won't do anything meaningful if the
      game has already ended. Will raise a NotFoundException error if an
      invalid urlsafe_game_key is passed.

 - **get_high_scores_p2**
    - Path: 'scoresp2'
    - Method: GET
    - Parameters: None
    - Returns: ScoreFormsP2.
    - Description: Returns all ScoreP2 (two player) high scores in the
      database ordered by players with the most pairs won.

 - **get_user_scores_p2**
    - Path: 'scoresp2/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreFormsP2 ordered by turns ascending.
    - Description: Returns all ScoreP2 scores for a given user. Raises a
      NotFoundException if the User does not exist.

 - **get_game_history_p1**
    - Path: 'historyp1/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameHistoryForms. List of GameHistoryForm.
    - Description: Returns a list of all moves taken during a single player
      game. The game can have ended. Will raise a NotFoundException error if
      the game doesn't exist.

 - **get_game_history_p2**
    - Path: 'historyp2/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameHistoryForms. List of GameHistoryForm.
    - Description: Returns a list of all moves taken during a two player game.
      The game can have ended. Will raise a NotFoundException error if the game
      doesn't exist.

 - **get_consecutive_turn_scores**
    - Path: 'consecutiveturns'
    - Method: GET
    - Parameters: None
    - Returns: ConsecutiveForms. A list of ConsecutiveForm.
    - Description: Returns list of users and their consecutive turns score
      ordered by turns.

 - **get_user_rankings**
    - Path: 'rankings'
    - Method: GET
    - Parameters: None
    - Returns: UserRankings. A list of User ordered by user_ranking.
    - Description: Returns list of users and their user_ranking ordered by
      user_ranking descending.

##Models Included:
- **User**
  - Stores unique user_name and (optional) email address.

- **GameP1**
    - Stores single player unique game states. Associated with User model via
      KeyProperty.

- **GameP2**
    - Stores 2 player unique game states. Associated with User model via
      KeyProperty.

- **ScoreP1**
  - Records completed single player games. Associated with Users model via
    KeyProperty.

- **ScoreP2**
  - Records completed two player games. Associated with Users model via
    KeyProperty.

- **ConsecutiveTurns**
  - Records consecutive turn bonus score. Associated with Users model via
    KeyProperty.

##Forms Included (message classes):
- **NewGameFormP1**
  - Inbound form to create a new single player game.

- **NewGameFormP2**
  - Inbound form to create a new two player game.

- **GameFormP1**
  - Representation of a single player Game's state.

- **GameFormP2**
  - Representation of a two player Game's state.

- **MakeMoveFormP1**
  - Inbound make move form (`x1`, `y`2), (`x2`, `y1`).

- **MakeMoveFormP2**
  - Inbound make move form (`x1`, `y`2), (`x2`, `y1`), user_name.

- **ScoreFormP1**
  - Representation of a single player completed game's Score.

- **ScoreFormP2**
  - Representation of a two player completed game's Score.

- **ScoreFormsP1**
  - Multiple ScoreFormP1 container.

- **ScoreFormsP2**
  - Multiple ScoreFormP2 container.

- **StringMessage**
  - General purpose String container.

- **ConsecutiveTurnsForm**
  - Representation of most consecutive turns per player (`user_name`, `turns`,          `board_size`).

- **ConsecutiveTurnsForms**
  - Multiple ConsecutiveForm container.

- **UserRanking**
  - Details about a users User ranking score.

- **UserRankings**
  - Collection of UserRanking; used to list all user ranking scores.

- **GameHistoryForm**
  - Details of co-ordinates and result taken by a player.

- **GameHistoryForms**
  - Collection of GameHistoryForm.
