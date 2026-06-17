import os
import sys
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool

# Configure terminal output encoding for Windows compatibility
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# 1. Load Environment Variables
load_dotenv()

# 2. Configure LLMs
# Option A: OpenRouter (Cloud API) - Highly recommended
# We use Llama 3.1 8B for the Collector because it natively supports tool use on OpenRouter
# We set max_tokens=1500 to keep the theoretical cost below your OpenRouter credits limit
tool_llm = LLM(
    model="openrouter/meta-llama/llama-3.1-8b-instruct",
    api_key=os.environ.get("OPENROUTER_API_KEY", "your-api-key"),
    max_tokens=1500,
)

# We use Qwen 2.5 7B for the Analyst, Visualizer, and Compiler (text-only tasks)
# We set max_tokens=1500 to keep the theoretical cost below your OpenRouter credits limit
qwen_llm = LLM(
    model="openrouter/qwen/qwen-2.5-7b-instruct",
    api_key=os.environ.get("OPENROUTER_API_KEY", "your-api-key"),
    max_tokens=1500,
)

# 3. Define Tools
# We use SerperDevTool to allow the Data Collector to search Google
search_tool = SerperDevTool()

# --- Shared Organizational Identity ---
ORG_BACKSTORY = """
You work for 'Aether Analytics Group' (AAG), a premium, cutting-edge data intelligence firm. 
Your communication style is highly professional, precise, and articulate. You always verify your 
facts and you take pride in producing top-tier, executive-ready insights.
"""

# 4. Define Agents
data_collector = Agent(
    role='Senior Data Harvester',
    goal='Gather the most recent and comprehensive raw data, news, and statistics regarding {topic}.',
    backstory=f"""You are an expert at finding hidden data and extracting key information from the web. 
    You excel at filtering out noise and finding hard facts. {ORG_BACKSTORY}""",
    tools=[search_tool],
    llm=tool_llm,
    verbose=True
)

data_analyst = Agent(
    role='Lead Data Analyst',
    goal='Analyze the raw data provided by the collector, identify key trends, correlations, and actionable insights regarding {topic}.',
    backstory=f"""You are a brilliant statistician and analyst. You can look at a pile of raw facts and 
    immediately see the underlying story. You never jump to conclusions without data backing it up. {ORG_BACKSTORY}""",
    llm=qwen_llm,
    verbose=True
)

data_visualizer = Agent(
    role='Information Architect',
    goal='Transform the analytical findings into structured markdown tables, bulleted lists, and clear visual structures.',
    backstory=f"""You are a master of information design. Even in a purely text-based medium, you know how 
    to use formatting, tables, and spacing to make complex data instantly readable and compelling. {ORG_BACKSTORY}""",
    llm=qwen_llm,
    verbose=True
)

report_compiler = Agent(
    role='Executive Editor & Publisher',
    goal='Compile the structured data and analysis into a final, polished executive report ready for the C-suite.',
    backstory=f"""You are the final gatekeeper for Aether Analytics Group. You ensure the final output is 
    not only factually accurate but also exceptionally well-written, engaging, and perfectly formatted. {ORG_BACKSTORY}""",
    llm=qwen_llm,
    verbose=True
)

# 5. Define Tasks
collect_task = Task(
    description='Search the web for the latest data, articles, and statistics regarding: {topic}. Gather at least 5 distinct key facts or data points.',
    expected_output='A raw compilation of data points, facts, and sources.',
    agent=data_collector
)

analyze_task = Task(
    description='Review the data points from the collector. Identify the top 3 trends and write a brief analytical paragraph explaining what this means for the industry.',
    expected_output='An analytical summary highlighting top trends and their implications.',
    agent=data_analyst
)

visualize_task = Task(
    description='Take the analytical summary and organize the key facts into a clear Markdown table. Structure the top 3 trends into a highly readable bulleted list.',
    expected_output='Markdown-formatted tables and lists representing the data.',
    agent=data_visualizer
)

compile_task = Task(
    description='Take all previous outputs and write the final "Aether Analytics Group Executive Report". Include an executive summary, the data tables, the trend analysis, and a final conclusion.',
    expected_output='A comprehensive, professional, multi-section Markdown report.',
    agent=report_compiler
)

# 6. Assemble the Crew
# We use Process.sequential (the default) to ensure data flows from Collector -> Analyst -> Visualizer -> Compiler
analytics_crew = Crew(
    agents=[data_collector, data_analyst, data_visualizer, report_compiler],
    tasks=[collect_task, analyze_task, visualize_task, compile_task],
    process=Process.sequential,
    verbose=True 
)

# 7. Kickoff the Pipeline
if __name__ == "__main__":
    print("🚀 Starting the Aether Analytics Group Pipeline...")
    
    # You can change the topic here
    topic_of_interest = "The impact of autonomous AI agents on software engineering jobs by 2030"
    
    # Run the crew
    result = analytics_crew.kickoff(inputs={'topic': topic_of_interest})
    
    print("\n\n" + "="*50)
    print("📊 FINAL EXECUTIVE REPORT:")
    print("="*50)
    print(result)
    
    # Optionally save to a file
    with open("final_report.md", "w", encoding="utf-8") as f:
        f.write(str(result))
    print("\nReport saved to final_report.md")
