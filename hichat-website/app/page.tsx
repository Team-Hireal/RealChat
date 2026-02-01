import Navigation from '@/components/layout/Navigation';
import Footer from '@/components/layout/Footer';
import Hero from '@/components/sections/Hero';
import Features from '@/components/sections/Features';
import FeatureCards from '@/components/sections/FeatureCards';
import Workflows from '@/components/sections/Workflows';
import HowItWorks from '@/components/sections/HowItWorks';
import Architecture from '@/components/sections/Architecture';
import CTA from '@/components/sections/CTA';

export default function Home() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      <Navigation />
      <Hero />
      <Features />
      <FeatureCards />
      <Workflows />
      <HowItWorks />
      <Architecture />
      <CTA />
      <Footer />
    </div>
  );
}
