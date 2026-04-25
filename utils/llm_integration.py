import os
import json
import google.generativeai as genai

def generate_suggestions(missing_skills, matched_skills, score, target_role="the target role"):
    """
    Generate real AI-powered structured suggestions using the Gemini API based on resume analysis.
    Returns a dictionary with keys: skill_roadmap, resume_tips, project_suggestions.
    """
    # Configure Gemini API using the environment variable
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    try:
        # Initialize the Gemini model. We use generation_config to ensure JSON output
        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
        
        prompt = f"""
        You are an expert career coach and technical recruiter. Review the following resume analysis against {target_role}:
        
        Match Score: {score}%
        Matched Skills: {', '.join(matched_skills) if matched_skills else 'None'}
        Missing Skills: {', '.join(missing_skills) if missing_skills else 'None'}
        
        Please provide actionable career advice in strict JSON format. 
        Your response must be a JSON object with the following schema:
        {{
            "skill_roadmap": [
                "1. Learn X to address the missing skill gap...",
                "2. Learn Y..."
            ],
            "resume_tips": [
                "1. Rewrite your experience section to highlight...",
                "2. Emphasize your matched skills by..."
            ],
            "project_suggestions": [
                "1. Build a project using [Missing Skill] and [Matched Skill]..."
            ]
        }}
        
        CRITICAL RULES:
        - Return ONLY the JSON object. Do not wrap it in markdown code blocks like ```json ... ```.
        - Ensure it is valid, parseable JSON.
        - Provide exactly 3 items per array.
        """
        
        response = model.generate_content(prompt)
        
        try:
            # Parse the JSON response
            suggestions = json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback if Gemini failed to return clean JSON (rare with application/json config but possible)
            # Try to strip markdown blocks if they slipped in
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            suggestions = json.loads(clean_text)
            
        return suggestions

    except Exception as e:
        print(f"Gemini API Error: {e}")
        # Fallback dictionary if API fails entirely
        return {
            "skill_roadmap": ["Focus on acquiring the missing skills listed below."],
            "resume_tips": ["Ensure your resume clearly quantifies past achievements."],
            "project_suggestions": ["Build a small portfolio project applying the missing skills."]
        }
