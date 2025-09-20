import os
from collections import Counter
import concurrent.futures

def process_text(file_path, config=None, output_text_signal=None, stop_event=None, success_counter=None, failure_counter=None, num_counter=None, active_counter=None):
    """处理文本文件"""
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        content = ""
        
        if file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        elif file_extension == '.md':
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        else:
            # 对于其他格式，暂时只获取文件信息
            content = f"文件: {os.path.basename(file_path)}"
        
        # 简单的处理逻辑
        word_count = len(content.split()) if content else 0
        result = f"文本文件处理完成，字数: {word_count}"
        
        if output_text_signal:
            output_text_signal.emit(f"{file_path} 处理成功: {result}")
        if success_counter:
            success_counter.update([file_path])
        
        return result
        
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
    test_path = "test.txt"
    if os.path.exists(test_path):
        result = process_text(test_path)
        print(result)
    else:
        print("测试文件不存在")
