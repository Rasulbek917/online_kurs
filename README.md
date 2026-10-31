# DarsHub — Django onlayn darslar sayti

O‘zbek tilidagi onlayn kurslar platformasi. Django admin panelida yo‘nalish, kurs va darslarni yarating; darsga MP4 video yuklang yoki YouTube/Vimeo havolasini kiriting.

## Ishga tushirish

```bash
cd online_teacher
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Sayt: http://127.0.0.1:8000/  
Admin: http://127.0.0.1:8000/admin/

## Kurs qo‘shish

1. Admin panelga kiring. **Backend** yo‘nalishi tayyor qo‘shilgan; xohlasangiz **Yo‘nalishlar** bo‘limida Frontend yoki boshqa yo‘nalish ham yarating.
3. **Kurslar** bo‘limidan kurs qo‘shing. Kurs sahifasida darslarni ham inline jadval orqali qo‘shish mumkin.
4. Har bir darsga video fayl yoki YouTube/Vimeo havolasini kiriting. Darslarni `Dars tartibi` raqami bo‘yicha tartiblang.
5. Har bir darsni alohida ochib, **Test savollari** bo‘limida aynan 10 ta savol, 4 tadan javob varianti va to‘g‘ri javobni kiriting. O‘quvchi 10 savoldan kamida 7 tasiga to‘g‘ri javob bersa, keyingi dars ochiladi.

O‘quvchining o‘tgan darslari hisobiga bog‘langan holda bazada saqlanadi. Admin panelda o‘quv natijalarini ko‘rish mumkin. O‘qituvchi qo‘shgan darslar `academy.add_lesson` huquqi bo‘lmasa qoralama sifatida saqlanadi; administrator ularni tekshirib chop etadi.

Jazzmin o‘rnatilmagan bo‘lsa, sayt standart Django admin panelidan foydalanadi.

Yuklangan rasmlar va videolar `media/` papkasida saqlanadi. Ishlab chiqarish muhitida `DEBUG=False`, kuchli maxfiy kalit, HTTPS, statik/media fayl saqlash va `ALLOWED_HOSTS` sozlamalarini yangilang.

## Vercel’ga deploy

Vercel `manage.py` va `config.settings.WSGI_APPLICATION` orqali Django loyihasini aniqlaydi. `STATIC_ROOT` mavjudligi sababli static fayllar build vaqtida yig‘ilib CDN orqali beriladi; alohida `vercel.json` yoki `collectstatic` build buyrug‘i kerak emas.

1. GitHub’dagi repozitoriyani Vercel’da **Add New → Project** orqali import qiling. Root Directory loyiha ildizi bo‘lib qolsin; Python runtime `requirements.txt` dan bog‘liqliklarni o‘rnatadi.
2. Vercel **Storage** bo‘limidan PostgreSQL bazasi va Blob ombori yarating hamda `online-kurs` loyihasiga ulang. PostgreSQL ulanishi uchun environment variable prefix `DATABASE` bo‘lsin; kod `DATABASE_URL`, `DATABASE_URL_POOLED` va Prisma/Postgres URL’larini qabul qiladi. Dars video va rasmlari uchun Blob store’ni **Public** rejimida yarating — bu sozlamada fayl URL’iga ega bo‘lgan har kim uni ko‘ra oladi.
3. Vercel **Settings → Environment Variables** bo‘limida quyidagini Production uchun kiriting (Preview uchun ham kerak bo‘lsa alohida belgilang):
   - `DJANGO_SECRET_KEY` — tasodifiy, maxfiy Django kaliti.
   - `ALLOWED_HOSTS` va `CSRF_TRUSTED_ORIGINS` — ixtiyoriy custom domen uchun, masalan `ALLOWED_HOSTS=example.com,www.example.com` va `CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com`. `.vercel.app` domenlari odatiy holatda ruxsat etiladi.
4. Git’ga push qiling va avtomatik Vercel deploymentni kuting. Production build davomida Django migratsiyalari avtomatik bajariladi.
5. `python manage.py createsuperuser` buyrug‘ini Vercel Production environment’idan olingan DB ulanishi bilan ishonchli muhitda bajarib admin yarating.

Vercel’dagi SQLite va lokal fayl tizimi doimiy emas: `.vercelignore` lokal `db.sqlite3`, `media/` va virtualenv’larni deploymentdan chiqaradi. Ishlab chiqarish ma’lumotlari PostgreSQL’da, yuklangan media esa Blob store’da saqlanadi. Blob store bu sozlamada public bo‘lgani uchun unga maxfiy yoki shaxsiy fayllarni yuklamang.
