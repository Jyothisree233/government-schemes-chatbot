from utils.db import get_all_schemes
from services.faiss_service import SchemeFAISS
from gemini_service import generate_gemini_response


# Create FAISS search system once
faiss_search = SchemeFAISS()

# Load schemes from SQLite
schemes = get_all_schemes()

# Build FAISS index
faiss_search.build_index(schemes)


def generate_recommendation_response(user_message):
    """
    RAG-based government scheme recommendation.

    User query
        ↓
    S-BERT embedding
        ↓
    FAISS semantic retrieval
        ↓
    Retrieved schemes
        ↓
    Gemini with retrieved context
        ↓
    Final response
    """

    query = user_message.strip()

    if not query:
        return "<p>Please enter your question.</p>"

    # 1. Retrieve relevant schemes using FAISS
    matched_schemes = faiss_search.search(query, top_k=5)

    # 2. If FAISS finds no schemes, use Gemini normally
    if not matched_schemes:
        return generate_gemini_response(query)

    # 3. Build RAG context from retrieved schemes
    context_parts = []

    for scheme in matched_schemes:
        context_parts.append(
            f"""
Scheme Name: {scheme.get('name', '')}
Category: {scheme.get('category', '')}
Description: {scheme.get('description', '')}
Eligibility: {scheme.get('eligibility', '')}
Benefits: {scheme.get('benefits', '')}
Required Documents: {scheme.get('required_documents', '')}
State: {scheme.get('state', '')}
Sector: {scheme.get('sector', '')}
Official Portal: {scheme.get('portal_link', '')}
"""
        )

    rag_context = "\n---\n".join(context_parts)

    # 4. Send user question + retrieved scheme context to Gemini
    return generate_gemini_response(
        query,
        rag_context=rag_context
    )