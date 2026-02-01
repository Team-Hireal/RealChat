# HiChat Website

A modern, responsive marketing website for HiChat - a WeChat-native personal copilot that supercharges your WeChat experience with AI-powered workflows and smart automation.

## Features

- **Modern Tech Stack**: Built with Next.js 16, React, TypeScript, and Tailwind CSS
- **Responsive Design**: Fully responsive layout that works on all devices
- **Dark Mode**: Automatic dark mode support based on system preferences
- **WeChat-Inspired Design**: Green theme colors inspired by WeChat's brand
- **Smooth Animations**: Custom animations and transitions for a polished UX
- **Component-Based Architecture**: Modular, reusable components

## Project Structure

```
hichat-website/
├── app/
│   ├── globals.css          # Global styles and custom animations
│   ├── layout.tsx            # Root layout with fonts
│   └── page.tsx              # Main homepage
├── components/
│   ├── layout/
│   │   ├── Navigation.tsx    # Top navigation bar with dark mode toggle
│   │   └── Footer.tsx        # Footer with links and social icons
│   └── sections/
│       ├── Hero.tsx          # Hero section with CTA buttons
│       ├── Features.tsx      # 6 core features grid
│       ├── FeatureCards.tsx  # Detailed feature cards (2-column)
│       ├── Workflows.tsx     # 13 workflows showcase
│       ├── HowItWorks.tsx    # 4-step process
│       ├── Architecture.tsx  # Hybrid AI architecture explanation
│       └── CTA.tsx           # Download and documentation CTAs
└── public/                   # Static assets
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Build for Production

```bash
npm run build
npm start
```

## Design System

### Colors

The website uses a WeChat-inspired green color palette:

- **Primary Green**: `#07c160` - Main brand color
- **Dark Green**: `#06ad56` - Hover states and accents
- **Light Green**: `#95ec69` - Gradients and highlights
- **Background**: `#ededed` (light) / `#2c2c2c` (dark)

### Typography

- System font stack for optimal performance and native feel
- Font weights: 400 (regular), 600 (semibold), 700 (bold)

### Components

All components are built with:
- Tailwind CSS for styling
- Lucide React for icons
- Responsive design patterns
- Dark mode support
- Smooth hover animations

## Key Sections

1. **Hero**: Eye-catching headline with CTA buttons and metrics
2. **Features**: 6 core features in a grid layout
3. **Feature Cards**: Detailed 2-column feature showcase
4. **Workflows**: Interactive 13 workflows display
5. **How It Works**: 4-step process explanation
6. **Architecture**: Privacy-first hybrid AI architecture
7. **CTA**: Download options for Mac/Windows
8. **Footer**: Links, resources, and social media

## Technologies

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Fonts**: Geist Sans & Geist Mono

## Development

### Adding New Sections

1. Create a new component in `components/sections/`
2. Import and add it to `app/page.tsx`
3. Style with Tailwind CSS classes

### Customizing Colors

Edit the CSS variables in `app/globals.css`:

```css
:root {
  --wechat-green: #07c160;
  --wechat-green-dark: #06ad56;
  --wechat-green-light: #95ec69;
}
```

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out the [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

## License

MIT

## Contact

For questions or support, visit [HiChat Documentation](#)
