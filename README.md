# self_tools — 文本处理与 RAG 工具集

一个用于处理长文本、批量生成摘要、构建本地知识库的 Python 工具库。

## 功能
- split_text(text, chunk_size=500)：按 Token 切分长文本，短文本不分块
- ask_deepseek(content, instruction)：调用 DeepSeek API，根据指令处理文本
- summarize_long_text(text, instruction, chunk_size=500, filename=None)：切分 + 调用 + 保存摘要
- process_folder(folder_path, output_dir=None)：遍历文件夹，生成所有文本文件的摘要报告
- init_knowledge_base(offline=False, model_path=None, db_path=None)：加载向量模型，连接 ChromaDB 知识库
- add_document_to_knowledge(file_path, collection, embedding_model, chunk_size=500)：将文本文件存入知识库
- ask_knowledge(query, collection, embedding_model, n_result=2)：基于知识库检索，生成回答
- run_agent(query, collection, embedding_model)：Agent 工具调用，模型自主判断是否查询知识库

## 依赖
- Python 3.9+
- 需要安装：tiktoken、requests、sentence-transformers、chromadb
- DeepSeek API Key（需放入环境变量 deepseek_API_key）

## 使用示例

### 1. 批量处理文件夹
import self_tools
self_tools.process_folder("M:/study/test_folder")

### 2. 构建知识库并提问
import self_tools
model, collection = self_tools.init_knowledge_base(offline=True)
self_tools.add_document_to_knowledge("M:/study/test.txt", collection, model)
answer = self_tools.ask_knowledge("Python 是什么", collection, model)
print(answer)

### 3. 完整流程（摘要生成 + 知识库 + 提问）
import self_tools
import os
import shutil
shutil.rmtree("M:/study/chroma_db", ignore_errors=True)
self_tools.process_folder("M:/study/test_folder")
model, collection = self_tools.init_knowledge_base(offline=True)
for f in os.listdir("M:/study/test_folder/summaries"):
    if f.endswith("_summary.md"):
        self_tools.add_document_to_knowledge(os.path.join("M:/study/test_folder/summaries", f), collection, model)
answer = self_tools.ask_knowledge("Python 是什么", collection, model)
print(answer)

### 4. Agent 工具调用
import self_tools
model, collection = self_tools.init_knowledge_base(offline=True)
self_tools.add_document_to_knowledge("M:/study/test_folder/帕帕斯卡技能表.csv", collection, model)
answer = self_tools.run_agent("帕帕斯卡的传动机制是什么？", collection, model)
print(answer)

## 日志
运行时会自动在 logs/process.log 中记录操作日志和错误信息。

## 文件结构
M:/study/
├── self_tools.py          # 核心工具库
├── run_batch.py           # 批量处理测试入口
├── run_pipeline.py        # 完整流程测试入口
├── README.md              # 项目说明
├── logs/                  # 日志目录
├── chroma_db/             # 向量数据库
├── test_folder/           # 测试数据
└── 暑假项目/              # 备份

## 附录
- 帕帕斯卡传动机制说明：见 `帕帕斯卡传动机制.md`
- 帕帕斯卡技能表：见 `帕帕斯卡技能表.csv`

## 命令行运行（run_pipeline.py）

你可以通过命令行参数指定文件夹路径和问题，无需修改代码：

python run_pipeline.py --folder M:/study/test_folder --question "Python 是什么"

参数说明：
- --folder：指定要处理的文件夹路径，程序会自动生成该文件夹内所有文本文件的摘要
- --question：指定要向知识库提问的问题
- --help：显示帮助信息

## 说明
这个工具是在 2026 年暑假期间学习 Python 和 AI Agent 开发时写的练习项目，主要用于练习函数封装、API 调用、分块处理、日志记录、向量检索和批量文件处理。