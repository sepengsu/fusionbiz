from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def chunk_file(input_path, save_dir, chunk_size=200, chunk_overlap=0):
    os.makedirs(save_dir, exist_ok=True)
    with open(input_path, encoding="utf-8") as f:
        text = f.read()

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_text(text)

    for i, chunk in enumerate(chunks):
        with open(os.path.join(save_dir, f"chunk_{i}.txt"), "w", encoding="utf-8") as out:
            out.write(chunk)
    print(f"[✅] {len(chunks)}개 청크 저장 완료: {save_dir}")
    return chunks

