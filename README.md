# soundspawn web

## ติดตั้ง
1. สร้าง Virtual ENV
```
python -m venv venv
```

2. ไปที่ `venv\Scripts\activate.bat` เพิ่มบรรทัดนี้ท้ายไฟล์
```
set POSTGRES_PASSWORD=<รหัส postgres เครื่องตัวเอง>
set POSTGRES_HOST=localhost
```


3. เข้าสู่ Virtual ENV
```
call "venv\Scripts\activate.bat"
```

4. ติดตั้ง dependencies
```
pip install -r requirements.txt
```

5. สร้าง Database ชื่อว่า `soundspawn` ใน pgAdmin
6. migrate ข้อมูล
```
python manage.py makemigrations
python manage.py migrate
```

7. Run server
```
python manage.py runserver
```