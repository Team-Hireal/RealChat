'use client';

import { Server, Shield, Lock } from 'lucide-react';
import { useLanguage } from '../LanguageProvider';

export default function Architecture() {
  const { t } = useLanguage();

  return (
    <section className="py-24 bg-white dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900 dark:text-white">
            {t('architecture.title')}
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto mb-6">
            {t('architecture.subtitle')}
          </p>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-4xl mx-auto">
            {t('architecture.description')}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-8 rounded-2xl bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border border-blue-200 dark:border-blue-800">
            <Server className="w-12 h-12 text-blue-600 dark:text-blue-400 mb-4" />
            <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">
              {t('architecture.localProcessing.title')}
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              {t('architecture.localProcessing.description')}
            </p>
          </div>

          <div className="p-8 rounded-2xl bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border border-purple-200 dark:border-purple-800">
            <Shield className="w-12 h-12 text-purple-600 dark:text-purple-400 mb-4" />
            <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">
              {t('architecture.cloudAI.title')}
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              {t('architecture.cloudAI.description')}
            </p>
          </div>

          <div className="p-8 rounded-2xl bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800">
            <Lock className="w-12 h-12 text-green-600 dark:text-green-400 mb-4" />
            <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">
              {t('architecture.encrypted.title')}
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              {t('architecture.encrypted.description')}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
