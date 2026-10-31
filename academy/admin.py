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
    extra = 0
    show_change_link = True
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
    extra = 1
    max_num = 10
    fields = ("order", "text", "image", ("option_a", "option_b"), ("option_c", "option_d"), "correct_option")
    verbose_name = "Test savoli"
    verbose_name_plural = "Darsdan keyingi test — 10 ta savol kiriting"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    fields = ("name", "icon", "slug")
    help_texts = {"icon": "Yo‘nalish belgisi sifatida emoji kiriting. Masalan: 💻 yoki 🎨."}

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "level", "published")
    list_editable = ("published",)
    list_select_related = ("category",)
    autocomplete_fields = ("category",)
    list_per_page = 25
    save_on_top = True
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
    list_display = ("title", "course", "order", "duration", "test_status", "published")
    list_editable = ("order", "published")
    list_select_related = ("course",)
    autocomplete_fields = ("course",)
    list_per_page = 25
    save_on_top = True

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(question_total=Count("questions"))

    @admin.display(description="Test tayyorligi")
    def test_status(self, obj):
        return f"{obj.question_total}/10 — " + ("Tayyor" if obj.question_total == 10 else "To‘ldirish kerak")

    list_filter = ("course", "published")
    search_fields = ("title", "course__title")
    ordering = ("course", "order")
    inlines = [LessonQuestionInline]
    fieldsets = (
        ("Dars haqida", {"fields": ("course", "title", "description", "order", "duration")} ),
        ("Video", {"description": "Video faylni yuklang yoki YouTube/Vimeo havolasini kiriting. Ikkalasini bir vaqtda to‘ldirmang.", "fields": ("video_file", "video_url")} ),
        ("Sayt sozlamalari", {"fields": ("published",)} ),
    )

from django.db.models import Count
from .models import UserProfile, LessonProgress

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone_number")
    list_filter = ("role",)
    search_fields = ("user__username", "phone_number")
    autocomplete_fields = ("user",)
    list_select_related = ("user",)

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "completed_at")
    search_fields = ("user__username", "lesson__title")
    list_filter = ("lesson__course", "completed_at")
    list_select_related = ("user", "lesson", "lesson__course")
    readonly_fields = ("completed_at",)
    autocomplete_fields = ("user", "lesson")
