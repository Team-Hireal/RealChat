#!/bin/bash

echo "============================================"
echo "🚀 RealChat - Vercel Deployment"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

cd "$(dirname "$0")/hichat-website"

echo -e "${BLUE}📦 Testing build locally...${NC}"
echo ""

# Test build
if npm run build; then
    echo ""
    echo -e "${GREEN}✅ Build successful!${NC}"
    echo ""
else
    echo ""
    echo -e "${YELLOW}❌ Build failed. Please fix errors before deploying.${NC}"
    exit 1
fi

echo "============================================"
echo "🌐 Ready to Deploy"
echo "============================================"
echo ""

echo "Choose deployment method:"
echo ""
echo "  1) Vercel CLI (Fastest - Recommended)"
echo "  2) GitHub + Vercel Dashboard"
echo "  3) Just show me the commands"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}Deploying with Vercel CLI...${NC}"
        echo ""

        # Check if Vercel CLI is installed
        if ! command -v vercel &> /dev/null; then
            echo "Installing Vercel CLI..."
            npm install -g vercel
        fi

        echo "Logging in to Vercel..."
        vercel login

        echo ""
        echo "Deploying to production..."
        vercel --prod

        echo ""
        echo -e "${GREEN}✅ Deployment complete!${NC}"
        echo ""
        echo "Your website is now live!"
        echo "Check your Vercel dashboard for the URL."
        ;;

    2)
        echo ""
        echo -e "${BLUE}GitHub + Vercel Dashboard Deployment${NC}"
        echo ""
        echo "Follow these steps:"
        echo ""
        echo "1. Push to GitHub:"
        echo "   ${YELLOW}cd /Users/test/Desktop/Hireal/RealChat${NC}"
        echo "   ${YELLOW}git init${NC}"
        echo "   ${YELLOW}git add hichat-website/${NC}"
        echo "   ${YELLOW}git commit -m \"Add HiChat website\"${NC}"
        echo "   ${YELLOW}git remote add origin https://github.com/yourusername/realchat.git${NC}"
        echo "   ${YELLOW}git push -u origin main${NC}"
        echo ""
        echo "2. Go to vercel.com and click 'New Project'"
        echo "3. Import your GitHub repository"
        echo "4. Set root directory to: ${YELLOW}hichat-website${NC}"
        echo "5. Click 'Deploy'"
        echo ""
        ;;

    3)
        echo ""
        echo -e "${BLUE}Deployment Commands${NC}"
        echo ""
        echo "Option A: Vercel CLI"
        echo "  ${YELLOW}npm install -g vercel${NC}"
        echo "  ${YELLOW}cd hichat-website${NC}"
        echo "  ${YELLOW}vercel login${NC}"
        echo "  ${YELLOW}vercel --prod${NC}"
        echo ""
        echo "Option B: GitHub + Vercel"
        echo "  1. Push to GitHub"
        echo "  2. Connect repo to Vercel"
        echo "  3. Set root directory: hichat-website"
        echo "  4. Deploy"
        echo ""
        ;;

    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "============================================"
echo "📚 Next Steps"
echo "============================================"
echo ""
echo "After deployment:"
echo "  • Visit your Vercel URL"
echo "  • Test all pages and features"
echo "  • Set up custom domain (optional)"
echo "  • Add analytics (optional)"
echo ""
echo "For backend deployment:"
echo "  • See VERCEL_DEPLOYMENT.md"
echo "  • Deploy to DigitalOcean/Railway"
echo "  • Connect via API"
echo ""
echo "============================================"
echo ""
