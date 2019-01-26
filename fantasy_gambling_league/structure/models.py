from django.db import models

from fantasy_gambling_league.users.models import User


class Season(models.Model):
    commissioner = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
    )
    players = models.ManyToManyField(User, related_name='seasons')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    weekly_allowance = models.DecimalField(
        default=100.0,
        decimal_places=2,
        max_digits=99
    )

