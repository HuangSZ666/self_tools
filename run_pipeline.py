import self_tools
import os
import shutil
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", required=True, help="要处理的文件夹路径")
    parser.add_argument("--question", required=True, help="要向知识库提问的问题")
    args = parser.parse_args()
    folder_path = args.folder
    question = args.question

    # 清空旧的知识库，重新建立
    shutil.rmtree("M:/study/chroma_db", ignore_errors=True)

    # 1. 处理文件夹：把每个 txt/csv/md 文件总结成 _summary.md（输出到 folder/summaries/）
    self_tools.process_folder(folder_path)

    # 2. 把 summaries 里的摘要存入知识库（chroma）
    #    store_summaries_to_knowledge 返回 (model, collection)，按此顺序接收
    model, collection = self_tools.store_summaries_to_knowledge(folder_path)

    # 3. 用知识库回答问题
    answer = self_tools.ask_knowledge(question, collection, model)
    print(answer)

    # 4. 打印日志目录（logs 在 M:/study 下）
    print(os.listdir("M:/study/logs"))

if __name__ == "__main__":
    main()
