'use client';

import Link from 'next/link';
import { Github, Twitter, Mail } from 'lucide-react';
import { useLanguage } from '../LanguageProvider';

export default function Footer() {
  const { t } = useLanguage();

  return (
    <footer className="bg-gray-900 dark:bg-black text-gray-300 py-16">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          {/* Brand */}
          <div className="md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-[#07c160] to-[#06ad56] rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-xl">R</span>
              </div>
              <span className="text-2xl font-bold text-white">{t('brandName')}</span>
            </div>
            <p className="text-gray-400 mb-6">
              {t('footer.tagline')}
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
            <h4 className="text-white font-semibold mb-4">{t('footer.product')}</h4>
            <ul className="space-y-3">
              <li><Link href="#features" className="hover:text-[#07c160] transition-colors">{t('footer.features')}</Link></li>
              <li><Link href="#workflows" className="hover:text-[#07c160] transition-colors">{t('footer.workflows')}</Link></li>
              <li><Link href="#pricing" className="hover:text-[#07c160] transition-colors">{t('footer.pricing')}</Link></li>
              <li><Link href="#download" className="hover:text-[#07c160] transition-colors">{t('nav.download')}</Link></li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-white font-semibold mb-4">{t('footer.resources')}</h4>
            <ul className="space-y-3">
              <li><Link href="#docs" className="hover:text-[#07c160] transition-colors">{t('footer.documentation')}</Link></li>
              <li><Link href="#api" className="hover:text-[#07c160] transition-colors">{t('footer.apiReference')}</Link></li>
              <li><Link href="#community" className="hover:text-[#07c160] transition-colors">{t('footer.community')}</Link></li>
              <li><Link href="#support" className="hover:text-[#07c160] transition-colors">{t('footer.support')}</Link></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="text-white font-semibold mb-4">{t('footer.company')}</h4>
            <ul className="space-y-3">
              <li><Link href="#about" className="hover:text-[#07c160] transition-colors">{t('footer.about')}</Link></li>
              <li><Link href="#blog" className="hover:text-[#07c160] transition-colors">{t('footer.blog')}</Link></li>
              <li><Link href="#careers" className="hover:text-[#07c160] transition-colors">{t('footer.careers')}</Link></li>
              <li><Link href="#contact" className="hover:text-[#07c160] transition-colors">{t('footer.contact')}</Link></li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-gray-800 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-gray-500 text-sm">
            © 2024 {t('brandName')}. {t('footer.allRightsReserved')}
          </p>
          <div className="flex gap-6 text-sm">
            <Link href="#privacy" className="text-gray-500 hover:text-[#07c160] transition-colors">
              {t('footer.privacy')}
            </Link>
            <Link href="#terms" className="text-gray-500 hover:text-[#07c160] transition-colors">
              {t('footer.terms')}
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
