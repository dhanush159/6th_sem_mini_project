# import requests
# from bs4 import BeautifulSoup
# import os
# from PIL import Image, UnidentifiedImageError
# from io import BytesIO
# import re

# def is_valid_text(txt):
#     if len(txt) < 20:
#         return False
#     if re.match(r'^\[.*?\]$', txt):
#         return False
#     return True

# def sanitize_filename(filename):
#     # Remove characters that are not allowed in Windows filenames
#     sanitized_filename = re.sub(r'[<>:"/\\|?*\x00-\x1F\x7F]', '_', filename)
#     return sanitized_filename[:255]  # Limit filename length to 255 characters

# def scrape(url, folder):
#     resp = requests.get(url)
#     if resp.status_code != 200:
#         print(f"Failed to retrieve the webpage. Status code: {resp.status_code}")
#         return

#     soup = BeautifulSoup(resp.content, 'html.parser')
#     for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form']):
#         tag.decompose()

#     txt = soup.get_text(separator='\n')
#     lines = (line.strip() for line in txt.splitlines())
#     chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
#     txt = '\n'.join(chunk for chunk in chunks if chunk)
#     valid_lines = [line for line in txt.split('\n') if is_valid_text(line)]
#     filtered_txt = '\n'.join(valid_lines)

#     imgs = soup.find_all('img')
#     if not os.path.exists(folder):
#         os.makedirs(folder)

#     for img in imgs:
#         img_url = img.get('src')
#         if img_url:
#             if img_url.startswith('//'):
#                 img_url = 'http:' + img_url
#             elif img_url.startswith('/'):
#                 img_url = url + img_url

#             img_name = os.path.basename(img_url)
#             img_resp = requests.get(img_url)
#             if img_resp.status_code == 200:
#                 try:
#                     img_data = img_resp.content
#                     img = Image.open(BytesIO(img_data))
#                     if img.size[0] > 100 and img.size[1] > 100 and 'svg' not in img_name:
#                         # Sanitize image filename
#                         img_name = sanitize_filename(img_name)

#                         with open(os.path.join(folder, img_name), 'wb') as f:
#                             f.write(img_data)
#                             print(f"Downloaded {img_name}")
#                     else:
#                         print(f"Skipped {img_name} (image is smaller than 100x100 pixels or is SVG)")
#                 except UnidentifiedImageError:
#                     print(f"Skipped {img_name} (unidentified image)")
#                 except Exception as e:
#                     print(f"An error occurred while processing {img_name}: {e}")
#     print(filtered_txt)
#     return filtered_txt

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import re

# Function to check if a text line is valid
def is_valid_text(txt):
    if len(txt) < 20:
        return False
    if re.match(r'^\[.*?\]$', txt):
        return False
    return True

# Function to sanitize filename
def sanitize_filename(filename):
    # Remove characters that are not allowed in Windows filenames
    sanitized_filename = re.sub(r'[<>:"/\\|?*\x00-\x1F\x7F]', '_', filename)
    return sanitized_filename[:255]  # Limit filename length to 255 characters

# Function to scrape text and images from a website
def scrape(url, folder='output'):
    try:
        # Fetch HTML content
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"Failed to retrieve the webpage. Status code: {resp.status_code}")
            return

        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Remove unwanted tags
        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form']):
            tag.decompose()

        # Extract and clean text
        txt = soup.get_text(separator='\n')
        lines = (line.strip() for line in txt.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        txt = '\n'.join(chunk for chunk in chunks if chunk)
        valid_lines = [line for line in txt.split('\n') if is_valid_text(line)]
        filtered_txt = '\n'.join(valid_lines)
        
        # Find all img tags
        imgs = soup.find_all('img')
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        for img in imgs:
            img_url = img.get('src')
            if img_url:
                # Handle relative URLs
                img_url = urljoin(url, img_url)

                # Extract image filename from URL
                img_filename = os.path.basename(urlparse(img_url).path)

                # Sanitize filename
                img_filename = sanitize_filename(img_filename)

                # Download and save image
                try:
                    img_resp = requests.get(img_url, headers=headers, timeout=10)
                    if img_resp.status_code == 200:
                        img_data = img_resp.content
                        img = Image.open(BytesIO(img_data))
                        if img.size[0] > 100 and img.size[1] > 100 and 'svg' not in img_filename:
                            with open(os.path.join(folder, img_filename), 'wb') as f:
                                f.write(img_data)
                                print(f"Downloaded {img_filename}")
                        else:
                            print(f"Skipped {img_filename} (image is smaller than 100x100 pixels or is SVG)")
                    else:
                        print(f"Failed to download {img_filename}. Status code: {img_resp.status_code}")
                except UnidentifiedImageError:
                    print(f"Skipped {img_filename} (unidentified image)")
                except Exception as e:
                    print(f"An error occurred while processing {img_filename}: {e}")

        return filtered_txt
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
