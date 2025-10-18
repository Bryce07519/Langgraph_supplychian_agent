# src/graph_builder.py
from langgraph.graph import StateGraph, END
from .graph_nodes import (
    GraphState, 
    analyze_event_node, 
    assess_impact_node, 
    brainstorm_solutions_node,
    review_and_decide_node,
    synthesize_report_node
)
from functools import partial

def build_graph(llm, llm_structured, llm_fast):
    workflow = StateGraph(GraphState)

    # 将LLM实例绑定到节点函数
    # 使用partial来固定llm参数，因为节点函数只接受一个state参数
    bound_analyze_event_node = partial(analyze_event_node, llm=llm)
    bound_assess_impact_node = partial(assess_impact_node, llm=llm)
    bound_brainstorm_solutions_node = partial(brainstorm_solutions_node, llm_structured=llm_structured)
    bound_review_and_decide_node = partial(review_and_decide_node, llm_fast=llm_fast)
    bound_synthesize_report_node = partial(synthesize_report_node, llm=llm)

    # 添加节点
    workflow.add_node("analyze_event", bound_analyze_event_node)
    workflow.add_node("assess_impact", bound_assess_impact_node)
    workflow.add_node("brainstorm_solutions", bound_brainstorm_solutions_node)
    workflow.add_node("review_and_decide", bound_review_and_decide_node)
    workflow.add_node("synthesize_report", bound_synthesize_report_node)

    # 定义边的流转关系
    workflow.set_entry_point("analyze_event")
    workflow.add_edge("analyze_event", "assess_impact")
    workflow.add_edge("assess_impact", "brainstorm_solutions")
    
    # 条件边：审查后决定是修正还是继续
    def decide_next_step(state: GraphState):
        if state['revision_needed']:
            return "brainstorm_solutions" # 返回方案生成节点形成循环
        else:
            return "synthesize_report"

    workflow.add_conditional_edges(
        "review_and_decide",
        decide_next_step,
        {
            "brainstorm_solutions": "brainstorm_solutions",
            "synthesize_report": "synthesize_report",
        }
    )
    workflow.add_edge("brainstorm_solutions", "review_and_decide")
    workflow.add_edge("synthesize_report", END)

    # 编译图
    app = workflow.compile()
    return app