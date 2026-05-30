import os
from typing import Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict
from app.tools import get_stock_data, get_news, get_announcements
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are ASX Intel, an expert Australian stock market analyst.

You have access to three tools:
1. get_stock_data — fetches real-time price, P/E ratio, market cap, dividend yield
2. get_news — fetches latest news and market sentiment
3. get_announcements — fetches official ASX company announcements via semantic search

When a user asks about an ASX stock:
1. ALWAYS call all three tools to gather comprehensive data
2. Synthesize the information into a structured analysis
3. ALWAYS end with a risk disclaimer

Your analysis must include:
- Current market position (price, valuation metrics)
- Recent news sentiment (bullish/bearish/neutral)
- Key announcements and their implications
- Strengths and risks
- Overall outlook

IMPORTANT: You are not a licensed financial advisor. Always include:
"⚠️ This analysis is for informational purposes only and does not constitute financial advice."
"""

tools = [get_stock_data, get_news, get_announcements]

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

def create_agent():
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    def agent_node(state: AgentState):
        messages = state["messages"]
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState):
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    tool_node = ToolNode(tools)

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()

def analyze_stock(ticker: str, question: str = None) -> str:
    agent = create_agent()
    
    if question:
        user_message = f"Analyze ASX stock {ticker.upper()}. Specific question: {question}"
    else:
        user_message = f"Provide a comprehensive analysis of ASX stock {ticker.upper()}."

    result = agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })

    final_message = result["messages"][-1]
    return final_message.content