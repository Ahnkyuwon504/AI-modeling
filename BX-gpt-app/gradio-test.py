import gradio as gr
import requests

"""
def greet(name):
    return "hi gradio! "

demo = gr.Interface(fn=greet, inputs="text", outputs="text")

# test
demo.launch(server_name="0.0.0.0")
"""

def llama_cpp_server_call(name):
    url = "http://localhost:8080/completions"
    headers = {"Content-Type": "application/json"}
    prompt = f"Hello, I'm {name}. What is my name?"
    data = {
        "prompt": prompt,
        "max_tokens": 50
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

demo = gr.Interface(fn=llama_cpp_server_call, inputs="text", outputs="text")
demo.launch(server_name="0.0.0.0")
