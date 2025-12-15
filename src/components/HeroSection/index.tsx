import React from 'react';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';
import { FiArrowRight } from 'react-icons/fi';

export default function HeroSection() {
  return (
    <section className={styles.hero}>
      <div className={styles.grid}></div>
      <div className={styles.container}>
        <div className={styles.heroContent}>
          <h1 className={styles.heroTitle}>
            Master the Future of <span className={styles.highlight}>Intelligent Systems</span>
          </h1>
          <p className={styles.heroDescription}>
            An interactive textbook for the next generation of roboticists and AI pioneers. Dive into Physical AI, humanoid robotics, and digital twin simulation.
          </p>
          <div className={styles.heroButtons}>
            <Link to="/docs/chapter-1-introduction-to-physical-ai" className={`button button--primary ${styles.button}`}>
              Start the Journey <FiArrowRight className={styles.buttonIcon} />
            </Link>
            <Link to="/#features" className={`button button--secondary ${styles.button}`}>
              Explore Features
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
