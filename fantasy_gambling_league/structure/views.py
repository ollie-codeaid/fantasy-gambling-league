from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils.text import slugify
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    UpdateView,
)
from django.views.generic.list import ListView

from .forms import SeasonForm
from .models import Season


class CommissionerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        season = self.get_object()
        if request.user == season.commissioner:
            return super().dispatch(request, *args, **kwargs)

        return self.handle_no_permission()


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


class SeasonUpdateView(LoginRequiredMixin, CommissionerRequiredMixin, UpdateView):
    login_url = '/accounts/login'
    success_url = '/'
    model = Season
    form_class = SeasonForm

    def form_valid(self, form):
        form.instance.slug = slugify(
            form.cleaned_data['name']
        )
        return super(SeasonUpdateView, self).form_valid(form)


class SeasonDeleteView(LoginRequiredMixin, CommissionerRequiredMixin, DeleteView):
    login_url = '/accounts/login'
    success_url = '/'
    model = Season


class SeasonListView(ListView):
    model = Season


class SeasonDetailView(DetailView):
    model = Season

