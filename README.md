# Backend Challenge - Tic Tac Toe task

The challenge is to create RESTful API for Tic Tac Toe game in python with DRF.

### Application Features

* It is possible for multiple pair of players to play games at the same time
* The backend checks whether a move is actually possible and report a failure if it is not
* API to check updates of games, i.e. whether the other player has made a move, if a game has been finished, etc.
* The games status lost/won is stored per user
* Token-Based-Authentication and Authorization 

### Application Architecture

* App is designed to operate with three models, they are below:
* Player: It has all player details
  * Its fields are:
    * id: PK, AutoField
    * player_id = User
    * created_date: AutoField
    * modified_date: AutoField
    * state(wait,ready): By default 'ready' but if other player is already playing game then it'll be 'wait'
    * symbol: User input

* Game: It has all games information
  * Its fields are:
    * id: PK, AutoField
    * name: User input
    * board: It is the game board, saved in db as a binary field.
    * status(game started, game finished): It is evaluated in the game, by default it is 'game started'
    * players: Game is in Many-to-many relation with the Players
    * count: It shows number of moves done on board
    * score: It carries game score
  
* Team: It has all teams information
  * Its fields are:
    * id: PK, AutoField
    * name: User input
    * players: Many-to-one relationship using foreign key with Player model
    * games: Game is in Many-to-many relation with the Teams
    * status(won, lost): It is evaluated in the game, by default it is 'lost'

### API's
* All api's are restricted to the authenticated users
* Response contains two fields: Message and HTTP status code
* [] Move API:
  * Method: POST
  * Endpoint: '/api/move/<row>/<column>'
* [] Check Game Updates API
  * Method: GET
  * Endpoint: '/api/move'
* [] High Score API
  * Method: GET
  * Endpoint: '/api/get_high_score_list'

### How to run?

* git clone the repository: git clone <url>
* Build the docker image with all dependencies installed: docker build -t image_name:tag_name .
* To run the image: docker run image_name:tag_name
  
### Improvements - TODO?

* Tests need to be implemented for all functionality
* Code can be more optimized to make views skinny
* Signals can be implemented to check game/team status
* Exception and error handling can be more improved
* Code comments needs to be added
