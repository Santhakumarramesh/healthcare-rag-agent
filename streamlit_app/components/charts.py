"""
Chart components using Plotly for data visualization.
"""
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any


def create_line_chart(data: Dict[str, Any], title: str, x_label: str = "Time", y_label: str = "Value"):
    """
    Create a line chart for time-series data.
    
    Args:
        data: Dictionary with 'x' and 'y' keys
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data.get("x", []),
        y=data.get("y", []),
        mode='lines+markers',
        line=dict(color='#0F4C81', width=2),
        marker=dict(size=6, color='#0F4C81'),
        fill='tozeroy',
        fillcolor='rgba(15, 76, 129, 0.1)'
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='#102A43', family='Inter')),
        xaxis_title=x_label,
        yaxis_title=y_label,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', size=12, color='#486581'),
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(showgrid=True, gridcolor='#D9E2EC'),
        yaxis=dict(showgrid=True, gridcolor='#D9E2EC'),
        hovermode='x unified'
    )
    
    return fig


def create_bar_chart(data: Dict[str, Any], title: str, x_label: str = "Category", y_label: str = "Count"):
    """
    Create a bar chart for categorical data.
    
    Args:
        data: Dictionary with 'x' and 'y' keys
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=data.get("x", []),
        y=data.get("y", []),
        marker=dict(
            color='#0F4C81',
            line=dict(color='#0C3B63', width=1)
        )
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='#102A43', family='Inter')),
        xaxis_title=x_label,
        yaxis_title=y_label,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', size=12, color='#486581'),
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#D9E2EC')
    )
    
    return fig


def create_donut_chart(labels: List[str], values: List[float], title: str):
    """
    Create a donut chart for distribution data.
    
    Args:
        labels: Category labels
        values: Values for each category
        title: Chart title
        
    Returns:
        Plotly figure
    """
    colors = ['#0F4C81', '#2CB1BC', '#2F855A', '#B7791F', '#C53030', '#486581']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(colors=colors[:len(labels)]),
        textinfo='label+percent',
        textfont=dict(size=12, family='Inter')
    )])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='#102A43', family='Inter')),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', size=12, color='#486581'),
        margin=dict(l=40, r=40, t=60, b=40),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.1
        )
    )
    
    return fig


def create_histogram(data: List[float], title: str, x_label: str = "Value", bins: int = 20):
    """
    Create a histogram for distribution analysis.
    
    Args:
        data: List of values
        title: Chart title
        x_label: X-axis label
        bins: Number of bins
        
    Returns:
        Plotly figure
    """
    fig = go.Figure(data=[go.Histogram(
        x=data,
        nbinsx=bins,
        marker=dict(
            color='#0F4C81',
            line=dict(color='#0C3B63', width=1)
        )
    )])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='#102A43', family='Inter')),
        xaxis_title=x_label,
        yaxis_title="Frequency",
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', size=12, color='#486581'),
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(showgrid=True, gridcolor='#D9E2EC'),
        yaxis=dict(showgrid=True, gridcolor='#D9E2EC')
    )
    
    return fig


def create_multi_line_chart(data: Dict[str, List], title: str, x_label: str = "Time"):
    """
    Create a multi-line chart for comparing multiple series.
    
    Args:
        data: Dictionary with series names as keys and lists of values
        title: Chart title
        x_label: X-axis label
        
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    colors = ['#0F4C81', '#2CB1BC', '#2F855A', '#B7791F']
    
    for idx, (name, values) in enumerate(data.items()):
        if name == 'x':
            continue
            
        fig.add_trace(go.Scatter(
            x=data.get('x', list(range(len(values)))),
            y=values,
            mode='lines+markers',
            name=name,
            line=dict(color=colors[idx % len(colors)], width=2),
            marker=dict(size=5)
        ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='#102A43', family='Inter')),
        xaxis_title=x_label,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', size=12, color='#486581'),
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(showgrid=True, gridcolor='#D9E2EC'),
        yaxis=dict(showgrid=True, gridcolor='#D9E2EC'),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig
