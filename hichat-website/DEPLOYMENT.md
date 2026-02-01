# HiChat Website - Deployment Guide

## Quick Deploy to Vercel

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial HiChat website"
   git push origin main
   ```

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will auto-detect Next.js and configure everything
   - Click "Deploy"

3. **Custom Domain** (Optional)
   - Go to Project Settings → Domains
   - Add your custom domain (e.g., hichat.app)
   - Follow DNS configuration instructions

## Environment Variables

No environment variables are required for the basic website. If you add API integrations later:

```env
# Example for future use
NEXT_PUBLIC_API_URL=https://api.hichat.app
NEXT_PUBLIC_ANALYTICS_ID=your-analytics-id
```

## Build Optimization

The website is already optimized with:
- ✅ Automatic code splitting
- ✅ Image optimization (Next.js Image component ready)
- ✅ CSS optimization with Tailwind
- ✅ TypeScript for type safety
- ✅ ESLint for code quality

## Performance Checklist

Before deploying to production:

- [ ] Add real images to `/public` folder
- [ ] Replace placeholder text with final copy
- [ ] Test on mobile devices
- [ ] Test dark mode
- [ ] Run `npm run build` locally to check for errors
- [ ] Test all links and buttons
- [ ] Add meta tags for SEO (in `app/layout.tsx`)
- [ ] Add favicon and app icons
- [ ] Set up analytics (optional)

## SEO Optimization

Add to `app/layout.tsx`:

```typescript
export const metadata = {
  title: 'HiChat - Supercharge Your WeChat',
  description: 'AI-powered WeChat copilot with smart workflows and automation',
  keywords: 'WeChat, AI, automation, productivity, chat management',
  openGraph: {
    title: 'HiChat - Supercharge Your WeChat',
    description: 'AI-powered WeChat copilot with smart workflows',
    images: ['/og-image.png'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'HiChat - Supercharge Your WeChat',
    description: 'AI-powered WeChat copilot with smart workflows',
    images: ['/twitter-image.png'],
  },
}
```

## Alternative Deployment Options

### Netlify
```bash
npm run build
# Deploy the `.next` folder
```

### AWS Amplify
- Connect your GitHub repo
- Build command: `npm run build`
- Output directory: `.next`

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Monitoring

After deployment, monitor:
- Page load times (should be < 2s)
- Core Web Vitals
- Error rates
- User analytics

## Support

For deployment issues:
- Check [Next.js Deployment Docs](https://nextjs.org/docs/deployment)
- Check [Vercel Documentation](https://vercel.com/docs)
