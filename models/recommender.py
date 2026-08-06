from utils.db import search_schemes
from gemini_service import generate_gemini_response

def generate_recommendation_response(user_message):
    """
    Parses user input, queries the database, and returns a formatted HTML response
    with relevant government scheme recommendations. If no match is found,
    delegates to the Google Gemini API to return a detailed AI-generated response.
    """
    query = user_message.strip()
    
    # Fetch matched schemes from the local database
    matched_schemes = search_schemes(query)
    
    # If no matching scheme exists in local database, call Gemini AI
    if not matched_schemes:
        return generate_gemini_response(query)
        
    # Format matching schemes from database into a clean responsive interface response
    response_html = f"<p>Based on your profile search, I found the following scheme(s) in our database:</p>"
    
    for idx, scheme in enumerate(matched_schemes, 1):
        # Color tags based on category
        cat_class = scheme['category'].replace('_', '-')
        cat_label = scheme['category'].replace('_', ' ').title()
        
        # Build Scheme details including Required Documents column
        response_html += (
            f"<div class='recommended-scheme-card'>"
            f"  <div class='scheme-card-header'>"
            f"    <span class='scheme-num'>{idx}</span>"
            f"    <h4>{scheme['name']}</h4>"
            f"    <span class='scheme-badge badge-{cat_class}'>{cat_label}</span>"
            f"  </div>"
            f"  <div class='scheme-card-body'>"
            f"    <p><strong>Description:</strong> {scheme['description']}</p>"
            f"    <p><strong>Eligibility:</strong> {scheme['eligibility']}</p>"
            f"    <p><strong>Benefits:</strong> {scheme['benefits']}</p>"
            f"    <p><strong>Required Documents:</strong> {scheme['required_documents']}</p>"
            f"  </div>"
            f"  <div class='scheme-card-footer'>"
            f"    <a href='{scheme['portal_link']}' target='_blank' class='scheme-apply-link'>"
            f"      Apply on Official Portal <i class='fa-solid fa-arrow-up-right-from-square'></i>"
            f"    </a>"
            f"  </div>"
            f"</div>"
        )
        
    response_html += "<p>Would you like to ask about eligibility details for another scheme, or check benefits for a different family member?</p>"
    return response_html
