import django_filters
from user.models import Profile


class MostWantedFilter(django_filters.FilterSet):

    CHOICES = (
        ('ascending', 'Ascending'),
        ('descending', 'Descending')
    )

    rating = django_filters.ChoiceFilter(label='Rating', choices=CHOICES, method='filter_by_order_rating')

    num_hired = django_filters.ChoiceFilter(label='Times hired', choices=CHOICES, method='filter_by_order_hired')

    class Meta:
        model = Profile
        fields = {
            'costs': ['lt'],
            'profession': ['exact'],

        }

    def filter_by_order_rating(self, queryset, name, value):
        exp_rat = 'rating' if value == 'ascending' else '-rating'
        return queryset.order_by(exp_rat)

    def filter_by_order_hired(self, queryset, name, value):
        exp_hir = 'hired' if value == 'ascending' else '-hired'
        return queryset.order_by(exp_hir)


class TopRatedFilter(django_filters.FilterSet):

    CHOICES = (
        ('ascending', 'Ascending'),
        ('descending', 'Descending')
    )

    rating = django_filters.ChoiceFilter(label='Rating', choices=CHOICES, method='filter_by_order_rating')

    num_hired = django_filters.ChoiceFilter(label='Times hired', choices=CHOICES, method='filter_by_order_hired')

    class Meta:
        model = Profile
        fields = {
            'costs': ['lt'],
            'profession': ['exact'],

        }

    def filter_by_order_rating(self, queryset, name, value):
        exp_rat = 'rating' if value == 'ascending' else '-rating'
        return queryset.order_by(exp_rat)

    def filter_by_order_hired(self, queryset, name, value):
        exp_hir = 'hired' if value == 'ascending' else '-hired'
        return queryset.order_by(exp_hir)
