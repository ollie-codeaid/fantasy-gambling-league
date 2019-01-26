from factory import DjangoModelFactory, Faker

from ..models import Season


class SeasonFactory(DjangoModelFactory):
    name = Faker('name')
    slug = Faker('slug')

    class Meta:
        model = Season

