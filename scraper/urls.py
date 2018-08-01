from django.conf.urls import url
from .views import show_info

urlpatterns = [
	url(r'(?P<url>.*)/$', show_info, name='show_info')
]