import base64
import re
import os
import io
from PIL import Image
import requests 
import json 
import threading 

class Counter:
    """ 计数器 : 用于多线程计数 """  
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            self.value += 1

    def decrement(self):
        with self.lock:
            self.value -= 1

    def get_value(self):
        with self.lock:
            return self.value


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')#对图像进行编码


def remove_punctuation_at_end(sentence):
    return re.sub(r'[。？！，、；：“”‘’《》（）【】『』「」\[\]\.,;:"\'?!(){}<>]+$', '', sentence)#去除句子末尾的标点符号


def compress_and_encode_image(image_path, quality=85, max_size=(1080, 1080)):
    """ 压缩和编码图像 """
    with Image.open(image_path) as img:
        img.thumbnail(max_size)
        if img.format == 'WEBP' or img.mode == 'RGBA':
            output_format = 'PNG'
            mime_type = 'image/png'
        else:
            output_format = img.format if img.format != 'JPEG' else 'JPEG'
            mime_type = f'image/{output_format.lower()}'

        img_bytes = io.BytesIO()
        img.save(img_bytes, format=output_format, quality=quality)
        img_bytes.seek(0)
        base64_encoded = base64.b64encode(img_bytes.read()).decode('utf-8')

    return base64_encoded, mime_type, output_format#返回编码后的图像，图像类型，图像格式

def call_llm_from_ollama(prompt,content,config,multimotai=False):
    """ 调用大模型API 
    """
    base_url = config["API_URL"]
    
    headers ={
       "Content-Type": "application/json" 
    }
    
    if multimotai:
        data = {
            "model": config["Model"],
            "prompt": prompt,
            "images": [content],
            "stream": False,
            "options": {
                "num_tokens": 300
            }
        }
    else:
        data = {
            "model": config["Model"],
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_tokens": 300
            }
        }
    print("请求URL:", base_url)
    print("请求头:", headers)
    print("请求数据:", json.dumps(data, indent=4))
    
    try:
        response = requests.post(base_url, headers=headers, json=data)
        response_data = response.json()
        if response_data["done"] == True:
            result  = response_data["response"]
            # 检查最后一个字符是否是')'或'）'
            if result[-1] not in [')', '）']:
                result = result[:-1]
            return result
        else:
            failure_counter.increment()#失败计数器加1
            num_counter.increment()
            output_text_signal.emit(f"API响应中缺少'choices'字段或'choices'为空: {response_data}")
    except requests.exceptions.RequestException as e:
        failure_counter.increment()
        num_counter.increment()
        output_text_signal.emit(f"HTTP请求失败: {e}")

    
        
        
    
    
    