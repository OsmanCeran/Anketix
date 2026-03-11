from django.urls import path
from . import views

app_name = "anketix"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("grafikler/", views.GrafiklerView.as_view(), name="grafikler"),
    path("anket-ekle/", views.anket_ekle, name="anket_ekle"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:soru_id>/vote/", views.vote, name="vote"),
]
