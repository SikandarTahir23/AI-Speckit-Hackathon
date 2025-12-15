# Browser Testing Checklist

**Quick checklist to verify all features in the browser**

---

## ✅ Pre-Test Setup

- [ ] Backend running at http://localhost:8000
- [ ] Frontend running at http://localhost:3000
- [ ] No console errors in terminal

Test command:
```bash
curl http://localhost:8000/health
curl http://localhost:3000
```

---

## Test 1: Basic Page Load

**URL:** http://localhost:3000/docs/chapter-1-introduction-to-physical-ai

**Expected:**
- [ ] Page loads successfully
- [ ] Chapter content displays
- [ ] "Translate to Urdu" button visible
- [ ] No JavaScript errors in console (F12 → Console)

**Not Expected (before sign-in):**
- [ ] Personalization buttons should NOT be visible yet

---

## Test 2: Translation (No Auth Required)

**Steps:**
1. [ ] Click "Translate to Urdu" button
2. [ ] See loading indicator "Translating to Urdu..."
3. [ ] Wait ~15-17 seconds (first request)
4. [ ] Side-by-side English/Urdu content appears
5. [ ] Three toggle buttons visible: "Both" | "English Only" | "Urdu Only"

**Verify:**
- [ ] English content on left
- [ ] Urdu content on right (RTL, right-aligned)
- [ ] Technical terms preserved in English (robot, AI, etc.)
- [ ] Toggle "English Only" → only English shows
- [ ] Toggle "Urdu Only" → only Urdu shows
- [ ] Toggle "Both" → side-by-side returns

**Test Caching:**
1. [ ] Refresh the page
2. [ ] Click "Translate to Urdu" again
3. [ ] Response should be instant (<2 seconds)
4. [ ] Console shows "cache HIT"

**Points:** 25 points ✅

---

## Test 3: Authentication (Feature 1)

**Steps:**
1. [ ] Look for "Sign In" button (likely in header)
2. [ ] Click "Sign In"
3. [ ] Click "Sign Up" to create new account

**Registration Form:**
- [ ] Email: test@example.com
- [ ] Password: Test123456 (min 8 chars, 1 upper, 1 lower, 1 digit)
- [ ] Software Background: Select "Intermediate"
- [ ] Hardware Background: Select "Basic"
- [ ] Python Familiar: ☑️ Check
- [ ] ROS Familiar: ☐ Uncheck
- [ ] AI/ML Familiar: ☑️ Check

**Submit and Verify:**
- [ ] Click "Sign Up" button
- [ ] Account created successfully
- [ ] Automatically signed in
- [ ] Email displayed in header/profile
- [ ] "Sign Out" button appears

**Test Session Persistence:**
1. [ ] Close browser completely
2. [ ] Reopen browser
3. [ ] Navigate to http://localhost:3000
4. [ ] Should still be logged in (no need to sign in again)
5. [ ] Email still shows in header

**Points:** 50 points ✅

---

## Test 4: Personalization (Requires Auth)

**Prerequisites:** Must be signed in from Test 3

**URL:** http://localhost:3000/docs/chapter-1-introduction-to-physical-ai

**Expected Now (after sign-in):**
- [ ] Three difficulty buttons visible at top:
  - 🌱 Beginner
  - 🚀 Intermediate
  - ⚡ Advanced

**Test Beginner Level:**
1. [ ] Click "Beginner" button
2. [ ] Loading spinner shows "Personalizing content..."
3. [ ] Wait ~5-10 seconds (first request)
4. [ ] Personalized content displays
5. [ ] Green badge shows "🌱 Beginner Level"
6. [ ] Content is simplified with analogies and explanations
7. [ ] "Change Level" button appears

**Test Caching:**
1. [ ] Click "Change Level"
2. [ ] Click "Beginner" again
3. [ ] Response is instant (<2 seconds)
4. [ ] Console shows "cache HIT"

**Test Advanced Level:**
1. [ ] Click "Change Level"
2. [ ] Click "Advanced"
3. [ ] Wait ~3-5 seconds (first request)
4. [ ] Content becomes more technical and dense
5. [ ] Orange badge shows "⚡ Advanced Level"
6. [ ] Compare with Beginner - should be noticeably different

**Test Intermediate Level:**
1. [ ] Click "Change Level"
2. [ ] Click "Intermediate"
3. [ ] Balanced content (between Beginner and Advanced)
4. [ ] Blue badge shows "🚀 Intermediate Level"

**Points:** 50 points ✅

---

## Test 5: Multiple Chapters

**Test on different chapters:**

1. [ ] Chapter 2: http://localhost:3000/docs/chapter-2-basics-of-humanoid-robotics
   - [ ] Personalization buttons visible (if signed in)
   - [ ] Translation button visible
   - [ ] Both features work

2. [ ] Chapter 5: http://localhost:3000/docs/chapter-5-ros2-fundamentals
   - [ ] Personalization buttons visible (if signed in)
   - [ ] Translation button visible
   - [ ] Both features work

3. [ ] Chapter 8: http://localhost:3000/docs/chapter-8-ethical-future
   - [ ] Personalization buttons visible (if signed in)
   - [ ] Translation button visible
   - [ ] Both features work

**Verify:**
- [ ] All 8 chapters have the same widgets
- [ ] Chapter IDs are correctly detected (1-8)
- [ ] Each chapter caches independently

---

## Test 6: Combined Features

**Scenario: Use both features together**

1. [ ] Sign in (if not already)
2. [ ] Navigate to Chapter 1
3. [ ] Click "Beginner" personalization
4. [ ] See simplified content
5. [ ] Scroll down to translation widget
6. [ ] Click "Translate to Urdu"
7. [ ] See personalized Beginner content translated to Urdu
8. [ ] Toggle display modes while viewing personalized content

**Verify:**
- [ ] Both features work independently
- [ ] No conflicts or errors
- [ ] Each caches separately

---

## Test 7: Error Handling

**Test without backend:**
1. [ ] Stop backend server (Ctrl+C in backend terminal)
2. [ ] Try to personalize content
3. [ ] Should see error message (not crash)
4. [ ] Try to translate
5. [ ] Should see error message (not crash)
6. [ ] Restart backend
7. [ ] Features work again

**Test sign-out:**
1. [ ] Click "Sign Out"
2. [ ] Navigate to a chapter
3. [ ] Personalization buttons should disappear
4. [ ] Translation should still work
5. [ ] Sign in again
6. [ ] Personalization buttons reappear

---

## Test 8: Performance Validation

**Measure response times:**

| Feature | First Request | Cached Request | Target | Status |
|---------|---------------|----------------|--------|--------|
| Personalization (Beginner) | ____ seconds | ____ seconds | <10s / <2s | [ ] |
| Personalization (Intermediate) | ____ seconds | ____ seconds | <10s / <2s | [ ] |
| Personalization (Advanced) | ____ seconds | ____ seconds | <10s / <2s | [ ] |
| Translation (Urdu) | ____ seconds | ____ seconds | <15s / <2s | [ ] |

**How to measure:**
1. Open Chrome DevTools (F12)
2. Go to Network tab
3. Trigger the request
4. Look at timing for the POST request

---

## Test 9: Browser Console Check

**Open DevTools (F12) → Console**

**Should see:**
- [ ] No red errors
- [ ] "cache HIT" or "cache MISS" messages for requests
- [ ] OpenAI API calls logging (optional)

**Should NOT see:**
- [ ] React errors
- [ ] 404 errors for missing files
- [ ] Authentication errors (401/403) when signed in
- [ ] CORS errors

---

## Test 10: Mobile Responsiveness (Optional)

**Test on mobile viewport:**
1. [ ] Open DevTools (F12)
2. [ ] Toggle device toolbar (Ctrl+Shift+M)
3. [ ] Select "iPhone 12 Pro" or similar
4. [ ] Navigate to a chapter

**Verify:**
- [ ] Difficulty buttons stack vertically or wrap nicely
- [ ] Translation toggles are touch-friendly
- [ ] Side-by-side layout becomes stacked on mobile
- [ ] Text is readable
- [ ] No horizontal scrolling

---

## Final Checklist - All Features Working

- [ ] ✅ Backend responding (http://localhost:8000/health)
- [ ] ✅ Frontend responding (http://localhost:3000)
- [ ] ✅ Can sign up new account
- [ ] ✅ Can sign in with credentials
- [ ] ✅ Session persists after browser restart
- [ ] ✅ Can personalize to Beginner level
- [ ] ✅ Can personalize to Intermediate level
- [ ] ✅ Can personalize to Advanced level
- [ ] ✅ Cached personalization responds <2s
- [ ] ✅ Can translate chapter to Urdu
- [ ] ✅ Side-by-side display works
- [ ] ✅ Display mode toggles work
- [ ] ✅ Cached translation responds <2s
- [ ] ✅ All 8 chapters have integrated features

---

## If All Checked: 🎉

**You have successfully verified all 125 hackathon points!**

- ✅ Feature 1 (Authentication): 50 points
- ✅ Feature 2 (Personalization): 50 points
- ✅ Feature 3 (Translation): 25 points

**Ready for demo!** 🚀

---

## Troubleshooting Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| Backend not responding | `cd backend && python -m uvicorn main:app --reload` |
| Frontend not responding | `npm start` |
| Components not appearing | Check browser console (F12), verify chapter title format |
| Personalization not working | Sign in first, check authentication |
| Translation not working | Check backend is running, verify API at http://localhost:8000/docs |
| Slow responses | First requests are slow (OpenAI API), cached requests should be fast |
| 401 errors | Sign in again, session may have expired |

---

## Support

For detailed guides, see:
- `COMPLETE_TESTING_GUIDE.md` - Comprehensive testing workflow
- `INTEGRATION_COMPLETE.md` - Integration architecture and details
- `PHASE4_TEST_RESULTS.md` - Personalization feature details
- `PHASE5_COMPLETE.md` - Translation feature details

Happy testing! 🎉
