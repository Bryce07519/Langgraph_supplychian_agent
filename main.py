# main.py
import argparse
# 修正1: 将 load_dotenv() 提前到所有src导入之前
# 这样可以确保在导入任何自定义模块（如graph_builder）时，环境变量已经就绪
from dotenv import load_dotenv
load_dotenv()

from src.graph_builder import build_graph
from src.llm_provider import get_llm, get_fast_llm
from IPython.display import Image

def main():
    load_dotenv()

    # --- 1. 参数解析，选择LLM ---
    parser = argparse.ArgumentParser(description="供应链风险分析AI Agent")
    parser.add_argument("--llm", type=str, default="openai", choices=["openai", "gemini", "deepseek", "local"],
                        help="选择使用的LLM provider")
    args = parser.parse_args()

    print(f"正在使用 {args.llm.upper()} 模型...")

    # --- 2. 初始化LLM和图 ---
    main_llm = get_llm(args.llm)
    # 结构化输出最好用能力强的模型
    structured_llm = get_llm(args.llm) 
    # 决策节点用快速模型
    fast_llm = get_fast_llm(args.llm) 

    app = build_graph(main_llm, structured_llm, fast_llm)

    # --- 3. 可视化图结构 ---
    try:
        graph_png = app.get_graph().draw_png()
        with open("supply_chain_workflow.png", "wb") as f:
            f.write(graph_png)
        print("工作流图已保存为 supply_chain_workflow.png")
        # 如果在Jupyter环境中，可以取消下面的注释来显示图像
        # display(Image(graph_png))
    except ImportError:
        print("无法生成可视化图，请确保已安装 pygraphviz 和 graphviz 系统库。")
    except Exception as e:
        print(f"生成可视化图时出错: {e}")

    # --- 4. 运行工作流 ---
    disruption_event = "位于苏伊士运河的一艘大型集装箱船搁浅，导致航道双向堵塞。"
    initial_state = {"disruption_event": disruption_event}
    
    print("\n--- 开始执行工作流 ---")
    final_state = app.invoke(initial_state)
    print("--- 工作流执行完毕 ---\n")

    final_report = final_state.get("report", "没有生成报告。")
    print("=" * 50)
    print("最终生成的响应报告:")
    print("=" * 50)
    print(final_report)

    # --- 5. 简单的工作流评估 ---
    print("\n" + "=" * 50)
    print("正在对报告进行质量评估...")
    print("=" * 50)
    evaluator_llm = get_llm(args.llm)
    eval_prompt = f"""你是一个评估机器人。请根据以下标准评估这份供应链响应报告的质量：
    1.  清晰度：报告是否易于理解？
    2.  完整性：是否涵盖了事件分析、影响、方案和建议？
    3.  可操作性：提出的建议是否具体且可行？
    
    请给出一个总体评分（1-10分）并简要说明理由。

    报告内容:
    ---
    {final_report}
    ---
    """
    evaluation = evaluator_llm.invoke(eval_prompt).content
    print(evaluation)

if __name__ == "__main__":
    main()