# AI Quant Sniper — Working Guide

This document explains the intended user workflow for the AI Quant Sniper dashboard and includes screenshots of the current interface.

> **Signal-only workflow:** The dashboard scans market data and displays a model-generated signal. The user makes the entry decision manually and must apply appropriate risk management. The screenshots do not establish that the model is profitable or that a trade is guaranteed to succeed.

## 1. Launch the application

1. Open the project folder.
2. Double-click `Run_Dashboard.bat`.
3. Wait for Streamlit to start, then open the local dashboard address shown in the terminal (the current launcher uses port `8016`, typically `http://localhost:8016`).

![Project files and launcher](screenshots/01-launch-files.png)

**What this shows:** The project directory contains the dashboard Python file, Windows batch launcher, trained model, training dataset, and Git ignore file.

## 2. Start the live scanner

1. Confirm that MetaTrader 5 is open and connected to the intended broker/account.
2. Confirm the broker provides the configured symbol (`BTCUSDT` by default in the current dashboard).
3. In the browser dashboard, click **🚀 START LIVE SCANNER**.

![Dashboard before scanning](screenshots/02-dashboard-start.png)

After the scanner starts, the dashboard displays a live-scanner status message.

## 3. Wait for a liquidity-sweep setup

The intended workflow is to let the scanner monitor the incoming market candles and wait for the strategy's liquidity-sweep conditions to be met. If no qualifying setup is detected, the dashboard should display a waiting/no-trade state along with the current price and model probabilities.

![Scanner waiting for a setup](screenshots/03-scanner-waiting.png)

**Important implementation note:** The visible screenshot shows a “Waiting for Liquidity Sweep… (No Trade)” message. Confirm in the strategy code that an actual liquidity-sweep detection rule is implemented and gates the model signal; a message alone does not prove that the condition is being checked correctly.

## 4. Review the alert and confidence

When the model's signal meets the configured confidence threshold, the dashboard displays a prominent BUY or SELL alert. The example below shows a **STRONG SELL SETUP** with a displayed AI confidence of **64.0%**.

![Example strong sell alert](screenshots/04-strong-sell-alert.png)

Before considering an entry, the user should independently check:
- Whether the liquidity sweep and any confirmation rules are genuinely satisfied.
- Whether the signal is still valid at the current market price.
- Stop-loss placement, position size, risk/reward, spread, and slippage.
- Daily loss limits and any personal or account-level risk restrictions.

The confidence percentage is a model output, not a guarantee of success. Do not enter solely because the alert is colored green or red.

## 5. Manual entry and risk management

The intended end-to-end flow is:

1. Launch `Run_Dashboard.bat`.
2. Open the dashboard and start the live scanner.
3. Wait for a qualifying liquidity-sweep setup.
4. Review the BUY/SELL direction and confidence shown by the model.
5. If the setup passes your rules, decide manually whether to enter.
6. Calculate position size from the account risk limit and stop-loss distance.
7. Define the stop loss and take profit before entering, and follow daily drawdown limits.
8. Record the outcome so that performance can be evaluated later.

**The current dashboard is a signal display, not an automatic execution or complete risk-management system.** Unless separately implemented and tested, it does not place orders, calculate a safe lot size, set broker-side SL/TP, or enforce account-level loss limits.

## Troubleshooting

- **Dashboard does not open:** Check the terminal output from `Run_Dashboard.bat` and verify port `8016` is available.
- **No live data:** Open and log in to MetaTrader 5; verify the broker-specific symbol name and available M1 history.
- **Scanner stays in waiting state:** This may simply mean no qualifying setup has appeared. Also inspect the application logs and verify the liquidity-sweep conditions are implemented as intended.
- **Unexpected BUY/SELL alerts:** Verify model feature order, preprocessing, class-label mapping, and confidence threshold against the model's training pipeline.

## Safety note

Use a demo account for testing. Validate the model with chronological out-of-sample data and realistic transaction costs before considering live use. Trading can result in substantial losses.
