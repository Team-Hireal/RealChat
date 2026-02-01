'use client';

import { Download, FileText, ArrowRight } from 'lucide-react';

export default function CTA() {
  return (
    <section className="py-24 bg-gradient-to-br from-[#07c160]/10 via-wechat-green-light/5 to-white dark:from-[#07c160]/20 dark:via-wechat-green-dark/10 dark:to-gray-900">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900 dark:text-white">
            Get Started
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            Choose your platform and start supercharging your WeChat today
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Download card */}
          <div className="group relative overflow-hidden rounded-3xl bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 hover:border-[#07c160] dark:hover:border-[#07c160] transition-all duration-500 hover:shadow-2xl hover:-translate-y-2">
            <div className="absolute inset-0 bg-gradient-to-br from-[#07c160] to-[#06ad56] opacity-0 group-hover:opacity-5 transition-opacity duration-500"></div>

            <div className="relative p-10">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#07c160] to-[#06ad56] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-xl">
                <Download className="w-10 h-10 text-white" />
              </div>

              <h3 className="text-3xl font-bold mb-4 text-gray-900 dark:text-white">
                Download
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6 text-lg">
                Get the desktop companion for Mac or Windows. Free and open source.
              </p>

              <div className="space-y-3 mb-8">
                <button className="w-full px-6 py-4 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-xl font-semibold hover:bg-gray-800 dark:hover:bg-gray-100 transition-all duration-300 flex items-center justify-between group/btn">
                  <span>Download for Mac</span>
                  <ArrowRight className="w-5 h-5 group-hover/btn:translate-x-1 transition-transform" />
                </button>
                <button className="w-full px-6 py-4 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-xl font-semibold hover:bg-gray-800 dark:hover:bg-gray-100 transition-all duration-300 flex items-center justify-between group/btn">
                  <span>Download for Windows</span>
                  <ArrowRight className="w-5 h-5 group-hover/btn:translate-x-1 transition-transform" />
                </button>
              </div>

              <p className="text-sm text-gray-500 dark:text-gray-500">
                Version 1.0.0 • macOS 11+ • Windows 10+
              </p>
            </div>
          </div>

          {/* Docs card */}
          <div className="group relative overflow-hidden rounded-3xl bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 hover:border-[#07c160] dark:hover:border-[#07c160] transition-all duration-500 hover:shadow-2xl hover:-translate-y-2">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-500 opacity-0 group-hover:opacity-5 transition-opacity duration-500"></div>

            <div className="relative p-10">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-xl">
                <FileText className="w-10 h-10 text-white" />
              </div>

              <h3 className="text-3xl font-bold mb-4 text-gray-900 dark:text-white">
                Documentation
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6 text-lg">
                Learn how to use HiChat, explore workflows, and customize your setup.
              </p>

              <div className="space-y-4 mb-8">
                <a href="#" className="block text-[#07c160] hover:text-[#06ad56] font-semibold flex items-center gap-2 group/link">
                  <span>Quick Start Guide</span>
                  <ArrowRight className="w-4 h-4 group-hover/link:translate-x-1 transition-transform" />
                </a>
                <a href="#" className="block text-[#07c160] hover:text-[#06ad56] font-semibold flex items-center gap-2 group/link">
                  <span>Workflow Library</span>
                  <ArrowRight className="w-4 h-4 group-hover/link:translate-x-1 transition-transform" />
                </a>
                <a href="#" className="block text-[#07c160] hover:text-[#06ad56] font-semibold flex items-center gap-2 group/link">
                  <span>API Reference</span>
                  <ArrowRight className="w-4 h-4 group-hover/link:translate-x-1 transition-transform" />
                </a>
                <a href="#" className="block text-[#07c160] hover:text-[#06ad56] font-semibold flex items-center gap-2 group/link">
                  <span>View on GitHub</span>
                  <ArrowRight className="w-4 h-4 group-hover/link:translate-x-1 transition-transform" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
