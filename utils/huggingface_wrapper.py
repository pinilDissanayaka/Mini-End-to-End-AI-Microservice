from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline, HuggingFaceEmbeddings
from utils.config import config


def load_llm_model(model_name: str = None) -> ChatHuggingFace:
    """Load the LLM model from HuggingFace"""
    if model_name is None:
        model_name = config.CHAT_MODEL
    
    llm = HuggingFacePipeline.from_model_id(
        model_id=model_name,
        task="text-generation",
        pipeline_kwargs=dict(
            max_new_tokens=config.LLM_MAX_NEW_TOKENS,
            do_sample=False,
            repetition_penalty=config.LLM_REPETITION_PENALTY,
        ),
    )

    chat_model = ChatHuggingFace(llm=llm)
    
    return chat_model


def load_embedding_model(model_name: str = None):
    """Load the embedding model from HuggingFace"""
    if model_name is None:
        model_name = config.EMBEDDING_MODEL
        
    model_kwargs = {"device": config.EMBEDDING_DEVICE}
    encode_kwargs = {"normalize_embeddings": config.EMBEDDING_NORMALIZE}
    
    embedding_model = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )
    
    return embedding_model


# Global instances
llm = load_llm_model()
embedding_model = load_embedding_model()
