from django.contrib import admin
from django import forms
from .models import Category, Course, Lesson, LessonQuestion
admin.site.site_header = "DarsHub boshqaruv paneli"
admin.site.site_title = "DarsHub Admin"
admin.site.index_title = "Xush kelibsiz! Kurs va darslaringizni shu yerdan boshqaring."
admin.site.index_template = "admin/dashboard.html"

class LessonAdminForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = "__all__"
        widgets = {
            "video_file": forms.FileInput(attrs={"accept": "video/*", "class": "video-upload-input"}),
        }
        labels = {
            "title": "Dars sarlavhasi",
            "video_file": "Video faylni tanlang",
            "video_url": "Yoki video havolasini kiriting",
        }
        help_texts = {
            "title": "Darsning saytda ko‘rinadigan nomi. Masalan: Python’da o‘zgaruvchilar.",
            "video_file": "Kompyuterdan MP4/MOV video tanlang. Video pastdagi media/lessons/videos/ papkasiga yuklanadi.",
            "video_url": "Fayl yuklamoqchi bo‘lmasangiz, YouTube yoki Vimeo havolasini qo‘ying.",
        }

class LessonInline(admin.StackedInline):
    model = Lesson
    form = LessonAdminForm
    extra = 1
    fields = ("title", "description", "order", "duration", "video_file", "video_url", "published")
    verbose_name = "Dars"
    verbose_name_plural = "Kurs darslari — sarlavha va video shu yerda kiritiladi"
    help_texts = {
        "title": "Masalan: Python’da o‘zgaruvchilar bilan ishlash.",
        "video_file": "Kompyuterdan MP4 video tanlang. Fayl katta bo‘lsa, YouTube havolasidan foydalaning.",
        "video_url": "YouTube yoki Vimeo manzilini shu yerga qo‘ying. Fayl yoki havola — bittasini kiriting.",
    }

class LessonQuestionInline(admin.StackedInline):
    model = LessonQuestion
    extra = 10
    fields = ("order", "text", "image", ("option_a", "option_b"), ("option_c", "option_d"), "correct_option")
    verbose_name = "Test savoli"
    verbose_name_plural = "Darsdan keyingi test — 10 ta savol kiriting"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon")
    prepopulated_fields = {"slug": ("name",)}
    fields = ("name", "icon", "slug")
    help_texts = {"icon": "Yo‘nalish belgisi sifatida emoji kiriting. Masalan: 💻 yoki 🎨."}

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "level", "published")
    list_filter = ("category", "level", "published")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [LessonInline]
    fieldsets = (
        ("Kurs haqida", {"fields": ("title", "category", "description", "cover")} ),
        ("Daraja va davomiylik", {"fields": ("level", "duration")} ),
        ("Sayt sozlamalari", {"fields": ("slug", "published")} ),
    )
    help_texts = {
        "published": "Belgini olib tashlasangiz kurs saytda ko‘rinmaydi.",
        "cover": "Kurs kartasida ko‘rinadigan rasm. Tavsiya: gorizontal rasm.",
    }

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm
    list_display = ("title", "course", "order", "duration", "published")
    list_filter = ("course", "published")
    search_fields = ("title", "course__title")
    ordering = ("course", "order")
    inlines = [LessonQuestionInline]
    fieldsets = (
        ("Dars haqida", {"fields": ("course", "title", "description", "order", "duration")} ),
        ("Video", {"description": "Video faylni yuklang yoki YouTube/Vimeo havolasini kiriting. Ikkalasini bir vaqtda to‘ldirmang.", "fields": ("video_file", "video_url")} ),
        ("Sayt sozlamalari", {"fields": ("published",)} ),
    )
