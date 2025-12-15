/**
 * PersonalizedChapter Component (Hackathon Bonus Feature 2)
 *
 * Displays personalized chapter content with difficulty badge
 * T060-T061: Content display, "Change Level" button
 */

import React from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import styles from './styles.module.css';

interface PersonalizedChapterProps {
  content: string;
  difficultyLevel: string;
  onChangeLevel?: () => void;
}

export default function PersonalizedChapter({
  content,
  difficultyLevel,
  onChangeLevel,
}: PersonalizedChapterProps) {
  const getDifficultyIcon = (level: string) => {
    switch (level) {
      case 'Beginner':
        return '🌱';
      case 'Intermediate':
        return '🚀';
      case 'Advanced':
        return '⚡';
      default:
        return '📖';
    }
  };

  const getDifficultyColor = (level: string) => {
    switch (level) {
      case 'Beginner':
        return '#38a169'; // Green
      case 'Intermediate':
        return '#3182ce'; // Blue
      case 'Advanced':
        return '#d69e2e'; // Orange
      default:
        return '#718096'; // Gray
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div
          className={styles.badge}
          style={{ backgroundColor: getDifficultyColor(difficultyLevel) }}
        >
          <span className={styles.badgeIcon}>{getDifficultyIcon(difficultyLevel)}</span>
          <span className={styles.badgeText}>{difficultyLevel} Level</span>
        </div>

        {onChangeLevel && (
          <button className={styles.changeButton} onClick={onChangeLevel}>
            <span>🔄</span>
            <span>Change Level</span>
          </button>
        )}
      </div>

      <div className={styles.content}>
        <Markdown remarkPlugins={[remarkGfm]}>{content}</Markdown>
      </div>

      <div className={styles.footer}>
        <p className={styles.footerText}>
          ✨ This content has been personalized for {difficultyLevel.toLowerCase()} level readers using AI
        </p>
      </div>
    </div>
  );
}
