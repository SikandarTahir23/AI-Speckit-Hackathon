import React, { useState, useRef, useEffect } from 'react';
import styles from './styles.module.css';
import { useAuth } from '../../contexts/AuthContext';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: Date;
}

interface Citation {
  chapter: string;
  section?: string;
  paragraph?: number;
}

const API_BASE_URL = 'http://localhost:8000';

export default function ChatbotWidget(): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // T034: Use auth context to display user state
  const { user } = useAuth();

  // Initial greeting when opened
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([
        {
          role: 'assistant',
          content: '👋 Hello! I\'m your Physical AI & Humanoid Robotics assistant.\n\nAsk me anything about:\n• Actuators and control systems\n• Sensors and perception\n• Robot kinematics and dynamics\n• Human-robot interaction\n\nI can also answer general robotics questions!',
          timestamp: new Date(),
        },
      ]);
    }
  }, [isOpen, messages.length]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: input,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      // Save session ID
      if (!sessionId) {
        setSessionId(data.session_id);
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.answer,
        citations: data.citations || [],
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);

      const errorMessage: Message = {
        role: 'assistant',
        content: '❌ Sorry, I encountered an error. Please ensure the backend API is running at http://localhost:8000',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      {/* Floating Chat Icon */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className={styles.chatbotTrigger}
          aria-label="Open chatbot"
        >
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          <span className={styles.chatbotBadge}>AI</span>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className={styles.chatbotContainer}>
          {/* Header */}
          <div className={styles.chatbotHeader}>
            <div className={styles.chatbotHeaderContent}>
              <div className={styles.chatbotHeaderIcon}>🤖</div>
              <div>
                <h3>Physical AI Assistant</h3>
                <p>Powered by RAG + OpenAI</p>
                {/* T034: Display auth state */}
                <p className={styles.authStatus}>
                  {user ? (
                    <>✓ Logged in as: <strong>{user.email}</strong></>
                  ) : (
                    <>ℹ️ Sign in for personalized features</>
                  )}
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className={styles.chatbotClose}
              aria-label="Close chatbot"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>

          {/* Messages */}
          <div className={styles.chatbotMessages}>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`${styles.chatbotMessage} ${
                  msg.role === 'user' ? styles.chatbotMessageUser : styles.chatbotMessageAssistant
                }`}
              >
                <div className={styles.chatbotMessageContent}>
                  {msg.content.split('\n').map((line, i) => {
                    // Render General AI Answer badge
                    if (line.includes('[General AI Answer]')) {
                      return (
                        <div key={i} className={styles.generalAiBadge}>
                          General AI Answer
                        </div>
                      );
                    }
                    // Skip markdown bold markers
                    if (line.startsWith('**') && line.endsWith('**')) {
                      return null;
                    }
                    return line ? <p key={i}>{line}</p> : <br key={i} />;
                  })}
                </div>

                {/* Citations */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className={styles.chatbotCitations}>
                    <strong>📚 Sources:</strong>
                    <ul>
                      {msg.citations.slice(0, 3).map((cite, i) => (
                        <li key={i}>
                          {cite.chapter}
                          {cite.section && ` - ${cite.section}`}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className={styles.chatbotMessageTime}>
                  {msg.timestamp.toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className={`${styles.chatbotMessage} ${styles.chatbotMessageAssistant}`}>
                <div className={styles.chatbotLoading}>
                  <div className={styles.spinner} />
                  <span>Thinking...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className={styles.chatbotInputContainer}>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about robotics, actuators, sensors..."
              className={styles.chatbotInput}
              rows={2}
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              className={styles.chatbotSend}
              aria-label="Send message"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </>
  );
}
