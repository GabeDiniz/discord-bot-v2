import qrcode # pip install qrcode
from PIL import Image

class MyQR:
  def __init__(self, size: int, padding: int):
    self.qr = qrcode.QRCode(box_size=size, border=padding)

  def create_qr(self, file_name: str, link: str, fg: str, bg: str):
    try:
      self.qr.add_data(link)  # Add data to QR code
      self.qr.make(fit=True)  # Generate the QR code
      qr_image = self.qr.make_image(fill_color=fg, back_color=bg)  # Create QR image with specified colors
      qr_image.save(file_name)  # Save the image
      return file_name

    except Exception as e:
      print(f"Error: {e}")
      return None

def generate(message):
  # Initialize QR Class
  myqr = MyQR(size=40, padding=1)
  # Create QR
  name = "qr.png"
  file_name = myqr.create_qr(name, message, fg="#BD8334", bg="#FAF3EF")
  return file_name