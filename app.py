import os
import base64
from flask import Flask, render_template, request
import cv2
import numpy as np

from utils import stage2_contours, stage3_perspective, stage4_filter

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def local_image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    img_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_str}"

@app.route('/', methods=['GET', 'POST'])
def index():
    results = {}
    current_step = 0
    error = None
    
    sel_filter = 'bw'
    sel_rotation = 0
    
    temp_path = os.path.join(UPLOAD_FOLDER, 'temp_image.jpg')

    if request.method == 'POST':
        action = request.form.get('action')

        try:
            if action == 'upload':
                if 'image' in request.files:
                    file = request.files['image']
                    if file.filename != '':
                        file.save(temp_path)
                        img = cv2.imread(temp_path)
                        
                        res2 = stage2_contours.find_paper(img)
                        
                        results = {
                            'original': local_image_to_base64(img),
                            'step2': res2 
                        }
                        current_step = 2 

            elif action == 'step3' or action == 'update_final':
                if os.path.exists(temp_path):
                    img = cv2.imread(temp_path)
                    
                    res2 = stage2_contours.find_paper(img)
                    
                    if res2['cnt'] is not None:
                        scan_res = stage3_perspective.get_scan(img, res2['cnt'])
                        warped_raw = scan_res['warped_raw']
                        warped_show = scan_res['warped_base64']
                        
                        sel_filter = request.form.get('filter', 'bw')
                        sel_rotation = int(request.form.get('rotation', 0))
                        
                        final_res = stage4_filter.apply_filter_and_save(
                            warped_raw, 
                            UPLOAD_FOLDER, 
                            filter_type=sel_filter, 
                            rotation=sel_rotation
                        )
                        
                        results = {
                            'original': local_image_to_base64(img),
                            'step2': res2,
                            'step3_img': warped_show,
                            'final_img': final_res['final_base64']
                        }
                        current_step = 3
                    else:
                        results = {
                            'original': local_image_to_base64(img),
                            'step2': res2
                        }
                        current_step = 2
                        error = "کاغذ پیدا نشد. لطفاً عکس واضح‌تری بگیرید."

        except Exception as e:
            error = f"خطا: {str(e)}"
            print(error) 

    return render_template('index.html', results=results, step=current_step, error=error, 
                           sel_filter=sel_filter, sel_rotation=sel_rotation)

if __name__ == '__main__':
    app.run(debug=True, port=5000)