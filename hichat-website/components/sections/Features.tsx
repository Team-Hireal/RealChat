'use client';

import { MessageSquare, ListChecks, Tag, Pin, Zap, Search } from 'lucide-react';

const features = [
  {
    icon: MessageSquare,
    title: 'Smart Triage',
    description: 'Automatically categorize and prioritize your messages based on importance and urgency.'
  },
  {
    icon: ListChecks,
    title: 'Reply Queue',
    description: 'Never miss a reply with intelligent tracking of conversations that need your attention.'
  },
  {
    icon: Tag,
    title: 'Chat Labels',
    description: 'Organize contacts with smart tags: Friends, Family, Work, Investors, Leads, and more.'
  },
  {
    icon: Pin,
    title: 'Pin Control',
    description: 'Auto-pin chats that need replies, auto-unpin when resolved. Stay organized effortlessly.'
  },
  {
    icon: Zap,
    title: 'Auto Replies',
    description: 'Safe, permission-based auto-replies with approval workflows. Never send by accident.'
  },
  {
    icon: Search,
    title: 'Search & Recall',
    description: 'Find any conversation instantly with natural language search. "Where did they send the address?"'
  }
];

export default function Features() {
  return (
    <section className="py-24 bg-white dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900 dark:text-white">
            What It Does
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            Powerful features that transform how you manage WeChat conversations
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group p-8 rounded-2xl bg-gradient-to-br from-gray-50 to-white dark:from-gray-800 dark:to-gray-900 border border-gray-200 dark:border-gray-700 hover:border-[#07c160] dark:hover:border-[#07c160] transition-all duration-300 hover:shadow-xl hover:-translate-y-1"
            >
              <div className="w-14 h-14 rounded-xl bg-[#07c160]/10 dark:bg-[#07c160]/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <feature.icon className="w-7 h-7 text-[#07c160]" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">
                {feature.title}
              </h3>
              <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
