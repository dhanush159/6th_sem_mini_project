import requests
from bs4 import BeautifulSoup
import os
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import re

def is_valid_text(txt):
    if len(txt) < 20:
        return False
    if re.match(r'^\[.*?\]$', txt):
        return False
    return True

def sanitize_filename(filename):
    # Remove characters that are not allowed in Windows filenames
    sanitized_filename = re.sub(r'[<>:"/\\|?*\x00-\x1F\x7F]', '_', filename)
    return sanitized_filename[:255]  # Limit filename length to 255 characters

def scrape(url, folder):
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Failed to retrieve the webpage. Status code: {resp.status_code}")
        return

    soup = BeautifulSoup(resp.content, 'html.parser')
    for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form']):
        tag.decompose()

    txt = soup.get_text(separator='\n')
    lines = (line.strip() for line in txt.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    txt = '\n'.join(chunk for chunk in chunks if chunk)
    valid_lines = [line for line in txt.split('\n') if is_valid_text(line)]
    filtered_txt = '\n'.join(valid_lines)

    imgs = soup.find_all('img')
    if not os.path.exists(folder):
        os.makedirs(folder)

    for img in imgs:
        img_url = img.get('src')
        if img_url:
            if img_url.startswith('//'):
                img_url = 'http:' + img_url
            elif img_url.startswith('/'):
                img_url = url + img_url

            img_name = os.path.basename(img_url)
            img_resp = requests.get(img_url)
            if img_resp.status_code == 200:
                try:
                    img_data = img_resp.content
                    img = Image.open(BytesIO(img_data))
                    if img.size[0] > 100 and img.size[1] > 100 and 'svg' not in img_name:
                        # Sanitize image filename
                        img_name = sanitize_filename(img_name)

                        with open(os.path.join(folder, img_name), 'wb') as f:
                            f.write(img_data)
                            print(f"Downloaded {img_name}")
                    else:
                        print(f"Skipped {img_name} (image is smaller than 100x100 pixels or is SVG)")
                except UnidentifiedImageError:
                    print(f"Skipped {img_name} (unidentified image)")
                except Exception as e:
                    print(f"An error occurred while processing {img_name}: {e}")
    print(filtered_txt)
    return filtered_txt
