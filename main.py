import asyncio

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from orchestrator.agent import orchestrator_agent

from utils import call_agent_async

load_dotenv()

db_url = "sqlite:///./finwise.db"
session_service = DatabaseSessionService(db_url=db_url)


initial_state = {
    "user_name": "Balivada Dinesh",
    "financial_data":[],
}


async def main_async():
    
    APP_NAME = "FinWise"
    USER_ID = "finaidinesh"

    #check for existing sessions in the database for this user
    existing_sessions = session_service.list_sessions(
        user_id=USER_ID, 
        app_name=APP_NAME
    )

    if existing_sessions and len(existing_sessions) > 0:
        SESSION_ID = existing_sessions[0].id
    else:
        # create a new session if no existing sessions found
        new_session = session_service.create_session(
            user_id=USER_ID,
            app_name=APP_NAME,
            initial_state=initial_state
        )
        SESSION_ID = new_session.id
        print(f"Created new session with ID: {SESSION_ID}")

    #Create a runner with the orchestrator agent and session service
    runner = Runner(
        agent=orchestrator_agent,
        session_service=session_service,
        app_name=APP_NAME,
    )
    
    # ===== PART 5: Interactive Conversation Loop =====
    print("\nWelcome to FinWise Agent Chat!")
    print("Your financial data will be remembered across conversations.")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Ending conversation. Goodbye!")
            break

        # Run the agent with the user input
        await call_agent_async(runner, USER_ID, SESSION_ID, user_input)


if __name__ == "__main__":
    asyncio.run(main_async())
