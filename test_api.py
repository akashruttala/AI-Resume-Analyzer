import requests

url = "http://127.0.0.1:5000/analyze"

try:
    with open("dummy_resume.pdf", "rb") as r_pdf, open("dummy_jd.pdf", "rb") as j_pdf:
        files = {
            'resume': ('dummy_resume.pdf', r_pdf, 'application/pdf'),
            'jd_file[]': ('dummy_jd.pdf', j_pdf, 'application/pdf')
        }
        
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("Analysis Success!")
            top_result = data['results'][0]
            print(f"Top Role: {top_result['role_name']}")
            print(f"Score: {top_result['score']}%")
            print(f"Matched Skills: {top_result['matched_skills']}")
            print(f"Missing Skills: {top_result['missing_skills']}")
            print("Suggestions Generated: Yes" if top_result['suggestions'] else "No")
            
            # Test download
            dl_url = f"http://127.0.0.1:5000{data['report_url']}"
            dl_resp = requests.get(dl_url)
            if dl_resp.status_code == 200:
                print(f"Report downloaded successfully ({len(dl_resp.content)} bytes).")
            else:
                print("Failed to download report.")
        else:
            print(f"Failed analysis: {response.text}")
except Exception as e:
    print(f"Connection error: {e}")
