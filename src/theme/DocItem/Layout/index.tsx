/**
 * DocItem/Layout Wrapper - Adds ChapterHeader to chapter pages
 * Displays language toggle and personalization controls in header area
 * Shows translated/personalized content when active
 */

import React from 'react';
import Layout from '@theme-original/DocItem/Layout';
import { useDoc } from '@docusaurus/plugin-content-docs/client';
import { ChapterContentProvider } from '@site/src/contexts/ChapterContentContext';
import ChapterHeader from '@site/src/components/ChapterHeader';
import ChapterContentDisplay from '@site/src/components/ChapterContentDisplay';
import type {Props} from '@theme/DocItem/Layout';

console.log('🔧 [DocItem/Layout] Module loaded with ChapterHeader & ContentDisplay!');

/**
 * Extract chapter ID from title (e.g., "Chapter 1: Introduction" -> 1)
 */
function extractChapterIdFromTitle(title: string): number | null {
  const match = title.match(/Chapter\s+(\d+)/i);
  return match ? parseInt(match[1], 10) : null;
}

export default function LayoutWrapper(props: Props) {
  // Get doc metadata
  const { metadata } = useDoc();

  // Get chapter ID from frontMatter or title
  const chapterId =
    metadata?.frontMatter?.chapterId ||
    extractChapterIdFromTitle(metadata?.title || '');

  // Debug logging
  console.log('📖 [DocItem/Layout] Rendering:', {
    title: metadata?.title,
    chapterId,
    hasChapterId: !!chapterId,
  });

  // If no chapter ID, render without header controls
  if (!chapterId) {
    console.log('⚠️ [DocItem/Layout] No chapter ID found, skipping ChapterHeader');
    return <Layout {...props} />;
  }

  return (
    <ChapterContentProvider>
      {/* ChapterHeader - positioned in top right of page */}
      <div style={{
        display: 'flex',
        justifyContent: 'flex-end',
        alignItems: 'center',
        marginBottom: '1.5rem',
        paddingTop: '0.5rem',
      }}>
        <ChapterHeader chapterId={chapterId} />
      </div>

      {/* Original doc layout (breadcrumb, title, content) */}
      <Layout {...props} />

      {/* ChapterContentDisplay - shows translated/personalized content when active */}
      <ChapterContentDisplay />
    </ChapterContentProvider>
  );
}
