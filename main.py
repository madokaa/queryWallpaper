import getopt
import glob
import sys
from os import path, listdir, system
from functools import reduce
from multiprocessing import Pool

import json

from PIL import Image

wallpaper_dir = 'D:/Wallpaper'


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


def get_file_info(file_name):
    return file_name, phash(file_name), path.getsize(file_name)


def init_index(img_dir):
    """ 初始化壁纸文件索引 """
    data_path = f'{path.dirname(__file__)}/wallpaper_data.json'
    included_extensions = ['jpg', 'jpeg', 'bmp', 'png']
    file_names = [f'{img_dir}/{fn}' for fn in listdir(img_dir) if any(fn.endswith(ext) for ext in included_extensions)]

    # 读取现有索引,并过滤已索引过的文件
    if path.exists(data_path):
        with open(f'{path.dirname(__file__)}/wallpaper_data.json', 'r', encoding='utf-8') as f:
            wallpaper_data = json.loads(f.read())
    else:
        wallpaper_data = []
    w_size = {}
    for item in wallpaper_data:
        w_size[item[0]] = item[2]
    file_names = list(filter(lambda fn: w_size.get(fn) is None or w_size.get(fn) != path.getsize(fn), file_names))

    # 索引文件(大于等于32个图片启用多进程)
    if len(file_names) == 0:
        return
    elif len(file_names) < 32:
        wallpaper_data = [get_file_info(n) for n in file_names]
    else:
        with Pool() as pool:
            wallpaper_data += pool.map(get_file_info, file_names)

    with open(f'{path.dirname(__file__)}/wallpaper_data.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(wallpaper_data, ensure_ascii=False, indent=2))


def query_wallpaper(monitor_id: int):
    """ 查找并打开当前使用壁纸 """
    if monitor_id is None:
        file_paths = glob.glob(path.expandvars(f'%APPDATA%/Microsoft/Windows/Themes/Transcoded_*'))
    else:
        file_paths = [path.expandvars(f'%APPDATA%/Microsoft/Windows/Themes/Transcoded_{monitor_id:03d}')]
    hs = [phash(i) for i in file_paths]

    with open(f'{path.dirname(__file__)}/wallpaper_data.json', 'r', encoding='utf-8') as f:
        wallpaper_data = json.load(f)

    for f in wallpaper_data:
        for h in hs:
            if hamming_distance(h, f[1]) <= 3:  # 默认5
                print(hamming_distance(h, f[1]), f, h)
                system(f'start "" "{f[0]}"')


def main(argv):
    init_index(wallpaper_dir)

    monitor_name = ''
    try:
        opts, args = getopt.getopt(argv, "hn:", ["name=", ])
    except getopt.GetoptError:
        print('main.py -n <monitor_name>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -n <monitor_name>')
            break
        elif opt in ("-n", "--name"):
            monitor_name = arg  # r'\\.\DISPLAY*'
    monitor_id = int(monitor_name[-1:]) - 1 if monitor_name != '' else None
    query_wallpaper(monitor_id)


if __name__ == '__main__':
    main(sys.argv[1:])
