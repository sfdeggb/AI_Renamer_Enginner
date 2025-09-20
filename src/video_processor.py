import os
from collections import Counter
import concurrent.futures

def process_video(file_path, config=None, output_text_signal=None, stop_event=None, success_counter=None, failure_counter=None, num_counter=None, active_counter=None):
    """处理视频文件"""
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension in ['.mp4', '.mov', '.avi', '.flv', '.mkv']:
            # 获取文件基本信息
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            result = f"视频文件处理完成，大小: {file_size_mb:.2f}MB"
            
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

if __name__ == "__main__":
    # 测试代码
    test_path = "test.mp4"
    if os.path.exists(test_path):
        result = process_video(test_path)
        print(result)
    else:
        print("测试视频不存在")
