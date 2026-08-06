import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment configurations
load_dotenv()

# Configure the Gemini SDK
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

def generate_gemini_response(user_query, chat_history=None):
    """
    Communicates with the Google Gemini API to generate a response when
    no local schemes are matched. Returns a formatted HTML response with a
    clear visual indicator that it is AI-generated.
    """
    if not api_ready:
        return (
            "<div class='ai-response-error'>"
            "  <h4><i class='fa-solid fa-triangle-exclamation'></i> AI Engine Offline</h4>"
            "  <p>The Gemini API key is missing or invalid. To activate AI search support, "
            "  please register a valid API key in the <code>.env</code> file in your project root.</p>"
            "</div>"
        )
        
    try:
        # Define model parameters
        model_name = "gemini-1.5-flash"
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=(
                "You are SchemeAI, a conversational assistant helping Indian citizens find government schemes. "
                "The user's query could not be matched directly with any schemes in our local database. "
                "Please search your global knowledge base and provide a detailed, helpful response about any relevant schemes, "
                "or answer their general query. "
                "You MUST format your response using standard HTML tags: <p> for paragraphs, "
                "<ul> and <li> for lists, <strong> for bold text, and <a> for links (set target='_blank'). "
                "Do NOT include any ```html wrapper tags, only return the raw inner HTML content. "
                "Keep your tone supportive and professional. Always advise them to double-check official portals."
            )
        )
        
        # Call the model
        response = model.generate_content(user_query)
        
        # Ensure we got text content back
        if response.text:
            ai_content = response.text.strip()
            
            # Format the output with a clear visual notice that it is AI-generated
            return (
                f"<div class='ai-response-box'>"
                f"  <div class='ai-badge'>"
                f"    <i class='fa-solid fa-wand-magic-sparkles'></i> AI-Generated Response"
                f"  </div>"
                f"  <div class='ai-content'>"
                f"    {ai_content}"
                f"  </div>"
                f"</div>"
            )
        else:
            return (
                "<div class='ai-response-error'>"
                "  <h4><i class='fa-solid fa-triangle-exclamation'></i> Empty AI Response</h4>"
                "  <p>The AI model processed your request but did not return any text. Please try phrasing your query differently.</p>"
                "</div>"
            )
            
    except Exception as e:
        # Gracefully handle connection errors or API blockages
        print(f"Gemini API Call Exception: {str(e)}")
        return (
            "<div class='ai-response-error'>"
            "  <h4><i class='fa-solid fa-wifi'></i> Network or API Error</h4>"
            "  <p>I failed to connect to the Gemini AI service. This could be due to internet "
            "  connectivity issues, rate limits, or invalid API configurations. Please try again shortly.</p>"
            "</div>"
        )
