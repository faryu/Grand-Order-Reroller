import time
import os, os.path
from settings import PB_KEY, POINTS_THRESHOLD
from main import ROLLS_FOLDER

CLOSENESS_THRESHOLD = 0.8

SS_5 = 700
S_5 = 500
A_5 = 300
B_5 = 200

SS_4 = 100
S_4 = 100
A_4 = 60
B_4 = 40
C_4 = 20
D_4 = 10

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

def identify_summons(image_path):
    import cv2
    import numpy as np

    image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2GRAY)
    summons = []
    points = 0

    for file_name, (point_value, actual_name) in possible_summons.items():
        template = cv2.imread(os.path.join('screenshots', 'summons', file_name + '.png'), cv2.IMREAD_GRAYSCALE)

        res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= CLOSENESS_THRESHOLD)

        for pt in zip(*loc[::-1]):

            # Due to weird behaviour, only add one instance of each summon
            if actual_name in summons:
                continue
            summons.append(actual_name)
            points += point_value

    return (summons, points) 

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
    summons, points = [], 0

    if os.path.isfile(file):
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
                    analyze(file, ROLLS_FOLDER)
        except Exception as e:
            print(repr(e))
            if NOTIF_ENABLE:
                pb.push_note('Ay Arshad, we fucked up - Mal', repr(e))
        time.sleep(60)
