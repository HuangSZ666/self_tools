import datetime
import os
import tiktoken
import requests
import logging
import time
from sentence_transformers import SentenceTransformer
import chromadb

os.makedirs("logs",exist_ok = True)
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s',
    handlers = [
        logging.FileHandler("logs/process.log"),
        logging.StreamHandler()
    ]
)

def split_text(text,chunk_size = 500) :
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    
    if len(tokens) > chunk_size :
        chunk_texts = []
        chunks = [tokens[i:i+chunk_size] for i in range(0, len(tokens), chunk_size)]
        
        for i, chunk in enumerate(chunks):
            chunk_text = encoding.decode(chunk)
            chunk_texts.append(chunk_text)
        
        return chunk_texts
    else :
        return [text]

def ask_deepseek(content,instruction):
    API_KEY = os.environ.get("deepseek_API_key")
    if not API_KEY:
        raise RuntimeError(
            "未设置环境变量 deepseek_API_key。\n"
            "Windows 全局：setx deepseek_API_key 你的key   （或：系统设置 -> 环境变量）\n"
            "Jupyter 当前会话：import os; os.environ['deepseek_API_key']='你的key'"
        )
    url = "https://api.deepseek.com/v1/chat/completions"
    prompt =  f"{instruction}\n\n{content}"
    data = {
        "model": "deepseek-v4-flash",
        "messages": [{"role": "user", "content": prompt}],
        "thinking_mode": "non-thinking"
    }

    response = requests.post(url, headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]  
    else:
        print(f"失败：{response.status_code}")
def summarize_long_text(text,instruction,chunk_size,filename= None ):
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"报告_{timestamp}.md"
    chunks = split_text(text,chunk_size)
    summaries = []
    for i,chunk in enumerate(chunks) :
        summary = ask_deepseek(chunk,instruction)
        summaries.append(f"【第{i+1}段】{summary}")
    jieguo = "\n".join(summaries)
    with open (filename,"w",encoding = "utf-8") as f:
        f.write("处理指令\n")
        f.write(instruction +"\n\n")
        f.write("原始内容\n")
        f.write(text +"\n\n")
        f.write("分析结果\n")
        f.write(jieguo)
    return jieguo


def process_folder(folder_path,output_dir = None):
    start_time = time.time()
    logging.info(f"开始处理文件夹:{folder_path}")
    if output_dir is None:
        output_dir = os.path.join(folder_path,"summaries")
        os.makedirs(output_dir,exist_ok = True)
    results =[]
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path,file_name)
        
        if os.path.isdir(file_path):  
            continue
        if file_name.endswith(("csv", "md", "txt")) and not file_name.endswith("_summary.md"):
            file_path = os.path.join(folder_path,file_name)
            try:
                with open (file_path,"r",encoding = "utf-8") as f:
                    content = f.read()
                    summary = summarize_long_text(text = content,instruction = "请简要总结一下这段内容",chunk_size=500,filename= None )
                    
            except Exception as e:
                logging.error(f"读取文件失败:{file_path},错误:{e}")
            base_name = os.path.splitext(file_name)[0]  # 去掉原有后缀
            output_file = os.path.join(output_dir,f"{base_name}_summary.md")
            
            with open(output_file,"w",encoding= "utf-8") as f :
                f.write(summary)
            logging.info(f"已处理:{file_name}->{output_file}")
            results.append(f"-{base_name}->{output_file}")
    with open (os.path.join(output_dir,"SUMMARY.md"),"w",encoding ="utf-8") as f:
        f.write("文件夹批量摘要报告\n\n")
        f.write("\n".join(results))
    logging.info(f"处理完成,输出目录{output_dir}")
    elapsed = time.time() - start_time
    logging.info(f"总耗时:{elapsed:.2f}秒")

def ask_knowledge(query, collection, embedding_model, n_result=2):
    query_embedding = embedding_model.encode([query])
    results = collection.query(
        query_embeddings=[query_embedding[0].tolist()],
        n_results=n_result,
    )
    retrieved_chunks = results["documents"][0]
    if not retrieved_chunks:
        return "未找到相关内容"
    context = "\n\n".join(retrieved_chunks)
    instruction = f"根据以下内容回答问题:\n\n{context}\n\n问题:{query}"
    answer = ask_deepseek(context, instruction)
    return answer

def init_knowledge_base(offline = False,model_path = None,db_path = None):
    if db_path is None:
        db_path="M:/study/chroma_db"
        os.makedirs(db_path,exist_ok = True)
    if not offline:
        try:
            os.environ.pop("HF_HUB_OFFLINE", None)
            os.environ.pop("TRANSFORMERS_OFFLINE", None)
            embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print("在线模式加载成功")
        except Exception :  
            print("在线模式失败，切换到离线模式")
            os.environ["HF_HUB_OFFLINE"] = "1"
            os.environ["TRANSFORMERS_OFFLINE"] = "1"
            if model_path is None:
                model_path = os.path.expanduser(
                    "~/.cache/huggingface/hub/models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2/"
                    "snapshots/e8f8c211226b894fcb81acc59f3b34ba3efd5f42"
                )
                embedding_model = SentenceTransformer(model_path)
    else:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        if model_path is None:
            model_path = os.path.expanduser(
                "~/.cache/huggingface/hub/models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2/"
                "snapshots/e8f8c211226b894fcb81acc59f3b34ba3efd5f42"
            )
            embedding_model = SentenceTransformer(model_path)
        print("模型加载成功")
    
    client = chromadb.PersistentClient(path = db_path)
    collection = client.get_or_create_collection(name="knowledge")
    return embedding_model ,collection 

def load_and_split(file_path,chunk_size = 200):
    with open (file_path,"r",encoding = "utf-8") as f:
        text = f.read()
    chunks = split_text(text,chunk_size)
    return chunks


def add_document_to_knowledge(file_path,collection,embedding_model,chunk_size = 500):
    chunk_texts = load_and_split(file_path,chunk_size)
    embeddings = embedding_model.encode(chunk_texts)
    
    for i,(chunk,emb) in enumerate(zip(chunk_texts,embeddings)) :
        collection.add(
            ids = [f"{file_path}_{i}"],
            documents = [chunk],
            embeddings = [emb.tolist()]
        )
    print(f"已存入{len(chunk_texts)}条数据")

def store_summaries_to_knowledge(folder_path):
    summary_folder = os.path.join(folder_path,"summaries")
    model,collection = init_knowledge_base(offline = True)
    for file_name in os.listdir(summary_folder):
        if file_name.endswith("_summary.md"):
            file_path = os.path.join(summary_folder,file_name)
            add_document_to_knowledge(file_path,collection,model)
    return model,collection     