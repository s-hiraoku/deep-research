# ブラウザを操作するAgent
# refers: https://github.com/huggingface/smolagents/tree/main/examples/open_deep_research

import argparse
import os
import threading

from dotenv import load_dotenv
from huggingface_hub import login
from smolagents import (
    CodeAgent,
    GoogleSearchTool,
    # HfApiModel,
    LiteLLMModel,
    LogLevel,
    ToolCallingAgent,
)

from scripts.text_inspector_tool import TextInspectorTool
from scripts.text_web_browser import (
    ArchiveSearchTool,
    FinderTool,
    FindNextTool,
    PageDownTool,
    PageUpTool,
    SimpleTextBrowser,
    VisitTool,
)
from scripts.visual_qa import visualizer

AUTHORIZED_IMPORTS = [
    "requests",
    "zipfile",
    "os",
    "pandas",
    "numpy",
    "sympy",
    "json",
    "bs4",
    "pubchempy",
    "xml",
    "yahoo_finance",
    "Bio",
    "sklearn",
    "scipy",
    "pydub",
    "io",
    "PIL",
    "chess",
    "PyPDF2",
    "pptx",
    "torch",
    "datetime",
    "fractions",
    "csv",
]
load_dotenv(override=True)
login(os.getenv("HF_TOKEN"))

append_answer_lock = threading.Lock()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "question",
        type=str,
        help="for example: 'How many studio albums did Mercedes Sosa release before 2007?'",
    )
    parser.add_argument("--model-id", type=str, default="o1")
    return parser.parse_args()


custom_role_conversions = {"tool-call": "assistant", "tool-response": "user"}

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"

BROWSER_CONFIG = {
    "viewport_size": 1024 * 5,
    "downloads_folder": "downloads_folder",
    "request_kwargs": {
        "headers": {"User-Agent": user_agent},
        "timeout": 300,
    },
    "serpapi_key": os.getenv("SERPAPI_API_KEY"),
}

os.makedirs(f"./{BROWSER_CONFIG['downloads_folder']}", exist_ok=True)


def create_agent(model_id="o1"):
    model_params = {
        "model_id": model_id,
        "custom_role_conversions": custom_role_conversions,
        "max_completion_tokens": 8192,
    }
    if model_id == "o1":
        model_params["reasoning_effort"] = "high"
    model = LiteLLMModel(**model_params)

    text_limit = 100000
    browser = SimpleTextBrowser(**BROWSER_CONFIG)
    WEB_TOOLS = [
        GoogleSearchTool(provider="serper"),
        VisitTool(browser),
        PageUpTool(browser),
        PageDownTool(browser),
        FinderTool(browser),
        FindNextTool(browser),
        ArchiveSearchTool(browser),
        TextInspectorTool(model, text_limit),
    ]
    text_webbrowser_agent = ToolCallingAgent(
        model=model,
        tools=WEB_TOOLS,
        max_steps=20,
        verbosity_level=2,
        planning_interval=4,
        name="search_agent",
        description="""A team member that will search the internet to answer your question.
    Ask him for all your questions that require browsing the web.
    Provide him as much context as possible, in particular if you need to search on a specific timeframe!
    And don't hesitate to provide him with a complex search task, like finding a difference between two webpages.
    Your request must be a real sentence, not a google search! Like "Find me this information (...)" rather than a few keywords.
    """,
        # 日本語訳:
        # インターネットを検索してあなたの質問に答えるチームメンバーです。
        # ウェブ閲覧が必要なすべての質問について彼に尋ねてください。
        # できるだけ多くのコンテキストを提供してください、特に特定の時間枠で検索する必要がある場合は重要です！
        # また、2つのウェブページの違いを見つけるなど、複雑な検索タスクを依頼することをためらわないでください。
        # あなたのリクエストは、いくつかのキーワードではなく、「この情報を見つけてください(...)」のような実際の文章である必要があります。
        provide_run_summary=True,
    )
    text_webbrowser_agent.prompt_templates["managed_agent"][
        "task"
    ] += """You can navigate to .txt online files.
    If a non-html page is in another format, especially .pdf or a Youtube video, use tool 'inspect_file_as_text' to inspect it.
    Additionally, if after some searching you find out that you need more information to answer the question, you can use `final_answer` with your request for clarification as argument to request for more information."""
    # 日本語訳:
    # オンラインの.txtファイルにナビゲートできます。
    # HTMLページ以外の形式、特に.pdfやYouTubeビデオの場合は、'inspect_file_as_text'ツールを使用して検査してください。
    # さらに、検索した後に質問に答えるためにより多くの情報が必要だと判断した場合は、明確化のリクエストを引数として`final_answer`を使用して、より多くの情報をリクエストできます。

    manager_agent = CodeAgent(
        model=model,
        tools=[visualizer, TextInspectorTool(model, text_limit)],
        max_steps=12,
        verbosity_level=LogLevel.OFF,
        additional_authorized_imports=AUTHORIZED_IMPORTS,
        planning_interval=4,
        managed_agents=[text_webbrowser_agent],
    )
    manager_agent.prompt_templates["managed_agent"]["task"] += (
        """Also, please make sure to verify that the output content and format requested in the task are correct before returning your final_answer."""
    )
    # 日本語訳:
    # また、タスクで要求された出力内容と形式が正しいことを確認してから、最終的な回答を返してください。

    return manager_agent


# def main():
#     args = parse_args()

#     agent = create_agent(model_id=args.model_id)

#     answer = agent.run(args.question)

#     print(f"Got this answer: {answer}")


# if __name__ == "__main__":
#     main()
