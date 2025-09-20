# AI文件重命名工具

## 介绍🤖🤖🤖
你的电脑里是否有很多文件因为之前简单的命名而不知道内容是什么？这个工具结合大语言模型(LLM)可以根据文件内容自动为你命名，你再也不用担心文件命名不当的问题了。

![重命名文件夹](/demo/rename.png)
![配置界面](/demo/config.png)
![帮助界面](/demo/help.png)

## 🚀 功能特性
* 支持本地ollama服务器模型调用和在线OpenAI模型调用
* 支持处理图片（png、svg、jpg等常见格式）、文档（txt、word、excel、pdf、md）和多媒体文件
* 智能内容分析，自动生成有意义的文件名
* 支持长文档摘要生成，节省API调用成本

## 💪 系统要求
* Nvidia CUDA 11.8或更新版本（如果你的电脑没有Nvidia GPU，需要在配置文件中将device设置为CPU）
* ffmpeg
* GTK-3
* ollama

##  快速开始
### 1. 安装ffmpeg
在Windows上，你可以从 `https://www.gyan.dev/ffmpeg/builds/` 下载ffmpeg。这是一个zip压缩包，你可以解压到系统的任何位置，然后将其添加到环境变量中。如果你对如何安装ffmpeg还有疑问，也许下面的博客文章可以指导你。
> https://blog.csdn.net/Dneccc/article/details/138825228

### 2. 安装GTK-3
> https://sourceforge.net/projects/gtk-win/
你可能需要参考以下博客：
> https://blog.csdn.net/bz_xyz/article/details/104637487

### 3. 安装ollama
你可以从 `https://ollama.com/` 下载并安装ollama

### 4. 克隆仓库
```
git clone https://github.com/2445868686/AiRename-Image.git
```