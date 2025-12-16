/**
 * ChapterContentDisplay Component
 *
 * Renders translated or personalized content based on ChapterContentContext state
 * Shows side-by-side English/Urdu when in translated mode
 * Shows personalized content when in personalized mode
 */

import React, { useState } from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useChapterContent } from '@site/src/contexts/ChapterContentContext';
import styles from './styles.module.css';

type DisplayMode = 'Both' | 'Original' | 'Urdu';

export default function ChapterContentDisplay() {
  const { viewMode, translationData, personalizationData } = useChapterContent();
  const [displayMode, setDisplayMode] = useState<DisplayMode>('Both');

  // Don't render anything if we're in original mode
  if (viewMode === 'original') {
    return null;
  }

  // Render translated content
  if (viewMode === 'translated' && translationData) {
    return (
      <div className={styles.container}>
        <div className={styles.translationHeader}>
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
                <Markdown remarkPlugins={[remarkGfm]}>{translationData.original}</Markdown>
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
                <Markdown remarkPlugins={[remarkGfm]}>{translationData.translated}</Markdown>
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

  // Render personalized content
  if (viewMode === 'personalized' && personalizationData) {
    const { content, level } = personalizationData;
    const levelIcons = {
      Beginner: '🌱',
      Intermediate: '🚀',
      Advanced: '⚡',
    };

    return (
      <div className={styles.container}>
        <div className={styles.personalizationHeader}>
          <div className={styles.badge}>
            <span className={styles.badgeIcon}>{levelIcons[level]}</span>
            <span className={styles.badgeText}>Personalized for {level} Level</span>
          </div>
        </div>

        <div className={styles.personalizedContent}>
          <Markdown remarkPlugins={[remarkGfm]}>{content}</Markdown>
        </div>

        <div className={styles.footer}>
          <p className={styles.footerText}>
            ✨ This content has been personalized for {level} level readers using AI
          </p>
        </div>
      </div>
    );
  }

  return null;
}
