from django.urls import path
from . import views
urlpatterns = [path("", views.home, name="home"), path("royxatdan-otish/", views.register, name="register"), path("royxatdan-otish/oqituvchi/", views.register, {"role": "teacher"}, name="teacher_register"), path("kirish/", views.user_login, name="login"), path("chiqish/", views.user_logout, name="logout"), path("kabinet/", views.dashboard, name="dashboard"), path("kurs/<str:slug>/", views.course_detail, name="course_detail"), path("kurs/<str:slug>/dars/<int:lesson_id>/test/", views.lesson_quiz, name="lesson_quiz")]
