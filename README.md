# Eternelle aura App

This is a full-stack application with a React frontend (Vite + TypeScript) and a Django backend (Django REST Framework).

## Structure

- `client/`: Frontend application (React + TypeScript + Vite + shadcn/ui)
- `server/`: Backend application (Django + Django REST Framework)

## Getting Started

### Prerequisites

- Node.js installed
- Python 3.8+ installed

### Installation

#### Backend (Server)

1. Navigate to the server directory:
   ```bash
   cd server
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install django djangorestframework django-cors-headers djangorestframework-simplejwt
   ```
   *(Note: If a requirements.txt exists, use `pip install -r requirements.txt`)*

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser (if needed):
   ```bash
   python manage.py createsuperuser
   ```

#### Frontend (Client)

1. Navigate to the client directory:
   ```bash
   cd client
   ```
2. Install dependencies:
   ```bash
   npm install
   ```

### Running the Application

You need to run both the backend and frontend servers.

#### 1. Start the Django Backend

In the `server` directory, you can use the helper script:

```bash
./start_server.sh
```

Or manually using the virtual environment:

```bash
./venv/bin/python manage.py runserver
```

The API will be available at `http://localhost:8000/api`.

#### 2. Start the React Frontend

In the `client` directory:

```bash
npm run dev
```

The application will be available at `http://localhost:8080`.

## Features

- **Store**: Browse products with image support.
- **Cart**: Add/remove items, update quantities.
- **Wishlist**: Save items for later.
- **Authentication**: Login using Django JWT (Username/Password).
  - Default Admin: `Protas` / `Protas@01` (if set up as requested).

# versetile-ecomerse
