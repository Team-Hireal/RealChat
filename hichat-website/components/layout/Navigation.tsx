'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { useLanguage } from '../LanguageProvider';
import { Languages } from 'lucide-react';

const navItems = [
  { id: 'intro', href: '#intro' },
  { id: 'features', href: '#features' },
  { id: 'workflows', href: '#workflows' },
  { id: 'how-it-works', href: '#how-it-works' },
  { id: 'download', href: '#download' }
];

export default function Navigation() {
  const [isDark, setIsDark] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [activeSection, setActiveSection] = useState('intro');
  const [indicatorStyle, setIndicatorStyle] = useState({ left: 0, width: 0 });
  const navRefs = useRef<{ [key: string]: HTMLAnchorElement | null }>({});
  const navContainerRef = useRef<HTMLDivElement>(null);
  const { locale, setLocale, t } = useLanguage();

  // Load saved theme preference on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDark(true);
      document.documentElement.classList.add('dark');
    } else {
      setIsDark(false);
      document.documentElement.classList.remove('dark');
      // Set default to light mode if no saved preference
      if (!savedTheme) {
        localStorage.setItem('theme', 'light');
      }
    }
  }, []);

  // Update indicator position whenever active section changes
  useEffect(() => {
    const updateIndicator = () => {
      const activeRef = navRefs.current[activeSection];
      const containerRef = navContainerRef.current;

      if (activeRef && containerRef) {
        const containerRect = containerRef.getBoundingClientRect();
        const activeRect = activeRef.getBoundingClientRect();

        setIndicatorStyle({
          left: activeRect.left - containerRect.left,
          width: activeRect.width
        });
      }
    };

    updateIndicator();
    // Update on window resize
    window.addEventListener('resize', updateIndicator);
    return () => window.removeEventListener('resize', updateIndicator);
  }, [activeSection]);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);

      // Detect active section based on scroll position
      const scrollPosition = window.scrollY;
      const windowHeight = window.innerHeight;

      // Get all sections with their positions
      const sectionPositions = navItems.map(item => {
        let element;
        if (item.href === '#intro') {
          element = document.querySelector('section');
        } else {
          element = document.querySelector(item.href);
        }

        if (element) {
          const rect = element.getBoundingClientRect();
          const absoluteTop = scrollPosition + rect.top;
          const absoluteBottom = absoluteTop + rect.height;

          return {
            id: item.id,
            top: absoluteTop,
            bottom: absoluteBottom,
            height: rect.height
          };
        }
        return null;
      }).filter(Boolean);

      // Find which section is most visible in the viewport
      const navHeight = 80;
      const viewportTop = scrollPosition + navHeight + 50; // Add offset for better detection

      // Check if we're at the very top
      if (scrollPosition < 100) {
        setActiveSection('intro');
        return;
      }

      // Find the section that contains the viewport top position
      let foundSection = null;
      for (const section of sectionPositions) {
        if (section && viewportTop >= section.top && viewportTop < section.bottom) {
          foundSection = section.id;
          break;
        }
      }

      // If no section found, find the closest one
      if (!foundSection && sectionPositions.length > 0) {
        const closest = sectionPositions.reduce((prev, curr) => {
          if (!prev || !curr) return prev || curr;
          const prevDist = Math.abs(prev.top - viewportTop);
          const currDist = Math.abs(curr.top - viewportTop);
          return currDist < prevDist ? curr : prev;
        });
        if (closest) {
          foundSection = closest.id;
        }
      }

      if (foundSection && foundSection !== activeSection) {
        setActiveSection(foundSection);
      }
    };

    handleScroll(); // Initial check
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [activeSection]);

  const toggleTheme = () => {
    const newTheme = !isDark;
    setIsDark(newTheme);
    document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', newTheme ? 'dark' : 'light');
  };

  const scrollToSection = (e: React.MouseEvent<HTMLAnchorElement>, sectionId: string) => {
    e.preventDefault();

    if (sectionId === '#intro') {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
      setActiveSection('intro');
    } else {
      const element = document.querySelector(sectionId);
      if (element) {
        const navHeight = 80;
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - navHeight;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    }
  };

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-white/80 dark:bg-[#1a1a1a]/80 backdrop-blur-lg shadow-sm'
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-br from-[#07c160] to-[#95ec69] rounded-2xl flex items-center justify-center">
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
            </div>
            <span className="text-xl font-bold text-gray-900 dark:text-white">
              {t('brandName')}
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center relative" ref={navContainerRef}>
            <div className="flex items-center space-x-8 relative pb-2">
              {navItems.map((item) => (
                <a
                  key={item.id}
                  ref={(el) => { navRefs.current[item.id] = el; }}
                  href={item.href}
                  onClick={(e) => scrollToSection(e, item.href)}
                  className={`text-gray-700 dark:text-gray-300 hover:text-[#07c160] dark:hover:text-[#07c160] transition-colors cursor-pointer font-medium py-2 relative ${
                    activeSection === item.id ? 'text-[#07c160] dark:text-[#07c160]' : ''
                  }`}
                >
                  {t(`nav.${item.id === 'how-it-works' ? 'howItWorks' : item.id}`)}
                </a>
              ))}

              {/* Green indicator - more prominent */}
              <div
                className="absolute bottom-0 h-1 bg-[#07c160] rounded-full transition-all duration-300 ease-out shadow-lg"
                style={{
                  left: `${indicatorStyle.left}px`,
                  width: `${indicatorStyle.width}px`,
                  transform: 'translateZ(0)' // Force GPU acceleration
                }}
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-3">
            {/* Language Toggle */}
            <button
              onClick={() => setLocale(locale === 'en' ? 'zh' : 'en')}
              className="p-2 rounded-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors flex items-center space-x-1"
              aria-label="Toggle language"
              title={locale === 'en' ? 'Switch to Chinese' : '切换到英文'}
            >
              <Languages className="w-5 h-5 text-gray-700 dark:text-gray-300" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {locale === 'en' ? '中文' : 'EN'}
              </span>
            </button>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
              aria-label="Toggle theme"
            >
            {isDark ? (
              <svg
                className="w-5 h-5 text-yellow-500"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
                  clipRule="evenodd"
                />
              </svg>
            ) : (
              <svg
                className="w-5 h-5 text-gray-700"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
              </svg>
            )}
          </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
