from openai import OpenAI

client = OpenAI(
    base_url='https://ms-ens-dbcc6191-9fb0.api-inference.modelscope.cn/v1',
    api_key='ms-bfa018d4-ad57-4de5-a14e-0b17fc83b07a', # ModelScope Token
)

response = client.chat.completions.create(
    model='Qwen/Qwen3-0.6B', # ModelScope Model-Id
    messages=[
        {
            'role': 'system',
            'content': 'You are a helpful assistant.'
        },
        {
            'role': 'user',
            'content': '你好'
        }
    ],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content, end='', flush=True)