# FSND-P4-Design-A-Game
Udacity Full Stack Nano Degree - Project 4

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.

##Game Description:
Guess a number is a simple guessing game. Each game begins with a random 'target'
number between the minimum and maximum values provided, and a maximum number of
'attempts'. 'Guesses' are sent to the `make_move` endpoint which will reply
with either: 'too low', 'too high', 'you win', or 'game over' (if the maximum
number of attempts is reached).
Many different Guess a Number games can be played by many different Users at any
given time. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

##Game Description - Concentration
This game is based on the popular card game, Concentration!

###Game modes:
-	Single player, where the score is kept of turns taken to win
-	Two player, where the score is pairs won

###Rules:
-	Player who creates the game selects board size of 2,4,8 squares.
-	Each turn a player flips 2 cards, if the 2 cards match they “win” / “keep”
  the pair of cards and take another turn. If two cards have been flipped
  that don’t match, the turn is over. The player can keep taking consecutive
  turns as long as they can flip 2 cards that match.
- Once all cards have been removed from play the game is over.
-	The player with the most pairs wins the game. The game can be tied if both
  players have the same amount of pairs.

###Bonus Stats:
-	Most consecutive turns taken (by matching pairs) ordered by player

##Files Included:
- api.py: Contains endpoints and game playing logic.
- app.yaml: App configuration.
- cron.yaml: Cronjob configuration.
- main.py: Handler for taskqueue handler.
- models.py: Entity and message definitions including helper methods.
- utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will
      raise a ConflictException if a User with that user_name already exists.

 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name_1, user_name_2, size
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name_n provided must correspond to
      an existing user - will raise a NotFoundException if not. Size must be
      's','m','l' (small, medium, large).

 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.

 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, user_name, loc
    - Returns: GameForm with new game state.
    - Description: Accepts a 'loc' and returns the updated state of the game.
      If this causes a game to end, a corresponding Score entity will be
      created.

 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).

 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms.
    - Description: Returns all Scores recorded by the provided player (unordered).
      Will raise a NotFoundException if the User does not exist.

 - **get_active_game_count**
    - Path: 'games/active'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Gets the number of games that are currently active.

##To Implement:
 - **most_consecutive_turns**
    - Path: 'consecutive'
    - Method: GET
    - Parameters: None
    - Returns: ConsecutiveForms
    - Description: Returns record of users and consecutive turns ordered by
      turns.

 - **get_user_games**
    - Path: 'user/{user_name}/games'
    - Method: GET
    - Parameters: None
    - Returns: UserGamesForms
    - Description: Gets details for users active games.

 - **cancel_game**
    - Path: 'game/cancel/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key
    - Returns: None??
    - Description: Cancels an active game.

 - **get_high_scores_p1**
    - Path: 'scores/p1/high_scores/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: HighScoresP1Forms
    - Description: High scores for single player mode.

 - **get_high_scores_p2**
    - Path: 'scores/p2/high_scores/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: HighScoresP2Forms
    - Description: High scores for 2 player mode.

 - **get_user_rankings**
    - Path: 'scores/user_rankings'
    - Method: GET
    - Parameters: None
    - Returns: UserRankingsForms
    - Description: Player leaderboard for 2 player mode.

 - **get_game_history**
    - Path: 'game/history/'
    - Method: 'GET'
    - Parameters: urlsafe_game_key
    - Returns: GameHistoryForms
    - Description: List of game state and player moves for a selected game.

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
  - Records completed 2 player games. Associated with Users model via
    KeyProperty.

##Forms Included:
- **GameFormP1**
  - Representation of a single player Game's state (`urlsafe_key`, `user_name`, `size`, `turns`, `game_over`, `message`).

- **GameFormP2**
  - Representation of a two player Game's state (`urlsafe_key`, `user_name1`, `user_name1_turns`, `user_name1_pairs`, `user_name2, `user_name2_turns`, `user_name2_pairs`, `size`, `game_over`, `message`).

- **MakeMoveForm**
  - Inbound make move form (`x`, `y`).

- **ScoreFormP1**
  - Representation of a single player completed game's Score (`user_name`, `date`, `won`, `turns`).

- **ScoreFormP2**
  - Representation of a two player completed game's Score (`user_name`, `date`, `won`, `turns`, `pairs`, `tie`).

- **ScoreFormsP1**
  - Multiple ScoreFormP1 container.

- **ScoreFormsP2**
  - Multiple ScoreFormP2 container.

- **StringMessage**
  - General purpose String container.

- **ConsecutiveTurnsForm**
  - Representation of most consecutive turns per player (`user_name`, `turns`, `board_size`).

- **ConsecutiveTurnsForms**
  - Multiple ConsecutiveForm container.

- **UserGameForm**
  - Details about a users active game (`user_name`, `urlsafe_key`, `player_turn`, `turn`).

- **UserGameForms**
  - Collection of UserGameForm; used to list all players active games.

- **HighScoresP1Form**
  - High score for single player mode (`user_name`, `turns`).

- **HighScoresP1Forms**
  - Collection of HighScoresP1Form.

- **HighScoresP2Form**
  - High score for two player mode (user_name, pairs).

- **HighScoresP2Forms**
  - Collection of HighScoresP2Form.

##Forms to implement
- **UserRankingsForm**
  - (user_name, ration, pairs).

- **UserRankingsForms**
  - Multiple UserRankingsForm container.

- **GameHistoryForm**
  - (urlsafe_key, user_name, turn, loc, pair=tue/false, won_flag).

- **GameHistoryForms
  - Multiple GameHistoryForm container.
