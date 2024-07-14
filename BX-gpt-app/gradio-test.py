import gradio as gr

def greet(name):
    return "우리 쭈 안뇽! "

demo = gr.Interface(fn=greet, inputs="text", outputs="text")

# test
demo.launch(server_name="0.0.0.0")
