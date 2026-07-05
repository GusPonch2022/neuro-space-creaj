import qrcode
import os

STATIC_DIR = "static"
QR_FILE = os.path.join(STATIC_DIR, "neuro_space_creaj_qr.png")

os.makedirs(STATIC_DIR, exist_ok=True)

url = "http://127.0.0.1:5000"

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=12,
    border=4,
)

qr.add_data(url)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save(QR_FILE)

print("QR generado correctamente en:", QR_FILE)