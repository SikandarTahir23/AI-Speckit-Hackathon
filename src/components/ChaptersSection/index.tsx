import React from 'react';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';
import { chapters } from '../../data/homepage';
import { FiArrowRight } from 'react-icons/fi';

export default function ChaptersSection() {
  return (
    <section className={styles.chapters} id="chapters">
      <div className={styles.container}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Explore the Curriculum</h2>
          <p className={styles.sectionSubtitle}>
            A comprehensive journey from the fundamentals of robotics to advanced, multi-modal AI systems.
          </p>
        </div>
        <div className={styles.chaptersGrid}>
          {chapters.map((chapter, index) => (
            <Link key={index} to={chapter.link} className={styles.chapterCard}>
              <div className={styles.cardHeader}>
                <div className={styles.chapterNumber}>{chapter.number}</div>
                <div className={styles.chapterTags}>
                  {chapter.tags.map(tag => (
                    <span key={tag} className={styles.tag}>{tag}</span>
                  ))}
                </div>
              </div>
              <h3 className={styles.chapterTitle}>{chapter.title}</h3>
              <p className={styles.chapterDescription}>{chapter.description}</p>
              <div className={styles.cardFooter}>
                <span>Read Chapter</span>
                <FiArrowRight className={styles.arrowIcon} />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
