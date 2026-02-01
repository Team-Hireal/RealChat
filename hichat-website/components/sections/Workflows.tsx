'use client';

import { Check } from 'lucide-react';
import { useLanguage } from '../LanguageProvider';

const workflowKeys = [
  'smartTriage',
  'replyQueue',
  'autoPin',
  'aiReplies',
  'messageForwarding',
  'scheduledMessages',
  'autoResponder',
  'contactManagement',
  'dailyDigest',
  'urgencyDetection',
  'groupChatFiltering',
  'spamDetection'
];

export default function Workflows() {
  const { t } = useLanguage();

  return (
    <section className="py-24 bg-gray-50 dark:bg-gray-800" id="workflows">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900 dark:text-white">
            {t('workflows.title')}
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            {t('workflows.subtitle')}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {workflowKeys.map((key, index) => (
            <div
              key={index}
              className="flex items-center gap-3 p-4 rounded-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 hover:border-[#07c160] dark:hover:border-[#07c160] transition-all duration-300 hover:shadow-lg group"
            >
              <div className="flex-shrink-0 w-6 h-6 rounded-full bg-[#07c160]/10 dark:bg-[#07c160]/20 flex items-center justify-center group-hover:bg-[#07c160] transition-colors duration-300">
                <Check className="w-4 h-4 text-[#07c160] group-hover:text-white transition-colors duration-300" />
              </div>
              <span className="text-gray-700 dark:text-gray-300 font-medium">
                {t(`workflows.list.${key}`)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
