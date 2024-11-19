import os
from langchain_community.utilities.sql_database import SQLDatabase
from prefix import SQL_PREFIX
from langgraph.prebuilt import create_react_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage,HumanMessage
from langchain_openai import ChatOpenAI
from boilerplate import (
    building_marker_format_boilerplate,
    holding_period_boilerplate,
    javascript_map_boilerplate,
    marker_boilerplate,
    school_marker_format_boilerplate,
    two_bed_holding_period_boilerplate,
)
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings


POSTGRES_USER=os.getenv("")
POSTGRES_USER = os.getenv("PG_USER")
POSTGRES_PASSWORD = os.getenv("PG_PASSWORD")
POSTGRES_PORT = os.getenv("PG_PORT")
POSTGRES_DB = os.getenv("PG_DB")
connection_string = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}/{POSTGRES_DB}"
db=SQLDatabase.from_uri(connection_string)
# Initialize the LLM with the Llama2 model
llm = ChatOpenAI(model="hugging-quants/Llama-3.2-1B-Instruct-Q8_0-GGUF",
   base_url="http://localhost:1234/v1", api_key="not-needed")
prefix = SQL_PREFIX.format(
     table_names=db.get_usable_table_names(),
     marker_boilerplate=marker_boilerplate,
     holding_period_boilerplate=holding_period_boilerplate,
     two_bed_holding_period_boilerplate=two_bed_holding_period_boilerplate,
     javascript_map_boilerplate=javascript_map_boilerplate,
     building_marker_format_boilerplate=building_marker_format_boilerplate,
     school_marker_format_boilerplate=school_marker_format_boilerplate,
 )
toolkit=SQLDatabaseToolkit(db=db,llm=llm)
tools=toolkit.get_tools()
system_message=SystemMessage(content=prefix)
agent_executor=create_react_agent(llm,tools,state_modifier=system_message)
def print_sql_1(sql):
    print(
        """
The SQL query is:

{}
    """.format(
            sql
        )
    )
def truncate_text(text, max_length=4000):
    return text[:max_length]
def process_question(prompted_question,conversation_history):
    prompt = prompted_question
    context = "\n".join(
        [
            f"Q: {entry['question']}\nA: {entry['answer']}"
            for entry in conversation_history
        ]
    )
    consolidated_prompt = f"""
    Previous conversation:
    {context}

    New question: {prompted_question}

    Please answer the new question, taking into account the context from the previous conversation if relevant.
    """
    prompt = consolidated_prompt if conversation_history else prompted_question

    content = []
    try:
        for s in agent_executor.stream({"messages": [HumanMessage(content=prompt)]}):
            print(s)
            for msg in s.get("agent", {}).get("messages", []):
                 for call in msg.tool_calls:
                     if sql := call.get("args",{}).get("query",None):
                         print(print_sql_1(sql))
                 content.append(msg.content)
                 print("\n")
                 print("******************************************")
    except Exception as e:
        print("Error occurred:", e)
    return content

