'use client';

import { MessageSquare, ListChecks, Tag, Pin, Zap, Search } from 'lucide-react';
import { useLanguage } from '../LanguageProvider';

const featureKeys = [
  { icon: MessageSquare, key: 'smartTriage' },
  { icon: ListChecks, key: 'replyQueue' },
  { icon: Tag, key: 'chatLabels' },
  { icon: Pin, key: 'pinControl' },
  { icon: Zap, key: 'autoReplies' },
  { icon: Search, key: 'searchRecall' }
];

export default function Features() {
  const { t } = useLanguage();

  return (
    <section className="py-24 bg-white dark:bg-gray-900" id="features">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900 dark:text-white">
            {t('features.title')}
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            {t('features.subtitle')}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {featureKeys.map((feature, index) => (
            <div
              key={index}
              className="group p-8 rounded-2xl bg-gradient-to-br from-gray-50 to-white dark:from-gray-800 dark:to-gray-900 border border-gray-200 dark:border-gray-700 hover:border-[#07c160] dark:hover:border-[#07c160] transition-all duration-300 hover:shadow-xl hover:-translate-y-1"
            >
              <div className="w-14 h-14 rounded-xl bg-[#07c160]/10 dark:bg-[#07c160]/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <feature.icon className="w-7 h-7 text-[#07c160]" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">
                {t(`features.${feature.key}.title`)}
              </h3>
              <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                {t(`features.${feature.key}.description`)}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
