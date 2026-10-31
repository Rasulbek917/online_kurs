import os
from types import SimpleNamespace
from unittest.mock import patch
from django.test import TestCase
from django.test import SimpleTestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Category, Course, Lesson, LessonQuestion, LessonProgress, UserProfile
from .storage_backends import VercelBlobStorage


class VercelBlobStorageTests(SimpleTestCase):
    @patch("academy.storage_backends.blob.put_blob")
    def test_saves_with_public_blob_and_returns_path(self, put_blob):
        put_blob.side_effect = lambda name, *args, **kwargs: SimpleNamespace(pathname=name)
        storage = VercelBlobStorage()
        upload = SimpleUploadedFile("lesson.mp4", b"video", content_type="video/mp4")

        name = storage.save("lessons/videos/lesson.mp4", upload)

        self.assertRegex(name, r"^lessons/videos/lesson_[a-zA-Z0-9]{8}\.mp4$")
        put_blob.assert_called_once()
        self.assertEqual(put_blob.call_args.kwargs["access"], "public")
        self.assertEqual(put_blob.call_args.kwargs["content_type"], "video/mp4")

    @patch.dict(os.environ, {"BLOB_STORE_ID": "store_test"})
    def test_builds_public_blob_url(self):
        storage = VercelBlobStorage()
        self.assertEqual(
            storage.url("lessons/videos/lesson one.mp4"),
            "https://store_test.public.blob.vercel-storage.com/lessons/videos/lesson%20one.mp4",
        )


class PlatformTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('student', password='test-password')
        self.category = Category.objects.get_or_create(name='Backend')[0]
        self.course = Course.objects.create(title='Python', category=self.category, description='Test')
        self.first = Lesson.objects.create(course=self.course, title='First', order=1)
        self.second = Lesson.objects.create(course=self.course, title='Second', order=2)
        for i in range(10):
            LessonQuestion.objects.create(lesson=self.first, text=str(i), option_a='A', option_b='B', option_c='C', option_d='D', correct_option='a', order=i)

    def test_public_pages_and_login_redirect(self):
        for url in ['/', '/kirish/', '/royxatdan-otish/', '/royxatdan-otish/oqituvchi/', '/admin/login/']:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        self.assertRedirects(self.client.get('/kabinet/'), '/kirish/?next=/kabinet/')

    def test_progress_survives_logout_and_unlocks_next_lesson(self):
        self.client.force_login(self.user)
        quiz = reverse('lesson_quiz', args=[self.course.slug, self.first.pk])
        self.assertEqual(self.client.get(quiz).status_code, 200)
        self.assertEqual(self.client.get(reverse('lesson_quiz', args=[self.course.slug, self.second.pk])).status_code, 302)
        answers = {f'question_{q.pk}': 'a' for q in self.first.questions.all()}
        self.assertTrue(self.client.post(quiz, answers).context['passed'])
        self.client.post(quiz, answers)
        self.assertEqual(LessonProgress.objects.count(), 1)
        self.client.logout()
        self.client.force_login(self.user)
        response = self.client.get(self.course.get_absolute_url())
        self.assertEqual(response.context['active_lesson'], self.second)
        self.assertEqual(self.client.get(reverse('lesson_quiz', args=[self.course.slug, self.second.pk])).status_code, 200)
        other = User.objects.create_user('other')
        self.client.force_login(other)
        self.assertEqual(self.client.get(self.course.get_absolute_url()).context['active_lesson'], self.first)

    def test_teacher_cannot_publish_without_permission(self):
        UserProfile.objects.create(user=self.user, role='teacher')
        self.client.force_login(self.user)
        response = self.client.post('/kabinet/', {'course': self.course.pk, 'title': 'Draft', 'order': 3, 'published': 'on'})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Lesson.objects.get(title='Draft').published)

    def test_logout_requires_post(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/chiqish/').status_code, 405)
        self.assertEqual(self.client.post('/chiqish/').status_code, 302)

    def test_admin_pages(self):
        admin = User.objects.create_superuser('admin', password='test-password')
        self.client.force_login(admin)
        for url in ['/admin/', '/admin/academy/course/', '/admin/academy/lesson/', '/admin/academy/userprofile/', '/admin/academy/lessonprogress/', f'/admin/academy/lesson/{self.first.pk}/change/', '/admin/academy/course/add/']:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_login_returns_to_course_and_blocks_external_redirect(self):
        response = self.client.post('/kirish/?next=' + self.course.get_absolute_url(), {'username': 'student', 'password': 'test-password'})
        self.assertRedirects(response, self.course.get_absolute_url())
        self.client.logout()
        response = self.client.post('/kirish/?next=https://example.com', {'username': 'student', 'password': 'test-password'})
        self.assertRedirects(response, '/kabinet/')
