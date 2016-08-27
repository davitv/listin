from django.conf.urls import url

from . import views

app_name = 'market'
urlpatterns = [
    url(r'^$', views.HomePageView.as_view(), name='index'),
]
