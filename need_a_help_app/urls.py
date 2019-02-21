from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('main', views.AppMainView.as_view(), name='main'),
    path('repairman_info/<int:pk>/', views.RepairmanDetailView.as_view(), name='repairman_info'),
    path('add_favorite/<int:user_id>/<int:rep_id>/', views.add_favorite, name='add_favorite'),
    path('del_favorite/<int:user_id>/<int:rep_id>/', views.del_favorite, name='del_favorite'),
    path('favorites/', views.show_favs, name='favorites'),
    path('requests_user/<int:pk>', views.RequestsView.as_view(), name='requests_user'),
    path('add_request/', views.RequestCreateView.as_view(), name='add_request'),
    path('request/<int:pk>/', views.RequestDetailView.as_view(), name='request_detail'),
    path('request/<int:pk>/update/', views.RequestUpdateView.as_view(), name='request_update'),
]
