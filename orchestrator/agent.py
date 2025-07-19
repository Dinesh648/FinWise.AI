from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext

#Define tools here for now


def add_financial_data(financial_data: str, tool_context:ToolContext) -> dict:
    """Add a new financial data point to the user's financial data list.
    
    Args:
        data_point: The financial data to be added.
        tool_context: Context for accessing and updating the session state.
        
    Returns:
        A confirmation message
    """
    print(f"--- Tool: add_financial_data called with financial_data '{financial_data}' ---")

    # Get the current financial data from the state
    current_financial_data_points = tool_context.state.get("financial_data_points", [])

    print(f"Current financial data points: {current_financial_data_points}")
    # Add the new financial data to the list
    current_financial_data_points.append(financial_data)

    # Update state with the new list of financial data
    tool_context.state["financial_data_points"] = current_financial_data_points

    return {
        "action" : "add_financial_data",
        "financial_data": financial_data,
        "message":f"Added financial data: {financial_data}",
    }

def view_financial_data(tool_context:ToolContext):
    """
    View all the current financial data of the user.
    Args:
        tool_context: Context for accessing the session state.
    Returns:
        A list of financial data entries.
    """

    print("--- Tool: view_financial_data called ---")

    # Get the financial data from the state
    financial_data_points = tool_context.state.get("financial_data_points", [])

    return {
        "action": "view_financial_data",
        "financial_data": financial_data_points,
        "count": len(financial_data_points)
    }

def update_financial_data(index: int, updated_text: str, tool_context: ToolContext):
    """
    Update an existing financial data entry.
    Args:
        index: The 1-based index of the financial data to update.
        updated_text: The new text to replace the existing financial data.
        tool_context: Context for accessing and updating the session state.

    Returns:
        A confirmation message with the updated financial data.
    """

    print(f"--- Tool: update_financial_data called with index {index} and updated_text '{updated_text}' ---")

    # Get the current financial data from the state
    financial_data_points = tool_context.state.get("financial_data_points", [])

    if not financial_data_points or index < 1 or index > len(financial_data_points):
        return {
            "action": "update_financial_data",
            "status": "error",
            "message": f"Could not find financial data at the specified index: {index}. Currently there are {len(financial_data)} entries."
        }
    # Update the specified financial data entry
    old_financial_data = financial_data_points[index - 1]
    financial_data_points[index - 1] = updated_text

    # Update state with the modified list
    tool_context.state["financial_data_points"] = financial_data_points

    return {
        "action": "update_financial_data",
        "index": index,
        "old_financial_data": old_financial_data,
        "new_financial_data": updated_text,
        "message": f"Updated financial data at index {index} from '{old_financial_data}' to '{updated_text}'"
    }


def delete_financial_data(index: int, tool_context: ToolContext):
    """
    Delete a financial data entry by its index.
    Args:
        index: The 1-based index of the financial data to delete.
        tool_context: Context for accessing and updating the session state.
        
    Returns:
        A confirmation message indicating the deletion status.
    """
    print(f"--- Tool: delete_financial_data called with index {index} ---")

    # Get the current financial data from the state
    financial_data_points = tool_context.state.get("financial_data_points", [])

    # Check if the index is valid
    if not financial_data_points or index < 1 or index > len(financial_data_points):
        return {
            "action": "delete_financial_data",
            "status": "error",
            "message": f"Could not find financial data at the specified index: {index}. Currently there are {len(financial_data_points)} entries."
        }
    
    # Delete the specified financial data entry
    deleted_financial_data = financial_data_points.pop(index - 1)

    # Update state with the modified list
    tool_context.state["financial_data_points"] = financial_data_points

    return {
        "action": "delete_financial_data",
        "index": index,
        "deleted_financial_data": deleted_financial_data,
        "message": f"Deleted financial data at index {index}: '{deleted_financial_data}'"
    }

def update_user_name(new_name: str, tool_context: ToolContext):
    """
    Update the user's name in the session state.
    
    Args:
        new_name: The new name to set for the user.
        tool_context: Context for accessing and updating the session state.
        
    Returns:
        A confirmation message indicating the update status.
    """
    
    print(f"--- Tool: update_user_name called with new_name '{new_name}' ---")

    # Update the user's name in the state
    tool_context.state["user_name"] = new_name

    return {
        "action": "update_user_name",
        "new_user_name": new_name,
        "message": f"User name updated to '{new_name}'"
    }


orchestrator_agent = Agent(
    name="orchestrator",
    model="gemini-2.0-flash",
    description="Orchestrator agent for managing tasks and coordinating between different agents.",
    instruction=""" 
    You must first greed the user when starting a conversation with "Hello, I am your FinWise Agent. What would like know about your finances today?"
    The user's information is stored in state:
    - User's name: {user_name}
    - Financial Data: {financial_data}

    You can help users manage their financial data by using the following capabilities:
    1. Add financial data
    2. View financial data
    3. Update financial data
    4. Delete financial data
    5. Update user name

    Always address the user by their name and you need to be smart in finding the right financial data:

    **FINANCIAL DATA MANAGEMENT**
    1. When the user asks to update or delete a financial data but doesn't provide an index:
       - If they mention the content of the financial data (e.g., "delete my financial data of tesla stocks"):, 
         look through the financial datas to find a match
       - If you find an exact or close match, use that index
       - Never clarify which financial data the user is referring to, just use the first match
       - If no match is found, list all financial datas and ask the user to specify
    
    2. When the user mentions a number or position:
       - Use that as the index (e.g., "delete financial data 2" means index=2)
       - Remember that indexing starts at 1 for the user
    
    3. For relative positions:
       - Handle "first", "last", "second", etc. appropriately
       - "First financial data" = index 1
       - "Last financial data" = the highest index
       - "Second financial data" = index 2, and so on
    
    4. For viewing:
       - Always use the view_financial datas tool when the user asks to see their financial datas
       - Format the response in a numbered list for clarity
       - If there are no financial datas, suggest adding some
    
    5. For addition:
       - Extract the actual financial data text from the user's request
       - Remove phrases like "add a financial data to"
       - Focus on the task itself (e.g., "add a financial data TATA to my portfolio" → add_financial data("TATA"))
    
    6. For updates:
       - Identify both which financial data to update and what the new text should be
       - For example, "change my second financial data to FinWise" → update_financial data(2, "FinWise")
    
    7. For deletions:
       - Confirm deletion when complete and mention which financial data was removed
       - For example, "I've deleted your financial data 'TATA' from your list."
    
    Remember to explain that you can remember their information across conversations.

    IMPORTANT:
    - use your best judgement to determine which financial data the user is referring to. 
    - You don't have to be 100 % correct, but try to be as close as possible.
    - Never ask the user to clarify which financial data they are referring to.    

    """,
    tools=[
        add_financial_data,
        view_financial_data,
        update_financial_data,
        delete_financial_data,
        update_user_name,
    ],
)