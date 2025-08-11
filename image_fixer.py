#!/usr/bin/env python
import os
import sys
import re
import zipfile
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image
import shutil
import time
from tqdm import tqdm

def download_image(image_url, save_dir):
    """
    下载图片到指定目录（返回相对路径），失败时重试多次
    """
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(image_url, timeout=15)
            response.raise_for_status()

            # 提取文件名
            img_name = os.path.basename(urlparse(image_url).path)
            if not img_name:  # 避免空文件名
                img_name = "img_" + str(abs(hash(image_url))) + ".jpg"

            img_path = os.path.join(save_dir, img_name)

            # 保存图片
            image = Image.open(BytesIO(response.content))
            image.save(img_path)
            return img_name  # 只返回文件名
        except Exception as e:
            print(f"[图片下载失败][第{attempt}次] {image_url} -> {e}")
            if attempt == max_retries:
                return None
            else:
                time.sleep(2)  # 等待2秒后重试

def extract_epub(epub_file, temp_dir):
    """ 解压 EPUB 到临时目录 """
    with zipfile.ZipFile(epub_file, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

def update_xhtml_images(xhtml_path, images_dir):
    """ 修改 XHTML 中的 <图片>URL 为 <img src="../images/..."> """
    with open(xhtml_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    changed = False
    for p_tag in soup.find_all('p'):
        text_content = p_tag.get_text(strip=True)
        if text_content.startswith("<图片>"):
            img_url = text_content[len("<图片>"):]
            if img_url.startswith("http") and "mitemin.net" in img_url:
                img_filename = download_image(img_url, images_dir)
                if img_filename:
                    img_tag = soup.new_tag('img', src=f"../images/{img_filename}")
                    p_tag.clear()
                    p_tag.append(img_tag)
                    changed = True

    if changed:
        with open(xhtml_path, 'w', encoding='utf-8') as file:
            file.write(str(soup))

def rebuild_epub(temp_dir, output_epub_file):
    """ 重新打包 EPUB（保证 mimetype 文件第一无压缩） """
    epub_files = []
    for foldername, subfolders, filenames in os.walk(temp_dir):
        for filename in filenames:
            filepath = os.path.join(foldername, filename)
            arcname = os.path.relpath(filepath, temp_dir)
            epub_files.append((filepath, arcname))

    with zipfile.ZipFile(output_epub_file, 'w') as zf:
        # mimetype 必须无压缩且第一个
        for filepath, arcname in epub_files:
            if arcname == "mimetype":
                zf.write(filepath, arcname, compress_type=zipfile.ZIP_STORED)
        # 其他文件正常压缩
        for filepath, arcname in epub_files:
            if arcname != "mimetype":
                zf.write(filepath, arcname, compress_type=zipfile.ZIP_DEFLATED)

def fix_epub_images(epub_file, output_epub_file):
    """ 主流程：解压 -> 修改 -> 打包 """
    temp_dir = "temp_epub"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    extract_epub(epub_file, temp_dir)

    # 确保 OEBPS/images 目录存在
    images_dir = os.path.join(temp_dir, "OEBPS", "images")
    os.makedirs(images_dir, exist_ok=True)

    # 处理所有 XHTML 文件
    text_dir = os.path.join(temp_dir, "OEBPS", "Text")
    for root, dirs, files in os.walk(text_dir):
        for file in tqdm(files):
            if file.endswith(".xhtml"):
                update_xhtml_images(os.path.join(root, file), images_dir)

    rebuild_epub(temp_dir, output_epub_file)

    # 清理临时目录
    shutil.rmtree(temp_dir)
    print(f"[完成] 新 EPUB 已保存到: {output_epub_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python fix_epub_images.py <输入EPUB> <输出EPUB>")
        sys.exit(1)
    epub_file = sys.argv[1]
    output_epub_file = sys.argv[2]
    if not os.path.isfile(epub_file):
        print(f"[错误] 找不到输入文件: {epub_file}")
        sys.exit(1)
    fix_epub_images(epub_file, output_epub_file)
