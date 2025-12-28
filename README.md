# MAA Inventory - Backend (Django + PostgreSQL)

Inventory backend API for the MAA Inventory System, built using Django.

---

## 🚀 Tech Stack
| Component | Technology |
|-----------|-------------|
| Backend   | Django (Python) |
| Database (dev) | SQLite (default) |
| Database (prod) | PostgreSQL |
| Virtual Env | `venv` |
| Project Folder | `maa-inventory` |

---

## 📁 Project Setup

If you're setting this up for the first time:

### 1️⃣ Clone the repository
```bash
git clone https://github.com/YOUR-USERNAME/maa-inventory.git
cd maa-inventory
```

### 2️⃣ Create & activate virtual environment (venv)
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### 3️⃣ Install dependencies
``` bash
pip install -r requirements.txt
```

### 4️⃣ Create .env file in project root

⚠️ Do NOT commit this file

``` bash
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True

# PostgreSQL (optional - when switching from SQLite)
DB_NAME=maa_inventory_db
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
```

### 5️⃣ Run database migrations
``` bash
python manage.py migrate
```

### 6️⃣ Create superuser (Admin access)
``` bash
python manage.py createsuperuser
```

### 7️⃣ Start the development server
``` bash
python manage.py runserver
```

### 7️⃣ Start the development server
``` bash
python manage.py runserver
```