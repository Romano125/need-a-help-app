from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('main', views.AppMainView.as_view(), name='main'),
    path('repairman_info/<int:pk>/', views.RepairmanDetailView.as_view(), name='repairman_info'),
    path('settings/<int:pk>/', views.UpdateUserView.as_view(), name='settings'),
    path('add_favorite/<int:user_id>/<int:rep_id>/', views.add_favorite, name='add_favorite'),
    path('del_favorite/<int:user_id>/<int:rep_id>/', views.del_favorite, name='del_favorite'),
    path('favorites/', views.show_favs, name='favorites'),
    path('requests_user/<int:user_id>', views.RequestsView.as_view(), name='requests_user'),
    path('add_request/', views.RequestCreateView.as_view(), name='add_request'),
]
