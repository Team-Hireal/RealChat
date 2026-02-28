'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Terminal, Download, Play, CheckCircle, AlertCircle, Apple } from 'lucide-react';
import { useLanguage } from '@/components/LanguageProvider';

const GITHUB_RELEASE_URL = 'https://github.com/Team-Hireal/RealChat/releases/download/v1.0.0/RealChat-1.0.0-arm64.dmg';

export default function ApplicationPage() {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState<'download' | 'quick' | 'docker' | 'manual'>('download');

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-[#07c160] transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            {t('application.backToHome')}
          </Link>
        </div>
      </div>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-[#06ad56] via-[#07c160] to-[#95ec69] bg-clip-text text-transparent">
            {t('application.title')}
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            {t('application.subtitle')}
          </p>
        </div>

        {/* Installation Method Tabs */}
        <div className="flex justify-center gap-4 mb-12">
          <button
            onClick={() => setActiveTab('download')}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'download'
                ? 'bg-[#07c160] text-white shadow-lg'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            {t('application.downloadApp') || 'Download App'}
          </button>
          <button
            onClick={() => setActiveTab('quick')}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'quick'
                ? 'bg-[#07c160] text-white shadow-lg'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            {t('application.quickStart')}
          </button>
          <button
            onClick={() => setActiveTab('docker')}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'docker'
                ? 'bg-[#07c160] text-white shadow-lg'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            {t('application.dockerSetup')}
          </button>
          <button
            onClick={() => setActiveTab('manual')}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'manual'
                ? 'bg-[#07c160] text-white shadow-lg'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            {t('application.manualSetup')}
          </button>
        </div>

        {/* Content Sections */}
        <div className="max-w-4xl mx-auto">
          {/* Download App */}
          {activeTab === 'download' && (
            <div className="space-y-8 animate-fade-in">
              <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg border border-gray-200 dark:border-gray-700">
                <h2 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white flex items-center gap-3">
                  <Apple className="w-8 h-8 text-[#07c160]" />
                  Download RealChat for macOS
                </h2>

                <div className="space-y-6">
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#07c160] text-white flex items-center justify-center font-bold">
                      1
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">Download the DMG</h3>
                      <a
                        href={GITHUB_RELEASE_URL}
                        className="inline-flex items-center gap-2 px-6 py-3 bg-[#07c160] hover:bg-[#06ad56] text-white rounded-lg font-medium transition-colors"
                      >
                        <Download className="w-5 h-5" />
                        Download RealChat-1.0.0-arm64.dmg
                      </a>
                      <p className="mt-3 text-gray-600 dark:text-gray-400">
                        File size: ~122 MB (Apple Silicon)
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#07c160] text-white flex items-center justify-center font-bold">
                      2
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">Install the App</h3>
                      <ol className="list-decimal list-inside text-gray-600 dark:text-gray-400 space-y-2">
                        <li>Open the downloaded DMG file</li>
                        <li>Drag "RealChat" to your Applications folder</li>
                        <li>Launch RealChat from Applications</li>
                      </ol>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#07c160] text-white flex items-center justify-center font-bold">
                      3
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">Grant Accessibility Permissions</h3>
                      <p className="text-gray-600 dark:text-gray-400 mb-3">
                        On first launch, you'll be prompted to grant accessibility permissions. This is required for RealChat to detect WeChat messages.
                      </p>
                      <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 border border-yellow-200 dark:border-yellow-800">
                        <p className="text-yellow-800 dark:text-yellow-200 text-sm">
                          <strong>Note:</strong> Go to System Settings → Privacy & Security → Accessibility to enable manually if prompted doesn't appear.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* System Requirements */}
              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-2xl p-6 border border-blue-200 dark:border-blue-800">
                <h3 className="text-lg font-semibold mb-4 text-blue-900 dark:text-blue-100 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5" />
                  System Requirements
                </h3>
                <ul className="space-y-2 text-blue-800 dark:text-blue-200">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4" />
                    macOS 12.0 or later (Monterey or newer)
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4" />
                    Apple Silicon (M1/M2/M3) Mac
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4" />
                    WeChat for Mac installed
                  </li>
                </ul>
              </div>
            </div>
          )}

          {/* Quick Start */}
          {activeTab === 'quick' && (
            <div className="space-y-8 animate-fade-in">
              <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg border border-gray-200 dark:border-gray-700">
                <h2 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white flex items-center gap-3">
                  <Play className="w-8 h-8 text-[#07c160]" />
                  {t('application.quickStartGuide')}
                </h2>

                <div className="space-y-6">
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#07c160] text-white flex items-center justify-center font-bold">
                      1
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">{t('application.cloneRepo')}</h3>
                      <div className="bg-gray-900 dark:bg-black rounded-lg p-4 font-mono text-sm text-gray-100 overflow-x-auto">
                        <code>git clone https://github.com/yourusername/realchat.git<br/>cd realchat</code>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#07c160] text-white flex items-center justify-center font-bold">
                      2
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">{t('application.runQuickStart')}</h3>
                      <div className="bg-gray-900 dark:bg-black rounded-lg p-4 font-mono text-sm text-gray-100 overflow-x-auto">
                        <code>chmod +x quick-start.sh<br/>./quick-start.sh</code>
                      </div>
                      <p className="mt-3 text-gray-600 dark:text-gray-400">
                        {t('application.quickStartDesc')}
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#07c160] text-white flex items-center justify-center font-bold">
                      3
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">{t('application.accessApp')}</h3>
                      <p className="text-gray-600 dark:text-gray-400 mb-3">
                        {t('application.accessAppDesc')}
                      </p>
                      <a
                        href="http://localhost:5001"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 px-6 py-3 bg-[#07c160] hover:bg-[#06ad56] text-white rounded-lg font-medium transition-colors"
                      >
                        <Terminal className="w-5 h-5" />
                        {t('application.openRealChat')}
                      </a>
                    </div>
                  </div>
                </div>
              </div>

              {/* Prerequisites */}
              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-2xl p-6 border border-blue-200 dark:border-blue-800">
                <h3 className="text-lg font-semibold mb-4 text-blue-900 dark:text-blue-100 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5" />
                  {t('application.prerequisites')}
                </h3>
                <ul className="space-y-2 text-blue-800 dark:text-blue-200">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4" />
                    {t('application.prereq1')}
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4" />
                    {t('application.prereq2')}
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4" />
                    {t('application.prereq3')}
                  </li>
                </ul>
              </div>
            </div>
          )}

          {/* Docker Setup */}
          {activeTab === 'docker' && (
            <div className="space-y-8 animate-fade-in">
              <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg border border-gray-200 dark:border-gray-700">
                <h2 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white flex items-center gap-3">
                  <Terminal className="w-8 h-8 text-[#07c160]" />
                  {t('application.dockerSetupGuide')}
                </h2>

                <div className="space-y-6">
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#07c160] text-white flex items-center justify-center font-bold">
                      1
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">{t('application.installDocker')}</h3>
                      <p className="text-gray-600 dark:text-gray-400 mb-3">
                        {t('application.installDockerDesc')}
                      </p>
                      <div className="flex gap-3">
                        <a
                          href="https://docs.docker.com/desktop/install/mac-install/"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-gray-700 dark:text-gray-300 transition-colors"
                        >
                          macOS
                        </a>
                        <a
                          href="https://docs.docker.com/desktop/install/windows-install/"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-gray-700 dark:text-gray-300 transition-colors"
                        >
                          Windows
                        </a>
                        <a
                          href="https://docs.docker.com/desktop/install/linux-install/"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-gray-700 dark:text-gray-300 transition-colors"
                        >
                          Linux
                        </a>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#07c160] text-white flex items-center justify-center font-bold">
                      2
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">{t('application.configureEnv')}</h3>
                      <div className="bg-gray-900 dark:bg-black rounded-lg p-4 font-mono text-sm text-gray-100 overflow-x-auto">
                        <code>cp .env.example .env<br/>nano .env</code>
                      </div>
                      <p className="mt-3 text-gray-600 dark:text-gray-400">
                        {t('application.configureEnvDesc')}
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#07c160] text-white flex items-center justify-center font-bold">
                      3
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">{t('application.startServices')}</h3>
                      <div className="bg-gray-900 dark:bg-black rounded-lg p-4 font-mono text-sm text-gray-100 overflow-x-auto">
                        <code>./start.sh</code>
                      </div>
                      <p className="mt-3 text-gray-600 dark:text-gray-400">
                        {t('application.startServicesDesc')}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Manual Setup */}
          {activeTab === 'manual' && (
            <div className="space-y-8 animate-fade-in">
              <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg border border-gray-200 dark:border-gray-700">
                <h2 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white flex items-center gap-3">
                  <Download className="w-8 h-8 text-[#07c160]" />
                  {t('application.manualSetupGuide')}
                </h2>

                <div className="space-y-6">
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#07c160] text-white flex items-center justify-center font-bold">
                      1
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">{t('application.installPython')}</h3>
                      <div className="bg-gray-900 dark:bg-black rounded-lg p-4 font-mono text-sm text-gray-100 overflow-x-auto">
                        <code>python3 -m venv venv<br/>source venv/bin/activate<br/>pip install -r requirements.txt</code>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#07c160] text-white flex items-center justify-center font-bold">
                      2
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">{t('application.installNode')}</h3>
                      <div className="bg-gray-900 dark:bg-black rounded-lg p-4 font-mono text-sm text-gray-100 overflow-x-auto">
                        <code>cd frontend<br/>npm install<br/>npm run build</code>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#07c160] text-white flex items-center justify-center font-bold">
                      3
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">{t('application.startApp')}</h3>
                      <div className="bg-gray-900 dark:bg-black rounded-lg p-4 font-mono text-sm text-gray-100 overflow-x-auto">
                        <code>python app.py</code>
                      </div>
                      <p className="mt-3 text-gray-600 dark:text-gray-400">
                        {t('application.startAppDesc')}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Support Section */}
        <div className="max-w-4xl mx-auto mt-12">
          <div className="bg-gradient-to-br from-[#07c160]/10 to-[#95ec69]/10 dark:from-[#07c160]/20 dark:to-[#06ad56]/20 rounded-2xl p-8 text-center">
            <h3 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
              {t('application.needHelp')}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              {t('application.needHelpDesc')}
            </p>
            <div className="flex justify-center gap-4">
              <a
                href="https://github.com/yourusername/realchat"
                target="_blank"
                rel="noopener noreferrer"
                className="px-6 py-3 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium transition-colors border border-gray-200 dark:border-gray-700"
              >
                {t('application.viewOnGitHub')}
              </a>
              <a
                href="https://github.com/yourusername/realchat/issues"
                target="_blank"
                rel="noopener noreferrer"
                className="px-6 py-3 bg-[#07c160] hover:bg-[#06ad56] text-white rounded-lg font-medium transition-colors"
              >
                {t('application.reportIssue')}
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
