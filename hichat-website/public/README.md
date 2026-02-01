# Public Assets Directory

This directory contains all static assets for the HiChat website.

## Directory Structure

```
public/
├── images/          # Product screenshots, photos, graphics
├── icons/           # SVG icons, favicons, app icons
└── media/           # Videos, audio files, animations
```

## Usage

### Images
Place product screenshots, hero images, feature graphics, and other photos here.

**Example:**
```tsx
<img src="/images/hero-screenshot.png" alt="HiChat Interface" />
```

### Icons
Store SVG icons, favicons, and app icons here.

**Example:**
```tsx
<img src="/icons/logo.svg" alt="HiChat Logo" />
```

### Media
Place video files, audio clips, and animated content here.

**Example:**
```tsx
<video src="/media/demo-video.mp4" controls />
```

## Best Practices

1. **Optimize images** before adding them (use WebP format when possible)
2. **Use descriptive filenames** (e.g., `hero-background.jpg` not `img1.jpg`)
3. **Keep file sizes small** for better performance
4. **Use SVG for icons** when possible for scalability
5. **Add alt text** for all images for accessibility

## Current Assets

- `icons/` - Contains default Next.js SVG icons (file.svg, globe.svg, next.svg, vercel.svg, window.svg)
- `images/` - Empty, ready for your product images
- `media/` - Empty, ready for your video/audio files

## Notes

- All files in this directory are publicly accessible at `/filename`
- Next.js automatically serves files from this directory
- Do not store sensitive information here
