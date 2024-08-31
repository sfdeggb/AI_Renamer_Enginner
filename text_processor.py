import os
import docx
import pandas as pd
import PyPDF2
import markdown
from collections import Counter
import concurrent.futures

import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM 

from utilts import Counter, call_llm_from_ollama

def extract_abstract(article_text):
    """提取文本摘要"""
    WHITESPACE_HANDLER = lambda k: re.sub('\s+', ' ', re.sub('\n+', ' ', k.strip()))

    #article_text = """Videos that say approved vaccines are dangerous and cause autism, cancer or infertility are among those that will be taken down, the company said.  The policy includes the termination of accounts of anti-vaccine influencers.  Tech giants have been criticised for not doing more to counter false health information on their sites.  In July, US President Joe Biden said social media platforms were largely responsible for people's scepticism in getting vaccinated by spreading misinformation, and appealed for them to address the issue.  YouTube, which is owned by Google, said 130,000 videos were removed from its platform since last year, when it implemented a ban on content spreading misinformation about Covid vaccines.  In a blog post, the company said it had seen false claims about Covid jabs "spill over into misinformation about vaccines in general". The new policy covers long-approved vaccines, such as those against measles or hepatitis B.  "We're expanding our medical misinformation policies on YouTube with new guidelines on currently administered vaccines that are approved and confirmed to be safe and effective by local health authorities and the WHO," the post said, referring to the World Health Organization."""

    model_name = "csebuetnlp/mT5_multilingual_XLSum"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    input_ids = tokenizer(
        [WHITESPACE_HANDLER(article_text)],
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=512
    )["input_ids"]

    output_ids = model.generate(
        input_ids=input_ids,
        max_length=84,
        no_repeat_ngram_size=2,
        num_beams=4
    )[0]

    summary = tokenizer.decode(
        output_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False
    )

    print(summary)


def process_text(file_path, config, output_text_signal, stop_event, success_counter, failure_counter, num_counter, active_counter):
    """处理文本文件
    这里读取的文件类型包括：.txt, .docx, .xls, .xlsx, .pdf, .md
    内容可能会存在过长的问题，例如：.pdf文件
    """
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        content = ""
        
        if file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        
        elif file_extension == '.docx':
            doc = docx.Document(file_path)
            content = "\n".join([para.text for para in doc.paragraphs])
        
        elif file_extension in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path)
            content = df.to_string()
        
        elif file_extension == '.pdf':
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfFileReader(file)
                content = "\n".join([reader.getPage(i).extract_text() for i in range(reader.numPages)])
        
        elif file_extension == '.md':
            with open(file_path, 'r', encoding='utf-8') as file:
                content = markdown.markdown(file.read())
        
        # 处理内容（例如，统计字数）
        #进行长文本信息摘要的提取
        word_count = len(content.split())
        if word_count > 2048:#字数大于2048时进行摘要提取,防止大模型token数量超限
            content = extract_abstract(content)
        output_text_signal.emit(f"{file_path} 处理成功，字数: {word_count}")
        success_counter.update([file_path]) 
    except Exception as e:
        output_text_signal.emit(f"{file_path} 处理失败: {str(e)}")
        failure_counter.update([file_path])
    
    finally:
        num_counter.update([file_path])
        active_counter.update([-1])
    #调佣大模型API函数
    call_llm_from_ollama(content, 
                         file_path, 
                         config, 
                         output_text_signal, 
                         stop_event, 
                         success_counter, 
                         failure_counter, 
                         num_counter, 
                         active_counter)
    
# 集成到现有的多线程处理框架中
def process_files_concurrently(config, output_text_signal, stop_event, active_counter):
    source_folder = config["Source_folder"]
    text_suffixes = ('.txt', '.docx', '.xls', '.xlsx', '.pdf', '.md')
    file_paths = []
    max_workers = 5

    for root, dirs, files in os.walk(source_folder):
        dirs[:] = [d for d in dirs if d != '.airenametmp']
        for filename in files:
            if filename.lower().endswith(text_suffixes):
                file_path = os.path.join(root, filename)
                file_paths.append(file_path)

    success_counter = Counter()
    failure_counter = Counter()
    num_counter = Counter()

    output_text_signal.emit(f"开始处理{len(file_paths)}个文件，线程:{max_workers}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_text_file, 
                                   file_path, 
                                   config,
                                   output_text_signal,
                                   stop_event, 
                                   success_counter,
                                   failure_counter, 
                                   num_counter,
                                   active_counter): file_path for file_path in file_paths}
        for future in concurrent.futures.as_completed(futures):
            if stop_event.is_set():
                break
            try:
                future.result()
            except Exception as exc:
                output_text_signal.emit(f'生成异常: {exc}')
    return len(file_paths), success_counter.value, failure_counter.value