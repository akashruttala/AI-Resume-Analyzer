import re
import spacy
from sentence_transformers import SentenceTransformer, util

# Load models globally so they don't reload on every function call
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback if download failed or hasn't finished, though typically it should be pre-downloaded
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

embedder = SentenceTransformer('all-MiniLM-L6-v2')

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s#\+\.]', '', text)
    return ' '.join(text.split())

def extract_skills(text):
    """
    Dynamic skill extraction using SpaCy NLP.
    Extracts proper nouns and alphanumeric terms instead of a static list.
    """
    doc = nlp(text)
    skills = set()
    
    # Custom patterns for tech skills
    for token in doc:
        # Avoid stop words and very short words (unless it's C or R, but usually tech acronyms are 2+ chars like C#, JS)
        if token.is_stop or len(token.text) <= 1:
            continue
            
        # If it's a proper noun or an all-caps word (like HTML, AWS)
        if token.pos_ == "PROPN" or (token.is_alpha and token.text.isupper()):
            skills.add(token.text.title())
            
        # Catch specific versions/symbols that might be tokenized oddly
        word_lower = token.text.lower()
        if word_lower in ['c++', 'c#', 'node.js', 'vue.js', '.net', 'react.js']:
            skills.add(word_lower.upper() if len(word_lower) <= 2 else word_lower.title())

    # Optionally extract specific noun chunks as skills (e.g., "Machine Learning", "Rest API")
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower()
        if any(keyword in chunk_text for keyword in ["learning", "development", "api", "framework", "database"]):
            # Filter out overly long chunks
            if len(chunk.text.split()) <= 3:
                skills.add(chunk.text.title())

    return list(skills)

def analyze_resume(resume_text, jd_text):
    # Calculate Semantic Similarity Score using Transformer Embeddings
    resume_embedding = embedder.encode(resume_text, convert_to_tensor=True)
    jd_embedding = embedder.encode(jd_text, convert_to_tensor=True)
    
    # Compute cosine similarity between the embeddings
    cosine_scores = util.cos_sim(resume_embedding, jd_embedding)
    score = round(cosine_scores[0][0].item() * 100, 2)
    score = max(0, min(100, score)) # bound between 0 and 100
    
    # Determine score interpretation
    if score >= 80:
        interpretation = "Strong Match"
    elif score >= 60:
        interpretation = "Moderate Match"
    else:
        interpretation = "Needs Improvement"
    
    # Skill Gap Analysis using dynamic NLP extraction
    resume_skills = set(extract_skills(resume_text))
    jd_skills = set(extract_skills(jd_text))
    
    # Because extraction is dynamic, we do case-insensitive comparisons behind the scenes
    # but display the Title-cased versions.
    resume_skills_lower = {s.lower() for s in resume_skills}
    jd_skills_lower = {s.lower() for s in jd_skills}
    
    matched_lower = jd_skills_lower.intersection(resume_skills_lower)
    missing_lower = jd_skills_lower.difference(resume_skills_lower)
    
    # Map back to original casing
    matched_skills = [s for s in jd_skills if s.lower() in matched_lower]
    missing_skills = [s for s in jd_skills if s.lower() in missing_lower]
    
    return {
        'score': score,
        'interpretation': interpretation,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills
    }
