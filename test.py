from tools.tavily_tool import tavily_search
from baclend import run_travel_agent

user_input = input("Enter your query :")

response = run_travel_agent(
    user_input=user_input,
    thread_id="test"
)

print(response["answer"])