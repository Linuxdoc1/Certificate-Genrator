from flask import Flask, render_template, request, send_file, after_this_request
from docxtpl import DocxTemplate
from docx2pdf import convert
from datetime import datetime
import os
from pathlib import Path

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/generate', methods=['POST'])
def generate_certificate():
    # Clean and format input fields
    name = request.form['name'].strip()
    reg_no = request.form['reg_no'].strip()
    course = request.form['course'].strip()
    college = request.form['college'].strip()
    domain = request.form['domain'].strip().title()
    issuer_name = request.form['issuer_name'].strip().title()

    # Format dates (no bold applied in .docx template)
    start_date = datetime.strptime(request.form['start_date'], "%Y-%m-%d").strftime("%d/%m/%Y")
    end_date = datetime.strptime(request.form['end_date'], "%Y-%m-%d").strftime("%d/%m/%Y")

    # Load Word template
    template_path = "refined_sample.docx"
    doc = DocxTemplate(template_path)

    # Template context with clean formatting
    context = {
        'name': name,
        'reg_no': reg_no,
        'course': course,
        'college': college,
        'domain': domain,
        'start_date': start_date,
        'end_date': end_date,
        'issuer_name': issuer_name
    }

    # Output to Downloads folder
    downloads_path = str(Path.home() / "Downloads")
    safe_name = name.replace(" ", "_").replace(".", "")
    docx_file = os.path.join(downloads_path, f"{safe_name}.docx")
    pdf_file = os.path.join(downloads_path, f"{safe_name}.pdf")

    # Render document
    doc.render(context)
    doc.save(docx_file)
    convert(docx_file, pdf_file)

    # Clean up DOCX immediately
    if os.path.exists(docx_file):
        os.remove(docx_file)

    # Clean up PDF after sending
    @after_this_request
    def cleanup(response):
        try:
            if os.path.exists(pdf_file):
                os.remove(pdf_file)
        except Exception as e:
            print(f"Cleanup error: {e}")
        return response

    return send_file(pdf_file, as_attachment=True, download_name=f"{safe_name}.pdf")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

