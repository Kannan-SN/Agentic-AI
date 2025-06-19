import streamlit as st
import pandas as pd
from typing import List, Dict, Any
import plotly.express as px
import plotly.graph_objects as go

def create_referral_results(recommendations: List[Dict[str, Any]]):
    """Create referral results display component"""
    
    if not recommendations:
        st.info("No referral recommendations available.")
        return
    
    st.subheader(f"🎯 Referral Recommendations ({len(recommendations)} paths)")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_score = sum(r.get('score', 0) for r in recommendations) / len(recommendations)
        st.metric("Average Score", f"{avg_score:.3f}")
    
    with col2:
        high_confidence = len([r for r in recommendations if r.get('confidence_level') == 'high'])
        st.metric("High Confidence", f"{high_confidence}/{len(recommendations)}")
    
    with col3:
        direct_paths = len([r for r in recommendations if r.get('type') == 'direct'])
        st.metric("Direct Paths", direct_paths)
    
    with col4:
        avg_success_prob = sum(r.get('success_probability', 0) for r in recommendations) / len(recommendations)
        st.metric("Avg Success Rate", f"{avg_success_prob:.0%}")
    
    # Display options
    view_mode = st.radio("View Mode", ["Summary Cards", "Detailed View", "Comparison Table"], horizontal=True)
    
    if view_mode == "Summary Cards":
        _display_recommendation_cards(recommendations)
    elif view_mode == "Detailed View":
        _display_recommendation_detailed(recommendations)
    else:  # Comparison Table
        _display_recommendation_table(recommendations)
    
    # Analytics section
    if len(recommendations) > 1:
        st.subheader("📊 Recommendations Analytics")
        _display_recommendation_analytics(recommendations)

def _display_recommendation_cards(recommendations: List[Dict[str, Any]]):
    """Display recommendations as cards"""
    
    for i, rec in enumerate(recommendations):
        with st.container():
            # Header with ranking and score
            col1, col2 = st.columns([3, 1])
            
            with col1:
                rank = rec.get('recommendation_rank', i + 1)
                alumni_details = rec.get('alumni_details', [{}])
                alumni_name = alumni_details[0].get('name', 'Unknown') if alumni_details else 'Unknown'
                company = alumni_details[0].get('current_company', 'Unknown') if alumni_details else 'Unknown'
                
                st.markdown(f"### #{rank} - {alumni_name} at {company}")
            
            with col2:
                score = rec.get('score', 0)
                confidence = rec.get('confidence_level', 'medium')
                
                # Color code by confidence
                color = "🟢" if confidence == 'high' else "🟡" if confidence == 'medium' else "🔴"
                st.markdown(f"**Score: {score:.3f}** {color}")
            
            # Key information
            col1, col2, col3 = st.columns(3)
            
            with col1:
                path_type = rec.get('type', 'unknown').replace('_', ' ').title()
                st.write(f"**Path Type:** {path_type}")
                
                success_prob = rec.get('success_probability', 0)
                st.write(f"**Success Rate:** {success_prob:.0%}")
            
            with col2:
                response_time = rec.get('estimated_response_time', 'Unknown')
                st.write(f"**Response Time:** {response_time}")
                
                connection_strength = rec.get('connection_strength', 0)
                st.write(f"**Connection:** {connection_strength:.2f}/1.0")
            
            with col3:
                # Alumni role and experience
                alumni_role = alumni_details[0].get('current_role', 'Unknown') if alumni_details else 'Unknown'
                st.write(f"**Role:** {alumni_role}")
                
                experience = alumni_details[0].get('years_of_experience', 0) if alumni_details else 0
                st.write(f"**Experience:** {experience} years")
            
            # Path description
            description = rec.get('path_description', 'No description available')
            st.write(f"**Strategy:** {description}")
            
            # Evaluation metrics (if available)
            if rec.get('evaluation'):
                eval_metrics = rec['evaluation']
                
                with st.expander("📈 Detailed Evaluation"):
                    metrics_col1, metrics_col2 = st.columns(2)
                    
                    with metrics_col1:
                        st.write(f"**Accessibility:** {eval_metrics.get('accessibility', 0):.2f}/1.0")
                        st.write(f"**Influence:** {eval_metrics.get('influence', 0):.2f}/1.0")
                        st.write(f"**Responsiveness:** {eval_metrics.get('responsiveness', 0):.2f}/1.0")
                    
                    with metrics_col2:
                        st.write(f"**Relevance:** {eval_metrics.get('relevance', 0):.2f}/1.0")
                        st.write(f"**Timing:** {eval_metrics.get('timing', 0):.2f}/1.0")
            
            # Next steps
            if rec.get('next_steps'):
                with st.expander("📋 Next Steps"):
                    for step in rec['next_steps']:
                        st.write(f"• {step}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"Generate Message", key=f"msg_{i}"):
                    st.session_state[f'selected_referral_{i}'] = rec
                    st.success("Ready to generate personalized message!")
            
            with col2:
                if st.button(f"Save Path", key=f"save_{i}"):
                    st.info("Referral path saved to favorites!")
            
            with col3:
                if st.button(f"More Details", key=f"details_{i}"):
                    st.session_state[f'show_details_{i}'] = True
            
            st.markdown("---")

def _display_recommendation_detailed(recommendations: List[Dict[str, Any]]):
    """Display detailed view of recommendations"""
    
    # Pagination for large lists
    items_per_page = 3
    total_pages = (len(recommendations) + items_per_page - 1) // items_per_page
    
    if total_pages > 1:
        page = st.selectbox("Page", range(1, total_pages + 1)) - 1
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(recommendations))
        page_recommendations = recommendations[start_idx:end_idx]
    else:
        page_recommendations = recommendations
    
    for i, rec in enumerate(page_recommendations):
        rank = rec.get('recommendation_rank', i + 1)
        alumni_details = rec.get('alumni_details', [{}])
        alumni_name = alumni_details[0].get('name', 'Unknown') if alumni_details else 'Unknown'
        
        with st.expander(f"#{rank} - {alumni_name} (Score: {rec.get('score', 0):.3f})", expanded=i == 0):
            _display_single_recommendation_detailed(rec)

def _display_single_recommendation_detailed(rec: Dict[str, Any]):
    """Display detailed view of a single recommendation"""
    
    # Alumni Information
    st.subheader("👤 Alumni Information")
    alumni_details = rec.get('alumni_details', [{}])
    
    if alumni_details:
        alumni = alumni_details[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Name:** {alumni.get('name', 'Unknown')}")
            st.write(f"**Company:** {alumni.get('current_company', 'Unknown')}")
            st.write(f"**Role:** {alumni.get('current_role', 'Unknown')}")
        
        with col2:
            st.write(f"**Experience:** {alumni.get('years_of_experience', 0)} years")
            st.write(f"**Industry:** {alumni.get('industry', 'Unknown')}")
            st.write(f"**Location:** {alumni.get('location', 'Unknown')}")
        
        with col3:
            st.write(f"**Graduation:** {alumni.get('graduation_year', 'N/A')}")
            st.write(f"**Willing to Refer:** {'Yes' if alumni.get('willing_to_refer', True) else 'No'}")
            
            capacity = alumni.get('max_referrals_per_month', 3)
            current = alumni.get('referral_count_this_month', 0)
            st.write(f"**Availability:** {capacity - current}/{capacity}")
    
    # Referral Path Information
    st.subheader("🛤️ Referral Path Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Path Type:** {rec.get('type', 'unknown').replace('_', ' ').title()}")
        st.write(f"**Overall Score:** {rec.get('score', 0):.3f}/1.0")
        st.write(f"**Connection Strength:** {rec.get('connection_strength', 0):.3f}/1.0")
        st.write(f"**Success Probability:** {rec.get('success_probability', 0):.0%}")
    
    with col2:
        st.write(f"**Confidence Level:** {rec.get('confidence_level', 'medium').title()}")
        st.write(f"**Estimated Response Time:** {rec.get('estimated_response_time', 'Unknown')}")
        st.write(f"**Referral Potential:** {rec.get('referral_potential', 'Unknown')}")
        st.write(f"**Contact Feasibility:** {rec.get('contact_feasibility', 'Unknown')}")
    
    # Strategy Description
    if rec.get('path_description'):
        st.subheader("📋 Strategy Description")
        st.write(rec['path_description'])
    
    # Evaluation Breakdown
    if rec.get('evaluation'):
        st.subheader("📊 Detailed Evaluation")
        evaluation = rec['evaluation']
        
        # Create radar chart for evaluation metrics
        metrics = ['accessibility', 'influence', 'responsiveness', 'relevance', 'timing']
        values = [evaluation.get(metric, 0) for metric in metrics]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=[metric.title() for metric in metrics],
            fill='toself',
            name='Evaluation Scores'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Risk Factors
    if rec.get('risk_factors'):
        st.subheader("⚠️ Risk Factors")
        for risk in rec['risk_factors']:
            st.warning(f"• {risk}")
    
    # Optimization Suggestions
    if rec.get('optimization_suggestions'):
        st.subheader("💡 Optimization Suggestions")
        for suggestion in rec['optimization_suggestions']:
            st.info(f"• {suggestion}")
    
    # Action Plan
    if rec.get('action_plan'):
        st.subheader("📅 Action Plan")
        action_plan = rec['action_plan']
        
        col1, col2 = st.columns(2)
        
        with col1:
            if action_plan.get('immediate_actions'):
                st.write("**Immediate Actions:**")
                for action in action_plan['immediate_actions']:
                    st.write(f"• {action}")
        
        with col2:
            if action_plan.get('follow_up_actions'):
                st.write("**Follow-up Actions:**")
                for action in action_plan['follow_up_actions']:
                    st.write(f"• {action}")
        
        if action_plan.get('preparation_required'):
            st.write("**Preparation Required:**")
            for prep in action_plan['preparation_required']:
                st.write(f"• {prep}")
    
    # Timeline
    if rec.get('timeline'):
        st.subheader("📆 Timeline")
        timeline = rec['timeline']
        
        for day, activity in timeline.items():
            st.write(f"**{day.replace('_', ' ').title()}:** {activity}")
    
    # Success Metrics
    if rec.get('success_metrics'):
        st.subheader("🎯 Success Metrics")
        metrics = rec['success_metrics']
        
        for metric, description in metrics.items():
            st.write(f"**{metric.replace('_', ' ').title()}:** {description}")

def _display_recommendation_table(recommendations: List[Dict[str, Any]]):
    """Display recommendations in table format"""
    
    # Prepare data for table
    table_data = []
    
    for rec in recommendations:
        alumni_details = rec.get('alumni_details', [{}])
        alumni = alumni_details[0] if alumni_details else {}
        
        row = {
            'Rank': rec.get('recommendation_rank', 0),
            'Alumni': alumni.get('name', 'Unknown'),
            'Company': alumni.get('current_company', 'Unknown'),
            'Role': alumni.get('current_role', 'Unknown'),
            'Score': rec.get('score', 0),
            'Type': rec.get('type', 'unknown').replace('_', ' ').title(),
            'Success Rate': f"{rec.get('success_probability', 0):.0%}",
            'Response Time': rec.get('estimated_response_time', 'Unknown'),
            'Confidence': rec.get('confidence_level', 'medium').title(),
            'Connection': f"{rec.get('connection_strength', 0):.2f}"
        }
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    
    # Style the dataframe
    def highlight_top_scores(val):
        if isinstance(val, (int, float)) and val >= 0.8:
            return 'background-color: lightgreen'
        elif isinstance(val, (int, float)) and val >= 0.6:
            return 'background-color: lightyellow'
        return ''
    
    styled_df = df.style.applymap(highlight_top_scores, subset=['Score'])
    st.dataframe(styled_df, use_container_width=True)
    
    # Download option
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Recommendations as CSV",
        data=csv,
        file_name="referral_recommendations.csv",
        mime="text/csv"
    )

def _display_recommendation_analytics(recommendations: List[Dict[str, Any]]):
    """Display analytics for recommendations"""
    
    tab1, tab2, tab3 = st.tabs(["Score Distribution", "Path Types", "Success Factors"])
    
    with tab1:
        # Score distribution histogram
        scores = [rec.get('score', 0) for rec in recommendations]
        
        fig = px.histogram(
            x=scores,
            nbins=10,
            title="Score Distribution",
            labels={'x': 'Score', 'y': 'Count'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Path types pie chart
        path_types = [rec.get('type', 'unknown') for rec in recommendations]
        type_counts = pd.Series(path_types).value_counts()
        
        fig = px.pie(
            values=type_counts.values,
            names=[name.replace('_', ' ').title() for name in type_counts.index],
            title="Path Types Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Success factors analysis
        success_probs = [rec.get('success_probability', 0) for rec in recommendations]
        connection_strengths = [rec.get('connection_strength', 0) for rec in recommendations]
        scores = [rec.get('score', 0) for rec in recommendations]
        
        # Create DataFrame for scatter plot
        scatter_data = pd.DataFrame({
            'Success Probability': success_probs,
            'Connection Strength': connection_strengths,
            'Overall Score': scores,
            'Alumni': [rec.get('alumni_details', [{}])[0].get('name', f'Alumni {i+1}') 
                      for i, rec in enumerate(recommendations)]
        })
        
        fig = px.scatter(
            scatter_data,
            x='Connection Strength',
            y='Success Probability',
            size='Overall Score',
            hover_name='Alumni',
            title="Success Factors Analysis",
            labels={
                'Connection Strength': 'Connection Strength',
                'Success Probability': 'Success Probability',
                'Overall Score': 'Overall Score'
            }
        )
        st.plotly_chart(fig, use_container_width=True)

def create_referral_summary(recommendations: List[Dict[str, Any]]):
    """Create a summary of referral recommendations"""
    
    if not recommendations:
        return
    
    st.subheader("📋 Referral Summary")
    
    # Top recommendation highlight
    top_rec = recommendations[0] if recommendations else None
    
    if top_rec:
        alumni_details = top_rec.get('alumni_details', [{}])
        alumni_name = alumni_details[0].get('name', 'Unknown') if alumni_details else 'Unknown'
        company = alumni_details[0].get('current_company', 'Unknown') if alumni_details else 'Unknown'
        score = top_rec.get('score', 0)
        
        st.success(f"🏆 **Top Recommendation:** {alumni_name} at {company} (Score: {score:.3f})")
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        high_score_count = len([r for r in recommendations if r.get('score', 0) >= 0.8])
        st.metric("High-Score Paths", f"{high_score_count}/{len(recommendations)}")
    
    with col2:
        direct_count = len([r for r in recommendations if r.get('type') == 'direct'])
        st.metric("Direct Connections", f"{direct_count}/{len(recommendations)}")
    
    with col3:
        avg_success = sum(r.get('success_probability', 0) for r in recommendations) / len(recommendations)
        st.metric("Average Success Rate", f"{avg_success:.0%}")
    
    # Recommended next action
    if recommendations:
        st.subheader("🎯 Recommended Next Action")
        
        best_path = recommendations[0]
        next_steps = best_path.get('next_steps', [])
        
        if next_steps:
            st.write(f"**Recommended first step:** {next_steps[0]}")
            
            if len(next_steps) > 1:
                with st.expander("See all next steps"):
                    for i, step in enumerate(next_steps, 1):
                        st.write(f"{i}. {step}")
        else:
            st.write("Generate personalized outreach message for the top recommendation.")