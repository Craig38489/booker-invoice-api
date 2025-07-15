from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import re

app = Flask(__name__)

def extract_invoice_data(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()

    lines = text.split('\n')
    invoice_number = ''
    invoice_date = ''

    for line in lines:
        if 'Invoice Number' in line:
            match = re.search(r'Invoice Number\s*:\s*(\d+)', line)
            if match:
                invoice_number = match.group(1)
        if 'Invoice Date' in line:
            match = re.search(r'Invoice Date\s*:\s*(\d{2}/\d{2}/\d{2})', line)
            if match:
                invoice_date = match.group(1)

    items = []
    capture = False

    for line in lines:
        if re.search(r'^CATEGORY\s+CODE\s+DESCRIPTION', line):
            capture = True
            continue
        if capture:
            if line.strip() == '' or line.startswith('Total'):
                break
            parts = re.split(r'\s{2,}', line.strip())
            if len(parts) >= 7:
                category, code, description, pack, size, qty, price, value, vat = (
                    parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6], parts[7], parts[8]
                )
                items.append({
                    'invoice_number': invoice_number,
                    'invoice_date': invoice_date,
                    'category': category,
                    'code': code,
                    'description': description,
                    'pack': pack,
                    'size': size,
                    'qty': qty,
                    'price': price,
                    'value': value,
                    'vat': vat
                })

    return {'data': items, 'status': 'success'}

@app.route('/extract', methods=['POST'])
def extract():
    if 'file' not in request.files:
        return jsonify({'status': 'fail', 'message': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'fail', 'message': 'No file selected'}), 400

    filepath = f"/tmp/{file.filename}"
    file.save(filepath)

    try:
        result = extract_invoice_data(filepath)
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
