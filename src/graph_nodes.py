# src/graph_nodes.py
from typing import List, TypedDict, Dict
import json

# 从 pydantic v2 导入
from pydantic import BaseModel, Field

# 修正: 导入的类名从 TavilySearchResults 更改为 TavilySearch
from langchain_tavily import TavilySearch

# --- 1. 定义图的状态 ---

class Solution(BaseModel):
    """供应链问题的应对方案"""
    title: str = Field(description="方案的简洁标题")
    description: str = Field(description="方案的详细描述")
    cost_analysis: str = Field(description="成本分析，如'高', '中', '低'")
    risk_analysis: str = Field(description="风险分析，如'高', '中', '低'")

class GraphState(TypedDict):
    """
    图的状态
    
    Attributes:
        disruption_event: 原始的中断事件描述
        analysis: 对事件的深入分析
        impacts: 对供应链的具体影响
        solutions: 提出的解决方案列表
        chosen_solution: 最终选择的方案
        report: 最终生成的报告
        revision_needed: 是否需要修正方案
        revision_feedback: 修正的反馈意见
    """
    disruption_event: str
    analysis: str
    impacts: str
    solutions: List[Solution]
    chosen_solution: Solution
    report: str
    revision_needed: bool
    revision_feedback: str

# --- 2. 定义工具 ---
# 修正: 实例化正确的类名 TavilySearch
search_tool = TavilySearch(max_results=3)


# --- 3. 定义图的节点 ---

def analyze_event_node(state: GraphState, llm) -> Dict:
    """分析初始事件的节点"""
    print("---NODE: ANALYZE EVENT---")
    prompt = f"""你是一位顶级的供应链分析师。请分析以下供应链中断事件，提供背景信息，并评估其潜在的严重性。
    事件: {state['disruption_event']}
    使用搜索工具获取最新的相关信息以支持你的分析。
    """
    search_results = search_tool.invoke(state['disruption_event'])
    
    # 将搜索结果整合进提示
    prompt_with_context = f"{prompt}\n\n相关新闻或数据:\n{search_results}"
    
    response = llm.invoke(prompt_with_context)
    return {"analysis": response.content}

def assess_impact_node(state: GraphState, llm) -> Dict:
    """评估事件影响的节点"""
    print("---NODE: ASSESS IMPACT---")
    prompt = f"""基于以下事件分析，请详细说明它对一家典型的全球电子消费品公司（例如，类似Apple或Samsung）可能产生的具体影响。
    请从以下几个方面考虑：
    1.  受影响的关键供应商或地区。
    2.  中断的运输路线和物流瓶颈。
    3.  可能面临短缺的零部件或最终产品。
    
    事件分析:
    {state['analysis']}
    """
    response = llm.invoke(prompt)
    return {"impacts": response.content}

def brainstorm_solutions_node(state: GraphState, llm_structured) -> Dict:
    """生成解决方案的节点，支持修正"""
    print("---NODE: BRAINSTORM SOLUTIONS---")
    class Solutions(BaseModel):
        """一系列针对供应链问题的应对方案"""
        solutions: List[Solution]

    # 如果使用本地LLM，需要特殊处理结构化输出
    if hasattr(llm_structured, '_llm_type') and llm_structured._llm_type == "custom_api_chat_model":
        # 为本地LLM构造特殊提示，要求其输出JSON格式
        # 如果需要修正，将反馈信息加入提示
        revision_prompt_part = ""
        if state.get("revision_needed"):
            print("    -> 检测到修正请求，正在优化方案...")
            revision_prompt_part = f"""
            注意：之前的方案被认为需要修正。请根据以下反馈进行优化或提出全新的方案：
            反馈: {state['revision_feedback']}
            """

        prompt = f"""你是一个富有创造力的供应链策略师。基于以下事件分析和影响评估，请提出3个具体、可行的应对方案。
        每个方案都应包含明确的描述、成本分析和风险评估。
        {revision_prompt_part}
        
        事件分析:
        {state['analysis']}
        
        具体影响:
        {state['impacts']}
        
        请以严格的JSON格式返回结果，不要包含其他文本，严格按照以下格式:
        ```json
        {{
            "solutions": [
                {{
                    "title": "方案标题",
                    "description": "方案详细描述",
                    "cost_analysis": "高|中|低",
                    "risk_analysis": "高|中|低"
                }}
            ]
        }}
        ```
        """
        response = llm_structured.invoke(prompt)
        # 解析返回的JSON文本
        try:
            # 提取代码块中的JSON内容
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]  # 移除 ```json 前缀
            if content.endswith("```"):
                content = content[:-3]  # 移除 ``` 后缀
            content = content.strip()
            
            # 检查内容是否为空
            if not content:
                raise ValueError("LLM返回的内容为空")
                
            solutions_data = json.loads(content)
            solutions = [Solution(**solution) for solution in solutions_data["solutions"]]
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # 打印错误信息以便调试
            print(f"DEBUG: LLM response content: '{response.content}'")
            raise ValueError(f"无法解析本地LLM的结构化输出: {e}")
    else:
        # 对于其他LLM，使用标准的with_structured_output方法
        planner = llm_structured.with_structured_output(Solutions)
        
        # 如果需要修正，将反馈信息加入提示
        revision_prompt_part = ""
        if state.get("revision_needed"):
            print("    -> 检测到修正请求，正在优化方案...")
            revision_prompt_part = f"""
            注意：之前的方案被认为需要修正。请根据以下反馈进行优化或提出全新的方案：
            反馈: {state['revision_feedback']}
            """

        prompt = f"""你是一个富有创造力的供应链策略师。基于以下事件分析和影响评估，请提出3个具体、可行的应对方案。
        每个方案都应包含明确的描述、成本分析和风险评估。
        {revision_prompt_part}
        
        事件分析:
        {state['analysis']}
        
        具体影响:
        {state['impacts']}
        """
        response = planner.invoke(prompt)
        solutions = response.solutions

    return {"solutions": solutions}

def review_and_decide_node(state: GraphState, llm_fast) -> Dict:
    """审查方案并做出决策的节点"""
    print("---NODE: REVIEW & DECIDE---")
    class Decision(BaseModel):
        """对方案的审查决策"""
        decision: str = Field(description="只能是 'accept' 或 'revise' 之一")
        feedback: str = Field(description="如果选择 'revise'，请提供具体的修改建议。如果'accept'，则说明选择该方案的理由。")
        chosen_solution_index: int = Field(description="如果 'accept'，选择的最佳方案的索引 (从0开始)。如果 'revise'，此项可忽略。")

    # 如果使用本地LLM，需要特殊处理结构化输出
    if hasattr(llm_fast, '_llm_type') and llm_fast._llm_type == "custom_api_chat_model":
        solutions_str = "\n\n".join([f"方案 {i}:\n{json.dumps(s.model_dump(), indent=2, ensure_ascii=False)}" for i, s in enumerate(state['solutions'])])
        
        prompt = f"""你是一位经验丰富的供应链总监。请审查以下应对方案，并决定是接受其中一个还是要求修正。
        一个好的方案应该具体、可操作，并能有效平衡成本和风险。如果方案过于笼统或风险评估不明确，请要求修正。
         
        现有方案:
        {solutions_str}
        
        请以严格的JSON格式返回结果，不要包含其他文本，严格按照以下格式:
        ```json
        {{
            "decision": "accept|revise",
            "feedback": "反馈内容",
            "chosen_solution_index": 0
        }}
        ```
        """
        decision_response = llm_fast.invoke(prompt)
        # 解析返回的JSON文本
        try:
            # 提取代码块中的JSON内容
            content = decision_response.content.strip()
            if content.startswith("```json"):
                content = content[7:]  # 移除 ```json 前缀
            if content.endswith("```"):
                content = content[:-3]  # 移除 ``` 后缀
            content = content.strip()
            
            # 检查内容是否为空
            if not content:
                raise ValueError("LLM返回的内容为空")
                
            decision_data = json.loads(content)
            decision_response = Decision(**decision_data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # 打印错误信息以便调试
            print(f"DEBUG: LLM response content: '{decision_response.content}'")
            raise ValueError(f"无法解析本地LLM的结构化输出: {e}")
    else:
        # 对于其他LLM，使用标准的with_structured_output方法
        reviewer = llm_fast.with_structured_output(Decision)
        
        solutions_str = "\n\n".join([f"方案 {i}:\n{json.dumps(s.model_dump(), indent=2, ensure_ascii=False)}" for i, s in enumerate(state['solutions'])])
        
        prompt = f"""你是一位经验丰富的供应链总监。请审查以下应对方案，并决定是接受其中一个还是要求修正。
        一个好的方案应该具体、可操作，并能有效平衡成本和风险。如果方案过于笼统或风险评估不明确，请要求修正。
        
        现有方案:
        {solutions_str}
        
        你的决策是什么？是 'accept' 还是 'revise'？请提供你的理由。
        """
        decision_response = reviewer.invoke(prompt)

    if decision_response.decision.lower() == 'revise':
        print(f"    -> 决策：修正方案。反馈: {decision_response.feedback}")
        return {
            "revision_needed": True, 
            "revision_feedback": decision_response.feedback
        }
    else:
        print(f"    -> 决策：接受方案。理由: {decision_response.feedback}")
        num_solutions = len(state['solutions'])
        chosen_idx = min(decision_response.chosen_solution_index, num_solutions - 1)
        if decision_response.chosen_solution_index >= num_solutions:
            print(f"    -> 警告：LLM返回的索引({decision_response.chosen_solution_index})越界，已自动修正为最大有效索引({chosen_idx})。")

        return {
            "revision_needed": False,
            "revision_feedback": "",
            "chosen_solution": state['solutions'][chosen_idx]
        }

def synthesize_report_node(state: GraphState, llm) -> Dict:
    """合成最终报告的节点"""
    print("---NODE: SYNTHESIZE REPORT---")
    
    solutions_formatted = "\n\n".join([
        f"备选方案 {i+1}: {s.title}\n"
        f"  - 描述: {s.description}\n"
        f"  - 成本分析: {s.cost_analysis}\n"
        f"  - 风险分析: {s.risk_analysis}"
        for i, s in enumerate(state['solutions'])
    ])
    
    chosen_solution_formatted = (
        f"推荐方案: {state['chosen_solution'].title}\n"
        f"  - 描述: {state['chosen_solution'].description}\n"
        f"  - 成本分析: {state['chosen_solution'].cost_analysis}\n"
        f"  - 风险分析: {state['chosen_solution'].risk_analysis}"
    )

    prompt = f"""你是一位专业的商业顾问。请将以下所有信息整合成一份结构清晰、专业的供应链中断事件响应报告。
    报告应包含以下部分：
    1.  事件摘要 (Executive Summary)
    2.  详细影响评估 (Detailed Impact Assessment)
    3.  备选方案分析 (Alternative Solutions Analysis)
    4.  最终推荐行动计划 (Recommended Action Plan)

    --- 输入信息 ---
    原始事件: {state['disruption_event']}
    
    事件分析详情: 
    {state['analysis']}
    
    具体影响评估: 
    {state['impacts']}
    
    所有考虑的备选方案:
    {solutions_formatted}
    
    最终推荐方案及理由:
    {chosen_solution_formatted}
    --- 报告结束 ---
    """
    report = llm.invoke(prompt)
    return {"report": report.content}