import os
from fastapi import FastAPI
import self_tools

app = FastAPI()

my_collection = None
my_model = None

@app.on_event("startup")
def startup_event():
    global my_model, my_collection
    print("正在加载 RAG 模型和向量数据库，请稍等...")
    
    my_model, my_collection = self_tools.init_knowledge_base(offline=True)
    
    # 直接用 add_document_to_knowledge 去读原始文件
    folder_path = "M:/study/test_folder" # 确认这里是你放 CSV 的路径
    try:
        if my_collection.count() == 0:
            print("知识库为空！开始直接存入原始文件...")
            for file_name in os.listdir(folder_path):
                # 只要是以 csv 或 txt 结尾的文件，直接塞进去
                if file_name.endswith((".csv", ".txt",".md")): 
                    file_path = os.path.join(folder_path, file_name)
                    print(f"正在处理并存入: {file_name}")
                    # 直接调用你最核心的入库函数
                    self_tools.add_document_to_knowledge(
                        file_path=file_path, 
                        collection=my_collection, 
                        embedding_model=my_model, 
                        chunk_size=300
                    )
            print(f"数据灌入完成！当前共有 {my_collection.count()} 条数据。")
        else:
            print(f"已有 {my_collection.count()} 条数据，跳过。")
    except Exception as e:
        print(f"出错: {e}")
        
    print("模型和数据库加载完成！")

@app.get("/")
def read_root():
    return {"message": "AI 后端服务正在运行"}

# 3. 真正的接口
@app.get("/ask_ai")
def ask_ai(question: str):
    # 检查一下模型有没有加载好，防止没加载完就访问报错
    if my_collection is None or my_model is None:
        return {"error": "模型还在加载中，请稍后再试"}
    
    # 4. 把全局变量传给你的函数
    ai_answer = self_tools.ask_knowledge(
        query=question, 
        collection=my_collection, 
        embedding_model=my_model
    )
    
    return {
        "你的问题": question,
        "AI的回答": ai_answer
    }

@app.get("/hello")
def my_test_func(name: str):
    return {"msg": f"FastAPI真好玩，{name}今天一定能拿到实习！"}