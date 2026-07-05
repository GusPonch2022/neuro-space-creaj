import qrcode
import os

URL = "https://neuro-space-creaj.onrender.com"

output_folder = os.path.join("web_server", "static")
os.makedirs(output_folder, exist_ok=True)

output_path = os.path.join(output_folder, "neuro_space_creaj_qr.png")

qr = qrcode.QRCode(
    version=None,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=12,
    border=4,
)

qr.add_data(URL)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save(output_path)

print("QR creado correctamente en:")
print(output_path)