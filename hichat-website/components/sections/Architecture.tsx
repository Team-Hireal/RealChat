'use client';

import { Shield, Database, Lock } from 'lucide-react';

export default function Architecture() {
  return (
    <section className="py-24 bg-white dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900 dark:text-white">
            Hybrid AI Architecture
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            Privacy-first design with local processing and optional cloud features
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <div className="p-8 rounded-2xl bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border border-blue-200 dark:border-blue-800">
            <Database className="w-12 h-12 text-blue-600 dark:text-blue-400 mb-4" />
            <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">
              Local Storage
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              All your data stays on your device, encrypted at rest. You own your information.
            </p>
          </div>

          <div className="p-8 rounded-2xl bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border border-purple-200 dark:border-purple-800">
            <Shield className="w-12 h-12 text-purple-600 dark:text-purple-400 mb-4" />
            <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">
              Hybrid Engine
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Local-first processing with optional cloud AI for advanced features. You choose.
            </p>
          </div>

          <div className="p-8 rounded-2xl bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800">
            <Lock className="w-12 h-12 text-green-600 dark:text-green-400 mb-4" />
            <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">
              Zero-Backend Default
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Works completely offline by default. No servers, no tracking, no data collection.
            </p>
          </div>
        </div>

        {/* Architecture diagram */}
        <div className="relative p-12 rounded-3xl bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 border-2 border-gray-200 dark:border-gray-700">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="flex-1 text-center p-6 bg-white dark:bg-gray-800 rounded-2xl shadow-lg">
              <div className="text-4xl mb-2">💻</div>
              <div className="font-bold text-gray-900 dark:text-white">Your Device</div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">Local Processing</div>
            </div>

            <div className="flex items-center gap-4">
              <div className="w-12 h-0.5 bg-[#07c160]"></div>
              <div className="text-[#07c160] font-bold">Encrypted</div>
              <div className="w-12 h-0.5 bg-[#07c160]"></div>
            </div>

            <div className="flex-1 text-center p-6 bg-white dark:bg-gray-800 rounded-2xl shadow-lg opacity-50">
              <div className="text-4xl mb-2">☁️</div>
              <div className="font-bold text-gray-900 dark:text-white">Cloud AI</div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">Optional</div>
            </div>
          </div>

          <div className="mt-8 text-center text-sm text-gray-600 dark:text-gray-400">
            <p className="font-semibold mb-2">You control what data leaves your device</p>
            <p>Cloud features are opt-in and can be disabled at any time</p>
          </div>
        </div>
      </div>
    </section>
  );
}
