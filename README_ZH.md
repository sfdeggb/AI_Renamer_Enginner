# AiRename-Engnner

## Intervew
Are there many files in your computer that you do not know what is because of the simple naming before, this tool combined with LLM can help you automatically name according to the content of your files, you no longer need to worry about the improper naming of files.
## Featuers
* 支持本地ollama服务器模型调用和在线openai 模型调用
* 支持修改图片（png,svg.jpg等常见格式)，文档（txt,word,excel,pdf.md)以及多媒体文件 
## Requirment
* Nvidia CUDA 11.8 or newer(if your computer do not have nvidia GPU, you need setting the config file value device to CPU). 
* ffmpeg
* GTK-3
* ollama
## Start
### 1. Install ffmpeg
On windows you can download the ffmpeg on `https://www.gyan.dev/ffmpeg/builds/`. 他是一个压缩包 你可以将他解压到你系统的任何位置，然后将他添加到环境变量里面。如果你对于如何安装ffmpeg还存在疑问，或许下面这篇Bolg可以指导你。
### 2. Install GTK-3
> https://sourceforge.net/projects/gtk-win/

### 2.Clone the repository
```
git clone https://github.com/2445868686/AiRename-Image.git
```
### 3.Install Dependencies
```
cd AiRename-Image
```
```
pip install -r requirements.txt
```
### Run
```
python start.py
```
## Reference
[video_summarize](https://github.com/StartHua/video_summarize/tree/main)
