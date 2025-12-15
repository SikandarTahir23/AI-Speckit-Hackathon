# Better Auth Setup Guide

This project now uses **Better Auth** for authentication instead of the previous FastAPI auth system.

## What Changed

### 1. Navbar Toggle Button
- ✅ **Fixed**: Removed duplicate color mode toggles
- ✅ **Functional**: Single dark mode toggle button now works properly
- The default Docusaurus toggle is disabled, using only the custom toggle

### 2. Authentication System
- ✅ **Better Auth**: Replaced FastAPI auth with Better Auth
- ✅ **Fixed Login/Signup**: Forms now work without errors
- ✅ **User Profile**: Signup includes profile questions (software/hardware background, skills)
- ✅ **Logout**: Added logout button for authenticated users

## Setup Instructions

### Prerequisites
- Node.js >= 20.0
- PostgreSQL database

### 1. Configure Database

Update the `auth-server/.env` file with your PostgreSQL connection:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/dacu_sikki
```

### 2. Install Dependencies

The Better Auth client is already installed in the main project. Install auth server dependencies:

```bash
cd auth-server
npm install
```

### 3. Initialize Database

Better Auth will automatically create the necessary tables on first run. Make sure your PostgreSQL database exists:

```sql
CREATE DATABASE dacu_sikki;
```

### 4. Start the Auth Server

In one terminal:

```bash
cd auth-server
npm run dev
```

The auth server will run on **http://localhost:3001**

### 5. Start the Frontend

In another terminal:

```bash
npm start
```

The Docusaurus site will run on **http://localhost:3000**

## Testing Authentication

1. Open http://localhost:3000
2. Click the **Login** button in the navbar
3. Create a new account with the signup form:
   - Enter name (optional)
   - Enter email
   - Enter password (min 8 chars, with uppercase, lowercase, and number)
   - Fill out profile questions
4. After signup, you'll be logged in automatically
5. Your name/email will appear in the navbar with a **Logout** button

## Architecture

```
┌─────────────────┐
│   Frontend      │
│  (Docusaurus)   │  Port 3000
│                 │
│  - Better Auth  │
│    React Client │
└────────┬────────┘
         │
         │ API Calls
         │
┌────────▼────────┐
│   Auth Server   │  Port 3001
│   (Node.js)     │
│                 │
│  - Better Auth  │
│  - Express      │
└────────┬────────┘
         │
         │ Database Queries
         │
┌────────▼────────┐
│   PostgreSQL    │
│                 │
│  - User Data    │
│  - Sessions     │
└─────────────────┘
```

## API Endpoints

The auth server exposes these endpoints:

- `POST /api/auth/sign-up/email` - Create new account
- `POST /api/auth/sign-in/email` - Login
- `POST /api/auth/sign-out` - Logout
- `GET /api/auth/session` - Get current session
- `GET /health` - Health check

## Troubleshooting

### "Cannot connect to auth server"
- Make sure the auth server is running on port 3001
- Check `auth-server/.env` configuration

### Database Connection Errors
- Verify PostgreSQL is running
- Check DATABASE_URL in `auth-server/.env`
- Ensure the database exists

### Frontend Auth Errors
- Clear browser cookies and local storage
- Restart both frontend and auth server
- Check browser console for detailed errors

## Environment Variables

### auth-server/.env
```env
BETTER_AUTH_SECRET=your-super-secret-key-change-this-in-production
BETTER_AUTH_URL=http://localhost:3001
DATABASE_URL=postgresql://user:password@localhost:5432/dacu_sikki
PORT=3001
FRONTEND_URL=http://localhost:3000
```

## Production Deployment

For production:

1. Update `BETTER_AUTH_SECRET` with a strong random key
2. Set `BETTER_AUTH_URL` to your production auth server URL
3. Update `FRONTEND_URL` to your production domain
4. Enable email verification in `auth-server/auth.js`:
   ```js
   emailAndPassword: {
     enabled: true,
     requireEmailVerification: true, // Change this to true
   }
   ```
5. Deploy the auth server separately (e.g., on Heroku, Render, or Railway)
6. Update the frontend's auth client base URL

## Next Steps

- [ ] Add email verification
- [ ] Add password reset functionality
- [ ] Add social login providers (Google, GitHub, etc.)
- [ ] Add role-based access control
- [ ] Add user profile management
