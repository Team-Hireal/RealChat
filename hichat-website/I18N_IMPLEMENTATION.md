# Internationalization (i18n) Implementation Guide

## ✅ What's Been Implemented

### 1. Language Infrastructure
- **LanguageProvider** (`components/LanguageProvider.tsx`): React Context for managing language state
- **Translation Files**:
  - `messages/en.json` - English translations
  - `messages/zh.json` - Chinese translations (中文)
- **Language Switcher**: Added to Navigation component with globe icon

### 2. Components Updated with Translations
- ✅ **Navigation** - All menu items and buttons
- ✅ **Hero** - Title, subtitle, CTA buttons, and metrics

### 3. Features
- Language preference saved to localStorage
- Smooth language switching without page reload
- Clean UI with language toggle button showing "中文" or "EN"
- All translations organized in JSON files for easy maintenance

## 🔄 Components Still Need Translation

The following components still have hardcoded English text and need to be updated:

### Priority 1 - Main Sections
1. **Features** (`components/sections/Features.tsx`)
   - Section title and subtitle
   - 6 feature cards (Smart Triage, Reply Queue, etc.)

2. **FeatureCards** (`components/sections/FeatureCards.tsx`)
   - Message Intelligence card
   - Workflow Automation card

3. **Workflows** (`components/sections/Workflows.tsx`)
   - Section title and subtitle
   - 13 workflow items

4. **HowItWorks** (`components/sections/HowItWorks.tsx`)
   - Section title and subtitle
   - 4 steps with titles and descriptions

5. **Architecture** (`components/sections/Architecture.tsx`)
   - Section title, subtitle, and description
   - 3 architecture features

6. **CTA** (`components/sections/CTA.tsx`)
   - Call-to-action title and subtitle
   - Download buttons
   - Free trial text

7. **Footer** (`components/layout/Footer.tsx`)
   - Tagline
   - All footer links and sections

### Priority 2 - Additional Pages
8. **Showcase Page** (`app/showcase/page.tsx`)
   - Component showcase content

## 📝 How to Add Translations to a Component

### Step 1: Import the useLanguage hook
```tsx
import { useLanguage } from '../LanguageProvider';
```

### Step 2: Use the hook in your component
```tsx
export default function YourComponent() {
  const { t } = useLanguage();

  return (
    <div>
      <h1>{t('section.title')}</h1>
      <p>{t('section.description')}</p>
    </div>
  );
}
```

### Step 3: Add translations to both JSON files

**messages/en.json:**
```json
{
  "section": {
    "title": "Your English Title",
    "description": "Your English description"
  }
}
```

**messages/zh.json:**
```json
{
  "section": {
    "title": "你的中文标题",
    "description": "你的中文描述"
  }
}
```

## 🎯 Translation Keys Structure

The translation keys are organized hierarchically:

```
nav.*          - Navigation menu items
hero.*         - Hero section content
features.*     - Features section
workflows.*    - Workflows section
howItWorks.*   - How It Works section
architecture.* - Architecture section
cta.*          - Call-to-action section
footer.*       - Footer content
```

## 🌐 Language Switcher

The language switcher is located in the Navigation component:
- Shows "中文" when in English mode
- Shows "EN" when in Chinese mode
- Saves preference to localStorage
- Accessible via keyboard and screen readers

## 📋 Next Steps

To complete the i18n implementation:

1. Update each component listed above to use the `useLanguage` hook
2. Replace all hardcoded text with `t('key.path')` calls
3. Ensure all translation keys exist in both `en.json` and `zh.json`
4. Test language switching on all pages
5. Verify Chinese text displays correctly with proper fonts

## 🔧 Maintenance

When adding new content:
1. Always add text to BOTH `messages/en.json` AND `messages/zh.json`
2. Use descriptive key names (e.g., `features.smartTriage.title`)
3. Keep the JSON structure organized by section
4. Test both languages after making changes

## 💡 Tips

- Use nested keys for better organization: `section.subsection.item`
- Keep translations concise for UI elements
- Consider cultural context when translating (not just literal translation)
- Test with longer Chinese text to ensure UI doesn't break
- Chinese text is often shorter than English, so layout should accommodate both

## 🐛 Troubleshooting

**Language not switching?**
- Check browser console for errors
- Verify localStorage is enabled
- Clear browser cache and reload

**Translation not showing?**
- Verify the key exists in both JSON files
- Check for typos in the key path
- Ensure the component is wrapped in LanguageProvider

**Chinese characters not displaying?**
- Check font support in globals.css
- Verify UTF-8 encoding in JSON files
