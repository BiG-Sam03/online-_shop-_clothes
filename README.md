# Online Shop (Clothes) – Python (No Framework) + MySQL

Simple web app using Python **standard library** for HTTP (no frameworks).
Database: **MySQL**

## Implemented Use Cases
- Register
- Login

## Setup (MySQL)
1. Start MySQL (XAMPP/WAMP).
2. Open phpMyAdmin and run `schema.sql` OR just run the app (it auto-creates DB/table using root).

> If your MySQL root password is not empty, edit `DB_CONFIG` in `db.py`.

## Install Requirements
```bash
pip install -r requirements.txt
```

## Run
```bash
python app.py
```
Open: http://localhost:8000

## Notes
- Passwords are hashed using PBKDF2 (stdlib).
- Sessions are kept in memory (simple for demo).
