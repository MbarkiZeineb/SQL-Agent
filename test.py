import os
from langchain_community.utilities.sql_database import SQLDatabase
from prefix import SQL_PREFIX
from langgraph.prebuilt import create_react_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage,HumanMessage
from langchain_openai import ChatOpenAI
from boilerplate import (
    holding_period_boilerplate,
    javascript_map_boilerplate,
    marker_boilerplate,
    two_bed_holding_period_boilerplate,
)
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.types import AgentType

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

toolkit=SQLDatabaseToolkit(db=db,llm=llm)
tools=toolkit.get_tools()
prefix = SQL_PREFIX.format(
     table_names=db.get_usable_table_names(),
     marker_boilerplate=marker_boilerplate,
     holding_period_boilerplate=holding_period_boilerplate,
     two_bed_holding_period_boilerplate=two_bed_holding_period_boilerplate,
     javascript_map_boilerplate=javascript_map_boilerplate
 )
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=False,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    prefix=prefix)
answer = agent_executor.invoke({"input": "Number of sales"})
print(answer)
