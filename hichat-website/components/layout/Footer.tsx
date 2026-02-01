import Link from 'next/link';
import { Github, Twitter, Mail } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-gray-900 dark:bg-black text-gray-300 py-16">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          {/* Brand */}
          <div className="md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-[#07c160] to-[#06ad56] rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-xl">Hi</span>
              </div>
              <span className="text-2xl font-bold text-white">HiChat</span>
            </div>
            <p className="text-gray-400 mb-6">
              Supercharge your WeChat with AI-powered workflows and smart automation.
            </p>
            <div className="flex gap-4">
              <a href="#" className="w-10 h-10 bg-gray-800 hover:bg-[#07c160] rounded-lg flex items-center justify-center transition-colors duration-300">
                <Github className="w-5 h-5" />
              </a>
              <a href="#" className="w-10 h-10 bg-gray-800 hover:bg-[#07c160] rounded-lg flex items-center justify-center transition-colors duration-300">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="#" className="w-10 h-10 bg-gray-800 hover:bg-[#07c160] rounded-lg flex items-center justify-center transition-colors duration-300">
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-white font-semibold mb-4">Product</h4>
            <ul className="space-y-3">
              <li><Link href="#features" className="hover:text-[#07c160] transition-colors">Features</Link></li>
              <li><Link href="#workflows" className="hover:text-[#07c160] transition-colors">Workflows</Link></li>
              <li><Link href="#pricing" className="hover:text-[#07c160] transition-colors">Pricing</Link></li>
              <li><Link href="#download" className="hover:text-[#07c160] transition-colors">Download</Link></li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-white font-semibold mb-4">Resources</h4>
            <ul className="space-y-3">
              <li><Link href="#docs" className="hover:text-[#07c160] transition-colors">Documentation</Link></li>
              <li><Link href="#guides" className="hover:text-[#07c160] transition-colors">Guides</Link></li>
              <li><Link href="#api" className="hover:text-[#07c160] transition-colors">API Reference</Link></li>
              <li><Link href="#support" className="hover:text-[#07c160] transition-colors">Support</Link></li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-white font-semibold mb-4">Legal</h4>
            <ul className="space-y-3">
              <li><Link href="#privacy" className="hover:text-[#07c160] transition-colors">Privacy Policy</Link></li>
              <li><Link href="#terms" className="hover:text-[#07c160] transition-colors">Terms of Service</Link></li>
              <li><Link href="#security" className="hover:text-[#07c160] transition-colors">Security</Link></li>
              <li><Link href="#contact" className="hover:text-[#07c160] transition-colors">Contact</Link></li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-gray-800">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-gray-500 text-sm">
              © 2026 HiChat. All rights reserved.
            </p>
            <p className="text-gray-500 text-sm">
              Made with ❤️ for WeChat power users
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
