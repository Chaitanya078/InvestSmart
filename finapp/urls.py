from django.urls import path,include
from finapp import views
from django.contrib import admin

urlpatterns = [
  path('',views.index,name='index')
]