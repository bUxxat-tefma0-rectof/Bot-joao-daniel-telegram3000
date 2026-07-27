from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import os

class ImageUtils:
    @staticmethod
    def download_image(url, save_path=None):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                if save_path:
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                return BytesIO(response.content)
        except:
            pass
        return None
    
    @staticmethod
    def create_watermark(image_bytes, text, position='bottom'):
        img = Image.open(image_bytes)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        if position == 'bottom':
            x = (img.width - text_width) // 2
            y = img.height - text_height - 20
        elif position == 'top':
            x = (img.width - text_width) // 2
            y = 20
        else:
            x = (img.width - text_width) // 2
            y = (img.height - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255, 128), font=font)
        
        output = BytesIO()
        img.save(output, format='PNG')
        output.seek(0)
        return output
    
    @staticmethod
    def resize_image(image_bytes, width=None, height=None):
        img = Image.open(image_bytes)
        
        if width and height:
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        elif width:
            ratio = width / img.width
            height = int(img.height * ratio)
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        elif height:
            ratio = height / img.height
            width = int(img.width * ratio)
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        output = BytesIO()
        img.save(output, format='PNG')
        output.seek(0)
        return output
    
    @staticmethod
    def compress_image(image_bytes, quality=80):
        img = Image.open(image_bytes)
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        return output
    
    @staticmethod
    def create_thumbnail(image_bytes, size=(128, 128)):
        img = Image.open(image_bytes)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        output = BytesIO()
        img.save(output, format='PNG')
        output.seek(0)
        return output

image_utils = ImageUtils()
