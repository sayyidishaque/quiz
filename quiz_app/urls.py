from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', views.logout_view, name='logout'),
    path('add_question/', views.add_question, name='add_question'),
    path('register/', views.register, name='register'),
    path('load_questions/', views.load_questions, name='load_questions'),
    path('quiz_result/<int:score>/', views.quiz_results, name='quiz_results'),  # Include the dynamic score parameter
]
