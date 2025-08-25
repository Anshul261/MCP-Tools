# Data Analysis Agent - AI-Powered Data Visualization System

A sophisticated data analysis system that combines **AGNO AI** multi-agent capabilities with **DuckDB** for high-performance analytics and **HTML/CSS/JavaScript** for professional dashboard generation.

## 🚀 Overview

This system automatically ingests Excel/CSV files, performs intelligent data type inference, and creates interactive HTML dashboards using AI agents. It replaces traditional Python plotting libraries with modern web-based visualizations for better formatting and user experience.

## 📁 File Structure

### Core Analysis Files

#### `html-dashboard-analysis.py` ⭐ **MAIN FILE**
**Purpose**: Primary entry point for the enhanced dashboard generation system.

**Key Features**:
- **Data Processing**: Automatic Excel/CSV ingestion with smart type inference
- **AGNO AI Integration**: Single powerful agent with DuckDB and Python tools
- **HTML Dashboard Generation**: Creates professional web-based dashboards
- **Rich Terminal UI**: Colored output with progress tracking
- **Interactive Session**: Continuous analysis workflow

**How it works**:
1. Loads and preprocesses data files (Excel/CSV → CSV for DuckDB)
2. Infers data types (dates, numbers, strings) automatically
3. Creates DuckDB table for fast SQL queries
4. Initializes AI agent with dashboard creation capabilities
5. Provides interactive command interface for analysis requests

**Usage**:
```bash
python html-dashboard-analysis.py
```

---

#### `improved-viz-analysis.py` 📊 **MULTI-AGENT VERSION**
**Purpose**: Advanced multi-agent system for collaborative data analysis.

**Architecture**:
- **Data Analyst Agent**: Specialized in SQL queries and statistical analysis
- **Visualization Specialist**: Focused on chart creation and design
- **Team Coordination**: AGNO AI team-based collaboration with reasoning tools

**Features**:
- Agent memory and session summaries
- Specialized agent roles for better task distribution
- Rich terminal interface with data type display
- Enhanced error handling for pandas operations

**Use Case**: When you need specialized analysis with multiple AI agents working together.

---

#### `viz-analysis.py` 🔧 **ORIGINAL VERSION**
**Purpose**: Initial implementation using Plotly for visualization.

**Issues Addressed**:
- SQL date parsing problems with Excel data
- Poor data type inference leading to query failures
- Single agent doing all tasks
- Plotly formatting and subplot compatibility issues

**Status**: Superseded by newer implementations but kept for reference.

---

### Template System

#### `dashboard_templates.py` 🎨 **TEMPLATE ENGINE**
**Purpose**: Solves f-string syntax conflicts when generating HTML/JavaScript code.

**Core Problem Solved**:
- Python f-strings conflict with JavaScript `{}` syntax
- Complex nested templates causing parser errors
- Inconsistent formatting in generated dashboards

**Template Functions**:

```python
get_html_template()           # Base HTML structure with CSS Grid
get_stat_card_template()      # KPI display cards
get_chart_card_template()     # Chart container cards  
get_insight_template()        # Data insights display
get_chart_js_template()       # Chart.js initialization code
```

**Safe Generation Method**:
1. Use placeholder strings like `{{STATS_CONTENT}}`
2. Build content sections separately
3. Combine using `.replace()` instead of f-strings
4. Avoids all syntax conflicts

---

### Data Processing Components

#### `DataProcessor` Class (in main files)
**Purpose**: Handles Excel/CSV file preprocessing and type inference.

**Key Methods**:
```python
clean_and_infer_types(file_path)  # Main processing function
```

**Processing Steps**:
1. **File Loading**: Supports .xlsx, .xls, .csv formats
2. **Data Cleaning**: Removes empty rows, handles missing values
3. **Type Inference**: 
   - Date/time columns → `datetime64`
   - Numeric columns → `int64`/`float64` 
   - Text columns → `object`
4. **CSV Export**: Saves processed data for DuckDB ingestion

**Error Handling**: Uses try/catch instead of deprecated pandas `errors='ignore'`

---

## 🛠 Technology Stack

### **AGNO AI Framework**
- **Multi-Agent Systems**: Level 4 reasoning and collaboration
- **Memory Management**: Session summaries and user memories
- **Tool Integration**: DuckDB, Python tools, reasoning capabilities

### **DuckDB Integration**
- **High-Performance Analytics**: In-memory OLAP database
- **SQL Query Engine**: Fast aggregations and complex queries
- **CSV Ingestion**: Direct file-to-table loading

### **Web Dashboard Technology**
- **Chart.js**: Interactive charts (line, bar, pie, doughnut)
- **CSS Grid**: Responsive dashboard layouts
- **Modern Web Standards**: HTML5, CSS3, ES6 JavaScript

### **Rich Terminal Interface**
- **Colored Output**: Status indicators and progress tracking
- **Data Tables**: Clean display of column types and statistics
- **Progress Bars**: Visual feedback during processing

---

## 🎯 Dashboard Types Generated

### **1. KPI Dashboards**
- Summary statistics cards
- Key performance indicators
- Trend indicators with color coding

### **2. Time-Series Analysis**
- Monthly/daily ticket volume trends
- Seasonal pattern identification
- Growth/decline visualization

### **3. Category Analysis**
- Ticket type distribution
- Category and subcategory breakdowns
- SLA performance by category

### **4. Comprehensive Dashboards**
- Multiple chart types in single view
- Coordinated color schemes
- Responsive grid layouts

---

## 🔧 Configuration

### **Environment Variables** (`.env` file)
```env
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment
AZURE_OPENAI_API_KEY=your-api-key
OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_ENDPOINT=your-endpoint
```

### **Data Requirements**
- **Supported Formats**: Excel (.xlsx, .xls), CSV (.csv)
- **Expected Structure**: Tabular data with headers
- **Key Columns**: Date/time columns for trend analysis
- **Size Limits**: Optimized for datasets up to 100K rows

---

## 📊 Example Workflows

### **Basic Analysis**
```bash
python html-dashboard-analysis.py
> create dashboard
```

### **Specific Analysis**
```bash
> monthly trends              # Time-series analysis
> category analysis          # Category breakdowns  
> sla performance           # SLA compliance dashboard
> ticket type distribution  # Simple distribution analysis
```

### **Complex Analysis**
```bash
> create a dashboard with all of these details: 
  Ticket Type Distribution, Monthly Volume, 
  Average Resolution Time, SLA Performance
```

---

## 🎨 Output Examples

### **Generated Files** (in `output/` folder)
- `ticket_type_distribution_dashboard.html` - Simple analysis
- `dashboard.html` - Comprehensive analysis
- `monthly_trends_dashboard.html` - Time-series focus
- `category_analysis_dashboard.html` - Category breakdown

### **Dashboard Features**
- **Responsive Design**: Works on desktop, tablet, mobile
- **Interactive Charts**: Hover effects, legends, zoom
- **Professional Styling**: Clean typography, color schemes
- **Fast Loading**: Optimized HTML/CSS/JS

---

## 🔍 Troubleshooting

### **Common Issues & Solutions**

#### **F-String Syntax Errors**
- **Problem**: Complex HTML/JS conflicts with Python f-strings
- **Solution**: Use `dashboard_templates.py` with `.replace()` method

#### **Data Type Inference Issues**
- **Problem**: Dates parsed as strings, causing SQL errors
- **Solution**: Enhanced type inference in `DataProcessor.clean_and_infer_types()`

#### **Agent Communication Problems**
- **Problem**: Multi-agent coordination failures
- **Solution**: Use single agent (`html-dashboard-analysis.py`) for complex tasks

#### **Memory Warnings**
- **Problem**: "MemoryDb not provided" warnings
- **Solution**: Normal operation, doesn't affect functionality

---

## 🚀 Future Enhancements

### **Planned Features**
- **REST API Integration**: Direct API data ingestion
- **Real-time Dashboards**: WebSocket-based live updates
- **Custom Chart Types**: D3.js integration for advanced visualizations
- **Export Options**: PDF/PNG export capabilities
- **Dashboard Templates**: Pre-built industry-specific layouts

### **Performance Optimizations**
- **Streaming Data Processing**: Handle larger datasets
- **Caching Layer**: Redis integration for repeated queries
- **Parallel Processing**: Multi-threaded data ingestion

---

## 📝 Development Notes

### **Code Quality**
- **Type Safety**: Proper error handling for data conversions
- **Clean Architecture**: Separation of concerns between agents
- **Template System**: Reusable components for dashboard generation

### **Testing Considerations**
- **Data Validation**: Input sanitization and validation
- **Cross-browser Compatibility**: Dashboard testing across browsers
- **Performance Benchmarks**: Query optimization and rendering speed

---

## 🤝 Contributing

When extending this system:

1. **Follow Template Pattern**: Use `dashboard_templates.py` for HTML generation
2. **Agent Specialization**: Create focused agents for specific tasks
3. **Error Handling**: Implement robust error handling for data operations
4. **Documentation**: Update README for new features

---

**Built with ❤️ using AGNO AI, DuckDB, and modern web technologies.**