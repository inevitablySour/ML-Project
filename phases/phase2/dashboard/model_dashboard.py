import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Cycling Model Performance Dashboard",
    page_icon="🚴",
    layout="wide"
)

st.title("Model Performance Dashboard")
st.markdown("### CAICLE Cycling Team - Top 10 Prediction Models")

# Load model results
def load_model_results():
    """
    Expected format:
    {
        'model_name': {
            'overall': {'precision': 0.85, 'recall': 0.72, 'f1': 0.78, 'accuracy': 0.88},
            'confusion_matrix': [[tn, fp], [fn, tp]],
            'feature_importance': {'feature1': 0.3, 'feature2': 0.25, ...},
            'class_report': {...}  # from classification_report
        }
    }
    """
    # Load from file - use path relative to this script
    try:
        script_dir = Path(__file__).parent
        json_path = script_dir / 'model_results.json'
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Demo data if file doesn't exist
        return {
            'Random Forest': {
                'overall': {'precision': 0.82, 'recall': 0.68, 'f1': 0.74, 'accuracy': 0.85},
                'confusion_matrix': [[15000, 2500], [3200, 7300]],
                'feature_importance': {'UCI_Ranking': 0.35, 'Age': 0.15, 'pps_Climber': 0.12, 'Recent_Performance': 0.18}
            },
            'Gradient Boosting': {
                'overall': {'precision': 0.78, 'recall': 0.75, 'f1': 0.76, 'accuracy': 0.83},
                'confusion_matrix': [[14500, 3000], [2625, 7875]],
                'feature_importance': {'UCI_Ranking': 0.42, 'pps_Sprint': 0.18, 'Age': 0.10, 'Race_Tier': 0.15}
            },
            'Logistic Regression': {
                'overall': {'precision': 0.76, 'recall': 0.70, 'f1': 0.73, 'accuracy': 0.81},
                'confusion_matrix': [[14200, 3300], [3150, 7350]],
                'feature_importance': {'UCI_Ranking': 0.28, 'pps_Climber': 0.22, 'Age': 0.14, 'Timelag_Avg': 0.20}
            }
        }

results = load_model_results()

# Sidebar - Model Selection
st.sidebar.header("Model Selection")
selected_models = st.sidebar.multiselect(
    "Compare Models:",
    options=list(results.keys()),
    default=list(results.keys())
)

# Sidebar - Metric Selection
st.sidebar.header("Metric Selection")
available_metrics = ['Precision', 'Recall', 'F1-Score', 'Accuracy']
selected_metrics = st.sidebar.multiselect(
    "Metrics to Display:",
    options=available_metrics,
    default=available_metrics
)

if not selected_metrics:
    st.sidebar.warning("Select at least one metric")

# Overall Performance Comparison
st.header("Overall Performance Metrics")
st.info("**Note:** Metrics shown represent the best performance across all tested thresholds (default 0.5 and optimized). Each model may use a different threshold to maximize its primary metric while maintaining recall > 15%.")

if selected_models:
    # Create comparison dataframe
    comparison_data = []
    for model in selected_models:
        metrics = results[model]['overall']
        comparison_data.append({
            'Model': model,
            'Precision': metrics['precision'],
            'Recall': metrics['recall'],
            'F1-Score': metrics['f1'],
            'Accuracy': metrics['accuracy']
        })
    
    df_comparison = pd.DataFrame(comparison_data)
    
    # Display metrics in columns (only for selected metrics)
    if selected_metrics:
        cols = st.columns(len(selected_metrics))
        
        for idx, metric in enumerate(selected_metrics):
            with cols[idx]:
                best_idx = df_comparison[metric].idxmax()
                best_model = df_comparison.loc[best_idx, 'Model']
                best_value = df_comparison.loc[best_idx, metric]
                
                # Get threshold info
                threshold_info = results[best_model]['overall'].get('threshold_label', 'Unknown')
                
                st.metric(
                    f"Best {metric}", 
                    f"{best_value:.2%}",
                    f"↑ {best_model}"
                )
                st.caption(f"Threshold: {threshold_info}")
    
    # Bar chart comparison (only selected metrics)
    if selected_metrics:
        fig_comparison = go.Figure()
        
        for metric in selected_metrics:
            fig_comparison.add_trace(go.Bar(
                name=metric,
                x=df_comparison['Model'],
                y=df_comparison[metric],
                text=[f"{v:.2%}" for v in df_comparison[metric]],
                textposition='auto',
            ))
    
        fig_comparison.update_layout(
            barmode='group',
            title='Model Performance Comparison',
            yaxis_title='Score',
            yaxis=dict(range=[0, 1]),
            height=400
        )
        
        # Add 75% precision threshold line only if Precision is selected
        if 'Precision' in selected_metrics:
            fig_comparison.add_hline(y=0.75, line_dash="dash", line_color="red", 
                                     annotation_text="Target Precision (75%)")
        
        st.plotly_chart(fig_comparison, width='stretch')
    else:
        st.warning("Please select at least one metric to display the comparison chart.")

    # Detailed Model Performance
    st.header("Individual Model Details")
    
    tabs = st.tabs(selected_models)
    
    for i, model_name in enumerate(selected_models):
        with tabs[i]:
            model_data = results[model_name]
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Confusion Matrix")
                cm = model_data['confusion_matrix']
                
                fig_cm = go.Figure(data=go.Heatmap(
                    z=[[cm[0][0], cm[0][1]], 
                       [cm[1][0], cm[1][1]]],
                    x=['Predicted Not Top-10', 'Predicted Top-10'],
                    y=['Actual Not Top-10', 'Actual Top-10'],
                    text=[[f'TN: {cm[0][0]}', f'FP: {cm[0][1]}'],
                          [f'FN: {cm[1][0]}', f'TP: {cm[1][1]}']],
                    texttemplate='%{text}',
                    colorscale='Blues',
                    showscale=False
                ))
                
                fig_cm.update_layout(
                    title=f'{model_name} Confusion Matrix',
                    height=400
                )
                
                st.plotly_chart(fig_cm, width='stretch')
                
                # Calculate additional metrics
                tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]
                total = tn + fp + fn + tp
                
                st.markdown(f"""
                **Additional Metrics:**
                - False Positive Rate: {fp/(fp+tn):.2%}
                - False Negative Rate: {fn/(fn+tp):.2%}
                - True Positive Count: {tp:,}
                - True Negative Count: {tn:,}
                """)
            
            with col2:
                st.subheader("Feature Importance")
                
                if 'feature_importance' in model_data:
                    features = model_data['feature_importance']
                    feat_df = pd.DataFrame({
                        'Feature': list(features.keys()),
                        'Importance': list(features.values())
                    }).sort_values('Importance', ascending=True)
                    
                    fig_feat = go.Figure(go.Bar(
                        x=feat_df['Importance'],
                        y=feat_df['Feature'],
                        orientation='h',
                        text=[f"{v:.2%}" for v in feat_df['Importance']],
                        textposition='auto',
                        marker_color='lightblue'
                    ))
                    
                    fig_feat.update_layout(
                        title=f'{model_name} Feature Importance',
                        xaxis_title='Importance',
                        height=400
                    )
                    
                    st.plotly_chart(fig_feat, width='stretch')
                    
                    st.info(f"🎯 Top feature: **{feat_df.iloc[-1]['Feature']}** "
                           f"({feat_df.iloc[-1]['Importance']:.2%})")
    
    # Business Context
    st.header("Business Impact")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Precision vs. Recall Trade-off")
        
        fig_scatter = go.Figure()
        
        for model in selected_models:
            metrics = results[model]['overall']
            fig_scatter.add_trace(go.Scatter(
                x=[metrics['recall']],
                y=[metrics['precision']],
                mode='markers+text',
                name=model,
                text=[model],
                textposition="top center",
                marker=dict(size=15)
            ))
        
        # Add target zone
        fig_scatter.add_hline(y=0.75, line_dash="dash", line_color="green",
                             annotation_text="Target Precision")
        fig_scatter.add_vrect(x0=0.65, x1=1.0, fillcolor="green", opacity=0.1,
                             annotation_text="Good Recall Zone", annotation_position="top left")
        
        fig_scatter.update_layout(
            xaxis_title='Recall',
            yaxis_title='Precision',
            xaxis=dict(range=[0, 1]),
            yaxis=dict(range=[0, 1]),
            height=400
        )
        
        st.plotly_chart(fig_scatter, width='stretch')
    
    with col2:
        st.subheader("Model Recommendations")
        
        # Find best model for precision
        best_precision_model = max(selected_models, 
                                  key=lambda m: results[m]['overall']['precision'])
        best_precision_value = results[best_precision_model]['overall']['precision']
        
        # Find best balanced model (F1)
        best_balanced_model = max(selected_models,
                                 key=lambda m: results[m]['overall']['f1'])
        best_balanced_value = results[best_balanced_model]['overall']['f1']
        
        if best_precision_value >= 0.75:
            st.success(f"**{best_precision_model}** meets target precision ({best_precision_value:.2%})")
            st.markdown("**Recommended for:** Investment decisions where false positives are costly")
        else:
            st.warning(f"Best precision is {best_precision_value:.2%} (target: 75%)")
            st.markdown("**Consider:** Hyperparameter tuning or ensemble methods")
        
        st.info(f"**{best_balanced_model}** has best balance (F1: {best_balanced_value:.2%})")
        st.markdown("**Recommended for:** Identifying breakthrough talent with balanced risk")
        
        st.markdown("""
        ---
        **Key Insights:**
        - High precision = Confident in predicted Top-10 riders
        - High recall = Don't miss potential stars
        - Use precision-focused model for recruitment
        - Use recall-focused model for talent scouting
        """)

else:
    st.warning("Please select at least one model from the sidebar.")

# Footer
st.markdown("---")
st.caption("CAICLE Cycling Analytics | Data-driven recruitment for professional cycling")
