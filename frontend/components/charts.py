import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_risk_gauge(risk_score):
    """Create a risk gauge chart"""
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
    return fig

def create_correlation_heatmap(data):
    """Create correlation heatmap"""
    correlation_matrix = data.corr()
    fig = px.imshow(correlation_matrix, 
                   title="Feature Correlation Matrix",
                   color_continuous_scale="RdBu")
    return fig

def create_timeline_chart(df, x_col, y_col, title):
    """Create timeline chart"""
    fig = px.line(df, x=x_col, y=y_col, title=title)
    return fig
