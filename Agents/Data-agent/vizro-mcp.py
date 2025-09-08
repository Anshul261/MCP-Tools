# Requirements
# vizro==0.1.44
import os
import asyncio
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

async def test_basic_functionality():
    """
    Test basic functionality without file uploads.
    This tests the simplest case first using async context manager.
    """
    print("Setting up agent with Vizro MCP and Azure OpenAI...")
    
    try:
        model = setup_azure_openai_model()
        
        print("Azure OpenAI model created successfully!")
        print("Connecting to Vizro MCP server...")
        
        async with MCPTools(command="uvx vizro-mcp") as mcp_tools:
            print("MCP server connection established!")
            
            agent = Agent(
                model=model,
                tools=[mcp_tools],
                markdown=True,
                description="You are a data visualization expert using Vizro to create dashboards and charts."
            )
            
            print("Agent created successfully!")
            print("Testing basic chart creation...")
            
            response = await agent.arun(
                "List the available datasets and create a simple visualization."
            )
            
            print("Response:")
            print(response.content)
        
        print("MCP connection closed properly.")
        
    except FileNotFoundError as e:
        print(f"Error: uvx command not found - {e}")
        print("Please ensure 'uv' is installed and 'uvx' is in your PATH")
        print("Install with: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("Then restart your terminal or run: source ~/.bashrc")
        
    except asyncio.TimeoutError as e:
        print(f"Timeout error: {e}")
        print("The MCP server took too long to respond. This could be due to:")
        print("- Slow server initialization")
        print("- Network connectivity issues") 
        print("- Heavy server load")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        print("Please check your environment variables and dependencies.")

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
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✓ uvx is available: {result.stdout.strip()}")
            return True
        else:
            print("✗ uvx is not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"✗ uvx not found: {e}")
        print("Please install uv package manager:")
        print("curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False

def main():
    """
    Main function to run the test.
    This orchestrates the entire test process.
    """
    print("Vizro MCP + AGNO + Azure OpenAI Test")
    print("=" * 40)
    
    if not check_environment():
        print("\nPlease set the required environment variables in your .env file.")
        return
    
    if not check_dependencies():
        print("\nPlease install the required dependencies.")
        return
    
    try:
        asyncio.run(test_basic_functionality())
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    main()
