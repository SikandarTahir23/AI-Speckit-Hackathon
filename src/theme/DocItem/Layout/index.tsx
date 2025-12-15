/**
 * DocItem/Layout Wrapper - Injects chapter features at the TOP
 * This is the correct component to wrap for adding content to doc pages
 */

import React from 'react';
import Layout from '@theme-original/DocItem/Layout';
import { useDoc } from '@docusaurus/plugin-content-docs/client';
import { useAuth } from '@site/src/contexts/AuthContext';
import ChapterPersonalization from '@site/src/components/ChapterPersonalization';
import TranslatedChapter from '@site/src/components/TranslatedChapter';
import type {Props} from '@theme/DocItem/Layout';

console.log('🔧 [DocItem/Layout] Module loaded!');

/**
 * Extract chapter ID from title (e.g., "Chapter 1: Introduction" -> 1)
 */
function extractChapterIdFromTitle(title: string): number | null {
  const match = title.match(/Chapter\s+(\d+)/i);
  return match ? parseInt(match[1], 10) : null;
}

export default function LayoutWrapper(props: Props) {
  // Get doc metadata - should work at Layout level
  const { metadata } = useDoc();

  // Get auth state
  const { user, loading: authLoading } = useAuth();

  // Get chapter ID from frontMatter or title
  const chapterId =
    metadata?.frontMatter?.chapterId ||
    extractChapterIdFromTitle(metadata?.title || '');

  // Debug logging
  console.log('📖 [DocItem/Layout] Rendering:', {
    title: metadata?.title,
    chapterId,
    hasChapterId: !!chapterId,
    authLoading,
    isAuthenticated: !!user,
    userEmail: user?.email || 'none'
  });

  // If no chapter ID, render without features
  if (!chapterId) {
    console.log('⚠️ [DocItem/Layout] No chapter ID found, skipping features');
    return <Layout {...props} />;
  }

  return (
    <>
      {/* CRITICAL: Feature buttons at TOP (before content) */}
      <div style={{
        marginTop: '1rem',
        marginBottom: '2rem',
        padding: '1.5rem',
        background: 'linear-gradient(135deg, rgba(26, 31, 46, 0.5) 0%, rgba(37, 45, 61, 0.5) 100%)',
        border: '2px solid rgba(0, 212, 255, 0.3)',
        borderRadius: '12px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)'
      }}>
        <div style={{
          fontSize: '1rem',
          color: '#00d4ff',
          marginBottom: '1.5rem',
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '1px',
          textShadow: '0 0 10px rgba(0, 212, 255, 0.5)'
        }}>
          📚 Chapter {chapterId} Features
        </div>

        {/* Translation Button - ALWAYS visible */}
        <div style={{ marginBottom: '1rem' }}>
          <TranslatedChapter chapterId={chapterId} />
        </div>

        {/* Personalization Button - Show immediately when auth ready */}
        {authLoading ? (
          <div style={{
            padding: '1.5rem',
            textAlign: 'center',
            color: '#c0c7d4',
            background: 'rgba(37, 45, 61, 0.5)',
            border: '2px solid rgba(0, 212, 255, 0.2)',
            borderRadius: '8px',
            fontSize: '0.95rem'
          }}>
            ⏳ Loading authentication...
          </div>
        ) : (
          <ChapterPersonalization
            chapterId={chapterId}
            isAuthenticated={!!user}
          />
        )}
      </div>

      {/* Original doc layout (content comes after buttons) */}
      <Layout {...props} />
    </>
  );
}
