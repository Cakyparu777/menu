# Running the Zuugchuu Application

This guide explains how to run both the frontend and backend servers for the restaurant menu application.

## Prerequisites

- Node.js and npm installed
- Python 3.x installed
- Expo CLI (installed via npm)

---

## Backend Server (FastAPI)

The backend server must be running for the app to work properly. It handles authentication, database operations, and API requests.

### Starting the Backend

```bash
# Navigate to backend directory
cd /Users/tuguldur.ganbaatar/Desktop/menu/backend

# Activate virtual environment
source venv/bin/activate

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Verify Backend is Running

The server should display:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started server process
INFO:     Application startup complete.
```

Test the API:
```bash
curl http://localhost:8001/
# Should return: {"message":"Welcome to Restaurant Menu API"}
```

### Backend API Endpoints

- **Base URL**: `http://localhost:8001/api/v1`
- **Auth**: `/auth/login`, `/auth/signup`
- **Users**: `/users/me`
- **Restaurants**: `/restaurants/*`
- **Menu**: `/menu/*`
- **Orders**: `/orders/*`

---

## Frontend Server (React Native / Expo)

The frontend connects to the backend API and provides the mobile/web interface.

### Starting the Frontend

```bash
# Navigate to frontend directory
cd /Users/tuguldur.ganbaatar/Desktop/menu/frontend

# Start Expo development server
npm start
```

### Running on Different Platforms

Once the Expo server is running, you can:

**iOS Simulator:**
```bash
# Press 'i' in the terminal or run:
npm run ios
```

**Android Emulator:**
```bash
# Press 'a' in the terminal or run:
npm run android
```

**Web Browser:**
```bash
# Press 'w' in the terminal or run:
npm run web
```

**Physical Device (Expo Go):**
1. Install Expo Go app on your device
2. Scan the QR code displayed in the terminal

---

## Database

The application uses SQLite database located at:
```
/Users/tuguldur.ganbaatar/Desktop/menu/backend/sql_app.db
```

### Viewing Database Contents

```bash
cd /Users/tuguldur.ganbaatar/Desktop/menu/backend
sqlite3 sql_app.db

# Inside SQLite shell:
.tables                    # List all tables
SELECT * FROM users;       # View users
SELECT * FROM restaurants; # View restaurants
.exit                      # Exit SQLite
```

---

## Troubleshooting

### Issue: "Login failed" or "Network Error"

**Cause**: Backend server is not running

**Solution**:
1. Check if backend is running on port 8001:
   ```bash
   lsof -i :8001
   ```
2. If not running, start the backend server (see above)

### Issue: "Cannot connect to API"

**Cause**: Frontend can't reach backend

**Solution**:
1. Verify backend is running on `http://0.0.0.0:8001`
2. Check frontend API configuration in `frontend/src/api/client.js`
3. Ensure your device/emulator can reach the backend IP

### Issue: Database errors

**Cause**: Database file is corrupted or missing

**Solution**:
1. Check if `sql_app.db` exists in backend directory
2. Restart backend server (it will recreate tables if needed)

---

## Running Both Servers

For development, you need **two terminal windows**:

**Terminal 1 - Backend:**
```bash
cd /Users/tuguldur.ganbaatar/Desktop/menu/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Terminal 2 - Frontend:**
```bash
cd /Users/tuguldur.ganbaatar/Desktop/menu/frontend
npm start
```

---

## Current Status

✅ **Backend Server**: Running on `http://0.0.0.0:8001`
✅ **Frontend Server**: Running on `http://localhost:8081`
✅ **Database**: SQLite database connected and operational
✅ **API Endpoints**: All endpoints tested and working

### Test Credentials

A test user has been created:
- **Email**: test@example.com
- **Password**: testpass123
- **Role**: customer

You can use these credentials to test the login functionality.

---

## Next Steps

1. Open the Expo app on your device or simulator
2. Try logging in with the test credentials
3. Create a new account using the signup screen
4. Test the restaurant and menu features

If you encounter any issues, ensure both servers are running and check the terminal output for error messages.
