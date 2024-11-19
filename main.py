from flask import Flask, abort, send_file, request
from io import BytesIO
import xmltodict
import hashlib
import qrcode
import os

app = Flask(__name__)

def load_files_config():
    try:
        with open('files.xml', 'r') as f:
            data = xmltodict.parse(f.read())
            files_dict = {}
            if isinstance(data['files']['file'], dict):
                data['files']['file'] = [data['files']['file']]
           
            for file in data['files']['file']:
                files_dict[file['name']] = {
                    'mimetype': file.get('mimetype', None),
                    'isPublic': file['isPublic'].lower() == 'true',
                    'password': file.get('password', None) if file['isPublic'].lower() == 'false' else None,
                    "checksum": file.get('checksum', 'true').lower() == 'true'
                }

            return files_dict
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

@app.route("/")
def index():
    files = load_files_config()
   
    return [filename for filename, info in files.items() if info['isPublic']]

@app.route("/<file>/checksum")
@app.route("/<file>/checksum/")
def checksum(file):
    files = load_files_config()

    if file not in files:
        abort(404)
        return

    file_info = files[file]
    print(file_info)
    if not file_info['checksum']:
        abort(405)
        return

    sha512 = hashlib.sha512()
    sha256 = hashlib.sha256()
    sha1 = hashlib.sha1()
    md5 = hashlib.md5()

    with open(f"files/{file}", "rb") as f:
        for byteblock in iter(lambda: f.read(4096), b""):
            sha512.update(byteblock)
            sha256.update(byteblock)
            sha1.update(byteblock)
            md5.update(byteblock)

    return {
        "sha512": sha512.hexdigest(),
        "sha256": sha256.hexdigest(),
        "sha1": sha1.hexdigest(),
        "md5": md5.hexdigest()
    }

@app.route("/<file>")
@app.route("/<file>/")
def give_file(file):
    files = load_files_config()
   
    if file not in files:
        abort(404)
        return
   
    file_info = files[file]
   
    if not file_info['isPublic']:
        if not file_info['password']:
            abort(500)
            return
           
        password = request.args.get("pass", "")
        if not password or password != file_info['password']:
            abort(403)
            return
   
    if not os.path.exists(f"files/{file}"):
        abort(404)
        return
   
    return send_file(
        f"files/{file}",
        download_name=file,
        mimetype=file_info['mimetype'] if file_info['mimetype'] else None
    )

@app.route("/<file>/download")
@app.route("/<file>/download/")
def download_file(file):
    files = load_files_config()
   
    if file not in files:
        abort(404)
        return
   
    file_info = files[file]
   
    if not file_info['isPublic']:
        if not file_info['password']:
            abort(500)
            return
           
        password = request.args.get("pass", "")
        if not password or password != file_info['password']:
            abort(403)
            return
   
    if not os.path.exists(f"files/{file}"):
        abort(404)
        return
   
    return send_file(
        f"files/{file}",
        download_name=file,
        mimetype="application/octet-stream"
    )

@app.route("/<file>/qrcode")
def generate_qrcode(file):
    files = load_files_config()
    
    if file not in files:
        abort(404)
        return
        
    file_info = files[file]
    
    base_url = request.host_url.rstrip('/')
    download_url = f"{base_url}/{file}"
    
    if not file_info['isPublic'] and file_info['password']:
        download_url += f"?pass={file_info['password']}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(download_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return send_file(
        img_buffer,
        mimetype='image/png',
        download_name=f"{file}_qr.png"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)