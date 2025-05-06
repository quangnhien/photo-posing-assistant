import aiohttp
from PIL import Image
import io
import numpy as np
import cv2
async def download_image_as_pil(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to fetch image: {resp.status}")
            image_bytes = await resp.read()
            return Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
async def download_image_as_np_array(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to fetch image: {resp.status}")
            image_bytes = await resp.read()
            pil_image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            return np.array(pil_image)  # Return NumPy array (RGB format)
        
def resize_image(image,size=368):
    scale =size/ image.shape[0]
    image = cv2.resize(image,None,fx=scale,fy=scale)
    return image
