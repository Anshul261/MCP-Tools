import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from datetime import datetime
import json
import os
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from openai import AzureOpenAI
from pathlib import Path
import streamlit as st
import base64


@dataclass
class AnalysisResult:
    """Structure for storing analysis results"""
    data_profile: Dict[str, Any]
    insights: str
    charts: List[Dict[str, Any]]
    summary_stats: Dict[str, Any]
    recommendations: List[str]


class ExcelAnalysisAgent:
    """
    Intelligent Excel Analysis Agent that automatically explores data,
    generates insights, and creates HTML dashboards.
    """
    
    def __init__(self, azure_endpoint: str, api_key: str, api_version: str = "2024-02-15-preview", deployment_name: str = "gpt-4"):
        """Initialize the agent with Azure OpenAI credentials"""
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.deployment_name = deployment_name
        self.analysis_history = []
        
    def analyze_excel_file(self, file_path: str) -> AnalysisResult:
        """
        Main orchestration method that performs complete Excel analysis
        """
        print(f"🔍 Starting analysis of {file_path}")
        
        # Step 1: Load and profile the data
        df, sheet_info = self._load_excel_file(file_path)
        data_profile = self._profile_dataset(df)
        
        # Step 2: Generate insights using LLM
        insights = self._generate_insights(data_profile, df)
        
        # Step 3: Create visualizations
        charts = self._create_visualizations(df, insights)
        
        # Step 4: Generate summary statistics
        summary_stats = self._generate_summary_stats(df)
        
        # Step 5: Get recommendations
        recommendations = self._generate_recommendations(data_profile, insights)
        
        result = AnalysisResult(
            data_profile=data_profile,
            insights=insights,
            charts=charts,
            summary_stats=summary_stats,
            recommendations=recommendations
        )
        
        self.analysis_history.append(result)
        print("✅ Analysis complete!")
        return result
    
    def _load_excel_file(self, file_path: str) -> Tuple[pd.DataFrame, Dict]:
        """Load Excel file and handle multiple sheets"""
        try:
            # Read all sheets to understand file structure
            excel_file = pd.ExcelFile(file_path)
            sheet_info = {
                'sheet_names': excel_file.sheet_names,
                'total_sheets': len(excel_file.sheet_names)
            }
            
            # For prototype, use the first sheet or largest sheet
            if len(excel_file.sheet_names) == 1:
                df = pd.read_excel(file_path)
                sheet_info['selected_sheet'] = excel_file.sheet_names[0]
            else:
                # Find the sheet with most data
                sheet_sizes = {}
                for sheet in excel_file.sheet_names:
                    try:
                        temp_df = pd.read_excel(file_path, sheet_name=sheet)
                        sheet_sizes[sheet] = len(temp_df)
                    except:
                        sheet_sizes[sheet] = 0
                
                largest_sheet = max(sheet_sizes, key=sheet_sizes.get)
                df = pd.read_excel(file_path, sheet_name=largest_sheet)
                sheet_info['selected_sheet'] = largest_sheet
                sheet_info['sheet_sizes'] = sheet_sizes
            
            # Clean column names
            df.columns = df.columns.astype(str).str.strip()
            
            print(f"📊 Loaded data: {df.shape[0]} rows, {df.shape[1]} columns")
            return df, sheet_info
            
        except Exception as e:
            raise Exception(f"Error loading Excel file: {str(e)}")
    
    def _profile_dataset(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive data profile"""
        profile = {
            'basic_info': {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'column_names': list(df.columns)
            },
            'data_types': {},
            'missing_values': {},
            'numeric_summary': {},
            'categorical_summary': {},
            'date_columns': [],
            'potential_keys': []
        }
        
        # Analyze each column
        for col in df.columns:
            col_data = df[col]
            
            # Data type analysis
            profile['data_types'][col] = str(col_data.dtype)
            profile['missing_values'][col] = {
                'count': col_data.isnull().sum(),
                'percentage': (col_data.isnull().sum() / len(df)) * 100
            }
            
            # Numeric analysis
            if pd.api.types.is_numeric_dtype(col_data):
                profile['numeric_summary'][col] = {
                    'mean': col_data.mean(),
                    'median': col_data.median(),
                    'std': col_data.std(),
                    'min': col_data.min(),
                    'max': col_data.max(),
                    'unique_values': col_data.nunique()
                }
            
            # Categorical analysis
            elif pd.api.types.is_object_dtype(col_data):
                profile['categorical_summary'][col] = {
                    'unique_values': col_data.nunique(),
                    'most_frequent': col_data.mode().iloc[0] if not col_data.mode().empty else None,
                    'top_categories': col_data.value_counts().head(5).to_dict()
                }
                
                # Check if it might be a date
                if self._could_be_date(col_data):
                    profile['date_columns'].append(col)
            
            # Check for potential key columns
            if col_data.nunique() == len(df) and col_data.isnull().sum() == 0:
                profile['potential_keys'].append(col)
        
        return profile
    
    def _could_be_date(self, series: pd.Series) -> bool:
        """Check if a series might contain dates"""
        sample = series.dropna().head(10)
        date_count = 0
        
        for value in sample:
            try:
                pd.to_datetime(value)
                date_count += 1
            except:
                continue
        
        return date_count > len(sample) * 0.7  # 70% threshold
    
    def _generate_insights(self, data_profile: Dict, df: pd.DataFrame) -> str:
        """Use LLM to generate intelligent insights about the data"""
        
        # Create a summary for the LLM
        prompt = f"""
        Analyze this dataset and provide intelligent insights:

        Dataset Overview:
        - Rows: {data_profile['basic_info']['rows']}
        - Columns: {data_profile['basic_info']['columns']}
        - Column Names: {', '.join(data_profile['basic_info']['column_names'])}

        Data Quality:
        Missing Values: {json.dumps({k: v['percentage'] for k, v in data_profile['missing_values'].items() if v['percentage'] > 0}, indent=2)}

        Numeric Columns Summary:
        {json.dumps(data_profile['numeric_summary'], indent=2, default=str)}

        Categorical Columns:
        {json.dumps(data_profile['categorical_summary'], indent=2)}

        Date Columns Detected: {data_profile['date_columns']}
        Potential Key Columns: {data_profile['potential_keys']}

        Please provide:
        1. Key insights about the data structure and quality
        2. Notable patterns or anomalies you can identify
        3. What this dataset likely represents (business context)
        4. Data quality issues and recommendations
        5. Interesting relationships worth exploring

        Be specific and actionable in your analysis.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are an expert data analyst. Provide clear, actionable insights about datasets."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating insights: {str(e)}"
    
    def _create_visualizations(self, df: pd.DataFrame, insights: str) -> List[Dict]:
        """Create business-focused visualizations based on intelligent data analysis"""
        charts = []
        
        # Get column types
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        date_cols = []
        
        # Identify date columns more intelligently
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['date', 'time', 'created', 'completed', 'modified']):
                try:
                    pd.to_datetime(df[col].dropna().head(100))
                    date_cols.append(col)
                except:
                    pass
        
        # Remove ID columns from meaningful analysis (they're just identifiers)
        meaningful_numeric_cols = [col for col in numeric_cols if not any(
            id_word in col.lower() for id_word in ['id', 'number', 'ref', 'ticket']
        )]
        
        # Identify key business columns based on common patterns
        status_cols = [col for col in categorical_cols if any(
            word in col.lower() for word in ['status', 'state', 'condition']
        )]
        
        category_cols = [col for col in categorical_cols if any(
            word in col.lower() for word in ['category', 'type', 'class', 'group']
        )]
        
        priority_cols = [col for col in categorical_cols if any(
            word in col.lower() for word in ['priority', 'severity', 'urgency', 'level']
        )]
        
        team_cols = [col for col in categorical_cols if any(
            word in col.lower() for word in ['team', 'owner', 'assigned', 'responsible']
        )]
        
        location_cols = [col for col in categorical_cols if any(
            word in col.lower() for word in ['location', 'site', 'school', 'branch', 'office']
        )]
        
        breach_cols = [col for col in df.columns if any(
            word in col.lower() for word in ['breach', 'sla', 'overdue', 'delayed']
        )]
        
        # 1. STATUS ANALYSIS - Most critical for operational insights
        for status_col in status_cols[:2]:
            if df[status_col].nunique() > 1:
                status_counts = df[status_col].value_counts()
                fig = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title=f"Distribution of {status_col}",
                    template="plotly_white"
                )
                fig.update_traces(textinfo='label+percent+value')
                charts.append({
                    'type': 'pie',
                    'title': f"Distribution of {status_col}",
                    'figure': fig,
                    'html': fig.to_html(include_plotlyjs='cdn'),
                    'business_insight': f"Shows operational status distribution for {status_col}"
                })
        
        # 2. CATEGORY/SUBCATEGORY ANALYSIS - Deep dive into issue types
        for cat_col in category_cols:
            if df[cat_col].nunique() > 1 and df[cat_col].nunique() <= 30:
                top_categories = df[cat_col].value_counts().head(15)
                fig = px.bar(
                    y=top_categories.index,
                    x=top_categories.values,
                    orientation='h',
                    title=f"Top Issues by {cat_col}",
                    template="plotly_white",
                    color=top_categories.values,
                    color_continuous_scale="Blues"
                )
                fig.update_layout(
                    yaxis_title=cat_col,
                    xaxis_title="Number of Tickets",
                    showlegend=False
                )
                charts.append({
                    'type': 'bar',
                    'title': f"Top Issues by {cat_col}",
                    'figure': fig,
                    'html': fig.to_html(include_plotlyjs='cdn'),
                    'business_insight': f"Identifies most common issue types in {cat_col}"
                })
        
        # 3. SLA BREACH ANALYSIS - Critical for performance monitoring
        for breach_col in breach_cols:
            if df[breach_col].dtype == 'bool' or df[breach_col].nunique() == 2:
                breach_data = df[breach_col].value_counts()
                fig = px.bar(
                    x=breach_data.index,
                    y=breach_data.values,
                    title=f"SLA Breach Analysis - {breach_col}",
                    template="plotly_white",
                    color=breach_data.index,
                    color_discrete_map={True: "red", False: "green", "True": "red", "False": "green"}
                )
                fig.update_layout(
                    xaxis_title="Breach Status",
                    yaxis_title="Number of Tickets"
                )
                charts.append({
                    'type': 'breach_analysis',
                    'title': f"SLA Breach Analysis - {breach_col}",
                    'figure': fig,
                    'html': fig.to_html(include_plotlyjs='cdn'),
                    'business_insight': f"Critical SLA performance metric showing breach rates"
                })
        
        # 4. TEAM/OWNER PERFORMANCE ANALYSIS
        for team_col in team_cols:
            if df[team_col].nunique() > 1 and df[team_col].nunique() <= 20:
                # Remove rows with missing team data for this analysis
                team_data = df[df[team_col].notna()]
                if len(team_data) > 0:
                    team_counts = team_data[team_col].value_counts().head(10)
                    fig = px.bar(
                        x=team_counts.values,
                        y=team_counts.index,
                        orientation='h',
                        title=f"Workload Distribution by {team_col}",
                        template="plotly_white"
                    )
                    fig.update_layout(
                        xaxis_title="Number of Tickets",
                        yaxis_title=team_col
                    )
                    charts.append({
                        'type': 'workload',
                        'title': f"Workload Distribution by {team_col}",
                        'figure': fig,
                        'html': fig.to_html(include_plotlyjs='cdn'),
                        'business_insight': f"Shows workload distribution across {team_col}"
                    })
        
        # 5. CROSS-ANALYSIS: Breach by Category (if both exist)
        if breach_cols and category_cols:
            breach_col = breach_cols[0]
            cat_col = category_cols[0]
            
            # Create crosstab analysis
            cross_data = pd.crosstab(df[cat_col], df[breach_col])
            if cross_data.shape[1] == 2:  # Has both breach and non-breach data
                # Calculate breach rates by category
                if True in cross_data.columns or 'True' in cross_data.columns:
                    true_col = True if True in cross_data.columns else 'True'
                    false_col = False if False in cross_data.columns else 'False'
                    
                    breach_rates = (cross_data[true_col] / (cross_data[true_col] + cross_data[false_col]) * 100).sort_values(ascending=False)
                    
                    fig = px.bar(
                        x=breach_rates.values,
                        y=breach_rates.index,
                        orientation='h',
                        title=f"Breach Rate by {cat_col} (%)",
                        template="plotly_white",
                        color=breach_rates.values,
                        color_continuous_scale="Reds"
                    )
                    fig.update_layout(
                        xaxis_title="Breach Rate (%)",
                        yaxis_title=cat_col
                    )
                    charts.append({
                        'type': 'breach_by_category',
                        'title': f"Breach Rate by {cat_col}",
                        'figure': fig,
                        'html': fig.to_html(include_plotlyjs='cdn'),
                        'business_insight': f"Critical insight: which {cat_col} types have highest breach rates"
                    })
        
        # 6. TIME-BASED ANALYSIS (if date columns exist)
        if date_cols:
            primary_date_col = date_cols[0]
            try:
                df_dates = df.copy()
                df_dates[primary_date_col] = pd.to_datetime(df_dates[primary_date_col])
                df_dates = df_dates.dropna(subset=[primary_date_col])
                
                if len(df_dates) > 0:
                    # Monthly trend analysis
                    df_dates['Month'] = df_dates[primary_date_col].dt.to_period('M')
                    monthly_counts = df_dates['Month'].value_counts().sort_index()
                    
                    fig = px.line(
                        x=[str(m) for m in monthly_counts.index],
                        y=monthly_counts.values,
                        title=f"Ticket Volume Trend Over Time",
                        template="plotly_white"
                    )
                    fig.update_layout(
                        xaxis_title="Month",
                        yaxis_title="Number of Tickets"
                    )
                    charts.append({
                        'type': 'time_trend',
                        'title': 'Ticket Volume Trend Over Time',
                        'figure': fig,
                        'html': fig.to_html(include_plotlyjs='cdn'),
                        'business_insight': "Shows ticket volume trends to identify seasonal patterns or emerging issues"
                    })
                    
                    # ADVANCED TIME HEATMAPS - New sophisticated analysis
                    
                    # 1. Comprehensive Day of Week vs Hour of Day Heatmap (Main Feature)
                    df_dates['DayOfWeek'] = df_dates[primary_date_col].dt.day_name()
                    df_dates['Hour'] = df_dates[primary_date_col].dt.hour
                    
                    # Create comprehensive pivot table for detailed heatmap
                    day_hour_pivot = df_dates.groupby(['DayOfWeek', 'Hour']).size().unstack(fill_value=0)
                    
                    # Reorder days properly (Sunday first to match the example)
                    day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
                    day_hour_pivot = day_hour_pivot.reindex(day_order)
                    
                    # Ensure all 24 hours are represented
                    all_hours = list(range(24))
                    for hour in all_hours:
                        if hour not in day_hour_pivot.columns:
                            day_hour_pivot[hour] = 0
                    day_hour_pivot = day_hour_pivot.reindex(columns=sorted(day_hour_pivot.columns))
                    
                    # Add totals row and column
                    day_hour_pivot.loc['Total'] = day_hour_pivot.sum()
                    day_hour_pivot['Total'] = day_hour_pivot.sum(axis=1)
                    
                    # Create hour labels (12AM, 1AM, etc.)
                    hour_labels = []
                    for hour in sorted(day_hour_pivot.columns[:-1]):  # Exclude 'Total' column
                        if hour == 0:
                            hour_labels.append('12AM')
                        elif hour < 12:
                            hour_labels.append(f'{hour}AM')
                        elif hour == 12:
                            hour_labels.append('12PM')
                        else:
                            hour_labels.append(f'{hour-12}PM')
                    hour_labels.append('Total')
                    
                    # Create the detailed heatmap with custom color scale
                    # Define color scale based on ticket volume ranges
                    max_val = day_hour_pivot.iloc[:-1, :-1].max().max()  # Exclude totals from max calculation
                    
                    # Create custom colorscale
                    colorscale = [
                        [0.0, '#ffffff'],      # White for 0
                        [0.1, '#e8f5e8'],      # Very light green for 1-5
                        [0.2, '#c3e6c3'],      # Light green for 6-15
                        [0.4, '#ffeb99'],      # Light yellow for 16-25
                        [0.6, '#ffcc80'],      # Orange for 26-40
                        [0.8, '#ff8a80'],      # Light red for 41-60
                        [1.0, '#d32f2f']       # Dark red for 60+
                    ]
                    
                    fig = px.imshow(
                        day_hour_pivot.values,
                        x=hour_labels,
                        y=day_hour_pivot.index,
                        title="Ticket Creation Heatmap: Complete Day-Hour Analysis",
                        color_continuous_scale=colorscale,
                        template="plotly_white",
                        aspect="auto"
                    )
                    
                    # Add text annotations for all values
                    for i, day in enumerate(day_hour_pivot.index):
                        for j, hour in enumerate(day_hour_pivot.columns):
                            value = day_hour_pivot.iloc[i, j]
                            # Choose text color based on cell value for readability
                            if value > max_val * 0.6:
                                text_color = "white"
                            else:
                                text_color = "black"
                            
                            fig.add_annotation(
                                x=j, y=i,
                                text=str(value),
                                showarrow=False,
                                font=dict(color=text_color, size=11, family="Arial Bold")
                            )
                    
                    # Customize layout for better readability
                    fig.update_layout(
                        xaxis_title="Hour of Day",
                        yaxis_title="Day of Week",
                        coloraxis_colorbar=dict(
                            title="Number of Tickets",
                            titleside="right"
                        ),
                        font=dict(size=12),
                        height=400,
                        margin=dict(l=80, r=80, t=80, b=80)
                    )
                    
                    # Add grid lines for better separation
                    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                    
                    charts.append({
                        'type': 'comprehensive_day_hour_heatmap',
                        'title': 'Comprehensive Ticket Heatmap: Day vs Hour with Totals',
                        'figure': fig,
                        'html': fig.to_html(include_plotlyjs='cdn'),
                        'business_insight': "Complete operational view: Exact ticket counts by day and hour with totals. Critical for staffing optimization and identifying peak support periods."
                    })
                    
                    # 2. Create a detailed table version for better readability
                    # This creates an HTML table version of the heatmap
                    def create_detailed_table():
                        table_html = '<div class="overflow-x-auto"><table class="min-w-full border-collapse border border-gray-300">'
                        
                        # Header row
                        table_html += '<thead><tr class="bg-gray-100">'
                        table_html += '<th class="border border-gray-300 px-2 py-1 font-bold">Day</th>'
                        for hour_label in hour_labels:
                            table_html += f'<th class="border border-gray-300 px-2 py-1 font-bold text-xs">{hour_label}</th>'
                        table_html += '</tr></thead><tbody>'
                        
                        # Data rows
                        for day in day_hour_pivot.index:
                            table_html += '<tr>'
                            table_html += f'<td class="border border-gray-300 px-2 py-1 font-bold">{day}</td>'
                            
                            for hour in day_hour_pivot.columns:
                                value = day_hour_pivot.loc[day, hour]
                                
                                # Color coding based on value
                                if value == 0:
                                    bg_color = '#ffffff'
                                    text_color = '#666666'
                                elif value <= 5:
                                    bg_color = '#e8f5e8'
                                    text_color = '#000000'
                                elif value <= 15:
                                    bg_color = '#c3e6c3'
                                    text_color = '#000000'
                                elif value <= 25:
                                    bg_color = '#ffeb99'
                                    text_color = '#000000'
                                elif value <= 40:
                                    bg_color = '#ffcc80'
                                    text_color = '#000000'
                                elif value <= 60:
                                    bg_color = '#ff8a80'
                                    text_color = '#000000'
                                else:
                                    bg_color = '#d32f2f'
                                    text_color = '#ffffff'
                                
                                table_html += f'<td class="border border-gray-300 px-2 py-1 text-center text-sm font-semibold" style="background-color: {bg_color}; color: {text_color};">{value}</td>'
                            
                            table_html += '</tr>'
                        
                        table_html += '</tbody></table></div>'
                        return table_html
                    
                    # Add the table as a separate "chart"
                    charts.append({
                        'type': 'detailed_table',
                        'title': 'Detailed Ticket Count Table by Day and Hour',
                        'figure': None,  # No plotly figure for this one
                        'html': create_detailed_table(),
                        'business_insight': "Exact ticket counts in tabular format for precise operational planning. Use this for staff scheduling and capacity planning."
                    })
                    
                    # 3. Peak Hours Summary Chart
                    hourly_totals = day_hour_pivot.loc['Total'][:-1]  # Exclude the 'Total' column
                    peak_hours = hourly_totals.nlargest(5)
                    
                    fig = px.bar(
                        x=[hour_labels[i] for i in peak_hours.index],
                        y=peak_hours.values,
                        title="Top 5 Peak Hours for Ticket Creation",
                        template="plotly_white",
                        color=peak_hours.values,
                        color_continuous_scale="Reds"
                    )
                    fig.update_layout(
                        xaxis_title="Hour of Day",
                        yaxis_title="Total Tickets",
                        showlegend=False
                    )
                    
                    # Add value annotations
                    for i, (hour_idx, value) in enumerate(peak_hours.items()):
                        fig.add_annotation(
                            x=i, y=value,
                            text=str(value),
                            showarrow=False,
                            yshift=10,
                            font=dict(size=12, color="black")
                        )
                    
                    charts.append({
                        'type': 'peak_hours_summary',
                        'title': 'Top 5 Peak Hours for Ticket Creation',
                        'figure': fig,
                        'html': fig.to_html(include_plotlyjs='cdn'),
                        'business_insight': f"Critical staffing insight: Peak hours are {', '.join([hour_labels[i] for i in peak_hours.index])} with {peak_hours.iloc[0]} tickets at the busiest time."
                    })
                    
                    # 2. Monthly vs Day of Week Heatmap
                    df_dates['MonthName'] = df_dates[primary_date_col].dt.strftime('%Y-%m')
                    month_day_pivot = df_dates.groupby(['MonthName', 'DayOfWeek']).size().unstack(fill_value=0)
                    month_day_pivot = month_day_pivot.reindex(columns=day_order)
                    
                    if len(month_day_pivot) > 1:  # Only create if we have multiple months
                        fig = px.imshow(
                            month_day_pivot.values,
                            x=month_day_pivot.columns,
                            y=month_day_pivot.index,
                            title="Monthly Ticket Patterns: Month vs Day of Week",
                            color_continuous_scale="Viridis",
                            template="plotly_white",
                            aspect="auto"
                        )
                        fig.update_layout(
                            xaxis_title="Day of Week",
                            yaxis_title="Month",
                            coloraxis_colorbar=dict(title="Number of Tickets")
                        )
                        
                        charts.append({
                            'type': 'month_day_heatmap',
                            'title': 'Monthly Patterns: Month vs Day of Week',
                            'figure': fig,
                            'html': fig.to_html(include_plotlyjs='cdn'),
                            'business_insight': "Shows seasonal patterns and identifies which days are consistently busiest across months"
                        })
                    
                    # 3. Hourly Distribution Throughout the Day
                    hourly_dist = df_dates.groupby('Hour').size()
                    
                    fig = px.bar(
                        x=hourly_dist.index,
                        y=hourly_dist.values,
                        title="Ticket Creation by Hour of Day",
                        template="plotly_white",
                        color=hourly_dist.values,
                        color_continuous_scale="Blues"
                    )
                    fig.update_layout(
                        xaxis_title="Hour of Day (24-hour format)",
                        yaxis_title="Number of Tickets",
                        xaxis=dict(tickmode='linear', tick0=0, dtick=1)
                    )
                    
                    # Add business hour annotations
                    fig.add_vrect(x0=9, x1=17, fillcolor="green", opacity=0.1, 
                                 annotation_text="Business Hours", annotation_position="top left")
                    
                    charts.append({
                        'type': 'hourly_distribution',
                        'title': 'Ticket Creation by Hour of Day',
                        'figure': fig,
                        'html': fig.to_html(include_plotlyjs='cdn'),
                        'business_insight': "Shows peak hours for ticket creation - essential for support team scheduling"
                    })
                    
                    # 4. Weekly Pattern Analysis
                    weekly_dist = df_dates.groupby('DayOfWeek').size().reindex(day_order)
                    
                    # Color code weekdays vs weekends
                    colors = ['#1f77b4' if day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] 
                             else '#ff7f0e' for day in weekly_dist.index]
                    
                    fig = px.bar(
                        x=weekly_dist.index,
                        y=weekly_dist.values,
                        title="Ticket Volume by Day of Week",
                        template="plotly_white",
                        color=weekly_dist.values,
                        color_continuous_scale="Blues"
                    )
                    fig.update_layout(
                        xaxis_title="Day of Week",
                        yaxis_title="Number of Tickets"
                    )
                    
                    # Add weekend vs weekday annotation
                    weekend_avg = weekly_dist[['Saturday', 'Sunday']].mean()
                    weekday_avg = weekly_dist[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']].mean()
                    
                    fig.add_annotation(
                        x=6, y=weekly_dist.max(),
                        text=f"Weekend Avg: {weekend_avg:.1f}<br>Weekday Avg: {weekday_avg:.1f}",
                        showarrow=True,
                        arrowhead=2,
                        bgcolor="rgba(255,255,255,0.8)"
                    )
                    
                    charts.append({
                        'type': 'weekly_pattern',
                        'title': 'Ticket Volume by Day of Week',
                        'figure': fig,
                        'html': fig.to_html(include_plotlyjs='cdn'),
                        'business_insight': "Compares weekday vs weekend ticket volumes - impacts staffing and SLA planning"
                    })
                    
                    # 5. Peak Hours Analysis with Business Context
                    # Calculate peak hours and create summary
                    peak_hours = hourly_dist.nlargest(3)
                    off_peak_hours = hourly_dist.nsmallest(3)
                    
                    # Create a comprehensive time analysis summary chart
                    fig = go.Figure()
                    
                    # Add hourly data as line
                    fig.add_trace(go.Scatter(
                        x=hourly_dist.index,
                        y=hourly_dist.values,
                        mode='lines+markers',
                        name='Hourly Distribution',
                        line=dict(color='blue', width=3),
                        marker=dict(size=8)
                    ))
                    
                    # Highlight peak hours
                    for hour in peak_hours.index:
                        fig.add_vline(x=hour, line_dash="dash", line_color="red", 
                                     annotation_text=f"Peak: {hour}:00")
                    
                    # Add business hours shading
                    fig.add_vrect(x0=9, x1=17, fillcolor="green", opacity=0.1, 
                                 annotation_text="Business Hours")
                    
                    fig.update_layout(
                        title="Peak Hours Analysis with Business Context",
                        xaxis_title="Hour of Day",
                        yaxis_title="Number of Tickets",
                        template="plotly_white",
                        showlegend=False
                    )
                    
                    charts.append({
                        'type': 'peak_hours_analysis',
                        'title': 'Peak Hours Analysis with Business Context',
                        'figure': fig,
                        'html': fig.to_html(include_plotlyjs='cdn'),
                        'business_insight': f"Peak ticket hours: {', '.join([f'{h}:00' for h in peak_hours.index])} - optimize staffing for these times"
                    })
                    
            except Exception as e:
                print(f"Error in time analysis: {e}")
                pass  # Skip if date parsing fails
        
        # 7. LOCATION-BASED ANALYSIS
        for loc_col in location_cols:
            if df[loc_col].nunique() > 1 and df[loc_col].nunique() <= 25:
                location_data = df[df[loc_col].notna()]
                if len(location_data) > 0:
                    loc_counts = location_data[loc_col].value_counts().head(15)
                    fig = px.bar(
                        x=loc_counts.values,
                        y=loc_counts.index,
                        orientation='h',
                        title=f"Ticket Volume by {loc_col}",
                        template="plotly_white"
                    )
                    fig.update_layout(
                        xaxis_title="Number of Tickets",
                        yaxis_title=loc_col
                    )
                    charts.append({
                        'type': 'location_analysis',
                        'title': f"Ticket Volume by {loc_col}",
                        'figure': fig,
                        'html': fig.to_html(include_plotlyjs='cdn'),
                        'business_insight': f"Identifies locations with highest support needs"
                    })
        
        # 8. DATA QUALITY VISUALIZATION - Enhanced missing values analysis
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
            missing_percentages = (missing_data / len(df) * 100).round(1)
            
            fig = px.bar(
                x=missing_percentages.values,
                y=missing_percentages.index,
                orientation='h',
                title="Data Quality: Missing Values Analysis",
                template="plotly_white",
                color=missing_percentages.values,
                color_continuous_scale="Reds"
            )
            fig.update_layout(
                xaxis_title="Missing Percentage (%)",
                yaxis_title="Column"
            )
            
            # Add annotations for critical missing data
            for i, (col, pct) in enumerate(missing_percentages.items()):
                if pct > 50:
                    fig.add_annotation(
                        x=pct,
                        y=i,
                        text=f"{pct}%",
                        showarrow=True,
                        arrowhead=2
                    )
            
            charts.append({
                'type': 'data_quality',
                'title': 'Data Quality: Missing Values Analysis',
                'figure': fig,
                'html': fig.to_html(include_plotlyjs='cdn'),
                'business_insight': "Critical data quality issues that may impact analysis reliability"
            })
        
        # 9. RESOLUTION TIME ANALYSIS (if we have created and completed dates)
        created_cols = [col for col in date_cols if 'created' in col.lower()]
        completed_cols = [col for col in date_cols if any(word in col.lower() for word in ['completed', 'closed', 'resolved'])]
        
        if created_cols and completed_cols:
            try:
                df_resolution = df.copy()
                created_col = created_cols[0]
                completed_col = completed_cols[0]
                
                df_resolution[created_col] = pd.to_datetime(df_resolution[created_col])
                df_resolution[completed_col] = pd.to_datetime(df_resolution[completed_col])
                
                # Calculate resolution time in hours
                resolution_data = df_resolution.dropna(subset=[created_col, completed_col])
                if len(resolution_data) > 0:
                    resolution_data['Resolution_Hours'] = (
                        resolution_data[completed_col] - resolution_data[created_col]
                    ).dt.total_seconds() / 3600
                    
                    # Remove negative and extreme values
                    resolution_data = resolution_data[
                        (resolution_data['Resolution_Hours'] > 0) & 
                        (resolution_data['Resolution_Hours'] < 24*30)  # Less than 30 days
                    ]
                    
                    if len(resolution_data) > 0:
                        fig = px.histogram(
                            resolution_data,
                            x='Resolution_Hours',
                            title="Resolution Time Distribution",
                            template="plotly_white",
                            nbins=30
                        )
                        fig.update_layout(
                            xaxis_title="Resolution Time (Hours)",
                            yaxis_title="Number of Tickets"
                        )
                        charts.append({
                            'type': 'resolution_time',
                            'title': 'Resolution Time Distribution',
                            'figure': fig,
                            'html': fig.to_html(include_plotlyjs='cdn'),
                            'business_insight': "Shows how quickly tickets are resolved - key performance metric"
                        })
            except:
                pass  # Skip if date calculation fails
        
        return charts
    
    def _generate_summary_stats(self, df: pd.DataFrame) -> Dict:
        """Generate summary statistics"""
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
            'categorical_columns': len(df.select_dtypes(include=['object']).columns),
            'missing_values_total': df.isnull().sum().sum(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
            'duplicate_rows': df.duplicated().sum()
        }
    
    def _generate_recommendations(self, data_profile: Dict, insights: str) -> List[str]:
        """Generate actionable recommendations using LLM"""
        
        prompt = f"""
        Based on this data analysis, provide 5-7 specific, actionable recommendations:

        Data Profile Summary:
        - Total rows: {data_profile['basic_info']['rows']}
        - Total columns: {data_profile['basic_info']['columns']}
        - Missing values found in: {[k for k, v in data_profile['missing_values'].items() if v['percentage'] > 0]}
        - Numeric columns: {len(data_profile['numeric_summary'])}
        - Categorical columns: {len(data_profile['categorical_summary'])}

        Generated Insights:
        {insights}

        Provide specific recommendations for:
        1. Data quality improvements
        2. Further analysis opportunities
        3. Visualization suggestions
        4. Business insights to explore
        5. Data preparation steps

        Format as a simple list of actionable items.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a data strategy consultant. Provide specific, actionable recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            
            recommendations_text = response.choices[0].message.content
            # Parse into list
            recommendations = [line.strip() for line in recommendations_text.split('\n') if line.strip() and not line.strip().startswith('#')]
            return recommendations[:7]  # Limit to 7 recommendations
            
        except Exception as e:
            return [f"Error generating recommendations: {str(e)}"]
    
    def generate_html_dashboard(self, analysis_result: AnalysisResult, filename: str = "dashboard.html") -> str:
        """Generate a complete HTML dashboard"""
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate charts HTML
        charts_html = ""
        for i, chart in enumerate(analysis_result.charts):
            # Add business insight if available
            insight_html = ""
            if 'business_insight' in chart:
                insight_html = f"""
                <div class="bg-blue-50 border-l-4 border-blue-400 p-3 mb-4">
                    <p class="text-sm text-blue-700"><strong>💡 Business Insight:</strong> {chart['business_insight']}</p>
                </div>
                """
            
            # Handle both plotly charts and HTML tables
            content_html = ""
            if chart['figure'] is not None:
                # Regular plotly chart
                content_html = f'<div id="chart-{i}" class="chart-container">{chart["html"]}</div>'
            else:
                # HTML table (like detailed heatmap table)
                content_html = f'<div class="table-container">{chart["html"]}</div>'
            
            charts_html += f"""
            <div class="bg-white rounded-lg shadow-md p-6 mb-6">
                <h3 class="text-xl font-semibold mb-4">{chart['title']}</h3>
                {insight_html}
                {content_html}
            </div>
            """
        
        # Generate summary table
        summary_html = ""
        for key, value in analysis_result.summary_stats.items():
            summary_html += f"""
            <tr class="border-b border-gray-200">
                <td class="py-2 px-4 font-medium text-gray-900">{key.replace('_', ' ').title()}</td>
                <td class="py-2 px-4 text-gray-700">{value}</td>
            </tr>
            """
        
        # Generate recommendations
        recommendations_html = ""
        for rec in analysis_result.recommendations:
            recommendations_html += f"<li class='mb-2 text-gray-700'>{rec}</li>"
        
        dashboard_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Excel Data Analysis Dashboard</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                .prose {{ max-width: none; }}
                .chart-container {{ min-height: 400px; }}
            </style>
        </head>
        <body class="bg-gray-50">
            <div class="container mx-auto px-4 py-8 max-w-7xl">
                <!-- Header -->
                <header class="bg-white rounded-lg shadow-md p-6 mb-8">
                    <div class="flex justify-between items-center">
                        <div>
                            <h1 class="text-3xl font-bold text-gray-800">📊 Excel Data Analysis Report</h1>
                            <p class="text-gray-600 mt-2">Automated analysis generated on {current_time}</p>
                        </div>
                        <div class="text-right">
                            <div class="text-sm text-gray-500">Dataset Summary</div>
                            <div class="text-lg font-semibold text-blue-600">
                                {analysis_result.summary_stats['total_rows']} rows × {analysis_result.summary_stats['total_columns']} columns
                            </div>
                        </div>
                    </div>
                </header>

                <!-- Key Insights -->
                <section class="bg-white rounded-lg shadow-md p-6 mb-8">
                    <h2 class="text-2xl font-semibold mb-4 text-gray-800">🔍 Key Insights</h2>
                    <div class="prose max-w-none text-gray-700 whitespace-pre-line">
{analysis_result.insights}
                    </div>
                </section>

                <!-- Quick Stats -->
                <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <div class="bg-white rounded-lg shadow-md p-6">
                        <div class="text-2xl font-bold text-blue-600">{analysis_result.summary_stats['total_rows']:,}</div>
                        <div class="text-sm text-gray-600">Total Rows</div>
                    </div>
                    <div class="bg-white rounded-lg shadow-md p-6">
                        <div class="text-2xl font-bold text-green-600">{analysis_result.summary_stats['total_columns']}</div>
                        <div class="text-sm text-gray-600">Columns</div>
                    </div>
                    <div class="bg-white rounded-lg shadow-md p-6">
                        <div class="text-2xl font-bold text-purple-600">{analysis_result.summary_stats['missing_values_total']:,}</div>
                        <div class="text-sm text-gray-600">Missing Values</div>
                    </div>
                    <div class="bg-white rounded-lg shadow-md p-6">
                        <div class="text-2xl font-bold text-orange-600">{analysis_result.summary_stats['memory_usage_mb']:.1f} MB</div>
                        <div class="text-sm text-gray-600">Memory Usage</div>
                    </div>
                </section>

                <!-- Visualizations -->
                <section class="mb-8">
                    <h2 class="text-2xl font-semibold mb-6 text-gray-800">📈 Business Intelligence Dashboard</h2>
                    <div class="grid grid-cols-1 gap-6">
                        {charts_html}
                    </div>
                </section>

                <!-- Recommendations -->
                <section class="bg-white rounded-lg shadow-md p-6 mb-8">
                    <h2 class="text-2xl font-semibold mb-4 text-gray-800">💡 Recommendations</h2>
                    <ul class="list-disc list-inside space-y-2">
                        {recommendations_html}
                    </ul>
                </section>

                <!-- Data Summary Table -->
                <section class="bg-white rounded-lg shadow-md p-6">
                    <h2 class="text-2xl font-semibold mb-4 text-gray-800">📋 Dataset Summary</h2>
                    <div class="overflow-x-auto">
                        <table class="min-w-full">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="py-3 px-4 text-left text-sm font-medium text-gray-900">Metric</th>
                                    <th class="py-3 px-4 text-left text-sm font-medium text-gray-900">Value</th>
                                </tr>
                            </thead>
                            <tbody>
                                {summary_html}
                            </tbody>
                        </table>
                    </div>
                </section>

                <!-- Footer -->
                <footer class="text-center py-8 text-gray-500 text-sm">
                    <p>Generated by Excel Analysis Agent • Powered by Azure OpenAI</p>
                </footer>
            </div>
        </body>
        </html>
        """
        
        # Save the dashboard
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        
        print(f"📄 Dashboard saved as {filename}")
        return dashboard_html


def create_streamlit_interface():
    """Create Streamlit interface for testing the agent"""
    
    st.set_page_config(
        page_title="Excel Analysis Agent",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Excel Analysis Agent")
    st.markdown("Upload an Excel file and get automated analysis with Azure OpenAI powered insights!")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Azure OpenAI Configuration")
        azure_endpoint = st.text_input(
            "Azure OpenAI Endpoint", 
            placeholder="https://your-resource.openai.azure.com/",
            help="Your Azure OpenAI endpoint URL"
        )
        api_key = st.text_input(
            "Azure OpenAI API Key", 
            type="password", 
            help="Enter your Azure OpenAI API key"
        )
        api_version = st.selectbox(
            "API Version", 
            ["2024-02-15-preview", "2023-12-01-preview", "2023-05-15"], 
            index=0,
            help="Azure OpenAI API version"
        )
        deployment_name = st.text_input(
            "Deployment Name", 
            value="gpt-4",
            help="Name of your deployed model (e.g., gpt-4, gpt-35-turbo)"
        )
        
        if st.button("ℹ️ About"):
            st.info("""
            This agent automatically:
            - Analyzes Excel file structure
            - Generates data insights using Azure OpenAI
            - Creates visualizations
            - Builds HTML dashboard
            - Provides recommendations
            
            **Azure Setup Required:**
            1. Azure OpenAI resource
            2. Deployed GPT-4 model
            3. API key and endpoint
            """)
    
    if not azure_endpoint or not api_key:
        st.warning("⚠️ Please enter your Azure OpenAI endpoint and API key in the sidebar to proceed.")
        st.info("""
        **Getting Started with Azure OpenAI:**
        1. Create an Azure OpenAI resource in Azure Portal
        2. Deploy a GPT-4 model
        3. Get your endpoint URL and API key from the resource
        4. Enter the details in the sidebar
        """)
        return
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload an Excel file (.xlsx or .xls format)"
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        temp_file_path = f"temp_{uploaded_file.name}"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            # Initialize agent
            agent = ExcelAnalysisAgent(azure_endpoint, api_key, api_version, deployment_name)
            
            # Show file info
            st.success(f"✅ File uploaded: {uploaded_file.name} ({uploaded_file.size:,} bytes)")
            
            if st.button("🚀 Analyze File", type="primary"):
                with st.spinner("🔍 Analyzing your Excel file with Azure OpenAI... This may take a few minutes."):
                    
                    # Perform analysis
                    result = agent.analyze_excel_file(temp_file_path)
                    
                    # Display results
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader("🔍 AI-Generated Insights")
                        st.write(result.insights)
                        
                        st.subheader("📈 Business Intelligence Visualizations")
                        for i, chart in enumerate(result.charts):
                            # Create expandable section for each chart
                            with st.expander(f"📊 {chart['title']}", expanded=True):
                                # Show business insight if available
                                if 'business_insight' in chart:
                                    st.info(f"💡 **Business Insight**: {chart['business_insight']}")
                                
                                # Display the chart or table
                                if chart['figure'] is not None:
                                    # Display plotly chart
                                    st.plotly_chart(
                                        chart['figure'], 
                                        use_container_width=True
                                    )
                                else:
                                    # Display HTML table (for detailed table format)
                                    st.markdown(chart['html'], unsafe_allow_html=True)
                    
                    with col2:
                        st.subheader("📊 Quick Stats")
                        for key, value in result.summary_stats.items():
                            st.metric(key.replace('_', ' ').title(), value)
                        
                        st.subheader("💡 Recommendations")
                        for i, rec in enumerate(result.recommendations, 1):
                            st.write(f"{i}. {rec}")
                    
                    # Generate and offer dashboard download
                    dashboard_html = agent.generate_html_dashboard(result, "analysis_dashboard.html")
                    
                    st.subheader("📄 Download Dashboard")
                    st.download_button(
                        label="Download HTML Dashboard",
                        data=dashboard_html,
                        file_name=f"analysis_{uploaded_file.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html"
                    )
                    
                    st.success("🎉 Analysis complete! Check out your insights above and download the dashboard.")
        
        except Exception as e:
            st.error(f"❌ Error analyzing file: {str(e)}")
            if "unauthorized" in str(e).lower() or "authentication" in str(e).lower():
                st.error("🔑 Authentication error. Please check your Azure OpenAI credentials.")
            elif "not found" in str(e).lower():
                st.error("🚫 Model not found. Please check your deployment name.")
        
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)


if __name__ == "__main__":
    # Run the Streamlit interface
    create_streamlit_interface()