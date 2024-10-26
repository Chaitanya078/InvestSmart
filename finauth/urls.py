from django.urls import path
from .views import signup, handlelogin, handlelogout, ActivateAccountView

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', handlelogin, name='login'),  # Ensure this line exists
    path('logout/', handlelogout, name='logout'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),
]
