import json
import os
import sys
from functools import reduce
from multiprocessing import Pool

from PIL import Image

wallpaper_dir = 'D:\\Wallpaper'


def phash(img):
    """ 计算pHash（8*8像素，64位灰度） """
    if isinstance(img, str):
        img = Image.open(img)
    img = img.resize((8, 8), Image.ANTIALIAS).convert('L')
    avg = reduce(lambda x, y: x + y, img.getdata()) / 64.
    return reduce(lambda x, y: x | (y[1] << y[0]), enumerate(map(lambda i: 0 if i < avg else 1, img.getdata())), 0)


def hamming_distance(a, b):
    """ 计算汉明距离

    小于或等于5说明两张图片很相似,大于10就很可能是两张不同的图片
    """
    return bin(a ^ b).count('1')


def get_phash(file_name):
    return file_name, phash(file_name)


def init_index(path):
    """ 初始化壁纸文件索引 """
    included_extensions = ['jpg', 'jpeg', 'bmp', 'png', 'gif']
    file_names = [f'{path}\\{fn}' for fn in os.listdir(path) if any(fn.endswith(ext) for ext in included_extensions)]

    pool = Pool()
    wallpaper_data = pool.map(get_phash, file_names)
    pool.close()
    pool.join()

    with open(f'{os.path.dirname(__file__)}\\wallpaper_data.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(wallpaper_data, ensure_ascii=False, indent=2))


def query_wallpaper():
    """ 查找并打开当前使用壁纸 """
    path = '%APPDATA%\\Microsoft\\Windows\\Themes\\TranscodedWallpaper'
    h = phash(Image.open(os.path.expandvars(path)))
    with open(f'{os.path.dirname(__file__)}\\wallpaper_data.json', 'r', encoding='utf-8') as f:
        wallpaper_data = json.load(f)
    for f in wallpaper_data:
        if hamming_distance(h, f[1]) <= 5:
            print(hamming_distance(h, f[1]), f, h)
            os.system(f'start "" "{f[0]}"')


if __name__ == '__main__':
    if 'init' in sys.argv[1:]:
        init_index(wallpaper_dir)
    else:
        query_wallpaper()
