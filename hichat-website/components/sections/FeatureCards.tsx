'use client';

import { MessageCircle, Bell, Pin, Zap, Brain, Calendar } from 'lucide-react';
import { useLanguage } from '../LanguageProvider';

const featureCardKeys = [
  { icon: MessageCircle, key: 'commandConsole', gradient: 'from-blue-500 to-cyan-500' },
  { icon: Bell, key: 'importantMessages', gradient: 'from-purple-500 to-pink-500' },
  { icon: Pin, key: 'replyQueue', gradient: 'from-orange-500 to-red-500' },
  { icon: Zap, key: 'autoReplies', gradient: 'from-green-500 to-emerald-500' },
  { icon: Brain, key: 'contactMemory', gradient: 'from-indigo-500 to-blue-500' },
  { icon: Calendar, key: 'dailyBrief', gradient: 'from-yellow-500 to-orange-500' }
];

export default function FeatureCards() {
  const { t } = useLanguage();

  return (
    <section className="py-[130px] bg-gradient-to-b from-gray-50 to-white dark:from-gray-800 dark:to-gray-900 flex items-center" id="features">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-3 text-gray-900 dark:text-white">
            {t('featureCards.title')}
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            {t('featureCards.subtitle')}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {featureCardKeys.map((card, index) => (
            <div
              key={index}
              className="group relative overflow-hidden rounded-2xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-transparent transition-all duration-500 hover:shadow-xl hover:-translate-y-1"
            >
              {/* Gradient overlay on hover */}
              <div className={`absolute inset-0 bg-gradient-to-br ${card.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-500`}></div>

              <div className="relative p-6">
                {/* Icon */}
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${card.gradient} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg`}>
                  <card.icon className="w-6 h-6 text-white" />
                </div>

                {/* Content */}
                <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">
                  {t(`featureCards.${card.key}.title`)}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed text-base">
                  {t(`featureCards.${card.key}.description`)}
                </p>

                {/* Decorative element */}
                <div className={`absolute -bottom-2 -right-2 w-24 h-24 bg-gradient-to-br ${card.gradient} opacity-0 group-hover:opacity-10 rounded-full blur-2xl transition-opacity duration-500`}></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
