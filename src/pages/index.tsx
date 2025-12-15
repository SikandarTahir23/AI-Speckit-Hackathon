import React, { useState } from 'react';
import Layout from '@theme/Layout';
import styles from './index.module.css';
import HeroSection from '../components/HeroSection';
import FeaturesSection from '../components/FeaturesSection';
import ChaptersSection from '../components/ChaptersSection';
import ChatbotWidget from '../components/ChatbotWidget';

export default function Home(): JSX.Element {
  const [showChatbot, setShowChatbot] = useState(false);

  return (
    <Layout
      title="Physical AI & Humanoid Robotics"
      description="An interactive textbook powered by AI, personalized learning, translation, and intelligent retrieval."
    >
      <main className={styles.homePage}>
        <HeroSection />
        <FeaturesSection />
        <ChaptersSection />
      </main>
      {showChatbot && <ChatbotWidget />}
      <button
        className={styles.chatbotTrigger}
        onClick={() => setShowChatbot(!showChatbot)}
        aria-label="Toggle chatbot"
      >
        <span className={styles.chatbotIcon}>💬</span>
      </button>
    </Layout>
  );
}
