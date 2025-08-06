# A2A Agent Templates

This directory contains three Python template files for creating A2A (Agent-to-Agent) servers using the Google ADK agent framework. These templates serve as starter kits for developers who are new to agent creation and need a minimal working setup to build from.

## Template Overview

### 1. `simple_agent.py` - Simple Conversational Agent
A basic conversational agent without any tools. Perfect for:
- Simple chat bots
- Basic conversation agents
- Learning the Google ADK framework
- Testing agent communication

**Key Features:**
- No external tools required
- Basic conversation processing
- Easy to customize and extend
- Minimal boilerplate code

### 2. `agent_with_tool.py` - Agent with Single Tool
A conversational agent that integrates one external tool. Ideal for:
- Calculator agents
- Search agents
- Data processing agents
- Single-purpose specialized agents

**Key Features:**
- One tool integration
- Tool input/output handling
- Error handling for tool execution
- Clear separation of concerns

### 3. `agent_with_tools.py` - Agent with Multiple Tools
A more advanced agent template showcasing multiple tools. Great for:
- Multi-functional agents
- Complex workflow agents
- Tool coordination and routing
- Advanced agent architectures

**Key Features:**
- Multiple tool integration
- Tool selection and routing logic
- Coordinated tool execution
- Scalable architecture

## Getting Started

### Prerequisites

1. **Install Dependencies:**
   ```bash
   pip install a2a google-adk litellm
   ```

2. **Set up Environment:**
   - Configure your model API keys (OpenAI, etc.)
   - Set up any required environment variables

### Using the Templates

1. **Choose Your Template:**
   - Start with `simple_agent.py` if you're new to agents
   - Use `agent_with_tool.py` for single-purpose agents
   - Use `agent_with_tools.py` for complex multi-tool agents

2. **Customize the Template:**
   - Fill in all `TODO:` sections
   - Update agent names and descriptions
   - Implement your specific logic
   - Configure your tools

3. **Test Your Agent:**
   - Run the agent locally
   - Test with sample queries
   - Debug and refine

## Template Structure

Each template follows the same structure:

```python
# 1. Imports and Dependencies
# 2. Agent Class Definition
# 3. Tool Functions (if applicable)
# 4. Agent Initialization
# 5. Invoke Method
# 6. A2A SDK Executor
# 7. Skill and Agent Card Definitions
```

## TODO Sections Guide

### Common TODOs Across All Templates

1. **Model Configuration:**
   ```python
   self.model_name = "gpt-4"  # TODO: Change to your preferred model
   ```

2. **Agent Identity:**
   ```python
   self.agent_name = "your_agent_name"  # TODO: Change to your agent name
   self.agent_description = "Your agent description"  # TODO: Update description
   ```

3. **App Configuration:**
   ```python
   app_name='your_app_name',  # TODO: Change to your app name
   user_id='your_user_id'     # TODO: Change to your user ID
   ```

4. **Skill Definition:**
   ```python
   skill = AgentSkill(
       id="your_skill_id",  # TODO: Change to your skill ID
       name="Your Skill Name",  # TODO: Change to your skill name
       description="Your skill description",  # TODO: Update description
       tags=["your", "tags"],  # TODO: Update tags
       examples=["Your examples"]  # TODO: Update examples
   )
   ```

### Template-Specific TODOs

#### Simple Agent (`simple_agent.py`)
- **Conversation Logic:** Implement your conversation handling in `process_conversation()`
- **Response Structure:** Define how your agent responds to different inputs

#### Agent with Tool (`agent_with_tool.py`)
- **Tool Implementation:** Define your tool logic in `my_tool()`
- **Tool Integration:** Connect your tool to the agent in `_initialize_agent()`

#### Agent with Tools (`agent_with_tools.py`)
- **Multiple Tools:** Implement each tool function (`tool_1()`, `tool_2()`, etc.)
- **Tool Selection:** Define routing logic in `tool_selector()`
- **Tool Registration:** Add all tools to the tools list in `_initialize_agent()`

## Example Customizations

### Simple Agent Example
```python
def process_conversation(self, query: str) -> str:
    # Custom conversation logic
    if "hello" in query.lower():
        return "Hello! How can I help you today?"
    elif "weather" in query.lower():
        return "I can't check the weather yet, but I'm here to chat!"
    else:
        return f"I understand you said: {query}. How can I assist you?"
```

### Single Tool Example
```python
def my_tool(self, input_data: str) -> str:
    # Calculator tool example
    try:
        result = eval(input_data)  # Simple calculator
        return f"Result: {result}"
    except:
        return "Error: Invalid calculation"
```

### Multiple Tools Example
```python
def tool_1(self, input_data: str) -> str:
    # Calculator tool
    return f"Calculated: {eval(input_data)}"

def tool_2(self, input_data: str) -> str:
    # Search tool
    return f"Searching for: {input_data}"

def tool_selector(self, query: str) -> str:
    if "calculate" in query.lower():
        return "Use tool_1 for calculations"
    elif "search" in query.lower():
        return "Use tool_2 for search"
    return "I have multiple tools available. What would you like to do?"
```

## Best Practices

1. **Error Handling:** Always wrap tool logic in try-catch blocks
2. **Logging:** Use the provided logger for debugging
3. **Documentation:** Update docstrings and comments
4. **Testing:** Test each tool individually before integration
5. **Security:** Validate inputs and sanitize outputs
6. **Performance:** Consider async operations for external API calls

## Troubleshooting

### Common Issues

1. **Import Errors:**
   - Ensure all dependencies are installed
   - Check Python path and virtual environment

2. **Model Configuration:**
   - Verify API keys are set correctly
   - Check model name compatibility

3. **Tool Integration:**
   - Ensure tool functions return strings
   - Check tool registration in agent initialization

4. **A2A SDK Issues:**
   - Verify executor class inheritance
   - Check event queue handling

### Debug Tips

1. **Enable Logging:**
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Test Individual Components:**
   - Test tools separately
   - Verify agent initialization
   - Check A2A SDK integration

3. **Use Print Statements:**
   - Add print statements for debugging
   - Remove before production

## Next Steps

After customizing your template:

1. **Create a Server:** Set up an A2A server using your agent
2. **Add Configuration:** Create config files for different environments
3. **Implement Testing:** Add unit tests for your agent and tools
4. **Deploy:** Deploy your agent to production
5. **Monitor:** Add monitoring and logging for production use

## Support

For issues and questions:
- Check the Google ADK documentation
- Review A2A SDK examples
- Test with minimal examples first
- Use the provided logging for debugging

## License

These templates are provided as-is for educational and development purposes. Customize them according to your specific needs and requirements. 