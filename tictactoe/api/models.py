from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
import pickle
import base64
import numpy as np

class Player(models.Model):
    wait = 'wait'
    ready = 'ready'
    PLAYER_STATE = [
        (wait, 'Wait'),
        (ready, 'Ready')
    ]
    
    def validate_unique_symbol(value):
        qs = Player.objects.filter(symbol=value)
        if qs:
            raise ValidationError(
            _('This symbol %(value)s is taken by another player, Please choose another symbol.'),
            params={'value': value},
        )

    id = models.AutoField(primary_key=True)
    player_id = models.ForeignKey('auth.User', related_name='users', on_delete=models.CASCADE, default=None)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    state = models.CharField(max_length=5, choices=PLAYER_STATE, default=ready, editable=False)
    symbol = models.CharField(max_length=1, validators=[validate_unique_symbol])
    
    def __str__(self):
        return "{}, {}".format(self.id, self.player_id.username)
        
class Game(models.Model):
    game_started = 'start'
    game_finished = 'end'
    GAME_STATUS_OPTIONS= [
        (game_started, 'Game started'),
        (game_finished, 'Game finished')
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10, blank=False, null=False)
    board = models.BinaryField()
    status = models.CharField(max_length=5, choices=GAME_STATUS_OPTIONS, default=game_started, editable=False)
    players = models.ManyToManyField(Player, through='Team')
    count = models.IntegerField(default=0, editable=False)
    score = models.FloatField(default=0.0, editable=False)
    
    def __str__(self):
        return "{}, {}".format(self.id, self.name)
    
    def save(self, *args, **kwargs):
        if self.pk is None:
            # transform numpy array to python byte using pickle dumps, then encoded by base64
            np_array = np.empty((3,3), dtype = str)
            np_bytes = pickle.dumps(np_array)
            np_base64 = base64.b64encode(np_bytes)
            self.board = np_base64
        super(Game, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ['id', 'score']
        
class Team(models.Model):
    lost = 'lost'
    win = 'won'
    TEAM_STATUS = [
        (lost, 'Lost'),
        (win, 'Won')
    ]
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10, default='filewave', blank=False, null=False)
    num_of_players = models.PositiveIntegerField(default=1, verbose_name="Number of Player", validators=[MinValueValidator(1)])
    players = models.ForeignKey(Player, verbose_name="Team Players", on_delete=models.CASCADE)
    games = models.ForeignKey(Game, verbose_name="Team Games", on_delete=models.CASCADE)
    status = models.CharField(max_length=5, choices=TEAM_STATUS, default=lost, editable=False)
    
    def __str__(self):
        return self.name
    
    # def validate_unique_symbol
    # # We need to validate that player should be the part of one team at a time
    
