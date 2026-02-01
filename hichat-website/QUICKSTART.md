# Quick Start Guide

## For Developers

### 1. Prerequisites
- Node.js 18 or higher
- npm (comes with Node.js)
- A code editor (VS Code recommended)

### 2. Installation

```bash
# Navigate to the project
cd hichat-website

# Install dependencies
npm install

# Start development server
npm run dev
```

The website will be available at http://localhost:3000 (or 3001 if 3000 is in use)

### 3. Project Overview

This is a Next.js 16 website with:
- **App Router** (not Pages Router)
- **TypeScript** for type safety
- **Tailwind CSS 4** for styling
- **Lucide React** for icons

### 4. File Structure

```
app/
  ├── layout.tsx      # Root layout (fonts, metadata)
  ├── page.tsx        # Homepage (imports all sections)
  └── globals.css     # Global styles + animations

components/
  ├── layout/         # Navigation, Footer
  └── sections/       # Hero, Features, etc.
```

### 5. Making Changes

#### Edit Content
Open any component file and edit the text directly:
```typescript
// components/sections/Hero.tsx
<h1>Supercharge Your WeChat</h1>  // Change this text
```

#### Add New Section
1. Create `components/sections/NewSection.tsx`
2. Import in `app/page.tsx`
3. Add `<NewSection />` where you want it

#### Change Colors
Edit `app/globals.css`:
```css
:root {
  --wechat-green: #07c160;  /* Change this */
}
```

#### Add New Component
```typescript
// components/ui/Button.tsx
export default function Button({ children }) {
  return (
    <button className="px-6 py-3 bg-wechat-green text-white rounded-full">
      {children}
    </button>
  );
}
```

### 6. Common Tasks

#### Add an Image
1. Put image in `public/` folder
2. Use Next.js Image component:
```typescript
import Image from 'next/image';

<Image
  src="/your-image.png"
  alt="Description"
  width={500}
  height={300}
/>
```

#### Add a New Page
1. Create `app/about/page.tsx`
2. Export a default component
3. Link to it: `<Link href="/about">About</Link>`

#### Style with Tailwind
Use utility classes:
```typescript
<div className="bg-white dark:bg-gray-900 p-8 rounded-xl shadow-lg">
  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
    Title
  </h2>
</div>
```

### 7. Development Tips

- **Hot Reload**: Changes auto-refresh the browser
- **TypeScript**: Hover over variables to see types
- **Tailwind**: Use VS Code Tailwind extension for autocomplete
- **Dark Mode**: Use `dark:` prefix for dark mode styles
- **Icons**: Browse icons at https://lucide.dev

### 8. Building for Production

```bash
# Create optimized build
npm run build

# Test production build locally
npm start
```

### 9. Deployment

**Vercel (Recommended)**:
1. Push code to GitHub
2. Import project on vercel.com
3. Deploy (automatic)

**Other Options**:
- Netlify
- AWS Amplify
- Docker
- Any Node.js hosting

### 10. Troubleshooting

**Port already in use**:
- Next.js will automatically use next available port
- Or kill the process: `lsof -ti:3000 | xargs kill`

**Module not found**:
```bash
rm -rf node_modules package-lock.json
npm install
```

**TypeScript errors**:
- Check for missing imports
- Run `npm run build` to see all errors

**Styling not working**:
- Check Tailwind class names
- Verify `globals.css` is imported in `layout.tsx`

### 11. Useful Commands

```bash
# Development
npm run dev          # Start dev server

# Production
npm run build        # Build for production
npm start            # Run production build

# Code Quality
npm run lint         # Run ESLint

# Package Management
npm install <pkg>    # Add new package
npm update           # Update packages
```

### 12. Resources

- [Next.js Docs](https://nextjs.org/docs)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Lucide Icons](https://lucide.dev)
- [React Docs](https://react.dev)

### 13. Best Practices

✅ **Do**:
- Use TypeScript types
- Follow component structure
- Use Tailwind utilities
- Keep components small and focused
- Test on mobile devices

❌ **Don't**:
- Modify `node_modules`
- Use inline styles (use Tailwind)
- Create huge components
- Forget to test dark mode
- Skip TypeScript types

### 14. Getting Help

- Check component files for examples
- Read error messages carefully
- Use browser DevTools
- Check Next.js documentation
- Search for Tailwind classes

---

**Ready to start?** Run `npm run dev` and open http://localhost:3000

**Questions?** Check the README.md or PROJECT_SUMMARY.md files.
