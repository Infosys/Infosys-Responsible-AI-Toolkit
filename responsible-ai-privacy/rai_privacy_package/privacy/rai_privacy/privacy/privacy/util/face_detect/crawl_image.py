import argparse
from tqdm import tqdm
from google_images_search import GoogleImagesSearch
import os 

GCS_CX = '495179597de2e4ab6'
GCS_DEVELOPER_KEY= os.getenv('GCS_DEVELOPER_KEY')

def crawl_image(query_text, save_dir, num=10, fileType='jpg|png', imgSize='MEDIUM'):
    gis = GoogleImagesSearch(GCS_DEVELOPER_KEY, GCS_CX)

    # define search params:
    _search_params = {
        'q': query_text,
        'num': num,
        'fileType': fileType,
        'imgSize': imgSize
    }

    gis.search(search_params=_search_params)
    for image in tqdm(gis.results()):
        image.download(save_dir)
        # image.resize(500, 500)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-q", "--query", type=str, help="String to query image")
    ap.add_argument("-d", "--out-dir", type=str, help="Path to download image")
    ap.add_argument("-n", "--number", type=int, choices=range(0, 10000), help="Number of result")
    ap.add_argument("-f", "--file-type", type=str, help="File type of result")
    ap.add_argument("-s", "--image-size", type=str, help="Image size of result")

    args = ap.parse_args()
    crawl_image(args.query, args.out_dir, num=args.number, fileType=args.file_type, imgSize=args.image_size)