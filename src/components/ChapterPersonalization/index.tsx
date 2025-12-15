/**
 * ChapterPersonalization Wrapper Component (Hackathon Bonus Feature 2)
 *
 * Combines ChapterControls and PersonalizedChapter for easy integration
 * T063-T064: Integration with chapter pages and authentication check
 */

import React, { useState } from 'react';
import ChapterControls from '../ChapterControls';
import PersonalizedChapter from '../PersonalizedChapter';

interface ChapterPersonalizationProps {
  chapterId: number;
  isAuthenticated: boolean;
  originalContent?: string; // Optional: to fallback to original
}

export default function ChapterPersonalization({
  chapterId,
  isAuthenticated,
  originalContent,
}: ChapterPersonalizationProps) {
  const [personalizedContent, setPersonalizedContent] = useState<string | null>(null);
  const [currentLevel, setCurrentLevel] = useState<string | null>(null);

  const handlePersonalizedContent = (content: string, level: string) => {
    setPersonalizedContent(content);
    setCurrentLevel(level);
  };

  const handleChangeLevel = () => {
    setPersonalizedContent(null);
    setCurrentLevel(null);
  };

  return (
    <div>
      <ChapterControls
        chapterId={chapterId}
        isAuthenticated={isAuthenticated}
        onPersonalizedContent={handlePersonalizedContent}
      />

      {personalizedContent && currentLevel && (
        <PersonalizedChapter
          content={personalizedContent}
          difficultyLevel={currentLevel}
          onChangeLevel={handleChangeLevel}
        />
      )}

      {!personalizedContent && originalContent && (
        <div style={{
          padding: '2rem',
          background: '#f7fafc',
          borderRadius: '8px',
          border: '1px dashed #cbd5e0',
          marginTop: '1rem'
        }}>
          <p style={{
            margin: 0,
            color: '#718096',
            textAlign: 'center',
            fontSize: '0.95rem'
          }}>
            👆 Select a difficulty level above to see personalized content
          </p>
        </div>
      )}
    </div>
  );
}
