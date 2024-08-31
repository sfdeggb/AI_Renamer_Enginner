import os
from moviepy.editor import VideoFileClip
from collections import Counter
import concurrent.futures
import argparse
import whisper

def extract_abstract_from_vedio(content):
    video_text = ""
    # Whisper模型
    WHISPER_MODEL = "csebuetnlp/mT5_multilingual_XLSum"#应该从配置文件中读取
    PROJECT_PATH = os.path.dirname(__file__)
    #UP_PROJECT_PATH = os.path.join(PROJECT_PATH, "video_summarize")
    MODE_PATH = os.path.join(PROJECT_PATH, "model")
    whisper_model = whisper.load_model(MODE_PATH + WHISPER_MODEL)
    
    return whisper_model.transcribe(content)["text"]  # 提取摘要    

def process_video(file_path, config, output_text_signal, stop_event, success_counter, failure_counter, num_counter, active_counter):
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension in ['.mp4', '.mov', '.avi', '.flv', '.mkv']:
            clip = VideoFileClip(file_path)
            try:
                extract_abstract_from_vedio(file_path)
            except Exception as e:
                raise ValueError(f"提取摘要失败: {str(e)}")
            duration = clip.duration  # 获取视频时长
            
            output_text_signal.emit(f"{file_path} 处理成功，时长: {duration} 秒")
            success_counter.update([file_path])
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")
        
    except Exception as e:
        output_text_signal.emit(f"{file_path} 处理失败: {str(e)}")
        failure_counter.update([file_path])
    
    finally:
        num_counter.update([file_path])
        active_counter.update([-1])

# 集成到现有的多线程处理框架中
def process_files_concurrently(config, output_text_signal, stop_event, active_counter):
    source_folder = config["Source_folder"]
    video_suffixes = ('.mp4', '.mov', '.avi', '.flv', '.mkv')
    file_paths = []
    max_workers = 5

    for root, dirs, files in os.walk(source_folder):
        dirs[:] = [d for d in dirs if d != '.airenametmp']
        for filename in files:
            if filename.lower().endswith(video_suffixes):
                file_path = os.path.join(root, filename)
                file_paths.append(file_path)

    success_counter = Counter()
    failure_counter = Counter()
    num_counter = Counter()

    output_text_signal.emit(f"开始处理{len(file_paths)}个视频文件，线程:{max_workers}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_video_file, file_path, config, output_text_signal, stop_event, success_counter, failure_counter, num_counter, active_counter): file_path for file_path in file_paths}
        for future in concurrent.futures.as_completed(futures):
            if stop_event.is_set():
                break
            try:
                future.result()
            except Exception as exc:
                output_text_signal.emit(f'生成异常: {exc}')
    return len(file_paths), success_counter.value, failure_counter.value

if __name__ =="__main__":
    PROJECT_PATH = os.path.dirname(__file__)
    #UP_PROJECT_PATH = os.path.join(PROJECT_PATH, "video_summarize")
    MODE_PATH = os.path.join(PROJECT_PATH, "model")
    print(MODE_PATH)