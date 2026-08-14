import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
api_ready = False

if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        api_ready = True
        print("Gemini API configured successfully.")
    except Exception as e:
        print(f"Error configuring Gemini API: {str(e)}")
else:
    print("Warning: GEMINI_API_KEY is missing or set to default placeholder in .env file.")


def generate_gemini_response(user_query, chat_history=None, rag_context=None):
    """
    Generates a Gemini response using retrieved government schemes
    as RAG context.
    """

    if not api_ready:
        return (
            "<div class='ai-response-error'>"
            "<h4><i class='fa-solid fa-triangle-exclamation'></i> AI Engine Offline</h4>"
            "<p>The Gemini API key is missing or invalid.</p>"
            "</div>"
        )

    try:
        model_name = "gemini-2.5-flash"

        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=(
                "You are SchemeAI, a helpful assistant for Indian government schemes. "
                "Answer the user's question using the government scheme information "
                "provided in the RAG context. "
                "Do not invent scheme details. "
                "If the context does not contain enough information, clearly say so. "
                "Use the retrieved schemes to give relevant, accurate answers. "
                "You MUST format your response using standard HTML tags such as "
                "<p>, <ul>, <li>, <strong>, and <a>. "
                "Do NOT include ```html wrapper tags. "
                "Always advise users to verify details on the official government portal."
            )
        )

        # Build the prompt using RAG context
        if rag_context:
            prompt = f"""
User Question:
{user_query}

Retrieved Government Scheme Information:
{rag_context}

Using ONLY the retrieved scheme information above as your primary source,
answer the user's question clearly and helpfully.

Explain the most relevant schemes, including eligibility, benefits,
required documents, and official application links when available.

Do not invent information that is not present in the retrieved context.
"""
        else:
            prompt = user_query

        response = model.generate_content(prompt)

        if response.text:
            ai_content = response.text.strip()

            return (
                "<div class='ai-response-box'>"
                "<div class='ai-badge'>"
                "<i class='fa-solid fa-wand-magic-sparkles'></i> "
                "AI-Generated Response"
                "</div>"
                "<div class='ai-content'>"
                f"{ai_content}"
                "</div>"
                "</div>"
            )

        return (
            "<div class='ai-response-error'>"
            "<h4><i class='fa-solid fa-triangle-exclamation'></i> Empty AI Response</h4>"
            "<p>The AI model did not return any text. Please try again.</p>"
            "</div>"
        )

    except Exception as e:
        print(f"Gemini API Call Exception: {str(e)}")

        return (
            "<div class='ai-response-error'>"
            "<h4><i class='fa-solid fa-wifi'></i> Network or API Error</h4>"
            "<p>Unable to connect to the Gemini AI service. "
            "Please try again shortly.</p>"
            "</div>"
        )