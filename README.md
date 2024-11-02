# soundspawn web

## ติดตั้ง
1. สร้าง Virtual ENV
```
python -m venv venv
```

2. เข้าสู่ Virtual ENV
```
call "venv\Scripts\activate.bat"
```

3. ติดตั้ง dependencies
```
pip install -r requirements.txt
```

4. สร้าง Database ชื่อว่า `soundspawn` ใน pgAdmin
5. migrate ข้อมูล
```
python manage.py makemigrations
python manage.py migrate
```

6. Run server
```
python manage.py runserver
```