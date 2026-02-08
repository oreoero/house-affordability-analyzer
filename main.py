# streamlit_calculator.py - Home Affordability Calculator using Streamlit

import math
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dataclasses import dataclass
from typing import List, Dict, Any
import numpy as np


@dataclass
class MortgageScenario:
    """Data class representing a mortgage scenario"""
    home_price: float
    down_payment_amount: float
    interest_rate: float
    loan_term_years: int
    monthly_income: float
    monthly_debts: float = 0
    property_tax_annual: float = 0
    insurance_annual: float = 0
    hoa_monthly: float = 0


class MortgageModel:
    """Model class handling all mortgage calculations"""
    
    @staticmethod
    def calculate_monthly_payment(principal: float, annual_rate: float, years: int) -> float:
        """Calculate monthly mortgage payment using standard formula"""
        if annual_rate == 0:
            return principal / (years * 12)
        
        monthly_rate = annual_rate / 12 / 100
        num_payments = years * 12
        
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                         ((1 + monthly_rate) ** num_payments - 1)
        
        return monthly_payment
    
    @staticmethod
    def calculate_affordability_metrics(scenario: MortgageScenario) -> Dict[str, Any]:
        """Calculate comprehensive affordability metrics"""
        loan_amount = scenario.home_price - scenario.down_payment_amount
        down_payment = scenario.down_payment_amount
        down_payment_percent = (scenario.down_payment_amount / scenario.home_price) * 100
        
        monthly_pi = MortgageModel.calculate_monthly_payment(
            loan_amount, scenario.interest_rate, scenario.loan_term_years
        )
        
        monthly_property_tax = scenario.property_tax_annual / 12
        monthly_insurance = scenario.insurance_annual / 12
        total_monthly_payment = monthly_pi + monthly_property_tax + monthly_insurance + scenario.hoa_monthly
        
        # Debt-to-income ratios
        front_end_ratio = (total_monthly_payment / scenario.monthly_income) * 100
        back_end_ratio = ((total_monthly_payment + scenario.monthly_debts) / scenario.monthly_income) * 100
        
        # Total costs
        total_payments = monthly_pi * scenario.loan_term_years * 12
        total_interest = total_payments - loan_amount
        
        return {
            'loan_amount': loan_amount,
            'down_payment': down_payment,
            'down_payment_percent': down_payment_percent,
            'monthly_pi': monthly_pi,
            'monthly_property_tax': monthly_property_tax,
            'monthly_insurance': monthly_insurance,
            'total_monthly_payment': total_monthly_payment,
            'front_end_ratio': front_end_ratio,
            'back_end_ratio': back_end_ratio,
            'total_payments': total_payments,
            'total_interest': total_interest,
            'affordable': front_end_ratio <= 28 and back_end_ratio <= 36
        }
    
    @staticmethod
    def generate_comparison_data(base_scenario: MortgageScenario, 
                               price_range: tuple, rate_range: tuple, 
                               down_payment_range: tuple) -> List[Dict]:
        """Generate data for comparison charts"""
        data = []
        
        # Price comparison
        price_values = np.linspace(price_range[0], price_range[1], 10)
        for price in price_values:
            # Keep the same down payment amount, but recalculate percentage for new price
            scenario = MortgageScenario(
                home_price=price,
                down_payment_amount=base_scenario.down_payment_amount,
                interest_rate=base_scenario.interest_rate,
                loan_term_years=base_scenario.loan_term_years,
                monthly_income=base_scenario.monthly_income,
                monthly_debts=base_scenario.monthly_debts,
                property_tax_annual=price * 0.01,  # Assume 1% property tax
                insurance_annual=price * 0.003,   # Assume 0.3% insurance
                hoa_monthly=base_scenario.hoa_monthly
            )
            metrics = MortgageModel.calculate_affordability_metrics(scenario)
            data.append({
                'scenario_type': 'Price Variation',
                'variable_value': price,
                'monthly_payment': metrics['total_monthly_payment'],
                'front_end_ratio': metrics['front_end_ratio'],
                'affordable': metrics['affordable']
            })
        
        # Rate comparison
        rate_values = np.linspace(rate_range[0], rate_range[1], 10)
        for rate in rate_values:
            scenario = MortgageScenario(
                home_price=base_scenario.home_price,
                down_payment_amount=base_scenario.down_payment_amount,
                interest_rate=rate,
                loan_term_years=base_scenario.loan_term_years,
                monthly_income=base_scenario.monthly_income,
                monthly_debts=base_scenario.monthly_debts,
                property_tax_annual=base_scenario.property_tax_annual,
                insurance_annual=base_scenario.insurance_annual,
                hoa_monthly=base_scenario.hoa_monthly
            )
            metrics = MortgageModel.calculate_affordability_metrics(scenario)
            data.append({
                'scenario_type': 'Rate Variation',
                'variable_value': rate,
                'monthly_payment': metrics['total_monthly_payment'],
                'front_end_ratio': metrics['front_end_ratio'],
                'affordable': metrics['affordable']
            })
        
        # Down payment comparison
        dp_values = np.linspace(down_payment_range[0], down_payment_range[1], 10)
        for dp_amount in dp_values:
            scenario = MortgageScenario(
                home_price=base_scenario.home_price,
                down_payment_amount=dp_amount,
                interest_rate=base_scenario.interest_rate,
                loan_term_years=base_scenario.loan_term_years,
                monthly_income=base_scenario.monthly_income,
                monthly_debts=base_scenario.monthly_debts,
                property_tax_annual=base_scenario.property_tax_annual,
                insurance_annual=base_scenario.insurance_annual,
                hoa_monthly=base_scenario.hoa_monthly
            )
            metrics = MortgageModel.calculate_affordability_metrics(scenario)
            data.append({
                'scenario_type': 'Down Payment Variation',
                'variable_value': dp_amount,
                'monthly_payment': metrics['total_monthly_payment'],
                'front_end_ratio': metrics['front_end_ratio'],
                'affordable': metrics['affordable']
            })
        
        return data


def create_payment_breakdown_chart(metrics: Dict[str, Any]) -> go.Figure:
    """Create a pie chart showing payment breakdown"""
    labels = ['Principal & Interest', 'Property Tax', 'Insurance', 'HOA']
    values = [
        metrics['monthly_pi'],
        metrics['monthly_property_tax'],
        metrics['monthly_insurance'],
        metrics.get('monthly_hoa', 0)
    ]
    
    # Filter out zero values
    filtered_labels = []
    filtered_values = []
    for label, value in zip(labels, values):
        if value > 0:
            filtered_labels.append(label)
            filtered_values.append(value)
    
    fig = go.Figure(data=[go.Pie(
        labels=filtered_labels,
        values=filtered_values,
        hole=0.3,
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>$%{value:,.0f}',
        marker=dict(colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    )])
    
    fig.update_layout(
        title="Monthly Payment Breakdown",
        font=dict(size=12),
        height=400
    )
    
    return fig


def create_comparison_charts(data: List[Dict]) -> go.Figure:
    """Create comparison charts for different scenarios"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Monthly Payment vs Home Price',
            'Monthly Payment vs Interest Rate',
            'Monthly Payment vs Down Payment %',
            'DTI Ratio Comparison'
        ),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Separate data by scenario type
    price_data = [d for d in data if d['scenario_type'] == 'Price Variation']
    rate_data = [d for d in data if d['scenario_type'] == 'Rate Variation']
    dp_data = [d for d in data if d['scenario_type'] == 'Down Payment Variation']
    
    # Price variation
    fig.add_trace(
        go.Scatter(
            x=[d['variable_value'] for d in price_data],
            y=[d['monthly_payment'] for d in price_data],
            mode='lines+markers',
            name='Price vs Payment',
            line=dict(color='blue'),
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Rate variation
    fig.add_trace(
        go.Scatter(
            x=[d['variable_value'] for d in rate_data],
            y=[d['monthly_payment'] for d in rate_data],
            mode='lines+markers',
            name='Rate vs Payment',
            line=dict(color='red'),
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Down payment variation
    fig.add_trace(
        go.Scatter(
            x=[d['variable_value'] for d in dp_data],
            y=[d['monthly_payment'] for d in dp_data],
            mode='lines+markers',
            name='Down Payment vs Payment',
            line=dict(color='green'),
            showlegend=False
        ),
        row=2, col=1
    )
    
    # DTI ratio comparison
    colors = {'Price Variation': 'blue', 'Rate Variation': 'red', 'Down Payment Variation': 'green'}
    for scenario_type in ['Price Variation', 'Rate Variation', 'Down Payment Variation']:
        scenario_data = [d for d in data if d['scenario_type'] == scenario_type]
        fig.add_trace(
            go.Scatter(
                x=[d['variable_value'] for d in scenario_data],
                y=[d['front_end_ratio'] for d in scenario_data],
                mode='lines+markers',
                name=f'{scenario_type}',
                line=dict(color=colors[scenario_type]),
                showlegend=True
            ),
            row=2, col=2
        )
    
    # Add affordability threshold line
    fig.add_hline(y=28, line_dash="dash", line_color="orange", 
                 annotation_text="28% DTI Threshold", row=2, col=2)
    
    fig.update_layout(height=800)
    
    # Update axis labels
    fig.update_xaxes(title_text="Home Price ($)", row=1, col=1)
    fig.update_xaxes(title_text="Interest Rate (%)", row=1, col=2)
    fig.update_xaxes(title_text="Down Payment ($)", row=2, col=1)
    fig.update_xaxes(title_text="Variable Value", row=2, col=2)
    fig.update_yaxes(title_text="Monthly Payment ($)", row=1, col=1)
    fig.update_yaxes(title_text="Monthly Payment ($)", row=1, col=2)
    fig.update_yaxes(title_text="Monthly Payment ($)", row=2, col=1)
    fig.update_yaxes(title_text="DTI Ratio (%)", row=2, col=2)
    
    return fig


def main():
    st.set_page_config(
        page_title="Home Affordability Calculator",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🏠 Home Affordability Calculator")
    st.caption("📍 Redmond, Washington")
    st.markdown("---")
    
    # Sidebar inputs
    st.sidebar.header("📊 Input Parameters")
    
    st.sidebar.subheader("Basic Information")
    home_price = st.sidebar.number_input("Home Price ($)", min_value=50000, max_value=5000000, value=1850000, step=10000)
    
    # Initialize down payment in session state if not exists
    if 'down_payment_amount' not in st.session_state:
        st.session_state.down_payment_amount = min(1000000, int(home_price * 0.2))
    
    # Initialize property tax in session state if not exists
    if 'property_tax_annual' not in st.session_state:
        st.session_state.property_tax_annual = int(home_price * 0.0105)  # Default 1.05% for Redmond, WA
    
    # Calculate reasonable down payment range
    min_down_payment = max(1000, int(home_price * 0.03))  # At least 3% or $1000
    max_down_payment = int(home_price * 1) 
    
    # Ensure current down payment is within valid range for new home price
    if st.session_state.down_payment_amount < min_down_payment:
        st.session_state.down_payment_amount = min_down_payment
    elif st.session_state.down_payment_amount > max_down_payment:
        st.session_state.down_payment_amount = max_down_payment

    down_payment_amount = st.sidebar.number_input(
        "Down Payment ($)", 
        min_value=min_down_payment, 
        max_value=max_down_payment, 
        value=st.session_state.down_payment_amount, 
        step=5000,
        key='down_payment_input'
    )
    
    # Update session state when user changes the value
    st.session_state.down_payment_amount = down_payment_amount
    
    interest_rate = st.sidebar.slider("Interest Rate (%)", min_value=3.0, max_value=10.0, value=6.5, step=0.1)
    loan_term_years = st.sidebar.selectbox("Loan Term (years)", [15, 20, 25, 30], index=3)
    
    st.sidebar.subheader("Financial Information")
    monthly_income = st.sidebar.number_input("Monthly Income ($)", min_value=1000, max_value=100000, value=25000, step=500)
    monthly_debts = st.sidebar.number_input("Monthly Debts ($)", min_value=0, max_value=50000, value=2500, step=100)
    
    # Update property tax default based on home price
    default_property_tax = int(home_price * 0.0105)  # 1.05% for Redmond, WA (King County)
    if 'property_tax_annual' not in st.session_state or st.session_state.get('last_home_price') != home_price:
        st.session_state.property_tax_annual = default_property_tax
        st.session_state.last_home_price = home_price
    
    property_tax_annual = st.sidebar.number_input(
        "Property Tax (Annual $)", 
        min_value=0, 
        max_value=100000, 
        value=st.session_state.property_tax_annual, 
        step=500,
        key='property_tax_input',
        help=f"Redmond, WA rate: ~1.05% (${default_property_tax:,})"
    )
    
    # Update session state when user changes the value
    st.session_state.property_tax_annual = property_tax_annual
    
    insurance_annual = st.sidebar.number_input("Insurance (Annual $)", min_value=0, max_value=20000, value=2800, step=100)
    hoa_monthly = st.sidebar.number_input("HOA (Monthly $)", min_value=0, max_value=2000, value=75, step=25)
    
    # Create scenario and calculate metrics
    scenario = MortgageScenario(
        home_price=home_price,
        down_payment_amount=down_payment_amount,
        interest_rate=interest_rate,
        loan_term_years=loan_term_years,
        monthly_income=monthly_income,
        monthly_debts=monthly_debts,
        property_tax_annual=property_tax_annual,
        insurance_annual=insurance_annual,
        hoa_monthly=hoa_monthly
    )
    
    metrics = MortgageModel.calculate_affordability_metrics(scenario)
    
    # Main content area
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.subheader("💰 Loan Details")
        st.metric("Loan Amount", f"${metrics['loan_amount']:,.0f}")
        st.metric("Down Payment", f"${metrics['down_payment']:,.0f}")
        st.caption(f"({metrics['down_payment_percent']:.1f}% of home price)")
        st.metric("Monthly P&I", f"${metrics['monthly_pi']:,.0f}")
        
    with col2:
        st.subheader("📋 Monthly Costs")
        st.metric("Property Tax", f"${metrics['monthly_property_tax']:,.0f}")
        st.metric("Insurance", f"${metrics['monthly_insurance']:,.0f}")
        st.metric("HOA", f"${hoa_monthly:,.0f}")
        st.metric("**Total Monthly**", f"**${metrics['total_monthly_payment']:,.0f}**")
        
    with col3:
        st.subheader("📊 Affordability")
        
        # Color code the ratios
        front_color = "green" if metrics['front_end_ratio'] <= 28 else "red"
        back_color = "green" if metrics['back_end_ratio'] <= 36 else "red"
        
        st.metric("Front-End Ratio", f"{metrics['front_end_ratio']:.1f}%")
        st.markdown(f"<p style='color: {front_color}'>{'✅ Good' if metrics['front_end_ratio'] <= 28 else '❌ High'} (≤28% recommended)</p>", unsafe_allow_html=True)
        
        st.metric("Back-End Ratio", f"{metrics['back_end_ratio']:.1f}%")
        st.markdown(f"<p style='color: {back_color}'>{'✅ Good' if metrics['back_end_ratio'] <= 36 else '❌ High'} (≤36% recommended)</p>", unsafe_allow_html=True)
        
        if metrics['affordable']:
            st.success("🎉 This home appears affordable!")
        else:
            st.error("⚠️ This home may be beyond your budget")
    
    st.markdown("---")
    
    # Charts section
    st.subheader("📈 Visual Analysis")
    
    # First row - Payment breakdown and Price comparison
    col1, col2 = st.columns(2)
    
    with col1:
        # Payment breakdown chart
        payment_chart = create_payment_breakdown_chart(metrics)
        st.plotly_chart(payment_chart, use_container_width=True)
    
    with col2:
        # Generate comparison data
        comparison_data = MortgageModel.generate_comparison_data(
            scenario,
            price_range=(home_price * 0.7, home_price * 1.3),
            rate_range=(max(1, interest_rate - 2), interest_rate + 2),
            down_payment_range=(home_price * 0.05, home_price * 0.80)  # 5% to 80% of home price
        )
        
        # Create individual price comparison chart
        price_data = [d for d in comparison_data if d['scenario_type'] == 'Price Variation']
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(
            x=[d['variable_value'] for d in price_data],
            y=[d['monthly_payment'] for d in price_data],
            mode='lines+markers',
            name='Monthly Payment',
            line=dict(color='blue')
        ))
        fig_price.update_layout(
            title="Monthly Payment vs Home Price",
            xaxis_title="Home Price ($)",
            yaxis_title="Monthly Payment ($)",
            height=400
        )
        st.plotly_chart(fig_price, use_container_width=True)
    
    # Second row - Interest rate and Down payment comparisons
    col3, col4 = st.columns(2)
    
    with col3:
        # Interest rate comparison chart
        rate_data = [d for d in comparison_data if d['scenario_type'] == 'Rate Variation']
        fig_rate = go.Figure()
        fig_rate.add_trace(go.Scatter(
            x=[d['variable_value'] for d in rate_data],
            y=[d['monthly_payment'] for d in rate_data],
            mode='lines+markers',
            name='Monthly Payment',
            line=dict(color='red')
        ))
        fig_rate.update_layout(
            title="Monthly Payment vs Interest Rate",
            xaxis_title="Interest Rate (%)",
            yaxis_title="Monthly Payment ($)",
            height=400
        )
        st.plotly_chart(fig_rate, use_container_width=True)
    
    with col4:
        # Down payment comparison chart
        dp_data = [d for d in comparison_data if d['scenario_type'] == 'Down Payment Variation']
        fig_dp = go.Figure()
        fig_dp.add_trace(go.Scatter(
            x=[(d['variable_value'] / home_price * 100) for d in dp_data],  # Convert to percentage
            y=[d['monthly_payment'] for d in dp_data],
            mode='lines+markers',
            name='Monthly Payment',
            line=dict(color='green')
        ))
        fig_dp.update_layout(
            title="Monthly Payment vs Down Payment %",
            xaxis_title="Down Payment (%)",
            yaxis_title="Monthly Payment ($)",
            height=400
        )
        st.plotly_chart(fig_dp, use_container_width=True)
    
    # Third row - DTI Ratio comparison
    st.subheader("📊 DTI Ratio Analysis")
    col5, col6 = st.columns(2)
    
    with col5:
        # DTI ratio comparison chart
        fig_dti = go.Figure()
        colors = {'Price Variation': 'blue', 'Rate Variation': 'red', 'Down Payment Variation': 'green'}
        for scenario_type in ['Price Variation', 'Rate Variation', 'Down Payment Variation']:
            scenario_data = [d for d in comparison_data if d['scenario_type'] == scenario_type]
            if scenario_type == 'Down Payment Variation':
                x_values = [(d['variable_value'] / home_price * 100) for d in scenario_data]
                x_title = "Down Payment (%)"
            elif scenario_type == 'Price Variation':
                x_values = [d['variable_value'] for d in scenario_data]
                x_title = "Home Price ($)"
            else:
                x_values = [d['variable_value'] for d in scenario_data]
                x_title = "Interest Rate (%)"
            
            fig_dti.add_trace(go.Scatter(
                x=x_values,
                y=[d['front_end_ratio'] for d in scenario_data],
                mode='lines+markers',
                name=f'{scenario_type}',
                line=dict(color=colors[scenario_type])
            ))
        
        fig_dti.add_hline(y=28, line_dash="dash", line_color="orange", 
                         annotation_text="28% DTI Threshold")
        fig_dti.update_layout(
            title="DTI Ratio Comparison",
            xaxis_title="Variable Value",
            yaxis_title="Front-End DTI Ratio (%)",
            height=400
        )
        st.plotly_chart(fig_dti, use_container_width=True)
    
    with col6:
        # Affordability summary chart
        affordability_counts = {}
        for scenario_type in ['Price Variation', 'Rate Variation', 'Down Payment Variation']:
            scenario_data = [d for d in comparison_data if d['scenario_type'] == scenario_type]
            affordable_count = sum(1 for d in scenario_data if d['affordable'])
            total_count = len(scenario_data)
            affordability_counts[scenario_type] = (affordable_count / total_count) * 100
        
        fig_afford = go.Figure(data=[
            go.Bar(
                x=list(affordability_counts.keys()),
                y=list(affordability_counts.values()),
                marker_color=['blue', 'red', 'green'],
                text=[f"{v:.0f}%" for v in affordability_counts.values()],
                textposition='auto'
            )
        ])
        fig_afford.update_layout(
            title="Affordability Rate by Scenario",
            xaxis_title="Scenario Type",
            yaxis_title="Affordable Scenarios (%)",
            height=400,
            yaxis=dict(range=[0, 100])
        )
        st.plotly_chart(fig_afford, use_container_width=True)
    
    # Additional insights
    st.markdown("---")
    st.subheader("💡 Key Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**Total Interest:** ${metrics['total_interest']:,.0f}")
        st.caption(f"Over {loan_term_years} years")
    
    with col2:
        st.info(f"**Total Payments:** ${metrics['total_payments']:,.0f}")
        st.caption(f"Principal + Interest only")
    
    with col3:
        savings_needed_months = metrics['down_payment'] / (monthly_income * 0.2)  # Assuming 20% savings rate
        st.info(f"**Save for:** {savings_needed_months:.1f} months")
        st.caption("At 20% income savings rate")
    
    # Footer
    st.markdown("---")
    st.markdown("*Calculator uses standard mortgage formulas. Front-end ratio ≤28% and back-end ratio ≤36% are considered affordable.*")


if __name__ == "__main__":
    main()
