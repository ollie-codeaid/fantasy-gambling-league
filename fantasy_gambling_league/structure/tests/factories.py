from datetime import datetime
from pytz import utc

from factory import DjangoModelFactory, Faker, LazyFunction
from factory.fuzzy import FuzzyDateTime

from ..models import Season, Gameweek


class SeasonFactory(DjangoModelFactory):
    name = Faker('name')
    slug = Faker('slug')

    class Meta:
        model = Season


class GameweekFactory(DjangoModelFactory):
    deadline = FuzzyDateTime(
        start_dt=datetime.now(utc)
    )

    class Meta:
        model = Gameweek
