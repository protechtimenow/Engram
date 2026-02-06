# HEARTBEAT.md

## Simmer Trading (2-3x per day)
If it's been >6 hours since last Simmer check:
1. Check agent status: `GET /api/simmer?action=status`
2. Check portfolio: `GET /api/simmer?action=portfolio`
3. Check positions: `GET /api/simmer?action=positions`
4. Browse weather markets: `GET /api/simmer?action=weather`
5. Update lastSimmerCheck timestamp in memory

### What to look for:
- **Positions near resolution** (<24h): Exit or hold?
- **Balance**: Above/below starting $10,000 SIM?
- **New weather markets**: Temperature, precipitation opportunities
- **Claim status**: Still unclaimed? Remind user to claim for real trading

### Simmer Agent Details:
- **Name**: engram-trader
- **Claim Code**: peak-86VN
- **Claim URL**: https://simmer.markets/claim/peak-86VN
- **Starting Balance**: 10,000 $SIM (virtual)
- **Limits**: $100/trade, $500/day

---

# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks above when you want the agent to check something periodically.
