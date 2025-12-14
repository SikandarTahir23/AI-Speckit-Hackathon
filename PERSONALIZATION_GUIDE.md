# Chapter Personalization Feature - Phase 4 Implementation Guide

## Overview

Phase 4 implements **User Story 2: Personalized Chapter Content** (50 hackathon points).

This feature allows authenticated users to adapt book chapters to their experience level (Beginner/Intermediate/Advanced) using AI-powered content transformation.

## Architecture

### Backend Components

1. **Personalization Agent** (`backend/agents/personalization_agent.py`)
   - Uses OpenAI GPT-3.5-turbo for content adaptation
   - Three difficulty-specific prompts with hallucination guardrails
   - Singleton pattern for efficiency

2. **Database Model** (`backend/models/personalized_content.py`)
   - Caches personalized content per (chapter_id, difficulty_level)
   - Unique constraint prevents duplicate entries
   - Optimized for fast cache retrieval (<2s)

3. **API Endpoint** (`backend/api/routes.py`)
   - `POST /personalize` - Protected by authentication
   - Rate limited to 10 requests/minute
   - Automatic cache lookup and storage
   - Fallback to original content on errors

### Frontend Components

1. **ChapterControls** (`src/components/ChapterControls/`)
   - Three-button difficulty selector (Beginner/Intermediate/Advanced)
   - Loading state with spinner
   - Error handling and display
   - Unauthenticated user message

2. **PersonalizedChapter** (`src/components/PersonalizedChapter/`)
   - Renders personalized markdown content
   - Difficulty level badge with color coding
   - "Change Level" button to reset selection
   - Responsive design for mobile

3. **ChapterPersonalization** (`src/components/ChapterPersonalization/`)
   - Wrapper component combining controls and display
   - Manages state between components
   - Easy integration into chapter pages

## Integration Steps

### Step 1: Backend Setup

Ensure the backend is running with all Phase 3 (authentication) and Phase 4 dependencies:

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload --port 8000
```

### Step 2: Frontend Setup

Dependencies are already installed (`react-markdown`, `remark-gfm`).

```bash
npm start
```

### Step 3: Integrate into Chapter Pages

To add personalization to a chapter page, import and use the `ChapterPersonalization` component:

```tsx
// In your chapter page (e.g., docs/chapter-3.tsx or chapter-3.mdx)
import ChapterPersonalization from '@site/src/components/ChapterPersonalization';
import { useContext } from 'react';
import { AuthContext } from '@site/src/contexts/AuthContext';

function ChapterPage() {
  const { user } = useContext(AuthContext);

  return (
    <div>
      <h1>Chapter 3: Actuation Systems</h1>

      {/* Add personalization widget */}
      <ChapterPersonalization
        chapterId={3}
        isAuthenticated={!!user}
      />

      {/* Original chapter content below */}
      {/* ... */}
    </div>
  );
}
```

### Step 4: Authentication Context (if not already set up)

Ensure `AuthContext` is available in `src/contexts/AuthContext.tsx`:

```tsx
import React, { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext({
  user: null,
  login: () => {},
  logout: () => {},
});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check session on load
    fetch('http://localhost:8000/auth/me', { credentials: 'include' })
      .then(res => res.ok ? res.json() : null)
      .then(data => data && setUser(data))
      .catch(() => {});
  }, []);

  const login = (userData) => setUser(userData);
  const logout = () => {
    fetch('http://localhost:8000/auth/logout', {
      method: 'POST',
      credentials: 'include',
    });
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
```

Wrap your app in the provider (in `src/theme/Root.tsx` or similar):

```tsx
import { AuthProvider } from '@site/src/contexts/AuthContext';

export default function Root({ children }) {
  return <AuthProvider>{children}</AuthProvider>;
}
```

## Usage Flow

### For Users

1. **Sign In**
   - User must be authenticated to use personalization
   - If not signed in, a message prompts them to sign in

2. **Select Difficulty Level**
   - Click one of three buttons: Beginner 🌱, Intermediate 🚀, Advanced ⚡
   - Loading indicator shows "Personalizing content for your level..."

3. **View Personalized Content**
   - Content is displayed with a difficulty badge
   - AI-adapted for selected level:
     - **Beginner**: Simplified language, analogies, jargon explained
     - **Intermediate**: Balanced technical depth with context
     - **Advanced**: Dense, technical, precise

4. **Change Level** (Optional)
   - Click "Change Level" button to reset and select a different level

### Performance Characteristics

- **First Request (Cache Miss)**: <10 seconds (includes OpenAI API call)
- **Subsequent Requests (Cache Hit)**: <2 seconds (database lookup only)
- **Rate Limit**: 10 requests/minute per user
- **Fallback**: Original content shown if personalization fails

## API Reference

### POST /personalize

**Request:**
```json
{
  "chapter_id": 3,
  "difficulty_level": "Beginner"
}
```

**Response:**
```json
{
  "chapter_id": 3,
  "difficulty_level": "Beginner",
  "personalized_content": "# Chapter 3: Actuation Systems (Beginner)\n\nActuators are like the muscles of a robot...",
  "cached": false,
  "processing_time_ms": 8450
}
```

**Error Responses:**
- `401 Unauthorized`: User not authenticated
- `404 Not Found`: Chapter ID invalid (must be 1-8)
- `429 Too Many Requests`: Rate limit exceeded (10/minute)
- `500 Internal Server Error`: Personalization failed (returns original content as fallback)

## Testing

### Manual Testing Checklist

1. **Unauthenticated Access**
   - ✅ Navigate to chapter page without signing in
   - ✅ Verify "Sign in to personalize" message displays
   - ✅ Verify buttons are disabled or hidden

2. **Beginner Level**
   - ✅ Sign in and select Beginner
   - ✅ Verify content is simplified with analogies
   - ✅ Check jargon is explained inline

3. **Advanced Level**
   - ✅ Select Advanced
   - ✅ Verify content is more technical and dense
   - ✅ Check analogies are removed

4. **Cache Performance**
   - ✅ Request same chapter+level twice
   - ✅ Verify second request completes in <2s
   - ✅ Check "cached: true" in response

5. **Error Handling**
   - ✅ Simulate OpenAI API failure (invalid API key)
   - ✅ Verify fallback to original content
   - ✅ Check error message displays

6. **Change Level**
   - ✅ Personalize chapter
   - ✅ Click "Change Level"
   - ✅ Select different level
   - ✅ Verify content regenerates

## Troubleshooting

### Issue: "Please sign in to use personalization features"

**Cause**: User is not authenticated
**Fix**: Implement and test authentication flow from Phase 3

### Issue: "Personalization failed"

**Cause**: OpenAI API error or rate limit
**Fix**:
- Check `OPENAI_API_KEY` in `.env`
- Verify API key has credits
- Check backend logs for detailed error

### Issue: Slow performance (>10s for first request)

**Cause**: Large chapter content or slow OpenAI API
**Fix**:
- Pre-generate cache entries using pre-generation script (Phase 6)
- Verify network connectivity
- Consider using GPT-3.5-turbo instead of GPT-4

### Issue: Content not displaying

**Cause**: Markdown rendering issue
**Fix**:
- Verify `react-markdown` and `remark-gfm` are installed
- Check browser console for errors
- Ensure content is valid markdown

## Pre-Generation Strategy (Phase 6)

For hackathon demo, pre-generate all 24 personalized versions (8 chapters × 3 levels):

```bash
cd backend
python scripts/pre_generate_cache.py
```

This ensures:
- All demo requests hit cache (<2s response)
- No OpenAI API delays during presentation
- Consistent, reviewed content quality

## Acceptance Criteria

✅ **SC-003**: Personalized content delivered in <10s for uncached requests
✅ **SC-004**: Cached personalization retrieved in <2s
✅ **SC-007**: Graceful fallback to original content on API failures
✅ **FR-012**: Three difficulty levels implemented (Beginner/Intermediate/Advanced)
✅ **FR-016**: Fallback mechanism prevents broken user experience
✅ **FR-017**: Unauthenticated users prompted to sign in

## Next Steps

After Phase 4 completion:
- **Phase 5**: Implement Urdu Translation (25 points)
- **Phase 6**: Pre-generation, testing, and demo preparation

## Support

For issues or questions:
- Check backend logs: `backend/logs/`
- Review FastAPI docs: `http://localhost:8000/docs`
- Test API endpoint directly: `POST http://localhost:8000/personalize`
