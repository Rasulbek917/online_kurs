from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django import forms
import re
from .models import Category, Course, Lesson, LessonQuestion
from .models import UserProfile

class LessonCreateForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ("course", "title", "description", "order", "duration", "video_file", "video_url", "published")
        widgets = {"video_file": forms.FileInput(attrs={"accept": "video/*"}), "description": forms.Textarea(attrs={"rows": 4})}

def register(request, role="student"):
    if request.user.is_authenticated: return redirect("dashboard")
    if role not in {"student", "teacher"}: role = "student"
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        phone_number = request.POST.get("phone_number", "").strip()
        digits = re.sub(r"\D", "", phone_number)
        if not username or len(password) < 6:
            error = "Ma’lumotlarni to‘g‘ri kiriting. Parol kamida 6 ta belgidan iborat bo‘lsin."
        elif not re.fullmatch(r"[+\d()\-\s]{7,24}", phone_number) or len(digits) < 7:
            error = "Telefon raqamini to‘g‘ri kiriting."
        elif User.objects.filter(username=username).exists(): error = "Bu foydalanuvchi nomi band."
        else:
            user = User.objects.create_user(username=username, password=password)
            UserProfile.objects.create(user=user, role=role, phone_number=phone_number)
            login(request, user)
            return redirect("dashboard")
    return render(request, "academy/register.html", {"error": error, "role": role})

def user_login(request):
    error = ""
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username", "").strip(), password=request.POST.get("password", ""))
        if user:
            login(request, user)
            return redirect("dashboard")
        error = "Foydalanuvchi nomi yoki parol noto‘g‘ri."
    return render(request, "academy/login.html", {"error": error})

def user_logout(request):
    logout(request)
    return redirect("home")

@login_required
def dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST" and profile.role == "teacher":
        form = LessonCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Dars muvaffaqiyatli qo‘shildi.")
            return redirect("dashboard")
    else: form = LessonCreateForm()
    return render(request, "academy/dashboard.html", {"profile": profile, "form": form})

def _completed_lessons(request, course):
    return set(request.session.get(f"completed_lessons_{course.pk}", []))

def _lesson_unlocked(lessons, lesson, completed):
    # For ties in the configured order, the preceding lesson is also a prerequisite.
    previous = [item for item in lessons.order_by("order", "id") if (item.order, item.pk) < (lesson.order, lesson.pk)]
    return not previous or str(previous[-1].pk) in completed

def home(request):
    if not request.user.is_authenticated:
        return render(request, "academy/welcome.html")
    courses = Course.objects.filter(published=True).select_related("category").annotate(total_lessons=Count("lessons", filter=Q(lessons__published=True)))
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    if query: courses = courses.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query))
    if category: courses = courses.filter(category__slug=category)
    categories = Category.objects.annotate(course_count=Count("courses", filter=Q(courses__published=True)))
    featured = Course.objects.filter(published=True).select_related("category").first()
    return render(request, "academy/home.html", {"courses":courses, "categories":categories, "query":query, "active_category":category, "featured":featured})

@login_required(login_url="login")
def course_detail(request, slug):
    course = get_object_or_404(Course.objects.select_related("category"), slug=slug, published=True)
    lessons = course.lessons.filter(published=True)
    completed = _completed_lessons(request, course)
    available = [lesson for lesson in lessons.order_by("order", "id") if _lesson_unlocked(lessons, lesson, completed)]
    requested = lessons.filter(pk=request.GET.get("lesson")).first() if request.GET.get("lesson", "").isdigit() else None
    active_lesson = requested if requested in available else (available[0] if available else None)
    return render(request, "academy/course_detail.html", {"course":course, "lessons":lessons, "active_lesson":active_lesson, "completed_lessons":completed, "unlocked_ids":{item.pk for item in available}})

@login_required(login_url="login")
def lesson_quiz(request, slug, lesson_id):
    course = get_object_or_404(Course, slug=slug, published=True)
    lessons = course.lessons.filter(published=True).order_by("order", "id")
    lesson = get_object_or_404(lessons, pk=lesson_id)
    completed = _completed_lessons(request, course)
    if not _lesson_unlocked(lessons, lesson, completed):
        return redirect(f"{course.get_absolute_url()}?lesson={lesson_id}")
    questions = list(lesson.questions.all())
    score = None
    passed = False
    error = ""
    if request.method == "POST":
        if len(questions) != 10:
            error = "Testni boshlash uchun admin panelda ushbu darsga aynan 10 ta savol kiriting."
        elif any(request.POST.get(f"question_{q.pk}") not in {"a", "b", "c", "d"} for q in questions):
            error = "Iltimos, barcha 10 ta savolga javob belgilang."
        else:
            score = sum(request.POST.get(f"question_{q.pk}") == q.correct_option for q in questions)
            passed = score >= 7
            if passed:
                completed.add(str(lesson.pk))
                request.session[f"completed_lessons_{course.pk}"] = sorted(completed)
                request.session.modified = True
    return render(request, "academy/quiz.html", {"course": course, "lesson": lesson, "questions": questions, "score": score, "passed": passed, "error": error, "completed_lessons": completed})
