/**
 * ChapterContentContext - Manages chapter content state
 * Allows ChapterHeader to control what content is displayed (original, translated, personalized)
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';

export type ViewMode = 'original' | 'translated' | 'personalized';
export type DifficultyLevel = 'Beginner' | 'Intermediate' | 'Advanced';

interface TranslationData {
  original: string;
  translated: string;
}

interface PersonalizationData {
  content: string;
  level: DifficultyLevel;
}

interface ChapterContentState {
  viewMode: ViewMode;
  translationData: TranslationData | null;
  personalizationData: PersonalizationData | null;
  setViewMode: (mode: ViewMode) => void;
  setTranslationData: (data: TranslationData) => void;
  setPersonalizationData: (data: PersonalizationData) => void;
  reset: () => void;
}

const ChapterContentContext = createContext<ChapterContentState | undefined>(undefined);

export function useChapterContent() {
  const context = useContext(ChapterContentContext);
  if (!context) {
    throw new Error('useChapterContent must be used within ChapterContentProvider');
  }
  return context;
}

interface ChapterContentProviderProps {
  children: ReactNode;
}

export function ChapterContentProvider({ children }: ChapterContentProviderProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('original');
  const [translationData, setTranslationData] = useState<TranslationData | null>(null);
  const [personalizationData, setPersonalizationData] = useState<PersonalizationData | null>(null);

  const reset = () => {
    setViewMode('original');
    setTranslationData(null);
    setPersonalizationData(null);
  };

  const value: ChapterContentState = {
    viewMode,
    translationData,
    personalizationData,
    setViewMode,
    setTranslationData,
    setPersonalizationData,
    reset,
  };

  return (
    <ChapterContentContext.Provider value={value}>
      {children}
    </ChapterContentContext.Provider>
  );
}
