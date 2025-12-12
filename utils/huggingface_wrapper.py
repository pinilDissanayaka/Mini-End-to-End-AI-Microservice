from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline, HuggingFaceEmbeddings


def load_llm_model(model_name: str) -> ChatHuggingFace:

    llm = HuggingFacePipeline.from_model_id(
            model_id="HuggingFaceH4/zephyr-7b-beta",
            task="text-generation",
            pipeline_kwargs=dict(
                max_new_tokens=512,
                do_sample=False,
                repetition_penalty=1.03,
            ),
        )

    chat_model = ChatHuggingFace(llm=llm)
    
    
    return chat_model


def load_embedding_model(model_name: str):
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": False}
    
    embedding_model = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )
    
    return embedding_model


llm = load_llm_model("HuggingFaceH4/zephyr-7b-beta")
embedding_model = load_embedding_model("sentence-transformers/all-MiniLM-L6-v2")