/**
 * Custom Footer Component
 * Modern, futuristic design for Physical AI & Humanoid Robotics platform
 */

import React, { JSX } from 'react';
import styles from './styles.module.css';

export default function Footer(): JSX.Element {
  const currentYear = new Date().getFullYear();

  return (
    <footer className={styles.footer}>
      <div className={styles.footerContainer}>
        {/* Main Content: Left (Brand) + Right (Social) */}
        <div className={styles.footerMain}>
          {/* Left Side: Project Title & Tagline */}
          <div className={styles.footerBrand}>
            <h3 className={styles.footerTitle}>
              Physical AI & Humanoid Robotics
            </h3>
            <p className={styles.footerTagline}>
              An interactive learning platform for Physical AI and Robotics.
            </p>
          </div>

          {/* Right Side: Social Media Icons */}
          <div className={styles.footerSocial}>
            <a
              href="https://github.com/SikandarTahir23/AI-Speckit-Hackathon"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.socialLink}
              aria-label="GitHub"
            >
              <svg
                className={styles.socialIcon}
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" />
              </svg>
            </a>

            <a
              href="https://www.linkedin.com/in/sikandar-tahir-356a56273/"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.socialLink}
              aria-label="LinkedIn"
            >
              <svg
                className={styles.socialIcon}
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" />
                <rect x="2" y="9" width="4" height="12" />
                <circle cx="4" cy="4" r="2" />
              </svg>
            </a>

            {/* <a
              href="https://www.facebook.com/Arain.Boyz380"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.socialLink}
              aria-label="Facebook"
            >
              <svg
                className={styles.socialIcon}
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z" />
              </svg>
            </a> */}
          </div>
        </div>

        {/* Bottom: Copyright */}
        <div className={styles.footerBottom}>
          <p className={styles.footerCopyright}>
            © {currentYear} Physical AI & Humanoid Robotics. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
