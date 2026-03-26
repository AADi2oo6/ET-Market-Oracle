import logging
from sqlalchemy.orm import Session
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.models.schema import NewsArticle

logger = logging.getLogger(__name__)

def get_vectorstore() -> PineconeVectorStore:
    """Initialize and return the vector store with embeddings."""
    embeddings = OpenAIEmbeddings(
        api_key=settings.FASTROUTER_API_KEY,
        base_url="https://api.fastrouter.ai/v1",
        model="text-embedding-3-small"
    )
    
    vectorstore = PineconeVectorStore(
        index_name=settings.PINECONE_INDEX_NAME,
        embedding=embeddings,
        pinecone_api_key=settings.PINECONE_API_KEY
    )
    return vectorstore

def embed_unprocessed_news(db: Session) -> int:
    """Fetch unprocessed news, chunk them, and add to Pinecone."""
    unprocessed = db.query(NewsArticle).filter(NewsArticle.is_embedded == False).all()
    
    if not unprocessed:
        return 0

    vectorstore = get_vectorstore()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    
    docs_to_add = []
    articles_to_update = []

    for article in unprocessed:
        text = f"Title: {article.title}\n\nSummary: {article.summary or ''}"
        chunks = text_splitter.split_text(text)
        
        for chunk in chunks:
            docs_to_add.append({
                "page_content": chunk,
                "metadata": {
                    "source": article.link,
                    "title": article.title,
                    "published_at": str(article.published_at) if article.published_at else ""
                }
            })
            
        articles_to_update.append(article)

    if docs_to_add:
        # PineconeVectorStore add_texts
        texts = [doc["page_content"] for doc in docs_to_add]
        metadatas = [doc["metadata"] for doc in docs_to_add]
        vectorstore.add_texts(texts=texts, metadatas=metadatas)
        
        # Mark as embedded
        for article in articles_to_update:
            article.is_embedded = True
        
        db.commit()
        logger.info(f"Successfully embedded {len(articles_to_update)} news articles.")
        
    return len(articles_to_update)
