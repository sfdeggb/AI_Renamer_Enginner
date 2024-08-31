# AiRename-Engnner

## Intervew🤖🤖🤖
Are there many files in your computer that you do not know what is because of the simple naming before, this tool combined with LLM can help you automatically name according to the content of your files, you no longer need to worry about the improper naming of files.</br>

![rename_floader](/demo/rename.jpg)
![config](/demo/config.jpg)

## 🚀Featuers
* Supports local ollama server model calls and online openai model calls
* Support to modify images (png,svg.jpg and other common formats), documents (txt,word,excel,pdf.md) and multimedia files
## 💪Requirment
* Nvidia CUDA 11.8 or newer(if your computer do not have nvidia GPU, you need setting the config file value device to CPU). 
* ffmpeg
*  GTK-3
* ollama
## 🔥Start
### 1. Install ffmpeg
On windows you can download the ffmpeg on `https://www.gyan.dev/ffmpeg/builds/`. It is a zip package that you can extract to any location on your system and then add it to the environment variables. If you still have questions about how to install ffmpeg, perhaps the following Bolg article can guide you.
> https://blog.csdn.net/Dneccc/article/details/138825228
### 2. Install GTK-3
> https://sourceforge.net/projects/gtk-win/
the following bolg you may need:
>https://blog.csdn.net/bz_xyz/article/details/104637487
### 3. Install the ollma
you can download and install ollama on `https://ollama.com/`
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
### 4.Run
```
python start.py
```
## 🔧 Reference
[video_summarize](https://github.com/StartHua/video_summarize/tree/main)


