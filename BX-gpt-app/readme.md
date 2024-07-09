# BX-gpt application

## Abstract



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







## TBD




## doc
---

### Data
- BwG 사내문서 공유사이트: https://pages.bwg.co.kr/ROOT/

### Embedding/Searching
- Raptor`Recursive Abstractive Processing for Tree-Organized Retrieval(2024)`: https://github.com/run-llama/llama_index/blob/main/llama-index-packs/llama-index-packs-raptor/examples/raptor.ipynb?fbclid=IwZXh0bgNhZW0CMTAAAR0RCkGhA8S9wpJSVyY8XSJuQG7qDeG6xA8MLs_bF2mRkqslty99Y5IP1Dk_aem_rGk9AfVWfB1QN2GAkNeKDQ
- Semantic Chunking: https://github.com/Filimoa/open-parse/blob/main/src/cookbooks/semantic_processing.ipynb
- Vector Search: https://www.mongodb.com/ko-kr
- 
