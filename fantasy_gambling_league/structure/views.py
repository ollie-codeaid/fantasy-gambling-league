from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, reverse
from django.utils.text import slugify
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    UpdateView,
)
from django.views.generic.list import ListView

from .forms import SeasonForm
from .models import Season, Gameweek


class CommissionerRequiredMixin:
    def get_commissioner(self):
        raise NotImplementedError()

    def dispatch(self, request, *args, **kwargs):
        commissioner = self.get_commissioner()

        if request.user == commissioner:
            return super().dispatch(request, *args, **kwargs)

        return self.handle_no_permission()


class SeasonCommissionerRequiredMixin(CommissionerRequiredMixin):
    def get_commissioner(self):
        return self.get_object().commissioner


class SeasonCreateView(LoginRequiredMixin, CreateView):
    login_url = '/accounts/login'
    success_url = '/'
    model = Season
    form_class = SeasonForm

    def form_valid(self, form):
        form.instance.commissioner = self.request.user
        form.instance.slug = slugify(
            form.cleaned_data['name']
        )
        return super(SeasonCreateView, self).form_valid(form)


class SeasonUpdateView(LoginRequiredMixin, SeasonCommissionerRequiredMixin, UpdateView):
    login_url = '/accounts/login'
    success_url = '/'
    model = Season
    form_class = SeasonForm

    def form_valid(self, form):
        form.instance.slug = slugify(
            form.cleaned_data['name']
        )
        return super(SeasonUpdateView, self).form_valid(form)


class SeasonDeleteView(LoginRequiredMixin, SeasonCommissionerRequiredMixin, DeleteView):
    login_url = '/accounts/login'
    success_url = '/'
    model = Season

class SeasonListView(ListView):
    model = Season


class SeasonDetailView(DetailView):
    model = Season


class GameweekCommissionerRequiredMixin(CommissionerRequiredMixin):
    def get_commissioner(self):
        season_slug = self.kwargs['season_slug']
        season = get_object_or_404(Season, slug=season_slug)

        return season.commissioner


class GameweekCreateView(LoginRequiredMixin, GameweekCommissionerRequiredMixin, CreateView):
    login_url = '/accounts/login'
    success_url = '/'
    model = Gameweek
    fields = ['deadline', 'spiel', ]

    def get_context_data(self, **kwargs):
        season_slug = self.kwargs['season_slug']

        context_data = super(GameweekCreateView, self).get_context_data(**kwargs)
        context_data.update({'season_slug': season_slug})

        return context_data

    def form_valid(self, form):
        season_slug = self.kwargs['season_slug']
        season = get_object_or_404(Season, slug=season_slug)

        form.instance.season = season
        form.instance.number = season.gameweek_set.count() + 1
        return super(GameweekCreateView, self).form_valid(form)


class GameweekUpdateView(LoginRequiredMixin, GameweekCommissionerRequiredMixin, UpdateView):
    login_url = '/accounts/login'
    success_url = '/'
    model = Gameweek
    fields = ['deadline', 'spiel', ]

    def get_object(self, queryset=None):
        season_slug = self.kwargs['season_slug']
        season = get_object_or_404(Season, slug=season_slug)

        if not queryset:
            queryset = self.get_queryset()
        
        return queryset.get(
            season=season,
            number=self.kwargs['number'],
        )

    def dispatch(self, request, *args, **kwargs):
        gameweek = self.get_object()
        if gameweek.number == gameweek.season.gameweek_set.count():
            return super().dispatch(request, *args, **kwargs)

        messages.error(request, 'Cannot edit Gameweek that is not latest')

        return HttpResponseRedirect(
            redirect_to=reverse(
                'structure:detail-season',
                kwargs={'slug': gameweek.season.slug}
            ),
        )


class GameweekDeleteView(LoginRequiredMixin, GameweekCommissionerRequiredMixin, DeleteView):
    login_url = '/accounts/login'
    success_url = '/'
    model = Gameweek

    def get_object(self, queryset=None):
        season_slug = self.kwargs['season_slug']
        season = get_object_or_404(Season, slug=season_slug)

        if not queryset:
            queryset = self.get_queryset()
        
        return queryset.get(
            season=season,
            number=self.kwargs['number'],
        )

    def dispatch(self, request, *args, **kwargs):
        gameweek = self.get_object()
        if gameweek.number == gameweek.season.gameweek_set.count():
            return super().dispatch(request, *args, **kwargs)

        messages.error(request, 'Cannot edit Gameweek that is not latest')

        return HttpResponseRedirect(
            redirect_to=reverse(
                'structure:detail-season',
                kwargs={'slug': gameweek.season.slug}
            ),
        )

class GameweekDetailView(DetailView):
    model = Gameweek

    def get_object(self, queryset=None):
        season_slug = self.kwargs['season_slug']
        season = get_object_or_404(Season, slug=season_slug)

        if not queryset:
            queryset = self.get_queryset()
        
        return queryset.get(
            season=season,
            number=self.kwargs['number'],
        )
