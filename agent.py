import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv


load_dotenv()




from tools import (
   search_professors,
   get_professor_details,
   get_professor_reviews,
   find_professors_by_course,
   get_top_professors_by_department,
   find_easy_professors,
   find_professors_by_teaching_style,
   compare_professors,
   list_departments,
)




def create_agent_executor():
   """Create and return a LangChain agent with all tools."""
   # Initialize OpenAI LLM
   llm = ChatOpenAI(
       model="gpt-4o-mini",
       temperature=0,
   )
  
   # Collect all tools
   tools = [
       search_professors,
       get_professor_details,
       get_professor_reviews,
       find_professors_by_course,
       get_top_professors_by_department,
       find_easy_professors,
       find_professors_by_teaching_style,
       compare_professors,
       list_departments,
   ]
  
   # System prompt for the agent
   system_prompt = """You are Compass AI, a helpful assistant that helps UC Davis students make informed decisions about professor selection during course planning.
      
You can help students:
- Search for professors by name
- Find professors by course code
- Get detailed information about professors including ratings and reviews
- Find top-rated professors by department
- Find professors with specific teaching styles
- Compare multiple professors
- Find professors with easier workloads


Be friendly, helpful, and provide clear recommendations based on the available data. If you need to use tools to answer questions, do so. Always be honest about what information you have access to."""
  
   # Create the agent using create_agent
   # create_agent signature: create_agent(model, tools, system_prompt=None)
   agent = create_agent(llm, tools, system_prompt=system_prompt)
  
   return agent




def main():
   """Main CLI loop for the agent."""
   # Check for OpenAI API key
   if not os.getenv("OPENAI_API_KEY"):
       print("Error: OPENAI_API_KEY environment variable is not set.")
       print("Please set it with: export OPENAI_API_KEY='your-api-key'")
       return
  
   # Create the agent
   print("Initializing Compass AI agent...")
   agent = create_agent_executor()
   print("Compass AI is ready! Type 'quit' to exit.\n")
  
   # Chat loop
   while True:
       try:
           # Get user input
           user_input = input("You: ").strip()
          
           # Check for quit command
           if user_input.lower() in ["quit", "exit", "q"]:
               print("\nGoodbye! Have a great day!")
               break
          
           # Skip empty input
           if not user_input:
               continue
          
           # Run the agent
           # create_agent returns an agent that expects messages format
           print("\nCompass AI: ", end="", flush=True)
           response = agent.invoke({
               "messages": [{"role": "user", "content": user_input}]
           })
          
           # Extract the last message content from the response
           if "messages" in response and len(response["messages"]) > 0:
               last_message = response["messages"][-1]
               if hasattr(last_message, "content"):
                   print(last_message.content)
               elif isinstance(last_message, dict) and "content" in last_message:
                   print(last_message["content"])
               else:
                   print(response)
           else:
               print(response)
           print()  # Add spacing between exchanges
          
       except KeyboardInterrupt:
           print("\n\nGoodbye! Have a great day!")
           break
       except Exception as e:
           print(f"\nError: {e}")
           print("Please try again or type 'quit' to exit.\n")




if __name__ == "__main__":
   main()
