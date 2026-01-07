from django.urls import path
from .views import signup,login_view,rewards_view,upload,dashboard,upload_cleaned,green_expert_api
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('rewards/', rewards_view, name='rewards'),
    path('upload/', upload, name='upload'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('upload-cleaned/<int:image_id>/',upload_cleaned, name='upload_cleaned'),
    path('chatbot/', green_expert_api, name='chatbot_page')
    

]
