# Vercel Deployment Guide for Engram A2A Debate System

## Quick Deploy (3 steps)

### 1️⃣ Log in to Vercel
```bash
npm i -g vercel
vercel login
```

### 2️⃣ Deploy to Production
```bash
cd C:\Users\OFFRSTAR0\Engram
vercel --prod
```

### 3️⃣ Configure Environment Variables (Vercel Dashboard)

Go to: https://vercel.com/dashboard → your project → Settings → Environment Variables

Add:
- **Key**: `OPENROUTER_API_KEY` → **Value**: `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`
- **Key**: `NEXT_PUBLIC_APP_URL` → **Value**: Your live URL (e.g., `https://engram-a2a.vercel.app`)

## Post-Deployment

**Test the live system:**
- Navigate to your deployed URL
- Visit `/a2a` page
- Test the debate system with real trading scenarios

**Next Steps (optional):**
1. Add TradingView widgets for charts
2. Enhance UI styling
3. Add export functionality
4. Implement price alerts

## Troubleshooting

**If build fails:**
- Check Vercel logs
- Ensure all dependencies are in package.json
- Run locally first: `npm run build`

**If API calls fail:**
- Verify `OPENROUTER_API_KEY` is set correctly
- Check Vercel function logs
- Test locally first: `curl http://localhost:3000/api/prices`

---

**Ready to deploy?** Just run `vercel --prod` from the Engram directory! 🚀
