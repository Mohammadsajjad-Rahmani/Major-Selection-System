from django.urls import path, include

from Main import views

urlpatterns = [
    path('', views.home, name='home'),
    path('analyze', views.analyze, name='analyze'),
]
