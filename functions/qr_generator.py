import qrcode # pip install qrcode
from PIL import Image


class MyQR:
  def __init__(self, size: int, padding: int):
    self.qr = qrcode.QRCode(box_size=size, border=padding)

  def create_qr(self, file_name: str, link: str, fg: str, bg: str):
    """
    This method generates a QR code from a link, sets its foreground and background colors, and saves it to a file.

    Returns
    -------
    file_name (str): Returns the file name if the QR code generation and saving are successful.
    None: If an error occurs
    """
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
  """
  This function splits a message into parts, extracts the link, and optional color values (foreground and background), 
  then generates a QR code using the MyQR class.

  Returns
  -------
  file_name (str): The name of the generated QR code file (qr.png by default).
  None: If an error occurs
  """
  try:
    data = message.split()  # Grab parameters
    
    link = data[0]
    # Check for color values
    fg = data[1] if len(data) > 1 else "#BD8334"
    bg = data[2] if len(data) > 2 else "#FAF3EF"

    myqr = MyQR(size=10, padding=4)
    file_name = myqr.create_qr("qr.png", link, fg, bg)
    return file_name
  except Exception as e:
    print(f"Error in generate function: {e}")
    return None