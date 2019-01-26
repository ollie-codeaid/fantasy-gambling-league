from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.text import slugify

from .models import Season


class SeasonForm(ModelForm):
    class Meta:
        model = Season
        fields = ['name', 'weekly_allowance']

    def clean_name(self):
        slug = slugify(self.cleaned_data['name'])

        if Season.objects.filter(slug=slug).exists():
            raise ValidationError(
                'Name must not clash with existing seasons'
            )
        return self.cleaned_data['name']
