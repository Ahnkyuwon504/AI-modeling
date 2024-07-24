from sentence_transformers import SentenceTransformer
import pymongo
import os
import gradio as gr
import requests
import json

embedding_model = SentenceTransformer("thenlper/gte-large")

"""get embedding vector"""
def get_embedding(text: str) -> list[float]:
    if not text.strip():
      print("empty")
      return []
    return embedding_model.encode(text).tolist()

"""Establish connection to the MongoDB."""
def get_mongo_client_db_collection(mongo_uri):
    try:
        client = pymongo.MongoClient(mongo_uri)
        db = client["spider504"]
        collection = db["240703_movie_collection"]
        print("Connection to MongoDB successful")
        return collection
    except pymongo.errors.ConnectionFailure as e:
        print(f"Connection failed: {e}")
        return None

"""Vector Search"""
def vector_search(user_query, collection):
    query_embedding = get_embedding(user_query)

    if query_embedding is None:
        return "Invalid query or embedding generation failed."

    # Define the vector search pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 50,  # Number of candidate matches to consider
                "limit": 2,  # Return top 4 matches
            }
        },
        {
            "$project": {
                "_id": 0,  # Exclude the _id field
                "text": 1,
                "score": {"$meta": "vectorSearchScore"},  # Include the search score
            }
        },
    ]

    results = collection.aggregate(pipeline)

    return list(results)

"""get document"""
def get_search_result(query, collection):
    get_knowledge = vector_search(query, collection)

    search_result = ""
    for result in get_knowledge:
        search_result += f"text: {result.get('text', 'N/A')}\n"
    return search_result

"""get prompt"""
def get_retrieval_prompt(query, collection):
    source_information = get_search_result(query, collection)

    combined_information = (
    f"""
    Query: {query}

    당신은 친절한 가이드 입니다.
    아래의 Document를 참고해 Query에 답변하세요.
    문서의 내용으로 답변할 수 없다면 모른다고 말해주세요.
    질문은 다시 말할 필요 없으며, 답변만 말해주세요. 

    Document:
    {source_information}
    """
    )
    return combined_information

"""RAG"""
def llama_cpp_server_call_rag(query):

    collection = get_mongo_client_db_collection(os.environ.get('MONGO_URI'))
    prompt = get_retrieval_prompt(query, collection)

    url = "http://" + os.environ.get('PRIVATE_IP') + ":8080/completion"
    headers = {"Content-Type": "application/json"}
    data = {
        "prompt": prompt,
        "n_predict": 512
    }

    response = requests.post(url, headers=headers, json=data)
    content = response.json().get('content')

    return content

"""INSTRUCTION TUNING"""
def llama_cpp_server_call_it(query):
    formatted_query = f"### Instruction: {query}\n\n### Response:"
    url = "http://" + os.environ.get('PRIVATE_IP') + ":8081/completion"
    headers = {"Content-Type": "application/json"}
    data = {
        "prompt": formatted_query,
        "n_predict": 512
    }

    response = requests.post(url, headers=headers, json=data)
    content = response.json().get('content')

    return content

"""RAG+INSTRUCTION TUNING"""
def llama_cpp_server_call_it_rag(query):

    collection = get_mongo_client_db_collection(os.environ.get('MONGO_URI'))
    prompt = get_retrieval_prompt(query, collection)
    formatted_prompt = f"### Instruction: {prompt}\n\n### Response:"

    url = "http://" + os.environ.get('PRIVATE_IP') + ":8081/completion"
    headers = {"Content-Type": "application/json"}
    data = {
        "prompt": prompt,
        "n_predict": 512
    }

    response = requests.post(url, headers=headers, json=data)
    content = response.json().get('content')

    return content

demo3 = gr.Interface(fn=llama_cpp_server_call_rag, inputs="text", outputs="text")
demo1 = gr.Interface(fn=llama_cpp_server_call_it, inputs="text", outputs="text")
demo2 = gr.Interface(fn=llama_cpp_server_call_it_rag, inputs="text", outputs="text")

def get_next_question(index):
    next_index = (index + 1) % len(questions_answers)
    next_question = questions_answers[next_index]["question"]
    next_answer = questions_answers[next_index]["answer"]
    return next_question, next_answer, next_index

json_file_path = "/home/ec2-user/models/CBP-Certi-instruction-data-preprocessed.jsonl"
questions_answers = []

with open(json_file_path, 'r', encoding='utf-8') as file:
    for line in file:
        json_line = json.loads(line)
        questions_answers.append({
            "question": json_line["question"],
            "answer": json_line["answer"]
        })

# 인터페이스를 구성
with gr.Blocks() as demo:
    gr.Markdown("# CBP Certi 예상문제 Pairs(5,100 rows)")
    question_index = gr.State(0)
    with gr.Column():
        question = gr.Markdown(f"**Question:** {questions_answers[0]['question']}")
        answer = gr.Markdown(f"**Answer:** {questions_answers[0]['answer']}", visible=False)

        with gr.Row():
            show_answer_btn = gr.Button("정답")
            next_question_btn = gr.Button("다음")

        def show_answer():
            return gr.update(visible=True)

        def next_question(index):
            next_q, next_a, next_index = get_next_question(index)
            return gr.update(value=f"**Question:** {next_q}"), gr.update(value=f"**Answer:** {next_a}", visible=False), next_index

        show_answer_btn.click(show_answer, [], [answer])
        next_question_btn.click(next_question, [question_index], [question, answer, question_index])
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("# CBP Certi 검색 LLM (16bit 양자화 beomi-gemma-ko-2b")
            with gr.Tabs():
                with gr.TabItem("FINE-TUNING"):
                    gr.Markdown("## CBP Certi Q/A 데이터셋 파인튜닝")
                    demo1.render()
                with gr.TabItem("FINE-TUNING+RAG"):
                    gr.Markdown("## CBP Certi Q/A 데이터셋 파인튜닝 + 마크다운 문서 유사도검색")
                    demo2.render()
                with gr.TabItem("RAG"):
                    gr.Markdown("## 마크다운 문서 유사도검색")
                    demo3.render()

demo.launch(server_name="0.0.0.0", server_port=7870)

