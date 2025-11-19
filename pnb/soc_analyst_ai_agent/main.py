from typing import List, Dict
from pnb.soc_analyst_ai_agent.graph.flow import build_graph
from pnb.soc_analyst_ai_agent.state_schema import State

def main(logs: List[Dict]) -> State:
    flow = build_graph()
    initial_state = State(logs=logs, accessed_by="l3_analyst@bank.co.in", user_role="L3")
    final_state = flow.invoke(initial_state)
    return final_state

