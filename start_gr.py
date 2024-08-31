import os 
import threading
import gradio as gr
import concurrent.futures

from image_processor import process_image
from text_processor import process_text
from video_processor import process_video
import json


def process_files_concurrently(source_floder,progress =gr.Progress()):
    #source_folder = self.config["Source_folder"]
    messages = []
    source_folder = source_floder
    text_suffixes = ('.txt', '.docx', '.xls', '.xlsx', '.pdf', '.md')
    video_suffixes = ('.mp4', '.mov', '.avi', '.flv', '.mkv')
    image_suffixes = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heif', '.heic', '.svg')
    file_paths = []
    max_workers = 5

    progress(0, desc="Starting...")#进度条显示
    for root, dirs, files in os.walk(source_folder):
        dirs[:] = [d for d in dirs if d != '.airenametmp']
        for filename in files:
            if filename.lower().endswith(text_suffixes + video_suffixes+image_suffixes):
                file_path = os.path.join(root, filename)
                file_paths.append(file_path)

    #self.output_text_signal.emit(f"开始处理{len(file_paths)}个文件，线程:{max_workers}")
    messages.append(f"开始处理{len(file_paths)}个文件，线程:{max_workers}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for file_path in file_paths:
            if file_path.lower().endswith(text_suffixes):
                future = executor.submit(process_text, file_path)
            elif file_path.lower().endswith(video_suffixes):
                future = executor.submit(process_video, file_path)
            elif file_path.lower().endswith(image_suffixes):
                future = executor.submit(process_image, file_path)
            else:
                continue
            futures.append(future)
        for future in concurrent.futures.as_completed(futures):
            if self.stop_event:#停止事件 如何从grado中获取
                break
            try:
                future.result()
            except Exception as exc:
                #self.output_text_signal.emit(f'生成异常: {exc}')
                messages.append(f'生成异常: {exc}')

def save_config(self, base_url, model, perplexity, access_token=None):
    # 读取配置文件，进行修改，保存
    with open('config.json', 'r') as f:
        config = json.load(f)

    config["Base_url"] = base_url
    config["Model"] = model
    config["Perplexity"] = perplexity
    if access_token:
        config["Access_token"] = access_token
    with open('config.json', 'w') as f:
        json.dump(config, f)
    return "Save Success"

class Main_ui():
    def __init__(self):
        self.stop_event = threading.Event()
        self.initUI()
        self.start_processing
        self.save_confg()
        
    def bind_function(self):
        self.start_processing = process_files_concurrently
        
    def initUI(self):
        with gr.Tab("Process Folder"):#处理文件夹界面
            with gr.Row():
                self.folder_path = gr.Textbox(label="Folder Path")#输入文件夹路径
            with gr.Row():
                self.log_output = gr.Textbox(lines=10, label="Processing Log", interactive=False)#输出处理日志
            with gr.Row():
                self.submit_btn = gr.Button("Submit")#提交按钮
                self.quit_btn = gr.Button("abort")#退出按钮

        with gr.Tab("Configuration"):#配置界面
            with gr.Row():
                self.base_url = gr.Textbox(label="Base URL")
            with gr.Row():
                self.model = gr.Dropdown(["model_a", "model_b", "model_c"], label="Model")
            with gr.Row():
                self.perplexity = gr.Slider(minimum=0, maximum=1.0, step=0.1, label="Perplexity")
            with gr.Row():
                self.access_token = gr.Textbox(label="Access Token Optional")
            with gr.Row():
                self.save_btn = gr.Button("Save")#保存按钮
                self.reset_btn = gr.Button("Reset")#重置按钮

    
    def trigger_process_folder_submit(self):
        self.submit_btn.click(self.process_data, inputs=self.folder_path,
                              outputs=[self.log_output])
        self.quit_btn.click(self.stop_processing)

        def stop_processing(self):
            self.stop_event = True
    
    def trigger_config_save_submit(self):
        self.save_btn.click(save_config, 
        inputs=[self.base_url, 
                self.model, 
                self.perplexity, 
                self.access_token], 
        outputs=gr.Textbox(label="Save Status"))

if __name__ == "__main__":
    ui = Main_ui()
    with gr.Blocks() as demo:
        ui.initUI()
        ui.trigger_config_save_submit()
    demo.launch()
    

