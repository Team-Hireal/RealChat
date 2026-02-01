'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import enMessages from '../messages/en.json';
import zhMessages from '../messages/zh.json';

type Locale = 'en' | 'zh';
type Messages = typeof enMessages;

interface LanguageContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const messages: Record<Locale, Messages> = {
  en: enMessages,
  zh: zhMessages,
};

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>('zh'); // Default to Chinese

  // Load saved language preference on mount
  useEffect(() => {
    const saved = localStorage.getItem('language') as Locale;
    if (saved && (saved === 'en' || saved === 'zh')) {
      setLocaleState(saved);
    } else {
      // Set default to Chinese if no saved preference
      setLocaleState('zh');
      localStorage.setItem('language', 'zh');
    }
  }, []);

  const setLocale = (newLocale: Locale) => {
    setLocaleState(newLocale);
    localStorage.setItem('language', newLocale);
  };

  // Translation function with nested key support
  const t = (key: string): string => {
    const keys = key.split('.');
    let value: any = messages[locale];

    for (const k of keys) {
      if (value && typeof value === 'object') {
        value = value[k];
      } else {
        return key; // Return key if translation not found
      }
    }

    return typeof value === 'string' ? value : key;
  };

  return (
    <LanguageContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
