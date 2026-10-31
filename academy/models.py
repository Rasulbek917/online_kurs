from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify

class UserProfile(models.Model):
    ROLE_CHOICES = [("student", "O‘quvchi"), ("teacher", "O‘qituvchi")]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField("Hisob turi", max_length=10, choices=ROLE_CHOICES, default="student")
    phone_number = models.CharField("Telefon raqami", max_length=24, blank=True, default="")
    def __str__(self): return f"{self.user.username} — {self.get_role_display()}"

class Category(models.Model):
    name = models.CharField("Nomi", max_length=80, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField("Ikonka (emoji)", max_length=8, default="✦")
    class Meta:
        verbose_name = "Yo‘nalish"
        verbose_name_plural = "Yo‘nalishlar"
        ordering = ["name"]
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    def __str__(self): return self.name

class Course(models.Model):
    title = models.CharField("Kurs nomi", max_length=180)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="courses", verbose_name="Yo‘nalish")
    description = models.TextField("Qisqacha tavsif")
    cover = models.ImageField("Kurs rasmi", upload_to="courses/", blank=True, null=True)
    level = models.CharField("Daraja", max_length=40, default="Boshlang‘ich")
    duration = models.CharField("Davomiyligi", max_length=40, default="6 hafta")
    published = models.BooleanField("Saytda ko‘rsatish", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"
        ordering = ["-created_at"]
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)
    def __str__(self): return self.title
    def get_absolute_url(self): return reverse("course_detail", args=[self.slug])
    @property
    def lesson_count(self): return self.lessons.count()

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Kurs")
    title = models.CharField("Dars nomi", max_length=180)
    description = models.TextField("Dars haqida", blank=True)
    video_file = models.FileField("Video fayl", upload_to="lessons/videos/", blank=True, null=True, help_text="MP4 video yuklang yoki pastdagi havolani kiriting.")
    video_url = models.URLField("Video havolasi", blank=True, help_text="YouTube yoki Vimeo havolasi")
    order = models.PositiveIntegerField("Dars tartibi", default=1)
    duration = models.CharField("Davomiyligi", max_length=30, blank=True)
    published = models.BooleanField("Saytda ko‘rsatish", default=True)
    class Meta:
        verbose_name = "Dars"
        verbose_name_plural = "Darslar"
        ordering = ["order", "id"]
    def __str__(self): return f"{self.course.title} — {self.title}"
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.video_file and self.video_url:
            raise ValidationError({"video_url": "Video fayl yoki havoladan faqat bittasini kiriting."})

    @property
    def embed_url(self):
        url = self.video_url
        if "youtu.be/" in url: return "https://www.youtube-nocookie.com/embed/" + url.split("youtu.be/")[-1].split("?")[0]
        if "youtube.com/watch" in url:
            from urllib.parse import urlparse, parse_qs
            vid = parse_qs(urlparse(url).query).get("v", [""])[0]
            return "https://www.youtube-nocookie.com/embed/" + vid if vid else ""
        if "youtube.com/embed/" in url: return url.replace("youtube.com", "youtube-nocookie.com")
        if "vimeo.com/" in url and "player.vimeo.com" not in url:
            return "https://player.vimeo.com/video/" + url.rstrip("/").split("/")[-1]
        return url

class LessonQuestion(models.Model):
    OPTION_CHOICES = [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")]
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="questions", verbose_name="Dars")
    text = models.CharField("Savol", max_length=500)
    image = models.ImageField("Savol rasmi", upload_to="questions/", blank=True, null=True, help_text="Savolga tegishli rasmni ixtiyoriy yuklang.")
    option_a = models.CharField("A javobi", max_length=300)
    option_b = models.CharField("B javobi", max_length=300)
    option_c = models.CharField("C javobi", max_length=300)
    option_d = models.CharField("D javobi", max_length=300)
    correct_option = models.CharField("To‘g‘ri javob", max_length=1, choices=OPTION_CHOICES)
    order = models.PositiveIntegerField("Tartib", default=1)

    class Meta:
        verbose_name = "Test savoli"
        verbose_name_plural = "Test savollari"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.lesson.title}: {self.text[:60]}"


class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "lesson"], name="unique_user_lesson_progress")]
