import os

resumes_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge", "resumes")
os.makedirs(resumes_dir, exist_ok=True)

resumes = [
    ("Sohaib_Mahmood_GoHighLevel_Specialist_Resume.pdf", "Sohaib Mahmood - GoHighLevel Specialist & CRM Architect"),
    ("Sohaib_Mahmood_GHL_Developer_Resume.pdf", "Sohaib Mahmood - GoHighLevel Full-Stack Developer & API Specialist"),
    ("Sohaib_Mahmood_GHL_Funnel_Builder_Resume.pdf", "Sohaib Mahmood - GoHighLevel Funnel Builder & UI/UX Specialist"),
    ("Sohaib_Mahmood_AI_Automation_Resume.pdf", "Sohaib Mahmood - AI & Workflow Automation Engineer (n8n, GHL, OpenAI)")
]

for filename, title in resumes:
    filepath = os.path.join(resumes_dir, filename)
    content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>
endobj
4 0 obj
<< /Length 250 >>
stream
BT
/F1 14 Tf
50 720 Td
({title}) Tj
/F1 10 Tf
0 -25 Td
(Email: sohaibmahmood5911@gmail.com | Portfolio: https://sohaibmahmood.vibepreview.com/) Tj
0 -20 Td
(4 Years Dedicated GoHighLevel Experience | 50+ Builds | 200+ Workflows | 40+ Sub-accounts) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
518
%%EOF
"""
    with open(filepath, "wb") as f:
        f.write(content.encode("latin-1"))

print("Created 4 specialized PDF resume versions in knowledge/resumes/")
