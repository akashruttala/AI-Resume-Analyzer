import os
import json
import concurrent.futures
from functools import lru_cache
from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify, send_file, Response
from werkzeug.utils import secure_filename
from utils.pdf_processor import extract_text_from_pdf
from utils.nlp_engine import analyze_resume
from utils.llm_integration import generate_suggestions
from utils.report_generator import generate_report

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORTS_FOLDER'] = 'reports'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit for scalability
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)

# Cache embeddings/analysis for identical JDs
@lru_cache(maxsize=32)
def cached_analyze_resume(resume_text, jd_text):
    return analyze_resume(resume_text, jd_text)

def process_jd_task(resume_text, jd_text, index, role_name="Job Role"):
    """
    Worker function to process a single JD concurrently.
    """
    if not jd_text.strip():
        return None
        
    analysis_result = cached_analyze_resume(resume_text, jd_text)
    
    try:
        suggestions = generate_suggestions(
            analysis_result['missing_skills'],
            analysis_result['matched_skills'],
            analysis_result['score'],
            target_role=role_name
        )
    except Exception as e:
        print(f"Failed to generate suggestions for {role_name}: {e}")
        suggestions = {
            "skill_roadmap": ["API Error. Focus on missing skills."],
            "resume_tips": ["API Error. Emphasize matched skills."],
            "project_suggestions": ["API Error. Build related projects."]
        }
        
    analysis_result['suggestions'] = suggestions
    analysis_result['role_name'] = role_name
    analysis_result['id'] = index
    return analysis_result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # 1. Validate PDF / File size
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume uploaded'}), 400
    resume_file = request.files['resume']
    if resume_file.filename == '':
        return jsonify({'error': 'No selected resume file'}), 400
    
    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(resume_file.filename))
    resume_file.save(resume_path)
    resume_text = extract_text_from_pdf(resume_path)
    
    if not resume_text or len(resume_text.strip()) == 0:
        return jsonify({'error': 'Could not extract text from Resume PDF. Ensure it is not an image-based PDF.'}), 400

    # 2. Gather Multiple JDs (Texts and Files)
    jd_texts_input = request.form.getlist('jd_text[]')
    jd_roles_input = request.form.getlist('jd_role[]')
    jd_files = request.files.getlist('jd_file[]')
    
    jd_list = []
    
    # Process text JDs
    for i, text in enumerate(jd_texts_input):
        if text.strip():
            role = jd_roles_input[i] if i < len(jd_roles_input) and jd_roles_input[i] else f"Job {len(jd_list) + 1}"
            jd_list.append((text, role))
            
    # Process PDF JDs
    for i, file in enumerate(jd_files):
        if file.filename != '':
            jd_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(jd_path)
            extracted = extract_text_from_pdf(jd_path)
            if extracted:
                # Use role if specified, otherwise filename
                role = jd_roles_input[i] if i < len(jd_roles_input) and jd_roles_input[i].strip() else file.filename.replace('.pdf', '')
                jd_list.append((extracted, role))
                
    if not jd_list:
        return jsonify({'error': 'No Job Descriptions provided.'}), 400

    # 3. Async Processing via ThreadPool
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_jd = {
            executor.submit(process_jd_task, resume_text, jd[0], idx, jd[1]): idx 
            for idx, jd in enumerate(jd_list)
        }
        
        for future in concurrent.futures.as_completed(future_to_jd):
            try:
                res = future.result(timeout=30) # 30s timeout per JD
                if res:
                    results.append(res)
            except Exception as exc:
                print(f"JD processing generated an exception: {exc}")

    # 4. Ranking System (Sort by Score Descending)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Take Top 3 to avoid overwhelming UI/PDF
    top_results = results[:3]
    
    if not top_results:
        return jsonify({'error': 'Failed to analyze any job descriptions.'}), 500

    # 5. Generate PDF Report (for the Top 1 match by default, or an aggregate)
    top_match = top_results[0]
    report_filename = f"Report_{secure_filename(resume_file.filename)}"
    report_path = os.path.join(app.config['REPORTS_FOLDER'], report_filename)
    generate_report(report_path, top_match, top_match['suggestions'], top_match['role_name'])
    
    # We save the raw JSON for export
    json_export_filename = f"Data_{secure_filename(resume_file.filename)}.json"
    json_export_path = os.path.join(app.config['REPORTS_FOLDER'], json_export_filename)
    with open(json_export_path, 'w') as f:
        json.dump(top_results, f)

    return jsonify({
        'results': top_results,
        'report_url': f"/download_report/{report_filename}",
        'json_url': f"/api/export_json/{json_export_filename}"
    })

@app.route('/download_report/<filename>')
def download_report(filename):
    report_path = os.path.join(app.config['REPORTS_FOLDER'], secure_filename(filename))
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    return jsonify({'error': 'Report not found'}), 404

@app.route('/api/export_json/<filename>')
def export_json(filename):
    file_path = os.path.join(app.config['REPORTS_FOLDER'], secure_filename(filename))
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, mimetype='application/json')
    return jsonify({'error': 'JSON not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
