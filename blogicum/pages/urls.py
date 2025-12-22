from django.urls import path
from .views import IndexPage, AboutPage, RulesPage

app_name = 'pages'

urlpatterns = [
    # Статические страницы
    path('welcome/', IndexPage.as_view(), name='welcome'),
    path('about/', AboutPage.as_view(), name='about'),
    path('rules/', RulesPage.as_view(), name='rules'),
]
