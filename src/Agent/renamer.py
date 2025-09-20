import os
import json

from openai import OpenAI


class RenamerAgent:
    def __init__(self, config_path="config/config.json"):
        # 读取配置文件
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        self.base_url = config.get("Base_url")
        self.api_key = config.get("Access_token")
        self.model = config.get("Model", "Qwen/Qwen3-0.6B")
        # 兼容大小写
        if self.model.lower() == "qwen":
            self.model = "Qwen/Qwen3-0.6B"
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    def generate_summary(self, content, max_length=500):
        """
        生成文档摘要
        输入：content（文档内容字符串），max_length（摘要最大长度）
        输出：摘要字符串
        """
        # 构造摘要prompt
        prompt = (
            f"请为以下文档生成一个简洁的摘要（不超过{max_length}字），重点突出文档的主要内容和主题：\n\n"
            f"{content}\n\n"
            "摘要："
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个专业的文档摘要助手。"},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )
        
        # 获取返回内容 - 处理流式响应
        result = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                result += chunk.choices[0].delta.content
        
        return result.strip()

    def renamer(self, content, original_filename=None, use_summary=True, max_content_length=1000):
        """
        输入：content（文档内容字符串），original_filename（可选，原始文件名，便于保留扩展名）
              use_summary（是否使用摘要），max_content_length（内容最大长度阈值）
        输出：建议的新文件名（字符串）
        """
        # 获取扩展名
        ext = ""
        if original_filename:
            _, ext = os.path.splitext(original_filename)
        
        # 判断是否需要生成摘要
        if use_summary and len(content) > max_content_length:
            # 生成摘要
            summary = self.generate_summary(content, max_length=300)
            content_for_renaming = summary
        else:
            content_for_renaming = content
        
        # 构造prompt
        prompt = (
            "请根据以下文档内容，生成一个简洁、准确、能体现文档主题的中文文件名（不超过10字），不要包含特殊字符，不要加扩展名，只返回文件名本身：\n\n"
            f"{content_for_renaming}\n\n"
            "文件名："
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个智能文件重命名助手。"},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )
        # 获取返回内容 - 处理流式响应
        result = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                result += chunk.choices[0].delta.content
        
        result = result.strip()
        # print('result:', result)
        # 去除可能的扩展名和特殊字符
        result = result.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")
        # 只保留前20个字符
        result = result[:20]
        # 拼接扩展名
        if ext:
            result = result + ext
        return result

# 示例用法
if __name__ == "__main__":
    agent = RenamerAgent()
    # 假设content是你读取到的文档内容
    content = "本报告详细分析了2024年中国人工智能行业的发展趋势与市场前景。"
    original_filename = "report.txt"
    new_filename = agent.renamer(content, original_filename)
    print("建议的新文件名：", new_filename)