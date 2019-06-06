import django_filters
from chat.models import Thread

class InboxFilter(django_filters.FilterSet):

	class Meta:
		model = Thread
		fields = {
			'names' : ['icontains'],
		}