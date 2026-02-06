# 🧠 R ML Trading Signal Generator

Machine learning trading signals using **tidymodels** - integrated with Engram's A2A debate system.

## What It Does

1. **Fetches price data** from CoinGecko (BTC, ETH, SOL, etc.)
2. **Engineers features**: SMAs, momentum, volatility, ratios
3. **Trains Random Forest model** to predict BUY/SELL/HOLD signals
4. **Outputs signal** with confidence scores and probabilities
5. **Integrates with A2A** for multi-agent validation

## Quick Start

### Generate Signal via API
```bash
# Get ML signal for BTC
curl https://engram-kappa.vercel.app/api/ml-signal?symbol=BTCUSDT

# Get formatted for A2A debate
curl https://engram-kappa.vercel.app/api/ml-signal?symbol=BTCUSDT&format=a2a

# Generate + auto-run A2A debate
curl -X POST https://engram-kappa.vercel.app/api/ml-signal \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "run_a2a": true}'
```

### Run Locally
```bash
# Generate signal
cd src/r_models
python run_model.py BTCUSDT

# Or directly in R
Rscript trading_signal_generator.R BTCUSDT
```

## Model Architecture

### Features Engineered
- **Price ratios**: price/SMA7, price/SMA21, SMA7/SMA21
- **Momentum**: 7-day, 14-day, 30-day returns
- **Volatility**: 7-day and 21-day standard deviation
- **Returns**: Log returns, simple returns

### ML Pipeline (tidymodels)
1. **Data splitting**: 80/20 train/test with stratification
2. **Preprocessing**: Normalization, correlation filtering
3. **Model**: Random Forest (ranger engine)
4. **Tuning**: Cross-validation grid search for min_n, mtry
5. **Metrics**: Accuracy, ROC-AUC, Precision, Recall

### Target Classes
- **BUY**: Future return > 0.5%
- **SELL**: Future return < -0.5%
- **HOLD**: Between -0.5% and +0.5%

## Integration with Engram

### A2A Debate Flow
```
Price Data → R ML Model → Signal (BUY/SELL/HOLD) 
                                    ↓
                            A2A Debate System
                            ├─ Proposer: ML Signal
                            ├─ Critic: Challenge assumptions
                            └─ Consensus: Final decision
                                    ↓
                            Trade Execution
```

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/ml-signal?symbol=BTCUSDT` | Get raw ML signal |
| `GET /api/ml-signal?format=a2a` | Get formatted for A2A |
| `POST /api/ml-signal` with `run_a2a: true` | Generate + debate |

## File Structure

```
src/r_models/
├── trading_signal_generator.R  # Main R script
├── run_model.py                # Python wrapper
├── signals/                    # Generated signals (JSON)
├── models/                     # Saved R models (.rds)
└── README.md                   # This file
```

## Requirements

### R Packages
```r
install.packages("tidymodels")
install.packages("tidyverse")
install.packages("lubridate")
install.packages("jsonlite")
install.packages("httr")
install.packages("ranger")  # Random Forest engine
```

### System
- R 4.0+
- Python 3.8+ (for wrapper)
- Internet connection (CoinGecko API)

## Future Enhancements

- [ ] Add more models (XGBoost, SVM, Neural Network)
- [ ] Feature importance tracking
- [ ] Model retraining pipeline
- [ ] Ensemble methods
- [ ] Custom feature engineering UI

---

**Powered by tidymodels** | **Integrated with Engram A2A**
