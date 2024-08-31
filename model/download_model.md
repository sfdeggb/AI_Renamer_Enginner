# 安装huggingface_hub
pip install -U huggingface_hub
注意：huggingface_hub 依赖于 Python>=3.8，此外需要安装 0.17.0 及以上的版本，推荐0.19.0+。

# 设置环境变量（指定下载镜像）
## Linux
export HF_ENDPOINT=https://hf-mirror.com
## windows
$env:HF_ENDPOINT = "https://hf-mirror.com"

# 下载模型（如gpt2)
huggingface-cli download --resume-download gpt2 --local-dir gpt2

#注意下载视频信息总结模型脚本文件无用
large-v2.pt模型下载地址：https://www.bilibili.com/read/cv28169729/
