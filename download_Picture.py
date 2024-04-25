import pandas as pd
import requests
import os
import re
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import logging
import threading
from io import BytesIO

# 最大线程数量
max_threads = 5

def download_image(url, save_path, delay=1):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            webp_image_rgb = Image.open(BytesIO(response.content)).convert("RGB")
            webp_image_rgb.save(save_path, 'JPEG')
            print("图片已下载到:", save_path)
            # time.sleep(delay)
            return True
        else:
            if response.status_code == 404:
                print("下载失败:", response.status_code, url)
                return False
            else:
                raise Exception("下载出现问题！！！！！", e)
    except Exception as e:
        print("下载异常:", e)
        raise e

def create_pdf(image_files, pdf_file):
    total_height = 0
    width = 0
    for image_path in image_files:
        img = Image.open(image_path)
        total_height += img.height
        width = img.width
    custom_page_size = (width, total_height)
    c = canvas.Canvas(pdf_file, pagesize=custom_page_size)
    x = 0  # 图片在PDF中的x坐标
    y = total_height  # 图片在PDF中的起始y坐标, 注意这个坐标是左下方
    for image_path in image_files:
        img = Image.open(image_path)
        y = y - img.height
        result = c.drawImage(image_path, x, y, img.width, img.height)
    # 结束PDF页面的编辑
    c.showPage()
    c.save()
    print("PDF文件已创建:", pdf_file)

def download_image_for_thread(image_url, save_path):
    # 已下载过， 且转换过，跳过
    if os.path.exists(save_path):
        return
    result = download_image(image_url, save_path)
    # 下载失败，资源失效，跳过
    if not result:
        return

def process_csv(csv_file, column_name, image_path, pdf_path):
    df = pd.read_csv(csv_file, encoding="UTF-8")
    grouped_data = df.groupby(column_name)
    pdf_images = []
    for group_name, group_data in grouped_data:
        try:
            group_name = clean_filename(group_name)
            group_pdf_file = os.path.join(pdf_path, f"{group_name}.pdf")
            # 校验存在
            if os.path.exists(group_pdf_file):
                continue
            image_files = []
            # 多线程下载
            threads = []

            for idx, row in group_data.iterrows():
                image_url = row['srcLink']  # 假设图片链接在CSV文件的'image_url'列中
                image_name = f"{group_name}_{idx}.jpg"
                save_path = os.path.join(image_path, image_name)
                image_files.append(save_path)
                thread = threading.Thread(target=download_image_for_thread, args=(image_url, save_path))
                threads.append(thread)
                thread.start()
                # 控制线程数量
                while threading.active_count() >= max_threads:
                    pass
            for thread in threads:
                thread.join()
            create_pdf(image_files, group_pdf_file)
            pdf_images.append(group_pdf_file)
        except Exception as e:
            logging.error("%s 生成pdf报错: %s", group_pdf_file, str(e), exc_info=True)
            print("生成pdf报错:", e)
    return pdf_images

def clean_filename(filename):
    # 移除非法字符
    cleaned_filename = re.sub(r'[\\/*?:"<>|]', '!', filename)
    cleaned_filename = cleaned_filename.replace("\n", " ")
    return cleaned_filename

def downloadFromCSV(folder_path, file_name):
    csv_file = os.path.join(folder_path, file_name)  # CSV文件路径
    csv_file_name = os.path.splitext(file_name)[0]
    image_path = os.path.join(csv_file_name, 'images')
    pdf_path = csv_file_name + "_pdf"
    if not os.path.exists(image_path):
        os.makedirs(image_path)
    if not os.path.exists(pdf_path):
        os.makedirs(pdf_path)
    column_name = 'getLink'  # 要按照其进行聚合的列名
    pdf_images = process_csv(csv_file, column_name, image_path, pdf_path)


if __name__ == "__main__":
    folder_path = '.\downloadCSVList'
    # 配置日志记录器
    logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    for file_name in os.listdir(folder_path):
        downloadFromCSV(folder_path=folder_path, file_name=file_name)