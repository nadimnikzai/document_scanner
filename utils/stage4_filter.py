import cv2
import os
import base64
import numpy as np

def image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    img_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_str}"

def apply_filter_and_save(warped_img, save_folder, filter_type='bw', rotation=0):
    
    if rotation == 90:
        warped_img = cv2.rotate(warped_img, cv2.ROTATE_90_CLOCKWISE)
    elif rotation == 180:
        warped_img = cv2.rotate(warped_img, cv2.ROTATE_180)
    elif rotation == 270:
        warped_img = cv2.rotate(warped_img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    
    final_img = warped_img.copy()
    
    if filter_type == 'bw':
        gray = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (25, 25), 0)
        normalized = cv2.divide(gray, blur, scale=255)
        sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(normalized, -1, sharpen_kernel)
        _, final_img = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
    elif filter_type == 'gray':
        final_img = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)
        
    elif filter_type == 'magic':
        hsv = cv2.cvtColor(warped_img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        s = cv2.multiply(s, 1.5) 
        s = np.clip(s, 0, 255).astype(np.uint8) 

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        v = clahe.apply(v)

        final_hsv = cv2.merge((h, s, v))
        enhanced_img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        final_img = cv2.filter2D(enhanced_img, -1, kernel)
        
    elif filter_type == 'original':
        final_img = warped_img

    filename = 'final_scanned.jpg'
    full_path = os.path.join(save_folder, filename)
    cv2.imwrite(full_path, final_img)
    
    return {
        'final_base64': image_to_base64(final_img),
        'file_path': filename
    }