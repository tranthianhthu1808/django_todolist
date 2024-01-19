from django.urls import path
from . import views 

urlpatterns = [
    path('', views.index, name='index'),
    path('delete/<str:pk>', views.delete,name='delete'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name="register"),
    # path('logout/', views.logout_page, name="logout"),
    # path('profile/<username>', views.profile, name='profile'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    # path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path("password_change", views.password_change, name="password_change"),
    path("password_reset", views.password_reset_request, name="password_reset"),
    path('reset/<uidb64>/<token>', views.passwordResetConfirm, name='password_reset_confirm'),
]
