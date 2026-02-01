'use client';

import { Download, Plug, Settings, Sparkles } from 'lucide-react';
import { useLanguage } from '../LanguageProvider';

const stepKeys = [
  { icon: Download, key: 'install', color: 'from-blue-500 to-cyan-500' },
  { icon: Plug, key: 'connect', color: 'from-purple-500 to-pink-500' },
  { icon: Settings, key: 'configure', color: 'from-orange-500 to-red-500' },
  { icon: Sparkles, key: 'enjoy', color: 'from-green-500 to-emerald-500' }
];

export default function HowItWorks() {
  const { t } = useLanguage();

  return (
    <section className="py-[180px] bg-white dark:bg-gray-900 flex items-center" id="how-it-works">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900 dark:text-white">
            {t('howItWorks.title')}
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            {t('howItWorks.subtitle')}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {stepKeys.map((step, index) => (
            <div key={index} className="relative">
              {/* Connector line */}
              {index < stepKeys.length - 1 && (
                <div className="hidden lg:block absolute top-16 left-[60%] w-[80%] h-0.5 bg-gradient-to-r from-gray-300 to-gray-200 dark:from-gray-700 dark:to-gray-800"></div>
              )}

              <div className="relative text-center">
                {/* Step number */}
                <div className="absolute -top-4 -left-4 w-8 h-8 rounded-full bg-[#07c160] text-white flex items-center justify-center font-bold text-sm shadow-lg">
                  {index + 1}
                </div>

                {/* Icon */}
                <div className={`w-32 h-32 mx-auto rounded-2xl bg-gradient-to-br ${step.color} flex items-center justify-center mb-6 shadow-xl hover:scale-110 transition-transform duration-300`}>
                  <step.icon className="w-16 h-16 text-white" />
                </div>

                {/* Content */}
                <h3 className="text-2xl font-bold mb-3 text-gray-900 dark:text-white">
                  {t(`howItWorks.steps.${step.key}.title`)}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                  {t(`howItWorks.steps.${step.key}.description`)}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
