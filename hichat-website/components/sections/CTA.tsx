'use client';

import { Download, FileText } from 'lucide-react';
import { useLanguage } from '../LanguageProvider';

export default function CTA() {
  const { t } = useLanguage();

  return (
    <section className="py-40 bg-gradient-to-br from-[#07c160]/10 via-[#95ec69]/5 to-white dark:from-[#07c160]/20 dark:via-[#06ad56]/10 dark:to-gray-900" id="download">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900 dark:text-white">
            {t('cta.title')}
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            {t('cta.subtitle')}
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-8">
          <a
            href="/application"
            className="group px-10 py-5 bg-[#07c160] hover:bg-[#06ad56] text-white rounded-full font-semibold text-xl transition-all duration-300 flex items-center gap-3 shadow-xl hover:shadow-2xl hover:scale-105"
          >
            <Download className="w-6 h-6" />
            {t('cta.getStarted')}
          </a>
        </div>

        <div className="text-center">
          <a
            href="#docs"
            className="inline-flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-[#07c160] dark:hover:text-[#07c160] transition-colors font-medium"
          >
            <FileText className="w-5 h-5" />
            {t('cta.viewDocs')}
          </a>
          <p className="mt-4 text-sm text-gray-500 dark:text-gray-500">
            {t('cta.freeTrial')}
          </p>
        </div>
      </div>
    </section>
  );
}
