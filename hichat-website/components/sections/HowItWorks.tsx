'use client';

import { Download, Plug, Scan, CheckCircle } from 'lucide-react';

const steps = [
  {
    icon: Download,
    title: 'Install',
    description: 'Download the desktop companion for Mac or Windows. Quick 2-minute setup.',
    color: 'from-blue-500 to-cyan-500'
  },
  {
    icon: Plug,
    title: 'Connect',
    description: 'Link with your WeChat desktop app. All processing happens locally on your device.',
    color: 'from-purple-500 to-pink-500'
  },
  {
    icon: Scan,
    title: 'Scan',
    description: 'HiChat analyzes your chats locally to understand context and relationships.',
    color: 'from-orange-500 to-red-500'
  },
  {
    icon: CheckCircle,
    title: 'Done',
    description: 'Start running workflows inside WeChat. Control everything via self-chat.',
    color: 'from-green-500 to-emerald-500'
  }
];

export default function HowItWorks() {
  return (
    <section className="py-24 bg-gradient-to-b from-gray-50 to-white dark:from-gray-800 dark:to-gray-900">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900 dark:text-white">
            How It Works
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            Get started in minutes with our simple 4-step process
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              {/* Connector line */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-16 left-full w-full h-0.5 bg-gradient-to-r from-[#07c160] to-[#95ec69] -z-10"></div>
              )}

              <div className="text-center">
                {/* Icon */}
                <div className={`w-32 h-32 mx-auto mb-6 rounded-3xl bg-gradient-to-br ${step.color} flex items-center justify-center shadow-xl hover:scale-110 transition-transform duration-300`}>
                  <step.icon className="w-16 h-16 text-white" />
                </div>

                {/* Step number */}
                <div className="inline-block px-4 py-1 bg-[#07c160] text-white rounded-full text-sm font-bold mb-4">
                  Step {index + 1}
                </div>

                {/* Content */}
                <h3 className="text-2xl font-bold mb-3 text-gray-900 dark:text-white">
                  {step.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
