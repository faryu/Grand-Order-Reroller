import cv2
import time
import datetime
import pyautogui
import numpy as np
import os, os.path
import pyperclip
import datetime
from PIL import Image
from settings import PASSWORD, NAME

############
# Settings #
PAUSE_TIME = 1.4
TIMING_MULT = 1.5
CLOSENESS_THRESHOLD = 0.8
ROLLS_FOLDER = 'rolls'
############

pyautogui.PAUSE = PAUSE_TIME
pyautogui.FAILSAFE = True

HOME_BUTTON = {'x': 1301, 'y': 676}
GO_ICON = {'x': 1049, 'y': 379}
APP_INFO = {'x': 44, 'y': 185}
CLEAR_DATA_ICON = {'x': 420, 'y': 380}
SKIP_BUTTON = {'x': 1200, 'y': 70}
CONFIRM = {'x': 830, 'y': 600}
ATTACK = {'x': 1125, 'y': 630}
EXCAL = {'x': 400, 'y': 250}
NAME_FIELD = {'x': 900, 'y': 400}
NAME_CONFIRM = {'x': 900, 'y': 500}
NAME_CONFIRM_2 = {'x': 850, 'y': 600}
NEXT = {'x': 1110, 'y': 700}
CLOSE = {'x': 640, 'y': 590}
MENU = {'x': 1190, 'y': 715}
LEFT_EDGE = {'x': 10,'y': 400}
EXIT_TOP_RIGHT = {'x': 1248,'y': 62}

SERV_HEIGHT = 540
CES_HEIGHT = 350
BIND_CODE_HEIGHT = 70

WIN_X = 0
WIN_Y = 0

def wait(given_time):
    time.sleep(TIMING_MULT * given_time)

def touch(x, y):
    while True:
        if loading_image_on_screen():
            continue
        if not image_is_on_screen('window'):
            check_window()
            continue
        break
    pyautogui.click(x=WIN_X+x, y=WIN_Y+y)

def move_to(x, y):
    pyautogui.moveTo(WIN_X + x, WIN_Y + y)

def drag_to(x, y, duration=0, button='left', tween=pyautogui.linear):
    pyautogui.dragTo(WIN_X + x, WIN_Y + y, duration=duration, button=button, tween=tween)

def touch_until_visible(x, y, image):
    while True:
        touch(x,y)
        result = wait_until(image, maxTries = 3)
        if result is not None:
            break

def skip_scene(skip, next = None):
    arr = [skip]
    maxTries = 1
    if next is not None: 
        arr.append(next)
        maxTries = None
    
    wait_until(skip)
    while wait_until(*arr, maxTries=maxTries) == 0:
        touch(**SKIP_BUTTON)
        touch(**CONFIRM)
        if next is not None:
            wait_until(next, maxTries = 2)
        else:
            wait(2)

def get_window_image():
    return cv2.cvtColor(np.array(pyautogui.screenshot(region=(WIN_X, WIN_Y, 1300, 750))), 
                    cv2.COLOR_BGR2GRAY)

IMAGE_CACHE = {}
def get_template(name):
    filepath = os.path.join('screenshots', name + '.png')
    if filepath not in IMAGE_CACHE:
        IMAGE_CACHE[filepath] = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    return IMAGE_CACHE[filepath]

def locate_center(template_name, window_image = None):
    try:
        template = get_template(template_name)
        
        if template is None: # Image not found
            return None

        image = window_image if window_image is not None else get_window_image()

        res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= CLOSENESS_THRESHOLD)

        for pt in zip(*loc[::-1]):
            min_y = min(loc[0])
            max_y = max(loc[0])
            min_x = min(loc[1])
            max_x = max(loc[1])
            x = int((max_x - min_x) / 2 + min_x)
            y = int((max_y - min_y) / 2 + min_y)
            return x, y
        return None
    except Exception as e:
        raise

def wait_locate_center(name):
    while True:
        loc = locate_center(name)
        if loc is None:
            continue
        return loc

def goto_home():
    global GO_ICON
    while True:
        touch(**HOME_BUTTON)
        wait_until('app')
        apploc = locate_center('app')
        if apploc is None:
            continue
        GO_ICON = {'x': apploc[0], 'y': apploc[1]}
        break


def close_app():
    goto_home()
    touch(x=1300, y=700)

    while True:
        result = wait_until('close_app_screen', 'close_app_empty', maxTries = 2)

        if result == 0:
            # App Switcher
            move_to(1150, 400)                                      # Move Cursor Over GO
            drag_to(1150, 100, duration = .5)
            wait(1)
        elif result == 1:                                           # All apps closed
            break
        elif result == None:                                        # Still apps open, but not fate
            break

def clear_app():
    while True:
        close_app()
        goto_home()
    
        # Open App Info
        move_to(**GO_ICON)
        drag_to(**APP_INFO, duration=5, tween=pyautogui.easeInOutExpo)
    
        result = wait_until('app_info', maxTries=5)
        if result is None:
            continue
        touch(982, 596)                                                 # Press delete data
        wait(1)
        touch(812, 505)                                                 # Press Ok
        break

def select_card(card_no):
    locations = {1: 140, 2: 390, 3: 650, 4: 900, 5: 1160}
    touch(x=locations[card_no], y=530)

def image_is_on_screen(template_name, window_image = None):
    return locate_center(template_name, window_image) is not None

def check_window():
    global WIN_X
    global WIN_Y

    window_msg = False
    while True:
        loc = window_location()
        if loc is None:
            if not window_msg:
                print("Waiting for window...")
                window_msg = True
            wait(1)
        else:
            WIN_X = loc[0]
            WIN_Y = loc[1]

            pyautogui.PAUSE = 0.0
            pyautogui.click(x=WIN_X+2, y=WIN_Y+2)
            pyautogui.PAUSE = PAUSE_TIME
            break    

def check_error(window_image):
    if window_image is None:
        window_image = get_window_image()
    for pos, image in enumerate(['connection_lost', 'support_designation_error']):
        if image_is_on_screen(image, window_image):
            raise ConnectionError(image)

def click_until(*images):
    pyautogui.PAUSE = 0.3
    
    while True:
        while not window_visible():
            wait(1)
        
        window_image = get_window_image()
        for pos, image in enumerate(images):
            if image_is_on_screen(image, window_image):
                pyautogui.PAUSE = PAUSE_TIME
                wait(0.5)
                return pos
        check_error(window_image)
        for _ in range(3):
            touch(**LEFT_EDGE)

def loading_image_on_screen(window_image = None):
    if window_image is None:
        window_image = get_window_image()
    for image in ['connecting', 'loading']:
        if image_is_on_screen(image, window_image):
            return True
    return False

def wait_until(*images, maxTries=None):
    start_time = datetime.datetime.now()
    timeout = 60
    if maxTries is not None:
        timeout += maxTries
    while True:
        window_image = get_window_image()
        for pos, image in enumerate(images):
            if image_is_on_screen(image, window_image):
                wait(0.5)
                return pos
        check_error(window_image)
        if loading_image_on_screen(window_image):
            start_time = datetime.datetime.now()
        else:
            delta = datetime.datetime.now() - start_time
            if maxTries is not None:
                if delta > datetime.timedelta(seconds=maxTries):
                    return None
            if delta > datetime.timedelta(seconds=timeout): # No reaction for some time?
                raise ConnectionError("timeout during wait: " + ','.join(images))

def wait_for_loading():
    notLoading = 0
    was_loading = False
    while notLoading < 3:
        if not loading_image_on_screen():
            notLoading += 1
        else:
            notLoading = 0
            was_loading = True
    return was_loading

def window_location():
    return pyautogui.locateOnScreen(os.path.join(
                                'screenshots', 
                                'window.png'))
def window_visible():
    return window_location() is not None

def scene_1_first_battle():
    wait_until('attack')
    touch(**ATTACK)
    select_card(1)
    select_card(2)
    select_card(3)

    wait_until('attack')
    touch(**ATTACK)
    select_card(1)
    select_card(2)
    select_card(3)

    wait_until('attack')
    touch(**ATTACK)
    select_card(1)
    select_card(2)
    select_card(3)

    wait_until('attack')
    touch(**ATTACK)
    wait(2)
    touch(**CONFIRM)
    select_card(1)
    select_card(2)
    select_card(3)
    wait_until('attack')

    touch(**ATTACK)
    touch(**EXCAL)
    select_card(1)
    select_card(2)
def scene_2_battle():
    wait_until('attack')
    touch(**ATTACK)
    select_card(2)
    select_card(3)
    select_card(1)

    wait_until('skill_selection')
    touch(x=166, y=607)                                         # Mash Ability
    touch(x=850, y=460)                                         # Confirm
    touch(x=644, y=455)                                         # Select Target
        
    wait_until('attack')
    touch(**ATTACK)
    wait(2)
    touch(x=1140, y=90)                                         # Battle Speed
    select_card(1)
    select_card(2)
    select_card(3)

    wait_until('battle_result_screen')
    click_until('next_button_after_battle')
    touch(**NEXT)

def scene_3_battle():
    wait_until('attack')
    touch(**ATTACK)
    select_card(1)
    select_card(2)
    select_card(3)

    wait_until('change_target_prompt')
    touch(x=300, y=330)                                         # Change Target
    touch(**ATTACK)
    select_card(1)
    select_card(3)
    select_card(2)

    wait_until('attack')
    touch(**ATTACK)
    select_card(1)
    select_card(2)
    select_card(3)

    wait_until('battle_result_screen')
    click_until('next_button_after_battle')
    touch(**NEXT)

def non_tutorial_battle():
    while True:
        result = wait_until('attack',
                            'battle_result_screen')

        if result == 0:
            touch(**ATTACK)
            select_card(1)
            select_card(2)
            select_card(3)
        else:
            break

    click_until('next_button_after_battle')
    touch(**NEXT)
    touch(x=320, y=650)                                         # Do Not Request friendship

def step_correction(scene):
    while True:
        result = wait_until(scene, maxTries=5)
        if result == 0:
            return None
        elif result == 1 or result == 2:
            wait_for_loading()
            continue
        else:
            possible_step = try_get_step()
            if possible_step is not None:
                return possible_step

def do_step(step):
    check_window()

    if step == 0:
        result = wait_until('skip_1', 'attack', 'name_prompt', maxTries=15)
        if result == 0:
            skip_scene('skip_1')
            return step
        elif result == 1:
            scene_1_first_battle()
        elif result == 2:
            return 2
        else:
            cor = step_correction('attack')
            if cor is not None:
                return cor
            return step
    elif step == 1:
        skip_scene('skip_2', 'name_prompt')
    elif step == 2:
        wait_until('name_prompt')
        touch(**NAME_FIELD)
        pyautogui.typewrite(NAME, interval = 0.25)
        touch(**NAME_CONFIRM)
        touch(**NAME_CONFIRM)
        touch(**NAME_CONFIRM_2)
    elif step == 3:
        skip_scene('skip_3', 'mission_x-a')
    elif step == 4:
        wait_until('mission_x-a')
        touch(x=650, y=390)                                         # Mission Select 1
        touch(x=1000, y=200)                                        # Mission Select 2
    elif step == 5:
        skip_scene('skip_4')
        # Second Battle
        scene_2_battle()
    elif step == 6:
        skip_scene('skip_5')
        while True:
            result = wait_until('saint_quartz_reward_screen_after_battle', 'mission_select_2')
            if result == 0:
                touch(x=640, y=430)
            elif result == 1:
                break
    elif step == 7:
        wait_until('mission_select_2')
        touch(x=640, y=430)                                         # Mission Select 1
        touch(x=1000, y=200)                                        # Mission Select 2
    elif step == 8:
        skip_scene('skip_6')
        # Third Battle
        scene_3_battle()
    elif step == 9:
        skip_scene('skip_7')
        if wait_until('saint_quartz_reward_screen_after_battle', maxTries=5) == 0:
            touch(**MENU)
    elif step == 10:
        # Summon
        result = wait_until('tutorial_summon_main_screen_prompt', 'bonus_close_button', 'tutorial_10x_button', maxTries=5)
        if result == 1:
            btn = wait_locate_center('bonus_close_button')
            touch(*btn)
        if result == 0 or result == 1:                                  # Reopening the app without having summoned
            wait_until('menu')
            touch(**MENU)                                               # Menu Button

            touch(x=540, y=680)                                         # Summon Button
            result = wait_until('tutorial_10x_button', maxTries = 5)

        if result is not None:
            touch(x=640, y=600)                                         # Select 10x Summon
            result = wait_until('enough_quartz', maxTries = 5)     # Wait for ok button. If it's not there, then it might be a reopened instances with formation as the next step
            if result is not None:
                touch(x=830, y=600)                                         # Confirm Summon

                click_until('next_button_during_tutorial_summon')
                touch(**NEXT)

                click_until('summon_button_after_tutorial_summon')

                # Finish Tutorial

                touch(x=760, y=700)                                         # Summon Button
                wait_until('setup_party_prompt_1')
                touch(**MENU)                                               # Menu Button

        wait_until('setup_party_prompt_2')
        touch(x=170, y=680)                                         # Formation Button
        wait_until('setup_party_prompt_3')
        touch(x=980, y=200)                                         # Party Setup
        wait_until('setup_party_prompt_4')
        touch(x=280, y=380)
        wait_until('setup_party_prompt_5')
        touch(x=360, y=310)                                         # Clear Overlay
        touch(x=360, y=310)                                         # Select Servant
        wait_until('setup_party_prompt_6')
        touch(**MENU)                                               # OK Button
        wait_until('setup_party_prompt_7')
        touch(x=100, y=75)                                          # Close Button
        
        while wait_until('setup_party_prompt_8', maxTries=1) == 0:
            touch(x=100, y=75)
    elif step == 11:
        # Final Battle - Non-deterministic                          

        wait_until('mission_select_3')
        touch(x=640, y=430)                                         # Mission Select 1
        touch(x=1000, y=200)                                        # Mission Select 2
        touch(x=1000, y=200)
        touch(x=500, y=300)                                         # Select Support

        touch_until_visible(**MENU, image='skip_8')                       # Start Button
        skip_scene('skip_8')

        non_tutorial_battle()
    elif step == 12:
        skip_scene('skip_9')
    elif step == 13:
        result = wait_until('login_bonus', maxTries=5)
        if result is not None:
            touch(**CLOSE)

            #while True:
            #    if image_is_on_screen('bonuses_received'):
            #        break
            #    touch(**CLOSE)
    elif step == 14:
        #touch(x=100, y=75)                                          # Close Button
        #wait(1)

        wait_until('menu')

        touch(x=440, y=700)                                         # Gift Box
        wait_until('receive_all_gifts_button')
        touch(x=1100, y=250)                                        # Receive All

        #click_until('lock')
        #touch(x=50, y=75)                                           # Close
        #click_until('lock')
        #touch(x=50, y=75)                                           # Close

        wait_until('all_gifts_received')
        touch(x=110, y=90)                                          # Close Prompt
    elif step == 15:
        wait_until('menu')

        # Multi Summon

        # wait_until('mission_select_protag')
        touch(**MENU)                                               # Menu Button
        touch(x=540, y=680)                                         # Summon Button        

        result = wait_until('first_multi_summon_info_prompt', maxTries=3)
        if result is None:
            result = wait_until('first_multi_summon_info_prompt', '1x_summon_button')

        if result == 0:
            touch(x=1250, y=65)                                         # Close Prompt

        #wait_until('10x_summon_button')
        #touch(x=840, y=600)                                         # Select 10x Summon
        #touch(x=840, y=600)                                         # Confirm Summon

        #click_until('first_multi_summon_ce_prompt')
        #touch(x=1250, y=55)
        #wait_until('next_button_during_tutorial_summon')
        #touch(**NEXT)
        #click_until('summon_button_after_tutorial_summon')

        # YOLO Summons

        #touch(x=770, y=700)                                         # Summon Button

        while True:
            result = wait_until('1x_summon_button',
                                'not_enough_quartz',
                                'enough_quartz',
                                'lock',
                                'lock_enabled',
                                'summon_screen_close_details')
            if result == 0:
                touch(x=450, y=600)                                     # 1x Summon
            elif result == 1:
                touch(x=440, y=600)
                break
            elif result == 2:                                       # More Summons
                touch(x=830, y=600)                                 # Confirm Summon
                wait(2)
                click_until('1x_summon_button','lock',
                            'lock_enabled',
                            'summon_screen_close_details')
            elif result == 3 or result == 4:
                touch(x=50, y=75)                                   # Close
            elif result == 5:
                touch(1247, 61)                                     # Close

        # Take Screenshots

        touch(**MENU)
        touch(x=175, y=675)                                         # Formation
        wait(1)
        
        result = wait_until('party_formation_prompt_close', 'party_formation_prompt_ready')
        if result == 0:
            touch(x=1250, y=70)                                         # Close
            wait_until('party_formation_prompt_ready')

        touch(x=1000, y=200)                                        # Party Setup
        touch(x=330, y=330)                                         # Open Servants

        wait_until('servant_list_ready')

        for _ in range(6):
            touch(x=1125, y=160)                                    # Sort by Rarity

        servants = pyautogui.screenshot(
                region=(WIN_X + 85, WIN_Y + 200, 1130, SERV_HEIGHT))

        touch(x=90, y=70)                                           # Close
        touch(x=335, y=510)                                         # Craft Essences
        
        result = wait_until('ce_prompt', maxTries=5)
        if result is None:
            result = wait_until('ce_prompt', 'ce_list_ready')

        if result == 0:
            touch(x=1075, y=710)                                        # Next
            touch(x=1250, y=70)                                         # Close
        
        wait_until('ce_list_ready')

        for _ in range(4):
            touch(x=1125, y=160)                                    # Sort by Rarity

        ces = pyautogui.screenshot(
                region=(WIN_X + 70, WIN_Y + 400, 1130, CES_HEIGHT))

        touch(x=90, y=70)                                           # Close
        touch(x=90, y=70)                                           # Close

        # Setup Folders For This Run

        #folder_name = os.path.join(ROLLS_FOLDER,
        #    datetime.datetime.now().strftime('%y_%m_%d_%H_%M'))
        
        #os.mkdir(folder_name)

        #results = Image.new('RGB', (1130, SERV_HEIGHT + CES_HEIGHT))
        #results.paste(servants, (0, 0))
        #results.paste(ces, (0, SERV_HEIGHT))
        #results.save(os.path.join(folder_name,
        #                        'rolls.png'))

        # Bind Code

        while True:
            touch(**MENU)
            touch(x=1080, y=680)

            result = wait_until('my_room_prompt', maxTries=2)
            if result is not None:
                touch(x=1240, y=66)

            while not image_is_on_screen('issue_transfer_number_prompt'):
                touch(x=1260, y=650)                                # Scroll
            touch(x= 950, y=380)                                    # Issue Transfer Number

            if not image_is_on_screen('transfer_number_issues_successfully'):
                touch(x=800, y=388)
                pyautogui.typewrite(PASSWORD, interval=0.25)
                touch(x=800, y=470)
                touch(x=800, y=470)
                pyautogui.typewrite(PASSWORD, interval=0.25)
                touch(x=640, y=610)
                touch(x=640, y=610)

            # In Memory of Account 17_07_05_15_44, we now make SURE
            # that a bind code was issued.

            result = wait_until('transfer_number_issues_successfully', maxTries=10)
            if result is None:
                raise ConnectionError("Failed to bind account")
            else:
                break

        bind_code = pyautogui.screenshot(
                region=(WIN_X + 530, WIN_Y + 330, 270, BIND_CODE_HEIGHT))

        touch(1009, 353)                                            # Copy Transfer Number

        filename = None
        transfer_code = pyperclip.paste()
        if transfer_code is not None:
            filename = str(transfer_code)

        if not filename:
            filename = datetime.datetime.now().strftime('%y_%m_%d_%H_%M')

        results = Image.new('RGB', (1130, SERV_HEIGHT + CES_HEIGHT + BIND_CODE_HEIGHT))
        if servants is not None:
            results.paste(servants, (0, 0))
        if ces is not None:
            results.paste(ces, (0, SERV_HEIGHT))

        results.paste(bind_code, (0, SERV_HEIGHT + CES_HEIGHT))
        results.save(os.path.join(ROLLS_FOLDER, filename + '.png'))

        # bind_code.save(os.path.join(ROLLS_FOLDER, filename + '.png'))
        # touch(x=430, y=600)                                         # Close Issue Transfer Number Screen
        clear_app()
    else:
        return -1
    return step + 1
        
def try_get_step():
    arr_steps = ['skip_1',
                'skip_2',
                'name_prompt',
                'skip_3',
                'mission_x-a',
                'skip_4',
                'skip_5',
                'mission_select_2',
                'skip_6',
                'skip_7',
                'tutorial_summon_main_screen_prompt',
                'mission_select_3',
                'skip_9',
                'login_bonus',
                'gifts_button',
                'menu']
    arr_quick = ['use_menu_to_summon','login_bonus', 'skip_1', 'skip_2', 'skip_3', 'skip_4', 'skip_5', 'skip_6', 'skip_7', 'skip_9', 'name_prompt', 'mission_select_3', 'mission_select_2', 'mission_x-a', 'gifts_button']
    result = wait_until(*arr_quick, maxTries=3)
    if result is not None:
        if result == 0:
            return 10   # Summon 10 free cards
        return arr_steps.index(arr_quick[result])
    return wait_until(*arr_steps)

if __name__ == '__main__':

    if not os.path.exists(ROLLS_FOLDER):
        os.mkdir(ROLLS_FOLDER)

    #app = pyautogui.screenshot(
    #            region=(WIN_X, WIN_Y, 1300, 750))

    #results = Image.new('RGB', (1300, 750))
    #results.paste(app, (0, 0))
    #results.save('app.png')

    while True:
        try:
            check_window()
            
            # First Launch
            close_app()
            goto_home()
            touch(**GO_ICON)                                            # Game Icon

            running = True
            maxTriesFirstAction = None
            while running:
                result = wait_until('title_screen2',
                                    'ip_ban',
                                    'grand_order_icon',
                                    'crash_from_launcher',
                                    'close_dialog',
                                    'please_tap_the_screen',
                                    'terms_of_service', 
                                    'login_bonus',
                                    'skip_1',
                                    'name_prompt', maxTries=maxTriesFirstAction)
                maxTriesFirstAction = 5
            
                if result == 0:                                             # Main Screen
                    touch(**LEFT_EDGE)
                    continue
                elif result == 1:                                           # IP Ban
                    running = False
                    close_app()
                    time.sleep(300)
                    break
                elif result == 2:                                           # Launcher
                    continue
                elif result == 3:                                           # Crash Message
                    touch(x=990, y=440)
                    running = False
                    break
                elif result == 4:                                           # News dialog
                    touch(**EXIT_TOP_RIGHT)
                    continue
                elif result == 5:
                    touch(**LEFT_EDGE)
                    continue
                elif result == 6:
                    touch(**CONFIRM)                                            # Accept ToS
                    continue
                elif result == 7:                                           # Login Bonus
                    touch(**CLOSE)
                    if try_get_step() is not None:
                        break
                elif result == 8:                                           # First skip screen of the tutorial
                    break
                elif result == 9:                                           # Name prompt
                    break
                elif result == None:
                    if wait_for_loading():
                        continue
                    result = wait_until('login_bonus', maxTries=3)
                    if result is not None:
                        touch(**CLOSE)
                    if try_get_step() is not None:
                        break
            if not running:
                continue

            step = None
            result = wait_until('skip_1', 'attack', 'name_prompt', 'terminal', maxTries=5)
            if result == 0 or result == 1:
                step = 0
            elif result == 3:
                step = 14
            else:
                step = try_get_step()

            while True:
                step = do_step(step)
                if step is None:
                    break
                if step == -1:
                    break
        except ConnectionError as e:
            print("Restart client: {}".format(repr(e.args)))
        except Exception as e:
            print(repr(e))

        
