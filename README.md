# CDM Reservation App 📚

A modern, full-stack web application for managing school resource reservations (CDM). Designed for both Students (to borrow items) and Administrators (to manage stock and requests).

## ✨ Features

- **Authentication & Roles**: Secure login for Students and Admins.
- **Resource Catalogue**: Browse Books, DVDs, and Equipment with real-time stock availability.
- **Smart Reservations**: 
  - Students can add multiple items to a cart.
  - Automatic return date calculation based on duration (7 or 14 days).
- **Admin Dashboard**:
  - Approve or Reject reservation requests.
  - **Stock Management**: Edit active quantity directly from the UI.
  - **Overdue Tracking**: Visual "RETARD" badges and email reminder simulation.
  - **Returns**: One-click "Mark as Returned" to automatically free up stock.
- **Reviews & Ratings**: Students can rate and review resources (5-star system).
- **Mobile PWA**: Installable on mobile and desktop devices (Progressive Web App).

## 🛠️ Tech Stack

- **Backend**: Python (FastAPI), SQLAlchemy (SQLite), JWT Auth.
- **Frontend**: React (Vite), TypeScript, TailwindCSS, Framer Motion.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js & npm

### 1. Backend Setup
Navigate to the `backend` folder:
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

**Run the Server:**
```bash
python -m uvicorn main:app --reload
```
The API will be available at `http://localhost:8000` (Docs at `/docs`).

### 2. Frontend Setup
Open a new terminal and navigate to the `frontend` folder:
```bash
cd frontend
npm install
```

**Run the Client:**
```bash
npm run dev
```
The app will open at `http://localhost:5173`.

## 👤 Default Credentials

**Admin Account:**
- **Username**: `admin`
- **Password**: `admin123`

**Student Account (Demo):**
- **Username**: `student1`
- **Password**: `password123`
*(Or click "S'inscrire" to create a new one)*

## 📱 Installing the App (PWA)
1. Open the app in **Chrome** or **Edge**.
2. Look for the **Install Icon** in the URL bar (computer) or tap "Add to Home Screen" in the menu (mobile).
3. The app works offline (basic caching) and launches in a standalone window.

## 🚀 Deployment
For instructions on how to deploy the app to production, see the [Deployment Guide](deployment.md).
