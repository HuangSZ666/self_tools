# self_tools — 基于 FastAPI 的 RAG 检索与 AI 后端服务

一个集成了长文本处理、批量摘要、本地知识库构建（RAG）与模型 API 调用的 Python 工具集。近期已完成工程化升级，通过 **FastAPI 封装为标准的 Web API 服务**，支持前后端分离调用与自动接口文档生成。

## 核心特性与工程优化
- **RAG 全链路打通**：支持文本切片、向量化（Sentence-Transformers）、存储（ChromaDB）与语义检索。
- **FastAPI 接口封装**：将本地 RAG 链路封装为标准的 HTTP/JSON 接口（`/ask_ai`），提供 Swagger UI 自动接口文档。
- **生命周期与并发优化**：利用 FastAPI 的 `startup` 事件与全局变量，实现模型与数据库的**“单次加载，全局复用”**，避免每次请求重复加载数百兆模型，大幅降低资源开销与响应延迟。
- **数据预处理机制**：在测试中发现向量检索对结构化表格（CSV/Excel）语义识别较差，现已支持将表格转化为自然语言文本（`.txt` / `.md`）自动切块入库，大幅提升数值类检索的精准度。
- **Agent 工具调用**：内置 `run_agent` 逻辑，让大模型自主判断是否需要查询本地知识库。

## 核心函数说明 (self_tools.py)
- `split_text(text, chunk_size=500)`：按 Token 切分长文本，短文本不分块。
- `ask_deepseek(content, instruction)`：调用 DeepSeek API，根据指令处理文本。
- `summarize_long_text(...)`：切分 + 调用 + 保存摘要。
- `process_folder(folder_path, output_dir=None)`：遍历文件夹，生成所有文本文件的摘要报告。
- `init_knowledge_base(offline=False, ...)`：加载本地向量模型，连接 ChromaDB 知识库。
- `add_document_to_knowledge(file_path, collection, embedding_model, chunk_size=500)`：将切分后的文本存入知识库。
- `ask_knowledge(query, collection, embedding_model, n_result=2)`：基于知识库检索，拼接上下文并生成回答。
- `run_agent(query, collection, embedding_model)`：Agent 工具调用，模型自主判断是否查库。

## 依赖环境
- Python 3.9+
- 需要安装：`tiktoken`, `requests`, `sentence-transformers`, `chromadb`, `fastapi`, `uvicorn`
- 需要配置环境变量：`deepseek_API_key`

## 快速启动与接口测试
### 1. 启动 FastAPI 服务
在项目根目录下运行：
uvicorn main:app --reload

启动成功后，访问 http://127.0.0.1:8000/docs 即可看到自动生成的 Swagger 接口文档。

### 2. 接口测试
在 Swagger UI 中展开 `/ask_ai` 接口，点击 "Try it out"，输入问题，点击 "Execute"，即可通过 API 获取大模型的 JSON 格式回答。
## 基础使用示例

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
self_tools.add_document_to_knowledge("M:/study/test_folder/技能表.txt", collection, model)
answer = self_tools.run_agent("帕帕斯卡的传动机制是什么？", collection, model)
print(answer)
## 命令行运行（run_pipeline.py）
你可以通过命令行参数指定文件夹路径和问题，无需修改代码：
python run_pipeline.py --folder M:/study/test_folder --question "Python 是什么"

参数说明：
- --folder：指定要处理的文件夹路径，程序会自动生成该文件夹内所有文本文件的摘要。
- --question：指定要向知识库提问的问题。
- --help：显示帮助信息。

## 日志与文件结构
运行时会自动在 logs/process.log 中记录操作日志和错误信息。

M:/study/
├── main.py                # FastAPI 服务入口，定义路由与启动事件
├── self_tools.py          # 核心工具库
├── run_batch.py           # 批量处理测试入口
├── run_pipeline.py        # 完整流程测试入口
├── README.md              # 项目说明
├── logs/                  # 日志目录 (已忽略)
├── chroma_db/             # 向量数据库 (已忽略)
├── test_folder/           # 测试数据目录
└── 暑假项目/              # 备份

## 附录
- 帕帕斯卡传动机制说明：见 test_folder/帕帕斯卡传动机制.md
- 帕帕斯卡技能表：已转化为自然语言文本 test_folder/技能表.txt