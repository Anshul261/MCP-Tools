#!/usr/bin/env python3
"""
Direct test of the visualization agent to ensure it creates files
"""
import os
import time
from pathlib import Path

# Import the agent setup from our main file
from agent import viz_specialist, duckdb_tools

def test_viz_agent_directly():
    """Test the visualization agent directly"""
    print("🧪 Testing Visualization Agent Directly")
    print("=" * 50)
    
    # Check if we have the data loaded
    try:
        result = duckdb_tools.execute_sql("SELECT COUNT(*) as count FROM data")
        print(f"✅ Data table accessible: {result}")
    except Exception as e:
        print(f"❌ Data table error: {e}")
        return False
    
    # Record files before
    output_dir = Path("output")
    files_before = set()
    if output_dir.exists():
        files_before = {f.name for f in output_dir.glob("*") if f.is_file()}
    
    print(f"📁 Files in output/ before: {len(files_before)}")
    
    # Test the agent with a direct request
    print("\n🤖 Asking agent to create a pie chart...")
    start_time = time.time()
    
    try:
        response = viz_specialist.run(
            "Create a pie chart of ticket categories from the data table. Query the Category column, count the tickets for each category, and save it as a PNG file in the output folder with the filename 'test_category_pie_chart.png'. Use matplotlib.",
            stream=False
        )
        
        print(f"Agent response: {response.content[:200]}...")
        
        # Wait a moment for file creation
        time.sleep(2)
        
        # Check for new files
        files_after = set()
        if output_dir.exists():
            files_after = {f.name for f in output_dir.glob("*") if f.is_file()}
        
        new_files = files_after - files_before
        print(f"📁 New files created: {new_files}")
        
        if len(new_files) > 0:
            print("✅ SUCCESS: Agent created files!")
            for f in new_files:
                file_path = output_dir / f
                print(f"   - {f} ({file_path.stat().st_size} bytes)")
            return True
        else:
            print("❌ FAILURE: No new files created")
            print("The agent is talking about creating files but not actually doing it")
            return False
            
    except Exception as e:
        print(f"❌ Agent execution error: {e}")
        return False

if __name__ == "__main__":
    success = test_viz_agent_directly()
    
    if success:
        print("\n🎉 Agent is working correctly!")
        print("The issue might be in the team coordination or API detection")
    else:
        print("\n❌ Agent needs fixing - not creating actual files")
        print("Need to investigate why Python tools aren't being used")