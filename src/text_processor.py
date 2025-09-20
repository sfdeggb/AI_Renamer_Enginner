import os
import re
from collections import Counter
import concurrent.futures
import logging

logger = logging.getLogger(__name__)

# 导入AI重命名器
try:
    import sys 
    sys.path.append(".")
    from Agent.renamer import RenamerAgent
    AI_RENAMER_AVAILABLE = True
except ImportError:
    AI_RENAMER_AVAILABLE = False

# 导入处理各种格式所需的库
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

def extract_text_from_file(file_path):
    """从各种格式的文件中提取文本内容"""
    file_extension = os.path.splitext(file_path)[1].lower()
    content = ""
    
    try:
        if file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        
        elif file_extension == '.md':
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        
        elif file_extension == '.pdf' and PDF_AVAILABLE:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
        
        elif file_extension == '.docx' and DOCX_AVAILABLE:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
        
        elif file_extension in ['.xls', '.xlsx'] and PANDAS_AVAILABLE:
            # 读取Excel文件的所有工作表
            excel_file = pd.ExcelFile(file_path)
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                # 将DataFrame转换为文本
                content += f"工作表: {sheet_name}\n"
                content += df.to_string() + "\n\n"
        
        else:
            # 对于不支持或缺少依赖的格式，返回基本信息
            content = f"文件: {os.path.basename(file_path)} (格式: {file_extension})"
    
    except Exception as e:
        content = f"文件: {os.path.basename(file_path)} (读取错误: {str(e)})"
    
    return content

def generate_smart_filename(content, original_filename):
    """基于文本内容生成智能文件名"""
    if not content or len(content.strip()) < 10:
        return original_filename
    
    # 清理内容，移除特殊字符和多余空白
    clean_content = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', content)
    clean_content = re.sub(r'\s+', ' ', clean_content).strip()
    
    # 提取关键词
    words = clean_content.split()
    if len(words) < 3:
        return original_filename
    
    # 统计词频，选择最重要的词
    word_count = Counter(words)
    # 过滤掉太短的词和常见停用词
    stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
    
    # 选择最重要的3-5个词
    important_words = []
    for word, count in word_count.most_common(10):
        if len(word) > 1 and word.lower() not in stop_words:
            important_words.append(word)
            if len(important_words) >= 5:
                break
    
    if not important_words:
        return original_filename
    
    # 生成新文件名
    base_name = '_'.join(important_words[:3])  # 最多使用3个词
    # 限制文件名长度
    if len(base_name) > 50:
        base_name = base_name[:50]
    
    # 获取原文件扩展名
    file_extension = os.path.splitext(original_filename)[1]
    
    # 生成最终文件名
    new_filename = f"{base_name}{file_extension}"
    
    # 确保文件名不包含非法字符
    new_filename = re.sub(r'[<>:"/\\|?*]', '_', new_filename)
    
    return new_filename

def rename_file_with_content(file_path, new_filename):
    """重命名文件"""
    try:
        directory = os.path.dirname(file_path)
        new_file_path = os.path.join(directory, new_filename)
        
        # 如果新文件名已存在，添加数字后缀
        counter = 1
        original_new_path = new_file_path
        while os.path.exists(new_file_path):
            name, ext = os.path.splitext(original_new_path)
            new_file_path = f"{name}_{counter}{ext}"
            counter += 1
        
        os.rename(file_path, new_file_path)
        return new_file_path
    except Exception as e:
        raise Exception(f"重命名失败: {str(e)}")

def process_text(file_path, config=None, output_text_signal=None, stop_event=None, success_counter=None, failure_counter=None, num_counter=None, active_counter=None):
    """处理文本文件并基于内容重命名"""
    try:
        # 提取文本内容
        content = extract_text_from_file(file_path)
        logger.info(f"提取文本内容长度: {len(content)}")
        
        if not content or len(content.strip()) < 10:
            result = f"文件内容过少，跳过重命名: {os.path.basename(file_path)}"
            if output_text_signal:
                output_text_signal.emit(result)
            return result
        
        original_filename = os.path.basename(file_path)
        
        # 优先使用AI重命名，如果不可用则使用传统方法
        if AI_RENAMER_AVAILABLE and config:
            try:
                # 使用AI重命名
                ai_renamer = RenamerAgent(config_path=config.get('config_path', 'config.json'))
                new_filename = ai_renamer.renamer(content, original_filename)
                logger.info(f"AI重命名结果: {new_filename}")
            except Exception as e:
                logger.warning(f"AI重命名失败，使用传统方法: {str(e)}")
                # 回退到传统方法
                new_filename = generate_smart_filename(content, original_filename)
        else:
            # 使用传统方法
            new_filename = generate_smart_filename(content, original_filename)
        
        # 如果新文件名与原文件名相同，跳过重命名
        if new_filename == original_filename:
            result = f"文件名已合适，无需重命名: {original_filename}"
            if output_text_signal:
                output_text_signal.emit(result)
            return result
        
        # 执行重命名
        new_file_path = rename_file_with_content(file_path, new_filename)
        
        # 统计信息
        word_count = len(content.split()) if content else 0
        method = "AI重命名" if AI_RENAMER_AVAILABLE and config else "传统重命名"
        result = f"重命名成功: {original_filename} -> {new_filename} (字数: {word_count}, 方法: {method})"
        
        if output_text_signal:
            output_text_signal.emit(result)
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
    test_path = "./test/doc/1.txt"
    config = {
        'config_path': 'config/config.json'
    }
    if os.path.exists(test_path):
        result = process_text(test_path, config)
        print(result)
    else:
        print("测试文件不存在")
