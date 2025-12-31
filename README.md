# STOCK-Option-Chain-AI-Predictor

# 📈 NIFTY Option Chain AI Predictor

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📌 Overview

The **NIFTY Option Chain AI Predictor** is a data-driven financial dashboard built with **Streamlit** and **Python**. It automates the analysis of NSE (National Stock Exchange) Option Chain data to predict market sentiment, support/resistance levels, and the likely settlement price for an upcoming expiry.

Instead of relying on gut feeling, this tool uses quantitative models like **Max Pain Theory**, **Put-Call Ratio (PCR)**, and **Implied Volatility (IV)** to generate probabilistic forecasts.

## 🚀 Features

* **📊 Automated Analysis:** Instantly processes raw NSE CSV data into actionable insights.
* **🎯 Max Pain Calculation:** Identifies the "Max Pain" strike price—the level where option writers lose the least money (often a magnet for expiry).
* **📉 Support & Resistance Detection:** Visualizes Open Interest (OI) "walls" to find strong support and resistance zones.
* **🐂 Market Sentiment:** Calculates the Put-Call Ratio (PCR) to determine if the market is Bullish or Bearish.
* **🔮 Predictive Range:** Estimates the expected trading range (Upper/Lower bounds) based on ATM Implied Volatility and Days to Expiry (DTE).
* **📈 Interactive Visualizations:** Built with **Plotly** for interactive bar charts and curves.

## 🧮 Theoretical Concepts Implemented

1.  **Max Pain Theory:** Based on the assumption that most options expire worthless. The model calculates the cumulative loss for option writers at every strike and identifies the point of minimum loss.
2.  **Put-Call Ratio (PCR):** A contrarian indicator.
    * PCR > 1.0: Bullish (More puts written, strong support).
    * PCR < 0.6: Bearish (More calls written, strong resistance).
3.  **Implied Volatility (IV) Move:** Used to calculate the statistical expected move using the formula:
    $$\text{Expected Move} = \text{Spot} \times \left( \frac{\text{IV}}{100} \right) \times \sqrt{\frac{\text{DTE}}{365}}$$

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Data Processing:** Pandas, NumPy
* **Visualization:** Plotly, Matplotlib
* **Language:** Python 3.x
🖥️ Usage
Open the app in your browser (usually http://localhost:8501).

Download a fresh Option Chain CSV from the NSE India website (or use a sample file).

Upload the CSV via the sidebar.

Adjust Days to Expiry (DTE) if necessary.

View the predictions, charts, and key levels instantly.

📸 Screenshots
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/33d1690c-ec42-41d0-9845-3671beab3124" />

<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/843aa10f-82ab-49c8-8b64-4d736a5bcc18" />



🔮 Future Improvements
Live API Integration: Fetch real-time data directly from NSE/Broker APIs instead of manual CSV upload.

Historical Backtesting: Add a module to test prediction accuracy against past expiries.

Greeks Analysis: Visualize Delta and Gamma exposure for advanced hedging insights.

🤝 Contributing
Contributions are welcome! Please fork the repository and create a pull request.


## 📂 Project Structure

```bash
├── app.py                   # Main Streamlit application
├── requirements.txt         # Project dependencies
├── option-chain-sample.csv  # Sample data for testing
└── README.md                # Project documentation
