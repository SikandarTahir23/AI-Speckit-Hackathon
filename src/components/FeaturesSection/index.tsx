import React from 'react';
import styles from './styles.module.css';
import { features } from '../../data/homepage';

const FeatureIcons = {
  chatbot: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.58 20 4 16.42 4 12C4 7.58 7.58 4 12 4C16.42 4 20 7.58 20 12C20 16.42 16.42 20 12 20Z" fill="currentColor"/>
      <path d="M12 6C9.24 6 7 8.24 7 11C7 12.19 7.47 13.24 8.22 14H7V16H17V14H15.78C16.53 13.24 17 12.19 17 11C17 8.24 14.76 6 12 6ZM12 14C10.34 14 9 12.66 9 11C9 9.34 10.34 8 12 8C13.66 8 15 9.34 15 11C15 12.66 13.66 14 12 14Z" fill="currentColor"/>
    </svg>
  ),
  personalization: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 6C13.1 6 14 6.9 14 8C14 9.1 13.1 10 12 10C10.9 10 10 9.1 10 8C10 6.9 10.9 6 12 6Z" fill="currentColor"/>
      <path d="M20 22H4V20C4 16.69 10 14.9 12 14.9C14 14.9 20 16.69 20 20V22ZM6 20H18C17.6 18.04 13.25 16.9 12 16.9C10.75 16.9 6.4 18.04 6 20Z" fill="currentColor"/>
    </svg>
  ),
  translation: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12.87 15.07L10.33 12.54L10.33 12.53L4.83 7.03L3.41 8.44L9.62 14.65L8.22 16.05L9.63 17.46L11.04 16.05L12.45 17.46L13.86 16.05L15.27 17.46L16.68 16.05L18.09 17.46L19.5 16.05L20.91 17.46L22.33 16.05L19.5 13.22L12.87 15.07ZM17.5 10.5C17.5 11.33 17.17 12.09 16.63 12.63L15.22 11.22C15.76 10.68 16.52 10.5 17.5 10.5Z" fill="currentColor"/>
      <path d="M11.5 3.5C10.12 3.5 9 4.62 9 6H11C11 5.45 11.45 5 12 5C12.55 5 13 5.45 13 6C13 6.55 12.55 7 12 7C11.45 7 11 7.45 11 8H9C9 9.38 10.12 10.5 11.5 10.5C12.88 10.5 14 9.38 14 8C14 6.62 12.88 5.5 11.5 5.5V3.5Z" fill="currentColor"/>
    </svg>
  ),
  authentication: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.58 20 4 16.42 4 12C4 7.58 7.58 4 12 4C16.42 4 20 7.58 20 12C20 16.42 16.42 20 12 20Z" fill="currentColor"/>
      <path d="M12 17C14.76 17 17 14.76 17 12C17 9.24 14.76 7 12 7C9.24 7 7 9.24 7 12C7 14.76 9.24 17 12 17ZM12 9C13.66 9 15 10.34 15 12C15 13.66 13.66 15 12 15C10.34 15 9 13.66 9 12C9 10.34 10.34 9 12 9Z" fill="currentColor"/>
    </svg>
  ),
};

export default function FeaturesSection() {
  return (
    <section className={styles.features} id="features">
      <div className={styles.container}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>An AI-Powered Learning Experience</h2>
          <p className={styles.sectionSubtitle}>
            Our platform integrates cutting-edge AI to create a dynamic and responsive educational environment.
          </p>
        </div>
        <div className={styles.featuresGrid}>
          {features.map((feature, index) => {
            const Icon = FeatureIcons[feature.icon];
            return (
              <div key={index} className={styles.featureCard}>
                <div className={styles.featureIcon}>
                  <Icon />
                </div>
                <h3 className={styles.featureTitle}>{feature.title}</h3>
                <p className={styles.featureDescription}>{feature.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
