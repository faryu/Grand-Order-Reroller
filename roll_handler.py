import time
import os, os.path
from settings import PB_KEY, POINTS_THRESHOLD
from main import ROLLS_FOLDER
from PIL import Image
import cv2
import numpy as np
import shutil
from skimage.measure import compare_ssim as ssim

CLOSENESS_THRESHOLD = 0.8
UNKNOWN_CARD_DIR = "unknown_card"
CARD_DIR = os.path.join('screenshots', 'summons')
CARD_IGNORE_DIR = 'ignore'
CARD_RATED_DIR = 'rating'

rating = {
    '5SS': 700,
    '5S': 500,
    '5A': 300,
    '5B': 200,
    '4SS': 150,
    '4S': 100,
    '4A': 60,
    '4B': 40,
    '4C': 20,
    '4D': 10
}

SS_5 = rating['5SS']
S_5 = rating['5S']
A_5 = rating['5A']
B_5 = rating['5B']

SS_4 = rating['4SS']
S_4 = rating['4S']
A_4 = rating['4A']
B_4 = rating['4B']
C_4 = rating['4C']
D_4 = rating['4D']

CARD_IGNORE = -1

try:
    from pushbullet import Pushbullet
    pb = Pushbullet(PB_KEY)
    NOTIF_ENABLE = True
except:
    NOTIF_ENABLE = False

# http://fategrandorder.gamea.co/c/nnp3zd71

possible_summons = {
    'waver': (SS_5, 'Waver'),
    'gil': (A_5, 'Gilgamesh'),
    'gil_large': (A_5, 'Gilgamesh'),
    'saber': (B_5, 'Arturia'),
    'saber_large': (B_5, 'Arturia'),
    'jeanne': (A_5, 'Jeanne'),
    'jeanne_large': (A_5, 'Jeanne'),
    'altera': (A_5, 'Altera'),
    'vlad': (A_5, 'Vlad'),
    'vlad_large': (A_5, 'Vlad'),
    'scope': (60, 'Kaleidoscope'),
    'scope_large': (60, 'Kaleidoscope'),
    'herc': (SS_4, 'Heracles'),
    'herc_large': (SS_4, 'Heracles'),
    'emiya': (B_4, 'EMIYA'),
    'emiya_large': (B_4, 'EMIYA'),
    'loz': (45, 'Limited.Over Zero'),
    'loz_large': (45, 'Limited.Over Zero'),
    'hf': (45, 'Heaven\'s Feel'), 
    'hf_large': (45, 'Heaven\'s Feel'),   
    'liz': (C_4, 'Elizabeth'),   
    'liz_large': (C_4, 'Elizabeth'), 
    'carmilla': (A_4, 'Cermilla'),
    'sieg': (C_4, 'Siegfried'),
    'sieg_large': (C_4, 'Siegfried'),
    'chevalier': (B_4, 'Chevalier'),
    'stheno': (D_4, 'Stheno'),
    'martha': (B_4, 'Martha'),
    'marie_antoinette': (B_4, 'Marie'),
    'craft': (40, 'Formal Craft'),
    'lancelot': (B_4, 'Lancelot'),
    'lancelot_large': (B_4, 'Lancelot'),
    'prisma': (40, 'Prisma Cosmos'),
    'prisma_large': (40, 'Prisma Cosmos'),
    'tamacat': (B_4, 'Tamano-cat'),
    'tamacat_large': (B_4, 'Tamano-cat'),
    'around': (30, 'Imaginary Around'),
    'atalanta': (C_4, 'Atalante'),
    'atalanta_large': (C_4, 'Atalante'),
    'lily': (C_4, 'Saber Lily'),
    'lily_large': (C_4, 'Saber Lily'),
    'nursery_rhyme': (A_4, 'Nursery Rhyme'),
    'helena_blavatsky': (B_4, 'Helena Blavatsky')
}

def send_notif(points, summons):
    if not NOTIF_ENABLE:
        return
    pb.push_note('Roll with {} points.'.format(points), ', '.join(summons))
    time.sleep(2)

IMAGE_CACHE = {}
def get_template(name):
    filepath = os.path.join(CARD_DIR, name + '.png') if not name.startswith(CARD_DIR) else name
    if filepath not in IMAGE_CACHE:
        IMAGE_CACHE[filepath] = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    return IMAGE_CACHE[filepath]

def identify_summons(image_path):
    #image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2GRAY)
    summons = []
    points = 0
    
    card_idx = 0
    cards = get_cards(image_path)
    for card in cards:
        detected = False

        card_gray = cv2.cvtColor(card, cv2.COLOR_BGR2GRAY)
        #star = get_template('star')

        #theight, twidth = star.shape
        #cheight, cwidth = card_gray.shape

        #if cheight < theight or cwidth < twidth:
        #    continue

        #res = cv2.matchTemplate(card_gray, star, cv2.TM_SQDIFF_NORMED)
        #loc = np.where(res >= CLOSENESS_THRESHOLD)
        #star_detected = False
        #for pt in zip(*loc[::-1]):
        #    star_detected = True
        #    break
        #if not star_detected:
        #    continue

        bg_min = None
        bg_max = None
        for file_name, (point_value, actual_name) in possible_summons.items():
            template = get_template(file_name)
            if template is None:
                continue

            theight, twidth = template.shape
            cheight, cwidth = card_gray.shape

            if cheight < theight or cwidth < twidth:
                continue

            if cheight == theight and cwidth == twidth and 'background' in file_name:
                s = ssim(card_gray, template)
                if bg_min is None or s < bg_min:
                    bg_min = s
                if bg_max is None or s > bg_max:
                    bg_max = s
            else:
                res = cv2.matchTemplate(card_gray, template, cv2.TM_CCOEFF_NORMED)
                loc = np.where(res >= CLOSENESS_THRESHOLD)

                for pt in zip(*loc[::-1]):
                    # Due to weird behaviour, only add one instance of each summon
                    if actual_name in summons:
                        continue
                
                    detected = True
                    if point_value == CARD_IGNORE:
                        break
            if detected:
                if point_value != CARD_IGNORE:
                    summons.append(actual_name)
                    points += point_value
                break

        if not detected:
            if bg_max is not None and bg_max > 0.8:         # Skip background images
                continue
            if not os.path.exists(UNKNOWN_CARD_DIR):
                os.mkdir(UNKNOWN_CARD_DIR)
            filename = os.path.basename(image_path)
            cv2.imwrite(os.path.join(UNKNOWN_CARD_DIR, "{:.2f}_{:.2f}_{}_{}".format(
                bg_max if bg_max is not None else 0, 
                bg_min if bg_min is not None else 0, 
                card_idx, 
                filename)), card)
        card_idx += 1
    return (summons, points) 

CARD_WIDTH = 165
CARD_HEIGHT = 181
CARD_HEIGHT_LAST_ROW = 137

def get_cards(file):
    im = Image.open(file)
    images = []

    for row in range(0, 4):
        top = (23 if row < 2 else 552) + 200 * (row%2)
        for column in range(0, 6):
            left = (5 if row < 2 else 21) + 187 * column
            serv = Image.new('RGB', (CARD_WIDTH, CARD_HEIGHT if row < 3 else CARD_HEIGHT_LAST_ROW))
            serv.paste(im, (-left, -top))

            card = cv2.cvtColor(np.array(serv), cv2.COLOR_RGB2BGR)
            images.append(card)

    return images

def analyze(file, rolls_folder = 'rolls'):
    file_abs = os.path.join(rolls_folder, file)
    if not os.path.isfile(file_abs):
        return

    new_name, summons, points = gen_new_folder_name(file_abs, rolls_folder)
    
    new_dir = os.path.join(rolls_folder, new_name)
    new_name = os.path.join(new_dir, file)

    if not os.path.exists(new_dir):
        os.mkdir(new_dir)
    os.rename(file_abs, new_name)

    if points >= POINTS_THRESHOLD:
        send_notif(points, summons)

    return (summons, points)

def gen_new_folder_name(file, rolls_folder = 'rolls'):
    summons, points = identify_summons(file)
    new_folder = os.path.join('{:0>4}_{}'.format(points, ('-'.join(summons) if points else 'Shit Roll')))[1:]

    return (new_folder, summons, points)

def removeEmptyfolders(path):
    for (_path, _dirs, _files) in os.walk(path, topdown=False):
        if _files: continue # skip remove
        try:
            os.rmdir(_path)
            print('Remove :', _path)
        except OSError as ex:
            print('Error :', ex)

if __name__ == '__main__':
    print('Reroll analyzer started...')

    if os.path.isdir(UNKNOWN_CARD_DIR):
        shutil.rmtree(UNKNOWN_CARD_DIR)

    rating_dir = os.path.join(CARD_DIR, CARD_RATED_DIR)
    for star_dir in os.listdir(rating_dir):
        if star_dir not in rating:
            print('unexpected rating entry: ' + star_dir)
            continue
        rating_val = rating[star_dir]
        for file in os.listdir(os.path.join(rating_dir, star_dir)):
            possible_summons[os.path.join(CARD_RATED_DIR, star_dir, file[:-4])] = (rating_val, file[:-4])

    for root, dirs, files in os.walk(os.path.join(CARD_DIR, CARD_IGNORE_DIR), topdown=False):
        for file in files:
            possible_summons[os.path.join(root, file)] = (CARD_IGNORE, '')

    if True:
        for root, dirs, files in os.walk(ROLLS_FOLDER, topdown=False):
            for name in files:
                if os.path.normpath(root) != os.path.normpath(ROLLS_FOLDER):
                    file = os.path.join(root, name)
                    os.rename(file, os.path.join(ROLLS_FOLDER, name))
        removeEmptyfolders(ROLLS_FOLDER)
    while True:
        try:
            for file in os.listdir(ROLLS_FOLDER):
                print('Scanning file: {}'.format(file))
                analyze(file, ROLLS_FOLDER)
        except Exception as e:
            print(repr(e))
            if NOTIF_ENABLE:
                pb.push_note('Ay Arshad, we fucked up - Mal', repr(e))
        time.sleep(60)
