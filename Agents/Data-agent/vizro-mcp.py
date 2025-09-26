# generates python code to read an excel file and create visualizations using vizro-mcp and Azure OpenAI but does not run the code
import os
import asyncio
import pandas as pd
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.tools.mcp import MCPTools

load_dotenv()

def setup_azure_openai_model():
    """
    Set up the Azure OpenAI model using environment variables.
    This handles the Azure OpenAI configuration separately.
    """
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") 
    api_version = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if not all([api_key, endpoint, deployment_name]):
        raise ValueError("Missing required Azure OpenAI environment variables")
    
    model = AzureOpenAI(
        id=deployment_name,
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint,
        azure_deployment=deployment_name,
    )
    
    return model

def read_excel_file(file_path):
    """
    Read an Excel file and prepare it for visualization.
    This handles the file reading and basic data preparation.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        print(f"Reading Excel file: {file_path}")
        df = pd.read_excel(file_path)
        
        # Get basic information about the dataset
        info = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        print(f"Data loaded successfully: {info['shape'][0]} rows, {info['shape'][1]} columns")
        print(f"Columns: {', '.join(info['columns'])}")
        
        return df, info
    
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None, None

def save_data_for_vizro(df, output_path="data_for_vizro.csv"):
    """
    Save the DataFrame as CSV for Vizro to use.
    Vizro typically works better with CSV files.
    """
    try:
        df.to_csv(output_path, index=False)
        print(f"Data saved as CSV: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error saving data: {e}")
        return None

async def test_with_excel_file(excel_file_path, user_request="Create visualizations from this data"):
    """
    Test functionality with an Excel file input.
    This combines file reading with the agent workflow.
    """
    print("Setting up agent with Excel data, Vizro MCP and Azure OpenAI...")
    
    try:
        # Step 1: Read the Excel file
        df, data_info = read_excel_file(excel_file_path)
        if df is None:
            print("Failed to read Excel file. Stopping.")
            return
        
        # Step 2: Save data in a format Vizro can use
        csv_path = save_data_for_vizro(df)
        if csv_path is None:
            print("Failed to save data for Vizro. Stopping.")
            return
        
        # Step 3: Set up the model
        model = setup_azure_openai_model()
        print("Azure OpenAI model created successfully!")
        
        # Step 4: Connect to MCP server
        print("Connecting to Vizro MCP server...")
        
        async with MCPTools(command="uvx vizro-mcp") as mcp_tools:
            print("MCP server connection established!")
            
            # Step 5: Create agent with enhanced description
            agent = Agent(
                model=model,
                tools=[mcp_tools],
                markdown=True,
                description=f"""You are a data visualization expert using Vizro to create dashboards and charts.
                
The user has provided an Excel file with the following structure:
- Shape: {data_info['shape'][0]} rows, {data_info['shape'][1]} columns  
- Columns: {', '.join(data_info['columns'])}
- Data saved as: {csv_path}

Please use this data to create appropriate visualizations based on the user's request."""
            )
            
            print("Agent created successfully!")
            print("Processing Excel data and creating visualizations...")
            
            # Step 6: Create enhanced prompt
            enhanced_request = f"""
I have uploaded an Excel file that has been converted to CSV format at '{csv_path}'.

Data structure:
- {data_info['shape'][0]} rows and {data_info['shape'][1]} columns
- Columns: {', '.join(data_info['columns'])}

User request: {user_request}

Please load this data and create appropriate visualizations using Vizro. Show me what insights can be derived from this dataset.
"""
            
            response = await agent.arun(enhanced_request)
            
            print("Response:")
            print(response.content)
        
        print("MCP connection closed properly.")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        print("Please check your file path and try again.")

def check_environment():
    """
    Check if all required environment variables are set.
    This validates the setup before running the main test.
    """
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    
    print("All required environment variables are set.")
    return True

def check_dependencies():
    """
    Check if required dependencies are available.
    """
    print("Checking dependencies...")
    
    try:
        import subprocess
        result = subprocess.run(["uvx", "--version"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"uvx is available: {result.stdout.strip()}")
            
            # Also check for pandas
            try:
                import pandas as pd
                print(f"pandas is available: {pd.__version__}")
                return True
            except ImportError:
                print("pandas is not installed. Please install it: pip install pandas openpyxl")
                return False
        else:
            print("uvx is not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"uvx not found: {e}")
        print("Please install uv package manager:")
        print("curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False

def main():
    """
    Main function to run the test with Excel file support.
    This orchestrates the entire process including file handling.
    """
    print("Vizro MCP + AGNO + Azure OpenAI Test with Excel Support")
    print("=" * 60)
    
    if not check_environment():
        print("\nPlease set the required environment variables in your .env file.")
        return
    
    if not check_dependencies():
        print("\nPlease install the required dependencies.")
        return
    
    # Get Excel file path from user
    excel_file = "//home//anshul//Projects//AI-Search-MCP//Agents/Data-agent//realistic_ticket_data.xlsx"
    
    if not excel_file:
        print("No file path provided. Exiting.")
        return
    
    # Optional: Get custom request from user
    custom_request = input("Enter your visualization request (or press Enter for default): ").strip()
    if not custom_request:
        custom_request = "Analyze this data and create meaningful visualizations that show key insights and patterns"
    
    try:
        asyncio.run(test_with_excel_file(excel_file, custom_request))
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    main()