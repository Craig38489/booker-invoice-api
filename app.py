from flask import Flask, request, jsonify
import fitz  # PyMuPDF

app = Flask(__name__)

def extract_invoice_data(pdf_path):
    doc = fitz.open(pdf_path)
    invoice_data = []
    invoice_number = ""
    invoice_date = ""

    for page in doc:
        text = page.get_text()
        lines = text.split("\n")

        for line in lines:
            if "Invoice Number" in line:
                invoice_number = line.split(":")[-1].strip()
            if "Invoice Date" in line:
                invoice_date = line.split(":")[-1].strip()

            parts = line.split()
            if len(parts) >= 7 and parts[0].isdigit():
                try:
                    code = parts[0]
                    description = " ".join(parts[1:-5])
                    pack = parts[-5]
                    size = parts[-4]
                    qty = parts[-3]
                    price = parts[-2]
                    value = parts[-1]
                    vat = "A"
                    invoice_data.append({
                        "invoice_number": invoice_number,
                        "invoice_date": invoice_date,
                        "code": code,
                        "description": description,
                        "pack": pack,
                        "size": size,
                        "qty": qty,
                        "price": price,
                        "value": value,
                        "vat": vat
                    })
                except Exception:
                    continue

    return invoice_data


@app.route('/extract', methods=['POST'])
def extract():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400
    file = request.files['file']
    path = "/tmp/" + file.filename
    file.save(path)
    try:
        data = extract_invoice_data(path)
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000, debug=True)
