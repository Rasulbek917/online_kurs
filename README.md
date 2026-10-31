# DarsHub — Django onlayn darslar sayti

O‘zbek tilidagi onlayn kurslar platformasi. Django admin panelida yo‘nalish, kurs va darslarni yarating; darsga MP4 video yuklang yoki YouTube/Vimeo havolasini kiriting.

## Ishga tushirish

```bash
cd online_dars
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations academy
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

O‘quvchining o‘tgan darslari hozircha brauzer sessiyasida saqlanadi.

Yuklangan rasmlar va videolar `media/` papkasida saqlanadi. Ishlab chiqarish muhitida `DEBUG=False`, kuchli maxfiy kalit, HTTPS, statik/media fayl saqlash va `ALLOWED_HOSTS` sozlamalarini yangilang.
