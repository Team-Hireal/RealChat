'use client';

import { Check, X, Info, AlertCircle, ArrowRight, Download, Star } from 'lucide-react';

export default function ComponentShowcase() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-5xl font-bold mb-4 text-gray-900 dark:text-white">
          Component Showcase
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 mb-16">
          All design components used in the HiChat website
        </p>

        {/* Buttons */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8 text-gray-900 dark:text-white">Buttons</h2>
          <div className="flex flex-wrap gap-4">
            <button className="px-6 py-3 bg-wechat-green hover:bg-wechat-green-dark text-white rounded-full font-semibold transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105">
              Primary Button
            </button>
            <button className="px-6 py-3 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-wechat-green border-2 border-wechat-green rounded-full font-semibold transition-all duration-300">
              Secondary Button
            </button>
            <button className="px-6 py-3 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-xl font-semibold hover:bg-gray-800 dark:hover:bg-gray-100 transition-all duration-300 flex items-center gap-2">
              <Download className="w-5 h-5" />
              With Icon
            </button>
            <button className="px-6 py-3 bg-gradient-to-r from-wechat-green to-wechat-green-dark text-white rounded-full font-semibold hover:shadow-xl transition-all duration-300">
              Gradient Button
            </button>
          </div>
        </section>

        {/* Cards */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8 text-gray-900 dark:text-white">Cards</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 hover:border-wechat-green transition-all duration-300 hover:shadow-xl">
              <div className="w-12 h-12 bg-wechat-green/10 rounded-xl flex items-center justify-center mb-4">
                <Check className="w-6 h-6 text-wechat-green" />
              </div>
              <h3 className="text-xl font-bold mb-2 text-gray-900 dark:text-white">Basic Card</h3>
              <p className="text-gray-600 dark:text-gray-400">Simple card with icon and text content.</p>
            </div>

            <div className="p-6 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 rounded-2xl border border-blue-200 dark:border-blue-800">
              <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center mb-4">
                <Info className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold mb-2 text-gray-900 dark:text-white">Gradient Card</h3>
              <p className="text-gray-600 dark:text-gray-400">Card with gradient background.</p>
            </div>

            <div className="group p-6 bg-white dark:bg-gray-800 rounded-2xl border-2 border-gray-200 dark:border-gray-700 hover:border-wechat-green transition-all duration-300 hover:shadow-2xl hover:-translate-y-2">
              <div className="w-12 h-12 bg-gradient-to-br from-wechat-green to-wechat-green-dark rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Star className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold mb-2 text-gray-900 dark:text-white">Hover Card</h3>
              <p className="text-gray-600 dark:text-gray-400">Card with hover animations.</p>
            </div>
          </div>
        </section>

        {/* Badges */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8 text-gray-900 dark:text-white">Badges</h2>
          <div className="flex flex-wrap gap-4">
            <span className="px-4 py-2 bg-wechat-green text-white rounded-full text-sm font-bold">
              Primary Badge
            </span>
            <span className="px-4 py-2 bg-blue-500 text-white rounded-full text-sm font-bold">
              Info Badge
            </span>
            <span className="px-4 py-2 bg-green-500 text-white rounded-full text-sm font-bold flex items-center gap-2">
              <Check className="w-4 h-4" />
              Success
            </span>
            <span className="px-4 py-2 bg-red-500 text-white rounded-full text-sm font-bold flex items-center gap-2">
              <X className="w-4 h-4" />
              Error
            </span>
            <span className="px-4 py-2 bg-yellow-500 text-white rounded-full text-sm font-bold flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              Warning
            </span>
          </div>
        </section>

        {/* Typography */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8 text-gray-900 dark:text-white">Typography</h2>
          <div className="space-y-4">
            <h1 className="text-6xl font-bold text-gray-900 dark:text-white">Heading 1</h1>
            <h2 className="text-5xl font-bold text-gray-900 dark:text-white">Heading 2</h2>
            <h3 className="text-4xl font-bold text-gray-900 dark:text-white">Heading 3</h3>
            <h4 className="text-3xl font-bold text-gray-900 dark:text-white">Heading 4</h4>
            <p className="text-xl text-gray-600 dark:text-gray-400">Large paragraph text</p>
            <p className="text-base text-gray-600 dark:text-gray-400">Regular paragraph text</p>
            <p className="text-sm text-gray-500 dark:text-gray-500">Small text</p>
          </div>
        </section>

        {/* Gradients */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8 text-gray-900 dark:text-white">Gradient Text</h2>
          <div className="space-y-4">
            <h1 className="text-6xl font-bold bg-gradient-to-r from-wechat-green-dark via-wechat-green to-wechat-green-light bg-clip-text text-transparent">
              WeChat Green Gradient
            </h1>
            <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
              Blue to Purple
            </h1>
            <h1 className="text-6xl font-bold bg-gradient-to-r from-orange-500 to-red-500 bg-clip-text text-transparent">
              Orange to Red
            </h1>
          </div>
        </section>

        {/* Icons */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8 text-gray-900 dark:text-white">Icon Containers</h2>
          <div className="flex flex-wrap gap-6">
            <div className="w-16 h-16 bg-wechat-green rounded-2xl flex items-center justify-center shadow-xl">
              <Check className="w-8 h-8 text-white" />
            </div>
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center shadow-xl">
              <Info className="w-8 h-8 text-white" />
            </div>
            <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-xl">
              <Star className="w-8 h-8 text-white" />
            </div>
            <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-500 rounded-2xl flex items-center justify-center shadow-xl">
              <AlertCircle className="w-8 h-8 text-white" />
            </div>
          </div>
        </section>

        {/* Links */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8 text-gray-900 dark:text-white">Links</h2>
          <div className="space-y-4">
            <a href="#" className="text-wechat-green hover:text-wechat-green-dark font-semibold flex items-center gap-2 group w-fit">
              <span>Link with Arrow</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </a>
            <a href="#" className="text-blue-500 hover:text-blue-600 underline">
              Underlined Link
            </a>
            <a href="#" className="text-gray-600 dark:text-gray-400 hover:text-wechat-green transition-colors">
              Subtle Link
            </a>
          </div>
        </section>

        {/* Color Palette */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8 text-gray-900 dark:text-white">Color Palette</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <div className="w-full h-24 bg-wechat-green rounded-xl shadow-lg mb-2"></div>
              <p className="text-sm font-mono text-gray-600 dark:text-gray-400">#07c160</p>
              <p className="text-sm font-semibold text-gray-900 dark:text-white">WeChat Green</p>
            </div>
            <div>
              <div className="w-full h-24 bg-wechat-green-dark rounded-xl shadow-lg mb-2"></div>
              <p className="text-sm font-mono text-gray-600 dark:text-gray-400">#06ad56</p>
              <p className="text-sm font-semibold text-gray-900 dark:text-white">Green Dark</p>
            </div>
            <div>
              <div className="w-full h-24 bg-wechat-green-light rounded-xl shadow-lg mb-2"></div>
              <p className="text-sm font-mono text-gray-600 dark:text-gray-400">#95ec69</p>
              <p className="text-sm font-semibold text-gray-900 dark:text-white">Green Light</p>
            </div>
            <div>
              <div className="w-full h-24 bg-gray-900 dark:bg-white rounded-xl shadow-lg mb-2"></div>
              <p className="text-sm font-mono text-gray-600 dark:text-gray-400">#1a1a1a</p>
              <p className="text-sm font-semibold text-gray-900 dark:text-white">Text Primary</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
