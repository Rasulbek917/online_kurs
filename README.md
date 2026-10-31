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
2. Doimiy PostgreSQL bazasini va S3-compatible media bucket’ni (masalan, Cloudflare R2) tayyorlang. Vercel **Settings → Environment Variables** bo‘limida quyidagilarni Production uchun kiriting (Preview uchun ham kerak bo‘lsa alohida belgilang):
   - `DJANGO_SECRET_KEY` — tasodifiy, maxfiy Django kaliti.
   - `DATABASE_URL` — PostgreSQL ulanish URL’i.
   - `AWS_STORAGE_BUCKET_NAME` — media bucket nomi.
   - `AWS_S3_ENDPOINT_URL` — S3 endpoint URL’i.
   - `AWS_ACCESS_KEY_ID` va `AWS_SECRET_ACCESS_KEY` — bucket uchun maxfiy credentials.
   - `AWS_S3_REGION_NAME` — R2 uchun `auto`; boshqa provider uchun uning region’i.
   - `AWS_S3_CUSTOM_DOMAIN` — ixtiyoriy, media uchun ochiq CDN domeni.
   - `ALLOWED_HOSTS` va `CSRF_TRUSTED_ORIGINS` — ixtiyoriy custom domen uchun, masalan `ALLOWED_HOSTS=example.com,www.example.com` va `CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com`. `.vercel.app` domenlari odatiy holatda ruxsat etiladi.
3. **Deploy** qiling yoki Git’ga push qilib avtomatik deploymentni kuting. Environment variable qo‘shilgan yoki o‘zgargan bo‘lsa, yangi deployment boshlang.
4. Saytni ishlatishdan oldin yuqoridagi production `DATABASE_URL` bilan `python manage.py migrate` bajaring va `python manage.py createsuperuser` orqali admin yarating. Bu buyruqlarni loyihani ishga tushiradigan ishonchli muhitdan bajaring; Vercel Function ishga tushganda migratsiyalar avtomatik bajarilmaydi.

Vercel’dagi SQLite va lokal fayl tizimi doimiy emas: `.vercelignore` lokal `db.sqlite3`, `media/` va virtualenv’larni deploymentdan chiqaradi. Ishlab chiqarish bazasi va yuklangan rasmlar/videolar PostgreSQL hamda S3-compatible bucket’da saqlanadi. Bucket fayllarni ommaviy o‘qishga ruxsat berishi yoki `AWS_S3_CUSTOM_DOMAIN` orqali ochiq CDN domeni sozlangan bo‘lishi kerak.
