from django.urls import path, include

urlpatterns = [
    path('', include('app.urls')),  #Incluye las URLs de la app
]