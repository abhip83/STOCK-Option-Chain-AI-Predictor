import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set Page Layout
st.set_page_config(page_title="STOCK Option Chain AI Predictor", layout="wide")

# --- 1. Data Processing Functions ---
@st.cache_data
def load_and_clean_data(file):
    # Load data, skipping the first row which is often a super-header
    df = pd.read_csv(file, header=1)
    
    # Standardize Column Names
    # Note: Adjust these indices if the NSE CSV format changes
    new_columns = [
        "Discard1", 
        "Calls_OI", "Calls_Chng_OI", "Calls_Vol", "Calls_IV", "Calls_LTP", "Calls_Net_Chng", "Calls_Bid_Qty", "Calls_Bid", "Calls_Ask", "Calls_Ask_Qty",
        "Strike",
        "Puts_Bid_Qty", "Puts_Bid", "Puts_Ask", "Puts_Ask_Qty", "Puts_Net_Chng", "Puts_LTP", "Puts_IV", "Puts_Vol", "Puts_Chng_OI", "Puts_OI",
        "Discard2"
    ]
    
    # Handle case where file might not match exact column count (basic error handling)
    if len(df.columns) == len(new_columns):
        df.columns = new_columns
    else:
        # Fallback: try to clean based on existing headers if standard format fails
        pass

    # Drop unnecessary columns
    cols_to_drop = [c for c in ["Discard1", "Discard2", "Unnamed: 0", "Unnamed: 22"] if c in df.columns]
    df = df.drop(columns=cols_to_drop)

    # Clean Numeric Data
    numeric_cols = [
        "Calls_OI", "Calls_Chng_OI", "Calls_Vol", "Calls_IV", "Calls_LTP", 
        "Strike", 
        "Puts_LTP", "Puts_IV", "Puts_Vol", "Puts_Chng_OI", "Puts_OI"
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '').str.replace('-', '0')
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Filter out zero strikes
    df = df[df['Strike'] > 0]
    
    return df

def calculate_max_pain(df):
    strikes = df['Strike'].unique()
    losses = []
    
    for price in strikes:
        # Loss for Call Writers: Max(0, Spot - Strike) * OI
        call_loss = np.maximum(0, price - df['Strike']) * df['Calls_OI']
        # Loss for Put Writers: Max(0, Strike - Spot) * OI
        put_loss = np.maximum(0, df['Strike'] - price) * df['Puts_OI']
        
        total_loss = call_loss.sum() + put_loss.sum()
        losses.append(total_loss)
    
    max_pain_idx = np.argmin(losses)
    return strikes[max_pain_idx], strikes, losses

# --- 2. Main Application UI ---

st.title("📈 STOCK Option Chain AI Predictor")
st.markdown("This application uses **Max Pain Theory** and **Put-Call Ratio (PCR)** analysis to predict market settlement levels.")

# Sidebar for Inputs
with st.sidebar:
    st.header("Upload Data")
    uploaded_file = st.file_uploader("Upload Option Chain CSV", type=["csv"])
    
    st.header("Settings")
    days_to_expiry = st.slider("Days to Expiry (DTE)", min_value=1, max_value=30, value=6)
    risk_free_rate = st.number_input("Risk Free Rate (%)", value=10.0)

if uploaded_file is not None:
    # Load Data
    try:
        df = load_and_clean_data(uploaded_file)
        
        # --- 3. Analysis Logic ---
        
        # 3.1 Basic Metrics
        total_call_oi = df['Calls_OI'].sum()
        total_put_oi = df['Puts_OI'].sum()
        pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0
        
        # 3.2 Support & Resistance
        resistance_strike = df.loc[df['Calls_OI'].idxmax(), 'Strike']
        support_strike = df.loc[df['Puts_OI'].idxmax(), 'Strike']
        
        # 3.3 Max Pain
        max_pain_price, strikes, losses = calculate_max_pain(df)
        
        # 3.4 Predicted Spot & Range (IV Based)
        # Find ATM Row
        closest_strike_idx = (df['Strike'] - max_pain_price).abs().idxmin()
        atm_row = df.loc[closest_strike_idx]
        
        # Est Spot = Strike + Call - Put
        est_spot = atm_row['Strike'] + atm_row['Calls_LTP'] - atm_row['Puts_LTP']
        
        # Calculate Expected Move using ATM IV
        avg_iv = (atm_row['Calls_IV'] + atm_row['Puts_IV']) / 2
        expected_move = est_spot * (avg_iv / 100) * np.sqrt(days_to_expiry / 365)
        
        lower_bound = est_spot - expected_move
        upper_bound = est_spot + expected_move

        # --- 4. Dashboard Display ---
        
        # KPI Row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Predicted Spot", f"{est_spot:,.0f}", f"±{expected_move:.0f}")
        col2.metric("Max Pain (Target)", f"{max_pain_price:,.0f}")
        col3.metric("PCR (Sentiment)", f"{pcr:.2f}", "Bullish" if pcr > 1 else "Bearish")
        col4.metric("Trading Range", f"{lower_bound:,.0f} - {upper_bound:,.0f}")

        # Analysis Tabs
        tab1, tab2, tab3 = st.tabs(["📊 Market Structures", "🎯 Max Pain Analysis", "📋 Raw Data"])

        with tab1:
            st.subheader("Open Interest Structure (Support & Resistance)")
            
            # Filter for relevant range to make chart readable
            zoom_range = 2000 # Show strikes +/- 2000 from spot
            df_chart = df[(df['Strike'] > est_spot - zoom_range) & (df['Strike'] < est_spot + zoom_range)]
            
            fig_oi = go.Figure()
            fig_oi.add_trace(go.Bar(x=df_chart['Strike'], y=df_chart['Calls_OI'], name='Calls (Resistance)', marker_color='red'))
            fig_oi.add_trace(go.Bar(x=df_chart['Strike'], y=df_chart['Puts_OI'], name='Puts (Support)', marker_color='green'))
            
            fig_oi.update_layout(barmode='overlay', title="Call vs Put Open Interest", xaxis_title="Strike Price", yaxis_title="Open Interest")
            st.plotly_chart(fig_oi, use_container_width=True)
            
            st.info(f"**Insight:** The highest Green bar is strong Support at **{support_strike}**. The highest Red bar is strong Resistance at **{resistance_strike}**.")

        with tab2:
            st.subheader("Max Pain Theory Visualization")
            st.write("The market tends to expire at the point where option writers lose the least money (the lowest point on this curve).")
            
            # Plot Max Pain
            fig_mp = go.Figure()
            fig_mp.add_trace(go.Scatter(x=strikes, y=losses, mode='lines+markers', name='Total Pain'))
            
            # Highlight Max Pain Point
            fig_mp.add_vline(x=max_pain_price, line_dash="dash", line_color="red", annotation_text="Max Pain")
            
            fig_mp.update_layout(title="Option Writer Loss vs Strike Price", xaxis_title="Strike Price", yaxis_title="Loss Value")
            st.plotly_chart(fig_mp, use_container_width=True)

        with tab3:
            st.subheader("Processed Option Chain Data")
            st.dataframe(df)

    except Exception as e:
        st.error(f"Error processing file: {e}")
        st.write("Please ensure you uploaded the standard NSE Option Chain CSV.")

else:
    st.info("👆 Please upload the 'option-chain-ED-NIFTY...' CSV file to begin analysis.")
    
    # Optional: Generate sample data button if you want to test without upload
    # (Omitted for brevity, assuming user has the file)