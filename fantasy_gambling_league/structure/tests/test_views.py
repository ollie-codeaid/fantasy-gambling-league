from datetime import datetime
from pytz import utc

from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from fantasy_gambling_league.users.tests.factories import UserFactory
from .factories import SeasonFactory, GameweekFactory
from ..models import Season, Gameweek


class TestCreateSeasonView(TestCase):
    url = reverse('structure:create-season')
    test_data = {
        'name': 'Test Season',
        'weekly_allowance': 1023.00,
    }

    def test_anonymous_user_redirected_on_get(self):
        response = self.client.get(self.url)

        assert response.status_code == 302
        assert 'login' in response.url

    def test_anonymous_user_redirected_on_post(self):
        response = self.client.post(self.url, data=self.test_data)

        assert response.status_code == 302
        assert 'login' in response.url
        assert Season.objects.count() == 0

    def test_successful_create(self):
        user = UserFactory()

        self.client.force_login(user)
        response = self.client.post(self.url, data=self.test_data)

        assert response.status_code == 302
        assert Season.objects.count() == 1
        season = Season.objects.first()

        assert season.name == self.test_data['name']
        assert season.weekly_allowance == self.test_data['weekly_allowance']
        assert season.commissioner == user
        assert season.slug == slugify(self.test_data['name'])

    def test_slug_unique_constraint(self):
        user = UserFactory()

        self.client.force_login(user)
        self.client.post(self.url, data=self.test_data)
        response = self.client.post(self.url, data=self.test_data)

        assert response.status_code == 200
        assert Season.objects.count() == 1
        form_errors = response.context['form'].errors

        assert 'Name must not clash with existing seasons' in form_errors['name']


class TestUpdateSeasonView(TestCase):
    test_data = {
        'name': 'Test Season',
        'weekly_allowance': 1023.00,
    }

    def setUp(self):
        self.user = UserFactory()
        self.season = SeasonFactory(commissioner=self.user)

    def get_url(self):
        return reverse(
            'structure:update-season', 
            kwargs={'slug': self.season.slug},
        )

    def test_anonymous_user_redirected_on_get(self):
        response = self.client.get(self.get_url())

        assert response.status_code == 302
        assert 'login' in response.url

    def test_anonymous_user_redirected_on_post(self):
        original_name = self.season.name
        original_weekly_allowance = self.season.weekly_allowance

        response = self.client.post(self.get_url(), data=self.test_data)

        assert response.status_code == 302
        assert 'login' in response.url
        self.season.refresh_from_db()

        assert self.season.name == original_name
        assert self.season.weekly_allowance == original_weekly_allowance

    def test_successful_update(self):
        self.client.force_login(self.user)
        response = self.client.post(self.get_url(), data=self.test_data)

        assert response.status_code == 302
        assert Season.objects.count() == 1
        season = Season.objects.first()

        assert season.name == self.test_data['name']
        assert season.weekly_allowance == self.test_data['weekly_allowance']
        assert season.slug == slugify(self.test_data['name'])

    def test_slug_unique_constraint(self):
        SeasonFactory(slug=slugify(self.test_data['name']))

        self.client.force_login(self.user)
        response = self.client.post(self.get_url(), data=self.test_data)

        assert response.status_code == 200
        form_errors = response.context['form'].errors

        assert 'Name must not clash with existing seasons' in form_errors['name']

    def test_non_commissioner_redirected_on_get(self):
        user = UserFactory()

        self.client.force_login(user)
        response = self.client.get(self.get_url())

        assert response.status_code == 302
        assert 'login' in response.url

    def test_non_commissioner_user_redirected_on_post(self):
        original_name = self.season.name
        original_weekly_allowance = self.season.weekly_allowance

        user = UserFactory()
        self.client.force_login(user)
        response = self.client.post(self.get_url(), data=self.test_data)

        assert response.status_code == 302
        assert 'login' in response.url
        self.season.refresh_from_db()

        assert self.season.name == original_name
        assert self.season.weekly_allowance == original_weekly_allowance


class TestDeleteSeasonView(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.season = SeasonFactory(commissioner=self.user)

    def get_url(self):
        return reverse(
            'structure:delete-season', 
            kwargs={'slug': self.season.slug},
        )

    def test_anonymous_user_redirected_on_get(self):
        response = self.client.get(self.get_url())

        assert response.status_code == 302
        assert 'login' in response.url

    def test_anonymous_user_redirected_on_post(self):
        response = self.client.post(self.get_url())

        assert response.status_code == 302
        assert 'login' in response.url
        assert Season.objects.count() == 1

    def test_successful_delete(self):
        self.client.force_login(self.user)
        response = self.client.post(self.get_url())

        assert response.status_code == 302
        assert Season.objects.count() == 0

    def test_non_commissioner_redirected_on_get(self):
        user = UserFactory()

        self.client.force_login(user)
        response = self.client.get(self.get_url())

        assert response.status_code == 302
        assert 'login' in response.url

    def test_non_commissioner_user_redirected_on_post(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.post(self.get_url())

        assert response.status_code == 302
        assert 'login' in response.url
        assert Season.objects.count() == 1


class TestSeasonListView(TestCase):
    def setUp(self):
        self.url = reverse('structure:list-seasons')
        self.seasons = SeasonFactory.create_batch(8)

    def test_anonymous_user_can_view_all_seasons(self):
        response = self.client.get(self.url)

        assert response.status_code == 200

        for season in self.seasons:
            assert season in response.context['object_list']


class TestSeasonDetailView(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.season = SeasonFactory(commissioner=self.user)

    def get_url(self):
        return reverse(
            'structure:detail-season', 
            kwargs={'slug': self.season.slug},
        )

    def test_anonymous_user_can_view_season_detail(self):
        response = self.client.get(self.get_url())

        assert response.status_code == 200

    def test_logged_in_user_can_view_season_detail(self):
        user = UserFactory()
        
        self.client.force_login(user)
        response = self.client.get(self.get_url())

        assert response.status_code == 200


class TestCreateGameweekView(TestCase):
    test_data = {
        'spiel': 'Some commentary',
        'deadline': datetime.now(),
    }

    def setUp(self):
        self.user = UserFactory()
        self.season = SeasonFactory(commissioner=self.user)

    def get_url(self):
        return reverse(
            'structure:create-gameweek', 
            kwargs={'season_slug': self.season.slug},
        )

    def test_anonymous_user_redirected_on_get(self):
        response = self.client.get(self.get_url())

        assert response.status_code == 302
        assert 'login' in response.url

    def test_anonymous_user_redirected_on_post(self):
        response = self.client.post(self.get_url(), data=self.test_data)

        assert response.status_code == 302
        assert 'login' in response.url
        assert Gameweek.objects.count() == 0

    def test_successful_create(self):
        self.client.force_login(self.user)
        response = self.client.post(self.get_url(), data=self.test_data)

        assert response.status_code == 302
        assert Gameweek.objects.count() == 1
        gameweek = Gameweek.objects.first()

        assert gameweek.season == self.season
        assert gameweek.number == 1
        assert gameweek.spiel == self.test_data['spiel']
        assert gameweek.deadline == self.test_data['deadline'].replace(tzinfo=utc)

    def test_number_incremented(self):
        self.client.force_login(self.user)
        self.client.post(self.get_url(), data={
            'spiel': 'One',
            'deadline': datetime.now(),
        })
        self.client.post(self.get_url(), data={
            'spiel': 'Two',
            'deadline': datetime.now(),
        })
        self.client.post(self.get_url(), data={
            'spiel': 'Three',
            'deadline': datetime.now(),
        })

        assert Gameweek.objects.count() == 3
        assert Gameweek.objects.get(spiel='One').number == 1
        assert Gameweek.objects.get(spiel='Two').number == 2
        assert Gameweek.objects.get(spiel='Three').number == 3

    def test_non_commissioner_redirected_on_get(self):
        user = UserFactory()

        self.client.force_login(user)
        response = self.client.get(self.get_url())

        assert response.status_code == 302
        assert 'login' in response.url

    def test_non_commissioner_user_redirected_on_post(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.post(self.get_url(), data=self.test_data)

        assert response.status_code == 302
        assert 'login' in response.url
        assert Gameweek.objects.count() == 0


class TestUpdateGameweekView(TestCase):
    test_data = {
        'spiel': 'Some commentary',
        'deadline': datetime.now(),
    }

    def setUp(self):
        self.user = UserFactory()
        self.season = SeasonFactory(commissioner=self.user)
        self.gameweek = GameweekFactory(
            season=self.season,
            number=1,
        )

    def get_url(self):
        return reverse(
            'structure:update-gameweek', 
            kwargs={
                'season_slug': self.season.slug,
                'number': self.gameweek.number,
            },
        )

    def test_anonymous_user_redirected_on_get(self):
        response = self.client.get(self.get_url())

        assert response.status_code == 302
        assert 'login' in response.url

    def test_anonymous_user_redirected_on_post(self):
        response = self.client.post(self.get_url(), data=self.test_data)

        assert response.status_code == 302
        assert 'login' in response.url

    def test_successful_update(self):
        self.client.force_login(self.user)
        response = self.client.post(self.get_url(), data=self.test_data)

        assert response.status_code == 302
        assert Gameweek.objects.count() == 1
        gameweek = Gameweek.objects.first()

        assert gameweek.season == self.season
        assert gameweek.number == 1
        assert gameweek.spiel == self.test_data['spiel']
        assert gameweek.deadline == self.test_data['deadline'].replace(tzinfo=utc)

    def test_non_commissioner_redirected_on_get(self):
        user = UserFactory()

        self.client.force_login(user)
        response = self.client.get(self.get_url())

        assert response.status_code == 302
        assert 'login' in response.url

    def test_non_commissioner_user_redirected_on_post(self):
        original_spiel = self.gameweek.spiel
        original_deadline = self.gameweek.deadline

        user = UserFactory()
        self.client.force_login(user)
        response = self.client.post(self.get_url(), data=self.test_data)

        assert response.status_code == 302
        assert 'login' in response.url
        self.gameweek.refresh_from_db()

        assert self.gameweek.spiel == original_spiel
        assert self.gameweek.deadline == original_deadline

    def test_update_not_possible_if_gameweek_not_latest(self):
        gameweek = GameweekFactory(
            season=self.season,
            number=2,
        )

        original_spiel = self.gameweek.spiel
        original_deadline = self.gameweek.deadline

        self.client.force_login(self.user)
        response = self.client.post(self.get_url(), data=self.test_data)

        assert response.status_code == 302
        self.gameweek.refresh_from_db()

        assert self.gameweek.spiel == original_spiel
        assert self.gameweek.deadline == original_deadline


class TestDeleteGameweekView(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.season = SeasonFactory(commissioner=self.user)
        self.gameweek = GameweekFactory(
            season=self.season,
            number=1,
        )

    def get_url(self):
        return reverse(
            'structure:delete-gameweek', 
            kwargs={
                'season_slug': self.season.slug,
                'number': self.gameweek.number,
            },
        )

    def test_anonymous_user_redirected_on_get(self):
        response = self.client.get(self.get_url())

        assert response.status_code == 302
        assert 'login' in response.url

    def test_anonymous_user_redirected_on_post(self):
        response = self.client.post(self.get_url())

        assert response.status_code == 302
        assert 'login' in response.url
        assert Gameweek.objects.count() == 1

    def test_successful_delete(self):
        self.client.force_login(self.user)
        response = self.client.post(self.get_url())

        assert response.status_code == 302
        assert Gameweek.objects.count() == 0

    def test_non_commissioner_redirected_on_get(self):
        user = UserFactory()

        self.client.force_login(user)
        response = self.client.get(self.get_url())

        assert response.status_code == 302
        assert 'login' in response.url

    def test_non_commissioner_user_redirected_on_post(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.post(self.get_url())

        assert response.status_code == 302
        assert 'login' in response.url
        assert Gameweek.objects.count() == 1

    def test_delete_not_possible_if_gameweek_not_latest(self):
        gameweek = GameweekFactory(
            season=self.season,
            number=2,
        )

        self.client.force_login(self.user)
        response = self.client.post(self.get_url())

        assert response.status_code == 302
        assert Gameweek.objects.count() == 2


class TestGameweekDetailView(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.season = SeasonFactory(commissioner=self.user)
        self.gameweek = GameweekFactory(
            season=self.season,
            number=1,
        )

    def get_url(self):
        return reverse(
            'structure:detail-gameweek', 
            kwargs={
                'season_slug': self.season.slug,
                'number': self.gameweek.number,
            },
        )

    def test_anonymous_user_can_view_season_detail(self):
        response = self.client.get(self.get_url())

        assert response.status_code == 200

    def test_logged_in_user_can_view_season_detail(self):
        user = UserFactory()
        
        self.client.force_login(user)
        response = self.client.get(self.get_url())

        assert response.status_code == 200

