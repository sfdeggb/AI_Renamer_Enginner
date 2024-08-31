import os
import subprocess
import argparse
from huggingface_hub import snapshot_download

def set_environment_variable():
    if os.name == 'nt':  # Windows
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
    else:  # Linux or other
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

def download_model(model_name, local_dir):
    try:
        snapshot_download(repo_id=model_name, local_dir=local_dir, resume_download=True)
        print(f"模型 {model_name} 已成功下载到 {local_dir}")
    except Exception as e:
        print(f"下载模型时出错: {e}")

def main():
    parser = argparse.ArgumentParser(description="下载 Hugging Face 模型")
    parser.add_argument("--model_name", type=str, required=True, help="要下载的模型名称")
    parser.add_argument("--local_dir", type=str, required=True, help="保存模型的本地目录")
    args = parser.parse_args()

    set_environment_variable()
    download_model(args.model_name, args.local_dir)

if __name__ == "__main__":
    main()