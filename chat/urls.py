from django.urls import path, re_path


from .views import ThreadView, InboxView

app_name = 'chat'
urlpatterns = [
    path("inbox/", InboxView.as_view()),
    path("messages/<str:username>", ThreadView.as_view(), name='messages'),
]
