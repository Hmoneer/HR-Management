# HR Management System

A complete backend system built with **Python 3 + FastAPI + SQLAlchemy (SQL)** for managing
the administrative structure between management and staff, including:

- 🔐 Authentication & role-based permissions (JWT) with five roles: **Manager, Deputy Manager, Accountant, HR, Employee**
- 🕒 Attendance tracking (check-in / check-out)
- ⚠️ Penalties & rewards management
- 💰 Automatic monthly salary calculation (base salary + rewards − penalties − absence deduction)

---

## 📁 Project Structure

```
hr-system/
├── app/
│   ├── main.py                 # App entry point, wires up all routers
│   ├── config.py                # App settings (environment variables)
│   ├── database.py              # Database connection (SQLAlchemy)
│   ├── seed.py                  # Auto-creates the first manager account
│   │
│   ├── models/                  # Database tables (SQLAlchemy Models)
│   │   ├── user.py              # User/Employee + job roles
│   │   ├── attendance.py        # Attendance records
│   │   ├── penalty_reward.py    # Penalties & rewards
│   │   └── salary.py            # Monthly salary records
│   │
│   ├── schemas/                 # Data validation models (Pydantic Schemas)
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── attendance.py
│   │   ├── penalty_reward.py
│   │   └── salary.py
│   │
│   ├── crud/                    # Database interaction logic
│   │   ├── user.py
│   │   ├── attendance.py
│   │   ├── penalty_reward.py
│   │   └── salary.py            # Monthly salary calculation logic
│   │
│   ├── core/                    # Security & permissions
│   │   ├── security.py          # Password hashing + JWT
│   │   └── permissions.py       # Role-based access control
│   │
│   └── routers/                 # API routes (each page/module is independent)
│       ├── auth.py              # POST /auth/login  |  GET /auth/me
│       ├── users.py             # Employee CRUD
│       ├── attendance.py        # Attendance check-in/out & management
│       ├── penalties_rewards.py # Penalties & rewards
│       └── salary.py            # Salary calculation & viewing
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

Each module (page) has its own dedicated file across `models`, `schemas`, `crud`, and
`routers`, all wired together through `main.py` and the database relationships
(`relationship`) between tables.

---

## ⚙️ Installation & Running

### 1. Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up environment variables

```bash
cp .env.example .env
# edit the values in .env as needed (especially SECRET_KEY in production)
```

### 3. Run the server

```bash
uvicorn app.main:app --reload
```

The app will run at: `http://127.0.0.1:8000`

- Interactive docs (Swagger UI): `http://127.0.0.1:8000/docs`
- Alternative docs (ReDoc): `http://127.0.0.1:8000/redoc`

### 4. First login

On first startup, the system automatically creates a **manager** account using the
credentials in `.env` (`FIRST_ADMIN_USERNAME` / `FIRST_ADMIN_PASSWORD`). Use it to log in,
then create the remaining accounts (deputy manager, accountant, HR, employees) via
`POST /users/`.

⚠️ **Important:** change the default manager password immediately in production.

---

## 🧑‍💼 Roles & Permissions

| Role | Permissions |
|---|---|
| **Manager** | Full access to everything: employees, attendance, penalties/rewards, salaries |
| **Deputy Manager** | Almost the same as Manager, except creating new manager/deputy-manager accounts |
| **Accountant** | Manages penalties/rewards + calculates and views salaries |
| **HR** | Manages employee records + attendance + penalties/rewards |
| **Employee** | Can only check in/out for themselves + view their own data (attendance, penalties/rewards, salary) |

Permissions are enforced in `app/core/permissions.py` using FastAPI Dependencies, so every
endpoint is protected according to the required role.

---

## 🔑 Authentication

The system uses **JWT Bearer Tokens**:

1. `POST /auth/login` with `username` and `password` (as form-data) → returns an `access_token`
2. Send the token in every subsequent request's header:
   ```
   Authorization: Bearer <access_token>
   ```
3. `GET /auth/me` returns the current logged-in user's data

---

## 📌 Main Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/auth/login` | Log in |
| GET | `/auth/me` | Current user's data |
| GET/POST | `/users/` | List/create employees |
| GET/PUT/DELETE | `/users/{id}` | View/update/delete an employee |
| POST | `/attendance/check-in` | Check in for today (self) |
| POST | `/attendance/check-out` | Check out for today (self) |
| GET/POST | `/attendance/` | List/add attendance records (admin use) |
| PUT/DELETE | `/attendance/{id}` | Update/delete an attendance record |
| GET/POST | `/penalties-rewards/` | List/add a penalty or reward |
| DELETE | `/penalties-rewards/{id}` | Delete a penalty/reward record |
| POST | `/salary/generate` | Calculate one employee's salary for a given month |
| POST | `/salary/generate-all` | Calculate all employees' salaries for a given month at once |
| GET | `/salary/` | List salary records |

The full list and exact details of every endpoint (inputs/outputs) are automatically
available at `/docs`.

---

## 💰 Salary Calculation Logic

An employee's net monthly salary is calculated as follows:

```
daily_rate        = base_salary / days_in_month
absence_deduction = daily_rate × number_of_absence_days_in_month
net_salary        = base_salary + total_rewards − total_penalties − absence_deduction
```

`POST /salary/generate-all` is called at the end of each month (manually or via a
scheduled/cron job) to calculate all active employees' salaries in one batch.

---

## 🗄️ Database

The project uses **SQLite** by default (a `hr_system.db` file is created automatically),
which works out of the box for development and testing with zero extra setup. To switch to
**PostgreSQL** or **MySQL** in production, just change the `DATABASE_URL` value in `.env`,
for example for PostgreSQL:

```
DATABASE_URL=postgresql://user:password@localhost:5432/hr_system
```

(make sure to install `psycopg2-binary` for PostgreSQL, or `pymysql`/`mysqlclient` for MySQL)

---

## 🛠️ Tech Stack

- **FastAPI** – core API framework
- **SQLAlchemy 2.0** – ORM for database access
- **Pydantic v2** – data validation
- **python-jose** – JWT creation/decoding
- **passlib[bcrypt]** – password hashing
- **Uvicorn** – ASGI server

---

## 📄 License

This project is open source and free to use and modify (MIT License).
