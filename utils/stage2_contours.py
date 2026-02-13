import cv2
import numpy as np
import base64

def image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    img_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_str}"

def find_paper(img_original):
    height, width = img_original.shape[:2]
    img_area = width * height
    min_area_threshold = 0.15 * img_area 

    
    gray = cv2.cvtColor(img_original, cv2.COLOR_BGR2GRAY)
    
    blur = cv2.GaussianBlur(gray, (11, 11), 0)
    
    edged = cv2.Canny(blur, 50, 150)
    
   
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))

    # اجرای A • B (Closing)
    # این تابع خودکار اول Dilate میکنه بعد Erode (طبق فرمول تصویرت)
    closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel, iterations=3)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    
    screenCnt = None
    status = "کاغذ پیدا نشد"
    
    for c in contours:
        area = cv2.contourArea(c)
        if area < min_area_threshold:
            continue
            
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        
        if len(approx) == 4:
            screenCnt = approx
            status = "کاغذ پیدا شد (دقیق)"
            break
            
    if screenCnt is None and len(contours) > 0:
        largest_c = contours[0]
        if cv2.contourArea(largest_c) > min_area_threshold:
            rect = cv2.minAreaRect(largest_c)
            box = cv2.boxPoints(rect)
            box = np.int64(box)
            screenCnt = box.reshape(4, 1, 2)
            status = "کاغذ پیدا شد (حالت تقریبی)"

    image_with_contours = img_original.copy()
    if screenCnt is not None:
        cv2.drawContours(image_with_contours, [screenCnt], -1, (0, 255, 0), 10)
    
    return {
        'contours_img': image_to_base64(image_with_contours), 
        'gray_img': image_to_base64(gray),                    
        'blur_img': image_to_base64(blur),                    
        'edge_img': image_to_base64(edged),                   
        'dilate_img': image_to_base64(closed),               
        'status': status,
        'cnt': screenCnt
    }