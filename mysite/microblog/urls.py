from django.urls import path
from . import views

app_name = 'microblog'
urlpatterns = [
    path('index/', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('user/<str:username>', views.user, name='user'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('follow/<str:username>', views.follow, name='follow'),
    path('unfollow/<str:username>', views.unfollow, name='unfollow'),
    path('explore/', views.explore, name='explore')
]
