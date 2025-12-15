/**
 * TranslatedChapter Component (Hackathon Bonus Feature 3)
 *
 * Side-by-side English and Urdu content display
 * T087-T091: Side-by-side layout, display modes, loading, error handling
 */

import React, { useState } from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import styles from './styles.module.css';

interface TranslatedChapterProps {
  chapterId: number;
  onTranslate?: () => void;
}

type DisplayMode = 'Both' | 'Original' | 'Urdu';

export default function TranslatedChapter({ chapterId, onTranslate }: TranslatedChapterProps) {
  const [originalContent, setOriginalContent] = useState<string>('');
  const [translatedContent, setTranslatedContent] = useState<string>('');
  const [displayMode, setDisplayMode] = useState<DisplayMode>('Both');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isTranslated, setIsTranslated] = useState(false);

  // Get API base URL from Docusaurus config
  const API_BASE_URL = (globalThis as any).docusaurus?.siteConfig?.customFields?.API_BASE_URL || 'http://localhost:8000';

  const handleTranslate = async () => {
    setError(null);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/translate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies
        body: JSON.stringify({
          chapter_id: chapterId,
          target_lang: 'ur',
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Translation failed');
      }

      const data = await response.json();
      console.log(`Translation ${data.cached ? 'cache HIT' : 'cache MISS'} - ${data.processing_time_ms}ms`);

      setOriginalContent(data.original_text);
      setTranslatedContent(data.translated_text);
      setIsTranslated(true);

      if (onTranslate) {
        onTranslate();
      }
    } catch (err: any) {
      console.error('Translation error:', err);
      setError(err.message || 'Failed to translate content');
    } finally {
      setLoading(false);
    }
  };

  if (!isTranslated) {
    return (
      <div className={styles.container}>
        <div className={styles.callToAction}>
          <div className={styles.ctaContent}>
            <h3>🌍 Urdu Translation Available</h3>
            <p>Read this chapter in Urdu with side-by-side English comparison</p>
            <button
              className={styles.translateButton}
              onClick={handleTranslate}
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className={styles.spinner}></div>
                  <span>Translating to Urdu...</span>
                </>
              ) : (
                <>
                  <span>🌐</span>
                  <span>Translate to Urdu</span>
                </>
              )}
            </button>
            {error && (
              <div className={styles.errorMessage}>
                <span>⚠️</span>
                <span>{error}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.badge}>
          <span className={styles.badgeIcon}>🌐</span>
          <span className={styles.badgeText}>Urdu Translation</span>
        </div>

        <div className={styles.controls}>
          <span className={styles.label}>Display:</span>
          <div className={styles.toggleGroup}>
            <button
              className={`${styles.toggleButton} ${displayMode === 'Both' ? styles.active : ''}`}
              onClick={() => setDisplayMode('Both')}
            >
              Both
            </button>
            <button
              className={`${styles.toggleButton} ${displayMode === 'Original' ? styles.active : ''}`}
              onClick={() => setDisplayMode('Original')}
            >
              English Only
            </button>
            <button
              className={`${styles.toggleButton} ${displayMode === 'Urdu' ? styles.active : ''}`}
              onClick={() => setDisplayMode('Urdu')}
            >
              Urdu Only
            </button>
          </div>
        </div>
      </div>

      <div className={styles.content}>
        {(displayMode === 'Both' || displayMode === 'Original') && (
          <div className={`${styles.column} ${displayMode === 'Both' ? styles.dual : styles.single}`}>
            <div className={styles.columnHeader}>
              <span className={styles.flag}>🇬🇧</span>
              <span>English Original</span>
            </div>
            <div className={styles.columnContent}>
              <Markdown remarkPlugins={[remarkGfm]}>{originalContent}</Markdown>
            </div>
          </div>
        )}

        {displayMode === 'Both' && <div className={styles.divider}></div>}

        {(displayMode === 'Both' || displayMode === 'Urdu') && (
          <div className={`${styles.column} ${displayMode === 'Both' ? styles.dual : styles.single}`}>
            <div className={styles.columnHeader}>
              <span className={styles.flag}>🇵🇰</span>
              <span>Urdu Translation</span>
            </div>
            <div className={`${styles.columnContent} ${styles.urdu}`}>
              <Markdown remarkPlugins={[remarkGfm]}>{translatedContent}</Markdown>
            </div>
          </div>
        )}
      </div>

      <div className={styles.footer}>
        <p className={styles.footerText}>
          ✨ Translated to Urdu using AI • Technical terms preserved in English for clarity
        </p>
      </div>
    </div>
  );
}
