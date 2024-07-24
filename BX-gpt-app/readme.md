# BX-gpt application

## 1. Abstract

### 1.0. idea
- CBP Certi 예상문제/검색 App
- llm 추론에 있어 cost지불하지 않고 사용할 수 있도록 로컬 모델 파인튜닝/vectordb RAG시스템 구축
- aws 컴퓨팅 자원에 대한 비용만 지불

### 1.1. Service1: RAG
- mongodb VectorSearch: CBP Certi 문서 chunking/embedding 후 질문에 대해 유사도검색을 거쳐 llm 답변 생성/근거제시
- embedding model: `jhgan/ko-sbert-sts`, 768차원 벡터 추출
- inference model: `bartowski/gemma-2-9b-it-GGUF`, 양자화 로드해 경량화

### 1.2. Service2: instruction-tuning
- llm 파인튜닝: CBP Certi 문서 data로 질의응답 dataset 생성해 학습
- 1 epoch(5,100 data), 약 80분 소요
- LoRA 적용
- base model: `beomi/gemma-ko-2b`, 마찬가지로 16비트 양자화 적용 

### 1.3. Service3: 예상문제
- Q/A generation: CBP Certi 문서 청킹 데이터로부터 openai api를 통해 예상문제 데이터 생성
- 무작위 display

### 1.4. etc
- CBP Certi/01-제품소개, 11-아키텍처, 12-공통, 21-베이스, 22-상품, 23-액터, 24-계약, 25-정산 파트의 마크다운 문서 기반
- 모델 추론시 API호출로 cost가 발생하지 않도록 로컬 llm을 설치/파인튜닝
- instruction-tuning에 필요한 dataset을 만들기 위해 openai api 사용(약 5달러 소모)

### 1.5. 환경
- AWS ec2 instance: g4dn.xlarge 모델(T4 GPU / vCPU 4 / 메모리 16GiB / 0.647USD
- docker: gradio 웹서버 컨테이너, llama.cpp 추론서버 컨테이너

## 2. 어플리케이션 구현 기술

### 2.1. llama.cpp
- C++로 작성된 오픈소스 소프트웨어 라이브러리, LLM 추론 수행
- CUDA와 같은 하드웨어 의존적인 추론 라이브러리와 달리 의존성이 적음
- `사전 양자화`를 통해 LLM을 효율적으로 운용 가능하며 CPU에서도 실행 가능
- GGUF 포맷으로 경량화해 LLM을 로드하고, cli 또는 docker container로 HTTP서버를 띄워 `REST API call`

### 2.2. instruction-tuning
- LLM이 user의 의도와 다른 답변을 주는 문제를 해결하기 위한 방법론
- `원하는 작업과 목표` 명시적 학습
- 타겟 타스크에 대한 instruction-output pair 데이터셋
- `Zero-shot` 즉 질문만으로 답변 도출하는 것이 목적

### 2.3. LoRA(Low-Rank Adaption)
- 모든 weight를 파인튜닝하는 대신, `커다란 행렬을 근사화하는 작은 행렬 두 개`를 파인튜닝
- 파인튜닝된 `어댑터`를 pretrain weight에 merge  

### 2.4. RAG
- LLM이 응답을 생성하기 전 외부의 신뢰할 수 있는 지식베이스를 참조
- Semantic Indexing: raw data에서 `원본데이터 추출 및 정제`(해당 app은 CBP certi pdf -> text) << 구현하지 못함
- Chunking: LLM 처리 최적화를 위해 문서의 `텍스트 분할`
- Embedding: 분할된 텍스트 `벡터로 인코딩`
- Vector Search: 임베딩 벡터공간에서 `query:사용자 질의`에 대한 `코사인 유사도 검색`(mongodb의 index)

### 2.5. API
- openai api 사용
- 청킹된 `CBP Certi` 문서를 프롬프트로 요청
- 아래의 프롬프트 사용
```python
"""
document를 참고해 question과 answer 쌍을 생성하세요.
question은 document의 내용에 대해 물어보는 내용입니다.
answer은 question에 대해 document를 기반으로 답변하는 내용입니다.
question과 answer 쌍을 10개 생성하세요.

요구사항은 다음과 같습니다:
1. 문제의 다양성을 위해 question은 비슷한 단어로 반복하지 않습니다.
2. answer은 최대한 간결한 내용으로 작성되어야 합니다.
3. question은 document에 대해 물어보는 내용이며, 100단어 정도로 구성해주세요.
4. answer은 document를 기반으로 자세한 내용이 포함되도록 제공되어야하지만 100단어 정도로 구성해주세요.
5. 출력 형식은 JSON포맷을 따라야 하며, Indentation은 없도록 출력하세요.

출력 형식은 아래 포맷을 참조하세요:
{"question": "컴퓨터의 구성 요소는 어떻게 되어 있나요??", "answer": "CPU, 주기억장치, 보조기억장치 등으로 이루어져 있습니다."}
{"question": "Java와 Python의 차이는 무엇인가요?", "answer": "컴파일 언어와 인터프리터 언어의 차이가 있는데요. 우선..."}
"""
```

### 2.6. mongoDB
- vector Database로 활용
- Atlas search를 통해 index config, 유사도검색

## 3. Architecture

### 3.1. App
![image](https://github.com/user-attachments/assets/5a9855e2-b507-4ae5-9fa6-62646ca6441e)

#### 3.1.1. docker container1: gradio web server
- 7870포트로 개방된 gradio web server로 User 접속 및 질의
- 예상문제 set 확인 가능 

#### 3.1.2. docker container2: RAG
- llama.cpp 구동
- User의 query는 임베딩되어 mongoDB에서 유사도검색을 거친 관련 있는 문서와 함께 prompt로 포맷팅
- gemma-2-9b-it 모델 추론

#### 3.1.3. docker container2: IT(instruction-tuning)
- llama.cpp 구동
- User의 query는 모델에 맞게 prompt로 포맷팅
- gemma-ko-2b 모델 추론 

### 3.2. model/data
![image](https://github.com/user-attachments/assets/62881e44-4591-4bc6-a07f-d7499d5a9a50)

#### 3.2.1. preprocess.ipynb
- CBP Certi 마크다운 문서 전처리/청킹
- api를 통해 instruction dataset 생성

#### 3.2.2. embed.ipynb
- 청킹된 문서를 벡터로 임베딩
- mongoDB 적재

#### 3.2.3. train.ipynb
- 모델 파인튜닝

#### 3.2.4. gradio-app.py
- gradio 웹서버 구동 

## 4. Review

- CBP certi PDF파일 내부의 텍스트를 의미론적으로 나누는 것이 꽤 어려웠습니다. 뉴스 기사처럼 텍스트가 쭉 있는게 아니어서 여러 시행착오 했습니다.
- Semantic을 반영한 chunking을 많이 시도했는데, CBP certi 특성상 문서가 아래 사진과 같이 문단으로 나누어져 있으므로, 그것을 기준으로 chunking한 결과가 가장 좋았습니다.
<img width="383" alt="image" src="https://github.com/Ahnkyuwon504/AI-modeling/assets/81452902/2542065c-fb6a-49a9-97b1-14973c0fb239">

- GPU 1대로는 빠른 추론속도를 기대하기 어려웠습니다.
- 학습을 colab에서 진행한 관계로 dataset의 볼륨이 적었고, 1 epoch만 가능했습니다.
- llama.cpp 을 통해 모델 로딩/추론서버 구축에 있어 수월했습니다.
- AWS 인스턴스 대여비용이 많이 나왔습니다. ㅜㅜ


## doc
---

### Data
- BwG 사내문서 공유사이트: 비공개

### Embedding/Searching
- Semantic Chunking: https://github.com/Filimoa/open-parse/blob/main/src/cookbooks/semantic_processing.ipynb
- Vector Search: https://www.mongodb.com/ko-kr

### DB
- mongoDB: https://www.mongodb.com/ko-kr

### Model
- embedding model: https://huggingface.co/jhgan/ko-sbert-sts
- base model(instruction tuning): https://huggingface.co/beomi/gemma-ko-2b
- base model(RAG) : https://huggingface.co/bartowski/gemma-2-9b-it-GGUF

