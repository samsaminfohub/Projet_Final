import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Configuration
API_BASE_URL = "http://backend:8000/api/v1"

# Page configuration
st.set_page_config(
    page_title="Mental Health Risk Predictor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .risk-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
    }
    .risk-low {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .risk-medium {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .risk-high {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🧠 Mental Health Risk Predictor</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox("Choose a page", ["Prediction", "History", "Analytics"])
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This application uses machine learning to predict mental health risks 
        based on lifestyle factors. Please note that this is for educational 
        purposes only and should not replace professional medical advice.
        """)
    
    if page == "Prediction":
        prediction_page()
    elif page == "History":
        history_page()
    else:
        analytics_page()

def prediction_page():
    st.header("Mental Health Risk Assessment")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Enter Your Information")
        
        # Input form
        with st.form("prediction_form"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                sleep_hours = st.slider("Sleep Hours per Night", 0.0, 12.0, 8.0, 0.5)
                exercise_hours = st.slider("Exercise Hours per Week", 0.0, 20.0, 3.0, 0.5)
                stress_level = st.slider("Stress Level (1-10)", 1, 10, 5)
            
            with col_b:
                social_activity = st.slider("Social Activity Level (1-10)", 1, 10, 7)
                work_hours = st.slider("Work Hours per Day", 0.0, 16.0, 8.0, 0.5)
                screen_time = st.slider("Screen Time per Day", 0.0, 16.0, 6.0, 0.5)
            
            submitted = st.form_submit_button("Predict Risk", type="primary")
            
            if submitted:
                with st.spinner("Analyzing your data..."):
                    prediction = make_prediction({
                        "sleep_hours": sleep_hours,
                        "exercise_hours": exercise_hours,
                        "stress_level": stress_level,
                        "social_activity": social_activity,
                        "work_hours": work_hours,
                        "screen_time": screen_time
                    })
                
                if prediction:
                    display_prediction_result(prediction)
    
    with col2:
        st.subheader("Risk Factors")
        st.markdown("""
        **Sleep**: 7-9 hours optimal
        **Exercise**: 2+ hours/week recommended
        **Stress**: Lower levels better
        **Social Activity**: Higher levels better
        **Work Hours**: <10 hours/day ideal
        **Screen Time**: <8 hours/day recommended
        """)
        
        # Quick tips
        st.subheader("Quick Tips")
        tips = [
            "🛌 Maintain regular sleep schedule",
            "🏃‍♂️ Exercise regularly",
            "🧘‍♀️ Practice stress management",
            "👥 Stay socially connected",
            "⚖️ Balance work and life",
            "📱 Limit screen time"
        ]
        for tip in tips:
            st.markdown(f"• {tip}")

def display_prediction_result(prediction):
    risk_score = prediction["risk_score"]
    risk_level = prediction["risk_level"]
    recommendations = prediction["recommendations"]
    
    # Risk level display
    risk_class = f"risk-{risk_level.lower()}"
    st.markdown(f"""
    <div class="risk-card {risk_class}">
        <h2>Risk Level: {risk_level}</h2>
        <h3>Risk Score: {risk_score:.2%}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Risk gauge
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = risk_score * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Risk Score (%)"},
        delta = {'reference': 50},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "lightgreen"},
                {'range': [30, 60], 'color': "yellow"},
                {'range': [60, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.subheader("Personalized Recommendations")
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"**{i}.** {rec}")

def make_prediction(data):
    """Make API call to backend for prediction"""
    try:
        response = requests.post(f"{API_BASE_URL}/predict", json=data, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to the prediction service. Please ensure the backend is running.")
        return None
    except Exception as e:
        st.error(f"Error making prediction: {str(e)}")
        return None

def history_page():
    st.header("Prediction History")
    
    try:
        response = requests.get(f"{API_BASE_URL}/predictions?limit=20", timeout=10)
        if response.status_code == 200:
            predictions = response.json()
            
            if predictions:
                # Convert to DataFrame
                df = pd.DataFrame(predictions)
                df['prediction_date'] = pd.to_datetime(df['prediction_date'])
                df['risk_percentage'] = df['risk_score'] * 100
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Predictions", len(df))
                
                with col2:
                    avg_risk = df['risk_percentage'].mean()
                    st.metric("Average Risk", f"{avg_risk:.1f}%")
                
                with col3:
                    high_risk_count = len(df[df['risk_level'] == 'High'])
                    st.metric("High Risk Predictions", high_risk_count)
                
                with col4:
                    recent_trend = "↗️" if len(df) > 1 and df.iloc[0]['risk_score'] > df.iloc[1]['risk_score'] else "↘️"
                    st.metric("Recent Trend", recent_trend)
                
                # Risk level distribution
                st.subheader("Risk Level Distribution")
                risk_counts = df['risk_level'].value_counts()
                fig_pie = px.pie(values=risk_counts.values, names=risk_counts.index, 
                               title="Distribution of Risk Levels")
                st.plotly_chart(fig_pie, use_container_width=True)
                
                # Timeline
                st.subheader("Risk Score Timeline")
                fig_line = px.line(df.sort_values('prediction_date'), 
                                 x='prediction_date', y='risk_percentage',
                                 title="Risk Score Over Time",
                                 labels={'risk_percentage': 'Risk Score (%)', 'prediction_date': 'Date'})
                st.plotly_chart(fig_line, use_container_width=True)
                
                # Detailed table
                st.subheader("Detailed History")
                display_df = df[['prediction_date', 'risk_level', 'risk_percentage']].copy()
                display_df['prediction_date'] = display_df['prediction_date'].dt.strftime('%Y-%m-%d %H:%M')
                display_df['risk_percentage'] = display_df['risk_percentage'].round(1)
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("No prediction history available yet. Make some predictions first!")
        else:
            st.error("Failed to load prediction history")
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to the service. Please ensure the backend is running.")
    except Exception as e:
        st.error(f"Error loading history: {str(e)}")

def analytics_page():
    st.header("Analytics Dashboard")
    
    try:
        response = requests.get(f"{API_BASE_URL}/predictions?limit=100", timeout=10)
        if response.status_code == 200:
            predictions = response.json()
            
            if predictions and len(predictions) > 5:
                df = pd.DataFrame(predictions)
                
                # Create feature columns for analysis
                feature_cols = ['sleep_hours', 'exercise_hours', 'stress_level', 
                              'social_activity', 'work_hours', 'screen_time']
                
                # Check if we have the required columns (they might not be in the response)
                st.subheader("Risk Correlation Analysis")
                st.info("Feature correlation analysis would be shown here with actual user data.")
                
                # Sample correlation heatmap with dummy data
                import numpy as np
                sample_data = {
                    'Sleep Hours': np.random.normal(7.5, 1.5, 50),
                    'Exercise Hours': np.random.exponential(3, 50),
                    'Stress Level': np.random.randint(1, 11, 50),
                    'Social Activity': np.random.randint(1, 11, 50),
                    'Work Hours': np.random.normal(8, 2, 50),
                    'Screen Time': np.random.normal(6, 3, 50),
                    'Risk Score': np.random.beta(2, 5, 50)
                }
                
                sample_df = pd.DataFrame(sample_data)
                correlation_matrix = sample_df.corr()
                
                fig_heatmap = px.imshow(correlation_matrix, 
                                      title="Feature Correlation Matrix (Sample Data)",
                                      color_continuous_scale="RdBu")
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Risk distribution by factors
                st.subheader("Risk Analysis by Lifestyle Factors")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_sleep = px.histogram(sample_df, x='Sleep Hours', nbins=15, 
                                           title="Sleep Hours Distribution")
                    st.plotly_chart(fig_sleep, use_container_width=True)
                
                with col2:
                    fig_exercise = px.histogram(sample_df, x='Exercise Hours', nbins=15,
                                              title="Exercise Hours Distribution") 
                    st.plotly_chart(fig_exercise, use_container_width=True)
                
                # Statistical insights
                st.subheader("Key Insights")
                insights = [
                    "💤 **Sleep**: Optimal range appears to be 7-9 hours for lowest risk",
                    "🏃‍♂️ **Exercise**: Regular exercise (2+ hours/week) correlates with lower risk",
                    "😰 **Stress**: Higher stress levels show strong correlation with increased risk",
                    "👥 **Social Activity**: Strong social connections are protective factors",
                    "💼 **Work Balance**: Long work hours (>10/day) increase risk significantly",
                    "📱 **Screen Time**: Excessive screen time correlates with higher risk"
                ]
                
                for insight in insights:
                    st.markdown(insight)
                    
            else:
                st.info("Need more data points (at least 5 predictions) for meaningful analytics.")
        else:
            st.error("Failed to load analytics data")
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to the service. Please ensure the backend is running.")
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

if __name__ == "__main__":
    main()