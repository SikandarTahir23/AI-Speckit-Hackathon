# Quick Test Guide - Phase 4 Personalization

## Prerequisites

1. **Backend running** on `http://localhost:8000`
2. **Frontend running** on `http://localhost:3000`
3. **Database migrated** with `alembic upgrade head`
4. **User account created** from Phase 3

## Quick API Test (Backend)

### 1. Test Authentication Required

```bash
# Should return 401 Unauthorized
curl -X POST http://localhost:8000/personalize \
  -H "Content-Type: application/json" \
  -d '{"chapter_id": 1, "difficulty_level": "Beginner"}'
```

Expected: `401 Unauthorized` (user not authenticated)

### 2. Test with Authentication

First, login to get session cookie:

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=yourpassword" \
  -c cookies.txt

# Then personalize with cookie
curl -X POST http://localhost:8000/personalize \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"chapter_id": 1, "difficulty_level": "Beginner"}'
```

Expected Response:
```json
{
  "chapter_id": 1,
  "difficulty_level": "Beginner",
  "personalized_content": "...",
  "cached": false,
  "processing_time_ms": 5000
}
```

### 3. Test Cache Hit (Run Same Request Again)

```bash
curl -X POST http://localhost:8000/personalize \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"chapter_id": 1, "difficulty_level": "Beginner"}'
```

Expected:
- `"cached": true`
- `processing_time_ms` < 2000

### 4. Test Invalid Chapter

```bash
curl -X POST http://localhost:8000/personalize \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"chapter_id": 99, "difficulty_level": "Beginner"}'
```

Expected: `404 Not Found`

### 5. Test Rate Limiting

Run this command 11 times rapidly:

```bash
for i in {1..11}; do
  curl -X POST http://localhost:8000/personalize \
    -H "Content-Type: application/json" \
    -b cookies.txt \
    -d "{\"chapter_id\": $i, \"difficulty_level\": \"Beginner\"}"
  echo ""
done
```

Expected: 11th request returns `429 Too Many Requests`

## Quick UI Test (Frontend)

### 1. Test Unauthenticated State

1. Open browser to `http://localhost:3000`
2. Navigate to a chapter page with personalization widget
3. Verify message: "🔒 Sign in to personalize this chapter"

### 2. Test Authenticated Personalization

1. Sign in using AuthWidget
2. Navigate to chapter with personalization
3. Click "Beginner" button
4. Verify:
   - ✅ Loading spinner appears
   - ✅ "Personalizing content..." message shows
   - ✅ Buttons are disabled during loading
   - ✅ After ~5-10s, personalized content displays
   - ✅ Badge shows "🌱 Beginner Level"
   - ✅ "Change Level" button appears

### 3. Test Cache Performance

1. Click "Change Level" button
2. Select "Beginner" again
3. Verify:
   - ✅ Response is fast (<2 seconds)
   - ✅ Content displays immediately
   - ✅ Console shows "cache HIT"

### 4. Test Different Levels

1. Click "Change Level"
2. Select "Advanced"
3. Compare content:
   - ✅ Advanced version is more technical
   - ✅ Badge shows "⚡ Advanced Level" in orange
   - ✅ No beginner explanations present

### 5. Test Error Handling

Simulate error by stopping backend:

1. Stop backend server
2. Click a difficulty button
3. Verify:
   - ✅ Error message appears
   - ✅ User is informed of failure
   - ✅ No broken UI

## Database Verification

Check cached entries in database:

```bash
# Connect to database
psql $DATABASE_URL

# Check cached personalized content
SELECT id, chapter_id, difficulty_level, LENGTH(personalized_text), created_at
FROM personalized_content
ORDER BY created_at DESC
LIMIT 10;
```

Expected:
- Each successful personalization creates a cache entry
- `chapter_id` matches request
- `difficulty_level` matches request
- `personalized_text` is non-empty

## Backend Logs Verification

Check logs for expected behavior:

```bash
# View recent logs
tail -f backend/logs/app.log
```

Look for:
- ✅ `Personalization request: chapter_id=X, level=Y, user=...`
- ✅ `Cache HIT` or `Cache MISS`
- ✅ `Cached personalized content for chapter X (Level)`
- ✅ Processing time logged

## Success Criteria Checklist

### Performance (SC-003, SC-004)
- [ ] Uncached personalization completes in <10s
- [ ] Cached personalization completes in <2s
- [ ] Processing time logged accurately

### Functionality (FR-012, FR-016, FR-017)
- [ ] Three difficulty levels work (Beginner/Intermediate/Advanced)
- [ ] Fallback to original content on errors
- [ ] Unauthenticated users see appropriate message

### Security
- [ ] Authentication required (401 without login)
- [ ] Rate limiting works (429 after 10 requests/minute)
- [ ] Session cookies handled correctly

### UI/UX
- [ ] Loading states display properly
- [ ] Error messages are user-friendly
- [ ] "Change Level" button resets state
- [ ] Difficulty badges color-coded correctly

## Troubleshooting

### Backend won't start
- Check `DATABASE_URL` in `.env`
- Check `OPENAI_API_KEY` in `.env`
- Run `alembic upgrade head`

### Frontend components not found
- Run `npm install` to install dependencies
- Check component imports match file paths
- Verify `react-markdown` and `remark-gfm` installed

### OpenAI API errors
- Check API key validity
- Check API credits/quota
- Review rate limits on OpenAI account

### Database errors
- Verify migration applied: `alembic current`
- Check table exists: `\dt personalized_content` in psql
- Ensure foreign key constraints valid

## Next Steps

Once all tests pass:
1. Document any issues found
2. Proceed to Phase 5 (Urdu Translation)
3. Plan Phase 6 (Pre-generation for demo)

## Quick Demo Script

For showing to judges:

1. **Show unauthenticated state**: "Personalization requires login"
2. **Sign in**: Quick signup/signin flow
3. **Select Beginner**: Content simplifies with analogies
4. **Change to Advanced**: Content becomes technical
5. **Show cache performance**: Re-select same level, <2s response
6. **Highlight value**: "Adapts to any learning level, cached for speed"

Total demo time: ~2 minutes
Points earned: **50 points** for Feature 2
