"""
Multi-Agent Interactive Session
Custom implementation for async MCP tool support
"""
import asyncio
from multi_agent_system import MultiAgentSystem


async def interactive_session():
    """Run interactive session with proper async support"""
    print("\n🎯 Multi-Agent Interactive Session")
    print("Available commands:")
    print("  - Ask any question (routed through Coordinator)")
    print("  - 'doc: <question>' - Direct to Document Agent")
    print("  - 'web: <question>' - Direct to Web Agent")
    print("  - 'status' - Show system status")
    print("  - 'quit', 'exit', 'q' - End session")
    print("-" * 50)
    
    # Initialize system
    print("🚀 Initializing Multi-Agent System...")
    system = MultiAgentSystem()
    
    try:
        success = await system.initialize_agents()
        if not success:
            print("❌ Failed to initialize system for interactive session")
            return
        
        print("\n✅ Multi-Agent System ready!")
        print("You can now ask questions or use direct agent commands.")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if user_input.lower() == 'status':
                    system._print_system_status()
                    continue
                
                # Check for direct agent commands
                if user_input.lower().startswith('doc:'):
                    query = user_input[4:].strip()
                    if query:
                        print("\n📚 Document Agent:")
                        try:
                            response = await system.document_agent.aprocess_query(query)
                            print(response)
                        except Exception as e:
                            print(f"Error: {e}")
                    continue
                
                if user_input.lower().startswith('web:'):
                    query = user_input[4:].strip()
                    if query:
                        print("\n🌐 Web Agent:")
                        try:
                            response = await system.web_agent.aprocess_query(query)
                            print(response)
                        except Exception as e:
                            print(f"Error: {e}")
                    continue
                
                # Default: route through coordinator
                print("\n🎯 Coordinator:")
                try:
                    result = await system.process_query(user_input)
                    
                    if "error" in result:
                        print(f"❌ Error: {result['error']}")
                    else:
                        # Show only the final coordinated response
                        if 'synthesis' in result and result['synthesis']:
                            print(result['synthesis'])
                        else:
                            # Fallback: show the most relevant response
                            responses = result.get('responses', {})
                            if 'document' in responses and responses['document']:
                                print(responses['document'])
                            elif 'web' in responses and responses['web']:
                                print(responses['web'])
                            else:
                                print("No response generated")
                
                except Exception as e:
                    print(f"❌ Error: {e}")
                    import traceback
                    traceback.print_exc()
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Session error: {e}")
    
    finally:
        print("\n🛑 Shutting down Multi-Agent System...")
        await system.shutdown()
        print("✅ Multi-Agent System shutdown complete")


if __name__ == "__main__":
    asyncio.run(interactive_session())