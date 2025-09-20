import os
from collections import Counter
import concurrent.futures
from PIL import Image
import base64
import io

def process_image(file_path, config=None, output_text_signal=None, stop_event=None, success_counter=None, failure_counter=None, num_counter=None, active_counter=None):
    """处理图片文件"""
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heif', '.heic', '.svg']:
            # 获取图片信息
            with Image.open(file_path) as img:
                width, height = img.size
                format_name = img.format
                mode = img.mode
            
            # 这里可以添加AI分析图片内容的逻辑
            # 目前只是获取基本信息
            result = f"图片信息: {width}x{height}, 格式: {format_name}, 模式: {mode}"
            
            if output_text_signal:
                output_text_signal.emit(f"{file_path} 处理成功: {result}")
            if success_counter:
                success_counter.update([file_path])
            
            return result
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")
        
    except Exception as e:
        error_msg = f"{file_path} 处理失败: {str(e)}"
        if output_text_signal:
            output_text_signal.emit(error_msg)
        if failure_counter:
            failure_counter.update([file_path])
        return error_msg
    
    finally:
        if num_counter:
            num_counter.update([file_path])
        if active_counter:
            active_counter.update([-1])

# 集成到现有的多线程处理框架中
def process_files_concurrently(config, output_text_signal, stop_event, active_counter):
    source_folder = config["Source_folder"]
    image_suffixes = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heif', '.heic', '.svg')
    file_paths = []
    max_workers = 5

    for root, dirs, files in os.walk(source_folder):
        dirs[:] = [d for d in dirs if d != '.airenametmp']
        for filename in files:
            if filename.lower().endswith(image_suffixes):
                file_path = os.path.join(root, filename)
                file_paths.append(file_path)

    success_counter = Counter()
    failure_counter = Counter()
    num_counter = Counter()

    output_text_signal.emit(f"开始处理{len(file_paths)}个图片文件，线程:{max_workers}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_image, file_path, config, output_text_signal, stop_event, success_counter, failure_counter, num_counter, active_counter): file_path for file_path in file_paths}
        for future in concurrent.futures.as_completed(futures):
            if stop_event.is_set():
                break
            try:
                future.result()
            except Exception as exc:
                output_text_signal.emit(f'生成异常: {exc}')
    return len(file_paths), success_counter.value, failure_counter.value

if __name__ == "__main__":
    # 测试代码
    test_path = "test_image.jpg"
    if os.path.exists(test_path):
        result = process_image(test_path)
        print(result)
    else:
        print("测试图片不存在")
