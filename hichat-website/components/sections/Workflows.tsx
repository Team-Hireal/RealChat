'use client';

import { useState } from 'react';
import { Check } from 'lucide-react';

const workflows = [
  { id: 1, name: 'Pin Reply Queue', description: 'Automatically pin chats that need your reply' },
  { id: 2, name: 'Unpin Resolved', description: 'Auto-unpin chats after you respond' },
  { id: 3, name: 'Daily Brief', description: 'Morning digest of important messages' },
  { id: 4, name: 'New Friend Auto Reply', description: 'Welcome new contacts with custom messages' },
  { id: 5, name: 'Busy Mode', description: 'Auto-reply during work hours' },
  { id: 6, name: 'Follow-up Reminders', description: 'Never forget to follow up' },
  { id: 7, name: 'Link/File Collector', description: 'Organize shared links and files' },
  { id: 8, name: 'Meeting Scheduling Draft', description: 'AI-powered meeting coordination' },
  { id: 9, name: 'Lead Tagging', description: 'Automatically tag potential leads' },
  { id: 10, name: 'Investor CRM Tags', description: 'Track investor relationships' },
  { id: 11, name: 'Unknown Sender Filter', description: 'Smart filtering of unknown contacts' },
  { id: 12, name: 'Weekly Recap', description: 'Weekly summary of conversations' },
  { id: 13, name: 'Export Notes', description: 'Local backup of your notes' }
];

export default function Workflows() {
  const [selectedWorkflow, setSelectedWorkflow] = useState(workflows[0]);

  return (
    <section className="py-24 bg-white dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900 dark:text-white">
            13 Powerful Workflows
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            Pre-built automation workflows that you can enable with one click
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Workflow list */}
          <div className="lg:col-span-1 space-y-2">
            {workflows.map((workflow) => (
              <button
                key={workflow.id}
                onClick={() => setSelectedWorkflow(workflow)}
                className={`w-full text-left p-4 rounded-xl transition-all duration-300 ${
                  selectedWorkflow.id === workflow.id
                    ? 'bg-[#07c160] text-white shadow-lg scale-105'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold">{workflow.name}</span>
                  {selectedWorkflow.id === workflow.id && (
                    <Check className="w-5 h-5" />
                  )}
                </div>
              </button>
            ))}
          </div>

          {/* Workflow canvas */}
          <div className="lg:col-span-2 bg-gradient-to-br from-[#07c160]/5 to-[#95ec69]/10 dark:from-[#07c160]/10 dark:to-[#06ad56]/20 rounded-3xl p-12 border-2 border-[#07c160]/20">
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="w-24 h-24 bg-[#07c160] rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-xl">
                  <span className="text-4xl font-bold text-white">{selectedWorkflow.id}</span>
                </div>
                <h3 className="text-3xl font-bold mb-4 text-gray-900 dark:text-white">
                  {selectedWorkflow.name}
                </h3>
                <p className="text-xl text-gray-600 dark:text-gray-400 max-w-md mx-auto">
                  {selectedWorkflow.description}
                </p>
                <button className="mt-8 px-8 py-3 bg-[#07c160] hover:bg-[#06ad56] text-white rounded-full font-semibold transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105">
                  Enable Workflow
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
