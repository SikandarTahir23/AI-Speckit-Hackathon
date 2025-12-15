# Quick Start Guide

## Prerequisites
- Node.js >= 20.0
- PostgreSQL database running

## 1. Install Dependencies

```bash
npm install
cd auth-server && npm install && cd ..
```

## 2. Configure Database

Edit `auth-server/.env`:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/dacu_sikki
```

Create the database:

```sql
CREATE DATABASE dacu_sikki;
```

## 3. Start Both Servers

### Terminal 1: Auth Server
```bash
npm run auth-server:dev
```

### Terminal 2: Frontend
```bash
npm start
```

## 4. Access the Application

- **Frontend**: http://localhost:3000
- **Auth Server**: http://localhost:3001

## Features Available

✅ **Dark Mode Toggle** - Single functional toggle in navbar
✅ **User Authentication** - Signup/Login with Better Auth
✅ **User Profile** - Software/Hardware background questions
✅ **Session Management** - Persistent login with logout button

## Testing Authentication

1. Click **Login** in the navbar
2. Switch to **Sign up** tab
3. Fill in:
   - Name (optional)
   - Email
   - Password (min 8 chars with uppercase, lowercase, number)
   - Profile questions
4. Click **Create Account**
5. You'll be logged in automatically

## Troubleshooting

**Can't connect to auth server:**
- Ensure auth server is running on port 3001
- Check terminal for errors

**Database errors:**
- Verify PostgreSQL is running
- Check `auth-server/.env` DATABASE_URL
- Ensure database exists

**Need more help?**
See [AUTH_SETUP.md](./AUTH_SETUP.md) for detailed setup instructions.
