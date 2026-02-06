#!/usr/bin/env Rscript
# Trading Signal Generator using tidymodels
# Integrates with Engram A2A system

# Install and load tidymodels
if (!require("tidymodels")) {
  install.packages("tidymodels", repos = "https://cloud.r-project.org/")
}
library(tidymodels)

# Load additional packages
if (!require("tidyverse")) install.packages("tidyverse")
if (!require("lubridate")) install.packages("lubridate")
if (!require("jsonlite")) install.packages("jsonlite")
if (!require("httr")) install.packages("httr")

library(tidyverse)
library(lubridate)
library(jsonlite)
library(httr)

# ============================================
# 1. DATA FETCHING
# ============================================

fetch_price_data <- function(symbol = "BTCUSDT", days = 90) {
  #' Fetch historical price data from CoinGecko
  
  coin_map <- list(
    "BTCUSDT" = "bitcoin",
    "ETHUSDT" = "ethereum",
    "SOLUSDT" = "solana",
    "ADAUSDT" = "cardano"
  )
  
  coin_id <- coin_map[[symbol]]
  if (is.null(coin_id)) coin_id <- "bitcoin"
  
  url <- sprintf(
    "https://api.coingecko.com/api/v3/coins/%s/market_chart?vs_currency=usd&days=%d",
    coin_id, days
  )
  
  response <- GET(url)
  data <- fromJSON(content(response, "text"))
  
  # Convert to dataframe
  prices <- data$prices %>%
    as.data.frame() %>%
    rename(timestamp = V1, price = V2) %>%
    mutate(
      date = as_datetime(timestamp / 1000),
      symbol = symbol
    )
  
  return(prices)
}

# ============================================
# 2. FEATURE ENGINEERING
# ============================================

engineer_features <- function(price_data) {
  #' Create technical indicators for ML
  
  price_data %>%
    arrange(date) %>%
    mutate(
      # Returns
      returns = (price - lag(price)) / lag(price),
      log_returns = log(price / lag(price)),
      
      # Moving averages
      sma_7 = zoo::rollmean(price, 7, fill = NA, align = "right"),
      sma_21 = zoo::rollmean(price, 21, fill = NA, align = "right"),
      sma_50 = zoo::rollmean(price, 50, fill = NA, align = "right"),
      
      # Price relative to MAs
      price_sma7_ratio = price / sma_7,
      price_sma21_ratio = price / sma_21,
      sma7_sma21_ratio = sma_7 / sma_21,
      
      # Volatility
      volatility_7 = zoo::rollapply(returns, 7, sd, fill = NA, align = "right"),
      volatility_21 = zoo::rollapply(returns, 21, sd, fill = NA, align = "right"),
      
      # Price momentum
      momentum_7 = price / lag(price, 7) - 1,
      momentum_14 = price / lag(price, 14) - 1,
      momentum_30 = price / lag(price, 30) - 1,
      
      # Target: Future return (1 day ahead)
      future_return = lead(returns, 1),
      signal = case_when(
        future_return > 0.005 ~ "BUY",
        future_return < -0.005 ~ "SELL",
        TRUE ~ "HOLD"
      )
    ) %>%
    drop_na()
}

# ============================================
# 3. ML MODEL BUILDING
# ============================================

build_trading_model <- function(feature_data) {
  #' Build Random Forest model for trading signals
  
  # Split data
  split <- initial_split(feature_data, prop = 0.8, strata = signal)
  train <- training(split)
  test <- testing(split)
  
  # Recipe
  rec <- recipe(signal ~ ., data = train) %>%
    update_role(date, timestamp, symbol, price, future_return, new_role = "ID") %>%
    step_normalize(all_numeric_predictors()) %>%
    step_corr(all_numeric_predictors(), threshold = 0.9) %>%
    step_naomit(all_predictors())
  
  # Model specification
  rf_spec <- rand_forest(
    trees = 500,
    min_n = tune(),
    mtry = tune()
  ) %>%
    set_engine("ranger", importance = "impurity") %>%
    set_mode("classification")
  
  # Workflow
  wf <- workflow() %>%
    add_recipe(rec) %>%
    add_model(rf_spec)
  
  # Cross-validation
  cv_folds <- vfold_cv(train, v = 5, strata = signal)
  
  # Grid search
  grid <- grid_regular(
    min_n(range = c(2, 10)),
    mtry(range = c(2, 8)),
    levels = 3
  )
  
  # Tune
  tuned <- tune_grid(
    wf,
    resamples = cv_folds,
    grid = grid,
    metrics = metric_set(accuracy, roc_auc, precision, recall)
  )
  
  # Best model
  best_params <- select_best(tuned, metric = "accuracy")
  final_wf <- finalize_workflow(wf, best_params)
  final_model <- fit(final_wf, train)
  
  # Evaluate
  predictions <- predict(final_model, test) %>%
    bind_cols(test)
  
  metrics <- predictions %>%
    metrics(truth = signal, estimate = .pred_class)
  
  confusion <- predictions %>%
    conf_mat(truth = signal, estimate = .pred_class)
  
  list(
    model = final_model,
    metrics = metrics,
    confusion = confusion,
    predictions = predictions,
    importance = final_model %>%
      extract_fit_parsnip() %>%
      vip::vi()
  )
}

# ============================================
# 4. SIGNAL GENERATION FOR ENGRAM
# ============================================

generate_signal <- function(symbol = "BTCUSDT", model_path = NULL) {
  #' Generate trading signal for Engram A2A system
  
  cat(sprintf("\n🔮 Generating signal for %s...\n", symbol))
  
  # Fetch latest data
  cat("📊 Fetching price data...\n")
  prices <- fetch_price_data(symbol, days = 90)
  
  # Engineer features
  cat("🔧 Engineering features...\n")
  features <- engineer_features(prices)
  
  # If model exists, use it; otherwise train new
  if (!is.null(model_path) && file.exists(model_path)) {
    cat("📦 Loading existing model...\n")
    model_data <- readRDS(model_path)
    model <- model_data$model
  } else {
    cat("🎯 Training new model...\n")
    model_data <- build_trading_model(features)
    model <- model_data$model
    
    # Save model
    saveRDS(model_data, sprintf("models/%s_model.rds", symbol))
    
    cat("\n📈 Model Performance:\n")
    print(model_data$metrics)
    
    cat("\n📊 Confusion Matrix:\n")
    print(model_data$confusion)
  }
  
  # Get latest prediction
  latest <- features %>%
    slice_tail(n = 1)
  
  prediction <- predict(model, latest, type = "prob") %>%
    bind_cols(predict(model, latest)) %>%
    bind_cols(latest %>% select(date, price, returns))
  
  # Format for Engram
  signal_output <- list(
    symbol = symbol,
    timestamp = as.character(Sys.time()),
    current_price = round(latest$price, 2),
    signal = prediction$.pred_class,
    confidence = max(
      prediction$.pred_BUY,
      prediction$.pred_SELL,
      prediction$.pred_HOLD
    ) %>% round(4),
    probabilities = list(
      buy = round(prediction$.pred_BUY, 4),
      sell = round(prediction$.pred_SELL, 4),
      hold = round(prediction$.pred_HOLD, 4)
    ),
    features = list(
      sma7_ratio = round(latest$price_sma7_ratio, 4),
      momentum_7 = round(latest$momentum_7, 4),
      volatility = round(latest$volatility_7, 4)
    ),
    model_type = "Random Forest (tidymodels)",
    recommendation = case_when(
      prediction$.pred_class == "BUY" ~ "Consider LONG position",
      prediction$.pred_class == "SELL" ~ "Consider SHORT position",
      TRUE ~ "No clear signal - HOLD"
    )
  )
  
  # Output as JSON for Engram integration
  json_output <- toJSON(signal_output, pretty = TRUE, auto_unbox = TRUE)
  
  cat("\n🎯 Signal Generated:\n")
  cat(json_output)
  cat("\n")
  
  return(signal_output)
}

# ============================================
# 5. MAIN EXECUTION
# ============================================

# Create models directory
if (!dir.exists("models")) {
  dir.create("models")
}

# Command line arguments
args <- commandArgs(trailingOnly = TRUE)

if (length(args) == 0) {
  symbol <- "BTCUSDT"
} else {
  symbol <- args[1]
}

# Generate signal
signal <- generate_signal(symbol)

# Save to file for Engram to read
output_file <- sprintf("signals/%s_signal.json", symbol)
if (!dir.exists("signals")) {
  dir.create("signals")
}
write_json(signal, output_file, pretty = TRUE, auto_unbox = TRUE)

cat(sprintf("\n💾 Signal saved to: %s\n", output_file))
cat("\n✅ Ready for Engram A2A integration!\n")
