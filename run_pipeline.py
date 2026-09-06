import self_tools
import os
import shutil
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder",required = True,help = "要处理的文件夹路径")
    parser.add_argument("--question",required = True,help = "要向知识库提问的问题")
    args = parser.parse_args()
    folder_path = args.folder
    question = args.question
    shutil.rmtree("M:/study/chroma_db")
    self_tools.process_folder(folder_path)
    model,collection = self_tools.init_knowledge_base(offline = True)
    summary_folder = os.path.join(folder_path,"summaries")
    
    for file_name in os.listdir(summary_folder):
        if file_name.endswith("_summary.md"):
            file_path = os.path.join(summary_folder,file_name)
            self_tools.add_document_to_knowledge(file_path,collection,model)
    answer = self_tools.ask_knowledge(question,collection,model)
    print(answer)
    print(os.listdir("logs"))
if __name__ == "__main__":
    main()
   