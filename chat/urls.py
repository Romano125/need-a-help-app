from django.urls import path
from .views import ThreadView, InboxView


urlpatterns = [
    path("inbox/<int:pk>", InboxView.as_view(), name='inbox'),
    path("messages/<str:username>", ThreadView.as_view(), name='messages'),
]
