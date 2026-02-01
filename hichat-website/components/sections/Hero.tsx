'use client';

import { ArrowRight, Play } from 'lucide-react';
import { useLanguage } from '../LanguageProvider';

export default function Hero() {
  const { t } = useLanguage();

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-[#07c160]/5 via-white to-[#95ec69]/10 dark:from-[#07c160]/10 dark:via-gray-900 dark:to-[#06ad56]/20">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#07c160]/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#95ec69]/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-24 text-center">
        {/* Main headline */}
        <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold mb-6 leading-tight">
          <span className="bg-gradient-to-r from-[#06ad56] via-[#07c160] to-[#95ec69] bg-clip-text text-transparent animate-fade-in">
            {t('hero.title')}
          </span>
        </h1>

        {/* Subheadline */}
        <p className="text-lg sm:text-xl md:text-2xl lg:text-3xl text-gray-700 dark:text-gray-300 mb-12 max-w-4xl mx-auto animate-fade-in-delay leading-relaxed">
          {t('hero.subtitle')}
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16 animate-fade-in-delay-2">
          <button className="group px-8 py-4 bg-[#07c160] hover:bg-[#06ad56] text-white rounded-full font-semibold text-lg transition-all duration-300 flex items-center gap-2 shadow-lg hover:shadow-xl hover:scale-105 w-full sm:w-auto">
            {t('hero.downloadButton')}
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
          <button className="group px-8 py-4 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-[#07c160] border-2 border-[#07c160] rounded-full font-semibold text-lg transition-all duration-300 flex items-center gap-2 shadow-lg hover:shadow-xl w-full sm:w-auto">
            <Play className="w-5 h-5" />
            {t('hero.watchDemo')}
          </button>
        </div>

        {/* Micro-metrics */}
        <div className="flex flex-wrap justify-center gap-6 sm:gap-8 text-sm md:text-base text-gray-600 dark:text-gray-400 animate-fade-in-delay-3">
          <div className="flex items-center gap-2">
            <span className="text-2xl sm:text-3xl font-bold text-[#07c160]">13</span>
            <span>{t('hero.workflows')}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-2xl sm:text-3xl font-bold text-[#07c160]">30{t('hero.dailyBrief')}</span>
            <span></span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-2xl sm:text-3xl font-bold text-[#07c160]">85%</span>
            <span>{t('hero.lessReplies')}</span>
          </div>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 border-2 border-[#07c160] rounded-full flex justify-center">
          <div className="w-1 h-3 bg-[#07c160] rounded-full mt-2 animate-pulse"></div>
        </div>
      </div>
    </section>
  );
}
