import os 
import threading
import gradio as gr
import concurrent.futures
import json
import time
from datetime import datetime

# 导入处理器模块
try:
    from src.image_processor import process_image
    from src.text_processor import process_text
    from src.video_processor import process_video
except ImportError as e:
    print(f"警告: 某些处理器模块未找到: {e}")

# 全局变量
stop_event = threading.Event()
processing_status = {"is_processing": False, "current_file": "", "progress": 0}

def process_files_concurrently(source_folder):
    """并发处理文件的主要函数"""
    global stop_event, processing_status
    
    if not source_folder or not os.path.exists(source_folder):
        return "❌ 错误: 请选择有效的文件夹路径"
    
    messages = []
    text_suffixes = ('.txt', '.docx', '.xls', '.xlsx', '.pdf', '.md')
    video_suffixes = ('.mp4', '.mov', '.avi', '.flv', '.mkv')
    image_suffixes = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heif', '.heic', '.svg')
    file_paths = []
    max_workers = 5

    # 重置停止事件
    stop_event.clear()
    processing_status["is_processing"] = True
    
    messages.append(f"🚀 开始扫描文件夹: {source_folder}")
    
    # 扫描文件
    for root, dirs, files in os.walk(source_folder):
        dirs[:] = [d for d in dirs if d != '.airenametmp']
        for filename in files:
            if filename.lower().endswith(text_suffixes + video_suffixes + image_suffixes):
                file_path = os.path.join(root, filename)
                file_paths.append(file_path)

    if not file_paths:
        processing_status["is_processing"] = False
        return "⚠️ 未找到支持的文件类型"
    
    messages.append(f"📁 找到 {len(file_paths)} 个文件，使用 {max_workers} 个线程处理")
    
    # 处理文件
    processed_count = 0
    success_count = 0
    error_count = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for file_path in file_paths:
            if stop_event.is_set():
                break
                
            if file_path.lower().endswith(text_suffixes):
                future = executor.submit(process_text, file_path)
            elif file_path.lower().endswith(video_suffixes):
                future = executor.submit(process_video, file_path)
            elif file_path.lower().endswith(image_suffixes):
                future = executor.submit(process_image, file_path)
            else:
                continue
            futures.append((future, file_path))
        
        for future, file_path in futures:
            if stop_event.is_set():
                messages.append("⏹️ 处理已停止")
                break
                
            processed_count += 1
            
            try:
                result = future.result()
                success_count += 1
                messages.append(f"✅ 处理成功: {os.path.basename(file_path)}")
            except Exception as exc:
                error_count += 1
                messages.append(f"❌ 处理失败: {os.path.basename(file_path)} - {str(exc)}")
    
    processing_status["is_processing"] = False
    messages.append(f"\n🎉 处理完成! 成功: {success_count}, 失败: {error_count}, 总计: {processed_count}")
    
    return "\n".join(messages)

def stop_processing():
    """停止处理"""
    global stop_event
    stop_event.set()
    return "⏹️ 正在停止处理..."

def save_config(base_url, model, perplexity, access_token=None):
    """保存配置"""
    try:
        config = {
            "Base_url": base_url,
            "Model": model,
            "Perplexity": perplexity,
            "Access_token": access_token or ""
        }
        
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return "✅ 配置保存成功!"
    except Exception as e:
        return f"❌ 配置保存失败: {str(e)}"

def load_config():
    """加载配置"""
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            return (
                config.get("Base_url", ""),
                config.get("Model", "llama2"),
                config.get("Perplexity", 0.7),
                config.get("Access_token", "")
            )
    except Exception as e:
        print(f"加载配置失败: {e}")
    
    return ("", "llama2", 0.7, "")

def get_supported_formats():
    """获取支持的文件格式"""
    return """
    📄 **文档格式**: .txt, .docx, .xls, .xlsx, .pdf, .md
    🎬 **视频格式**: .mp4, .mov, .avi, .flv, .mkv  
    🖼️ **图片格式**: .jpg, .jpeg, .png, .gif, .bmp, .tiff, .webp, .heif, .heic, .svg
    """

# 自定义CSS样式
custom_css = """
/* 主容器样式 */
.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
}

/* 标题样式 */
.title {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.5em !important;
    font-weight: bold !important;
    text-align: center !important;
    margin-bottom: 20px !important;
}

/* 标签页样式 */
.tab-nav {
    background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%) !important;
    border-radius: 10px !important;
    padding: 5px !important;
}

/* 按钮样式 */
.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    border-radius: 25px !important;
    color: white !important;
    font-weight: bold !important;
    padding: 12px 30px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
}

.btn-primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4) !important;
}

.btn-danger {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%) !important;
    border: none !important;
    border-radius: 25px !important;
    color: white !important;
    font-weight: bold !important;
    padding: 12px 30px !important;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3) !important;
}

.btn-danger:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 25px rgba(255, 107, 107, 0.4) !important;
}

/* 输入框样式 */
.input-box {
    border-radius: 15px !important;
    border: 2px solid #e0e0e0 !important;
    transition: all 0.3s ease !important;
    background: #fafafa !important;
}

.input-box:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    background: white !important;
}

/* 卡片样式 */
.card {
    background: white !important;
    border-radius: 20px !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
    padding: 25px !important;
    margin: 15px 0 !important;
    border: 1px solid #f0f0f0 !important;
}

/* 进度条样式 */
.progress-bar {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
    border-radius: 10px !important;
}

/* 状态指示器 */
.status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
}

.status-processing {
    background: #ffd93d;
    animation: pulse 1.5s infinite;
}

.status-ready {
    background: #6bcf7f;
}

.status-error {
    background: #ff6b6b;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

/* 响应式设计 */
@media (max-width: 768px) {
    .gradio-container {
        padding: 10px !important;
    }
    
    .title {
        font-size: 2em !important;
    }
}

/* 美化滚动条 */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}
"""

def create_interface():
    """创建主界面"""
    
    # 加载配置
    base_url, model, perplexity, access_token = load_config()
    
    with gr.Blocks(
        css=custom_css,
        title="AI智能文件重命名工具",
        theme=gr.themes.Soft()
    ) as demo:
        
        # 主标题
        gr.HTML("""
        <div class="title">
            🤖 AI智能文件重命名工具
        </div>
        <div style="text-align: center; color: #666; margin-bottom: 30px; font-size: 1.2em;">
            基于大语言模型的智能文件重命名解决方案
        </div>
        """)
        
        # 状态指示器
        with gr.Row():
            status_indicator = gr.HTML("""
            <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 15px; color: white; font-weight: bold;">
                <span class="status-indicator status-ready"></span>
                <span>系统就绪 - 准备处理文件</span>
            </div>
            """)
        
        # 主要标签页
        with gr.Tabs():
            
            # 文件处理标签页
            with gr.Tab("📁 文件处理", elem_classes="card"):
                gr.Markdown("### 🚀 开始处理文件")
                
                with gr.Row():
                    with gr.Column(scale=3):
                        folder_input = gr.Textbox(
                            label="📂 选择文件夹路径",
                            placeholder="请输入要处理的文件夹路径...",
                            elem_classes="input-box"
                        )
                    with gr.Column(scale=1):
                        folder_button = gr.Button("📁 浏览文件夹", elem_classes="btn-primary")
                
                with gr.Row():
                    with gr.Column():
                        start_button = gr.Button("▶️ 开始处理", variant="primary", elem_classes="btn-primary")
                    with gr.Column():
                        stop_button = gr.Button("⏹️ 停止处理", variant="stop", elem_classes="btn-danger")
                
                # 日志输出
                log_output = gr.Textbox(
                    label="📋 处理日志",
                    lines=15,
                    interactive=False,
                    elem_classes="input-box"
                )
                
                # 支持的文件格式说明
                with gr.Accordion("📋 支持的文件格式", open=False):
                    gr.Markdown(get_supported_formats())
            
            # 配置标签页
            with gr.Tab("⚙️ 系统配置", elem_classes="card"):
                gr.Markdown("### 🔧 AI模型配置")
                
                with gr.Row():
                    with gr.Column():
                        base_url_input = gr.Textbox(
                            label="🌐 API基础URL",
                            value=base_url,
                            placeholder="例如: http://localhost:11434/api/generate",
                            elem_classes="input-box"
                        )
                        
                        model_dropdown = gr.Dropdown(
                            choices=["llama2", "llama3", "qwen", "chatglm", "custom"],
                            value=model,
                            label="🤖 选择模型",
                            elem_classes="input-box"
                        )
                        
                        perplexity_slider = gr.Slider(
                            minimum=0.1,
                            maximum=2.0,
                            step=0.1,
                            value=perplexity,
                            label="🎯 创造性参数 (Perplexity)",
                            elem_classes="input-box"
                        )
                        
                        access_token_input = gr.Textbox(
                            label="🔑 访问令牌 (可选)",
                            value=access_token,
                            type="password",
                            placeholder="如果需要的话，请输入访问令牌",
                            elem_classes="input-box"
                        )
                
                with gr.Row():
                    save_config_button = gr.Button("💾 保存配置", elem_classes="btn-primary")
                    reset_config_button = gr.Button("🔄 重置配置", elem_classes="btn-danger")
                
                config_status = gr.Textbox(
                    label="📊 配置状态",
                    interactive=False,
                    elem_classes="input-box"
                )
            
            # 关于标签页
            with gr.Tab("ℹ️ 关于", elem_classes="card"):
                gr.Markdown("""
                ### 🎯 项目介绍
                
                这是一个基于AI大模型的智能文件重命名工具，能够根据文件内容自动生成有意义的文件名。
                
                ### ✨ 主要特性
                - 🤖 支持多种AI模型 (Ollama, OpenAI等)
                - 📄 支持多种文件格式 (文档、图片、视频)
                - ⚡ 多线程并发处理
                - 🎨 现代化Web界面
                - 📊 实时处理进度显示
                
                ### 🛠️ 技术栈
                - **后端**: Python + Gradio
                - **AI模型**: Ollama/OpenAI + Whisper + mT5
                - **文档处理**: PyPDF2, python-docx, pandas
                - **视频处理**: moviepy, ffmpeg
                - **图像处理**: PIL/Pillow
                
                ### 📞 联系方式
                如有问题或建议，请通过GitHub Issues联系我们。
                """)
        
        # 事件绑定
        start_button.click(
            fn=process_files_concurrently,
            inputs=[folder_input],
            outputs=[log_output]
        )
        
        stop_button.click(
            fn=stop_processing,
            outputs=[log_output]
        )
        
        save_config_button.click(
            fn=save_config,
            inputs=[base_url_input, model_dropdown, perplexity_slider, access_token_input],
            outputs=[config_status]
        )
        
        reset_config_button.click(
            fn=lambda: ("", "llama2", 0.7, ""),
            outputs=[base_url_input, model_dropdown, perplexity_slider, access_token_input]
        )
    
    return demo

if __name__ == "__main__":
    # 创建并启动界面
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
