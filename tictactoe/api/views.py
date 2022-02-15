from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from rest_framework import status
from django.http import Http404
from .models import Player, Game
from .serializers import GameSerializer
import base64
import pickle
import numpy as np

def check_rows(board):
    # check inline vertical and horizontal
    for row in board:
        if len(set(row)) == 1:
            return True
    return False

def check_diagonals(board):
    # (0,0) == (1,1) == (2,2)
    if len(set([board[i][i] for i in range(len(board))])) == 1: 
        return True
    
    # (0,2) == (1,1) == (2,0)
    if len(set([board[i][len(board)-i-1] for i in range(len(board))])) == 1:
        return True
    
    return False

def check_win(board):
    #transposition to check rows, then columns
    for newBoard in [board, np.transpose(board)]:
        result = check_rows(newBoard)
        if result:
            return result
    return check_diagonals(board)

def play_your_turn(row, column, game_obj, current_player):
    # TIC TAC TOE Board
    game_board = game_obj.board
    turns_count = game_obj.count
    
    np_bytes = base64.b64decode(game_board)
    np_array = pickle.loads(np_bytes)
    if not np_array[row][column]:
        # Existing board but the cell is empty
        np_array[row][column] = current_player.symbol
    else:
        return False

    np_bytes = pickle.dumps(np_array)
    np_base64 = base64.b64encode(np_bytes)
    game_obj.board = np_base64
    game_obj.count = turns_count + 1
    
    # After fifth move, there are chances to win or lose
    if turns_count > 4:
        if check_win(np_array):
            # Update game status
            game_obj.status = 'end'
            unique, counts = np.unique(np_array, return_counts=True)
            array_dic = dict(zip(unique, counts))
            game_obj.score = array_dic[current_player.symbol]/9
            for team in current_player.team_set.all():
                # Update team status
                team.status = 'won'
                team.save()
    game_obj.save()
    return True

def change_players_state(game_obj, current_player, state):
    for player in game_obj.players.all():
        if player != current_player:
            player.state = state
            player.save()
    game_obj.save()   
            
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def GetHighScoreList(request):
    player = Player.objects.get(player_id=request.user.id)
    player_won_games_score = player.team_set.filter(status='won').order_by('games__score').values_list('games__score', flat=True)
    return Response(player_won_games_score, status=status.HTTP_200_OK)
    
class Move(APIView):
    permission_classes = (IsAuthenticated,)
    def get_object(self, pk):
        try:
            return Game.objects.get(pk=pk)
        except Game.DoesNotExist:
            raise Http404
        
    def get(self, request, *args, **kwargs):
        """
        To check game updates/status
        """
        current_player_id = request.user.id
        current_player = Player.objects.get(player_id=current_player_id)
        game_objs = current_player.game_set.all()
        serializer = GameSerializer(game_objs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        row = kwargs.get('row', None)
        column = kwargs.get('column', None)
        if not (row in range(0,3) and column in range(0,3)):
            return Response("Invalid value for row or column", status=status.HTTP_400_BAD_REQUEST)
        
        current_player_id = request.user.id
        current_player = Player.objects.get(player_id=current_player_id)
        try:
            active_game = current_player.game_set.get(status='start')
        except Game.DoesNotExist:
            return Response("Game is Finished", status=status.HTTP_400_BAD_REQUEST)
        
        # Player can move if the game status is started
        game_obj = self.get_object(active_game.id)
    
        # Player can move only if its status is ready and not waiting
        if current_player.state == 'ready':
            change_players_state(game_obj, current_player, 'wait')
            if play_your_turn(row, column, game_obj, current_player):
                current_player.state = 'wait'
                current_player.save()
                change_players_state(game_obj, current_player, 'ready')
                return Response("Successful Move by %s" %(request.user.username), status=status.HTTP_200_OK)
            else:
                return Response("Failed Move", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Please wait. Other player has to move", status=status.HTTP_400_BAD_REQUEST)