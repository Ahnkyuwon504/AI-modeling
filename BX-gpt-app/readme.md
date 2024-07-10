# BX-gpt application

## Abstract

### idea
- llm 추론에 있어 cost지불하지 않고도 임직원이 사용할 수 있도록 로컬 모델 파인튜닝/vectordb 구축
- colab/T4 GPU 사용으로 학습과 추론에 있어 컴퓨팅자원이 제한되어 성능은 다소 떨어짐

### Service1. instruction-tuning
- llm 파인튜닝: CBP Certi 문서 data로 질의응답 dataset 생성해 학습에 사용

### Service2. RAG
- mongodb VectorSearch: CBP Certi 문서 chunking/embedding 후 질문에 대해 유사도검색을 거쳐 llm 답변 생성/근거제시

### Service3. 예상문제
- Q/A generation: white noise로부터 CBP Certi 문서 중 무작위로 추출해 q/a instruction 파인튜닝된 llm을 통해 예상문제/답변 생성

### etc
- CBP Certi/01-제품소개, 11-아키텍처, 12-공통, 21-베이스, 22-상품, 23-액터, 24-계약, 25-정산 파트의 마크다운 문서 기반
- 모델 추론시 API호출로 cost가 발생하지 않도록 로컬 llm을 설치/파인튜닝
- instruction-tuning에 필요한 dataset을 만들기 위해 api 사용(약 원)



## 어플리케이션 구현 기술

### instruction-tuning

### RAG
- Semantic Indexing: raw data에서 원본데이터 추출 및 정제(해당 app은 CBP certi pdf -> text) `유사한 의미노드` 기반 그룹화
- Chunking: LLM 처리 최적화를 위해 문서의 `텍스트 분할`
- Embedding: 분할된 텍스트를 `벡터로 인코딩`
- Vector Search: 임베딩 벡터공간에서 `query:사용자 질의`에 대한 `코사인 유사도 검색`(mongodb의 index)



## Architecture(App)



## Architecture(Infra) 



## Environment







## Review

- CBP certi PDF파일 내부의 텍스트를 의미론적으로 나누는 것이 꽤 어려웠습니다. 뉴스 기사처럼 텍스트가 쭉 있는게 아니어서 여러 시행착오 했습니다.
- Semantic을 반영한 chunking을 많이 시도했는데, CBP certi 특성상 문서가 아래 사진과 같이 문단으로 나누어져 있으므로, 그것을 기준으로 chunking한 결과가 가장 좋았습니다.
<img width="383" alt="image" src="https://github.com/Ahnkyuwon504/AI-modeling/assets/81452902/2542065c-fb6a-49a9-97b1-14973c0fb239">





## doc
---

### Data
- BwG 사내문서 공유사이트: https://pages.bwg.co.kr/ROOT/

### Embedding/Searching
- Raptor`Recursive Abstractive Processing for Tree-Organized Retrieval(2024)`: https://github.com/run-llama/llama_index/blob/main/llama-index-packs/llama-index-packs-raptor/examples/raptor.ipynb?fbclid=IwZXh0bgNhZW0CMTAAAR0RCkGhA8S9wpJSVyY8XSJuQG7qDeG6xA8MLs_bF2mRkqslty99Y5IP1Dk_aem_rGk9AfVWfB1QN2GAkNeKDQ
- Semantic Chunking: https://github.com/Filimoa/open-parse/blob/main/src/cookbooks/semantic_processing.ipynb
- Vector Search: https://www.mongodb.com/ko-kr
- 
