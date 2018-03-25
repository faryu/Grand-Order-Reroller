import cv2
import time
import datetime
import pyautogui
import numpy as np
import os, os.path
import pyperclip
from PIL import Image
from settings import PASSWORD, NAME

############
# Settings #
PAUSE_TIME = 1.5
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

SERV_HEIGHT = 540
CES_HEIGHT = 350
BIND_CODE_HEIGHT = 70

WIN_X = 0
WIN_Y = 0

def wait(given_time):
    time.sleep(TIMING_MULT * given_time)

def touch(x, y):
    pyautogui.click(x=WIN_X+x, y=WIN_Y+y)

def move_to(x, y):
    pyautogui.moveTo(WIN_X + x, WIN_Y + y)

def drag_to(x, y, duration=0, button='left', tween=pyautogui.linear):
    pyautogui.dragTo(WIN_X + x, WIN_Y + y, duration=duration, button=button, tween=tween)

def skip_scene():
    wait_for_loading()

    touch(**SKIP_BUTTON)
    touch(**CONFIRM)

def close_app():
    touch(**HOME_BUTTON)
    touch(x=1300, y=700)

    while True:
        result = wait_until('close_app_screen', 'close_app_empty', maxTries = 5)

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
    touch(**HOME_BUTTON)
    
    # Open App Info
    move_to(**GO_ICON)
    drag_to(**APP_INFO, duration=5, tween=pyautogui.easeInQuad)
    
    wait_until('app_info')
    touch(982, 596)                                                 # Press delete data
    wait(1)
    touch(812, 505)                                                 # Press Ok

def select_card(card_no):
    locations = {1: 140, 2: 390, 3: 650, 4: 900, 5: 1160}
    touch(x=locations[card_no], y=530)

def image_is_on_screen(template_name):
    template = cv2.imread(os.path.join(
                                'screenshots', 
                                template_name + '.png'), 
                    cv2.IMREAD_GRAYSCALE)
    image = cv2.cvtColor(
                np.array(pyautogui.screenshot(
                        region=(WIN_X, WIN_Y, 1300, 750))), 
                cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= CLOSENESS_THRESHOLD)

    # Not sure why this works but okay
    for pt in zip(*loc[::-1]):
        return True

    return False

def click_until(*images):
    pyautogui.PAUSE = 0.2 * PAUSE_TIME
    
    while True:
        while not window_visible():
            wait(1)
        for pos, image in enumerate(images):
            if image_is_on_screen(image):
                pyautogui.PAUSE = PAUSE_TIME
                wait(0.5)
                return pos

        for _ in range(3):
            touch(**LEFT_EDGE)

def wait_until(*images, maxTries=None):
    while True:
        for pos, image in enumerate(images):
            if image_is_on_screen(image):
                wait(0.5)
                return pos
        if maxTries is not None:
            maxTries -= 1
            if maxTries <= 0:
                return None

def wait_for_loading():
    notLoading = 0
    while notLoading < 3:
        if wait_until('connecting', 'loading', maxTries=2) is None:
            notLoading += 1
        else:
            notLoading = 0
            wait(0.5)

def window_location():
    return pyautogui.locateOnScreen(os.path.join(
                                'screenshots', 
                                'window.png'))
def window_visible():
    return window_location() is not None

if __name__ == '__main__':

    if not os.path.exists(ROLLS_FOLDER):
        os.mkdir(ROLLS_FOLDER)

    window_msg = False
    while not window_visible():
        if not window_msg:
            print("Waiting for window...")
            window_msg = True
        wait(1)

    winlocation = window_location()
    if winlocation is None:
        print('window not found!')
        exit(1)

    WIN_X = winlocation[0]
    WIN_Y = winlocation[1]

    app = pyautogui.screenshot(
                region=(WIN_X, WIN_Y, 1300, 750))

    results = Image.new('RGB', (1300, 750))
    results.paste(app, (0, 0))
    results.save(os.path.join(ROLLS_FOLDER,
                            'app.png'))

    while True:
        # Clear Data
        close_app()
        clear_app()
        

        # First Launch
        touch(**HOME_BUTTON)
        touch(**GO_ICON)                                            # Game Icon

        result = wait_until('title_screen2',
                            'ip_ban',
                            'grand_order_icon',
                            'crash_from_launcher',
                            'relaunch_screen')

        if result == 0:                                             # Main Screen
            pass

        # Failed To Launch?

        elif result == 1:                                           # IP Ban
            close_app()
            time.sleep(600)
            continue

        elif result == 2:                                           # Launcher
            continue

        elif result == 3:                                           # Crash Message
            touch(x=990, y=440)
            continue

        elif result == 4:                                           # Relaunch without clearing
            close_app()
            touch(**CLEAR_DATA_ICON)
            wait(1)
            continue

        # Intro
        click_until('terms_of_service')
        touch(**CONFIRM)                                            # Accept ToS
        wait_until('skip_1')
        skip_scene()

        # First Battle

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

        # Story

        wait_until('skip_2')
        skip_scene()

        wait_until('name_prompt')
        touch(**NAME_FIELD)
        pyautogui.typewrite(NAME, interval = 0.25)
        touch(**NAME_CONFIRM)
        touch(**NAME_CONFIRM)
        touch(**NAME_CONFIRM_2)

        wait_until('skip_3')
        skip_scene()

        wait_until('mission_x-a')
        touch(x=650, y=390)                                         # Mission Select 1
        touch(x=1000, y=200)                                        # Mission Select 2
        wait_until('skip_4')
        skip_scene()

        # Second Battle

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

        wait_until('skip_5')
        skip_scene()

        wait_until('saint_quartz_reward_screen_after_battle')
        touch(x=640, y=430)

        # Story

        wait_until('mission_select_2')
        touch(x=640, y=430)                                         # Mission Select 1
        touch(x=1000, y=200)                                        # Mission Select 2
        wait_until('skip_6')
        skip_scene()

        # Third Battle

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

        wait_until('skip_7')
        skip_scene()

        wait_until('saint_quartz_reward_screen_after_battle')
        touch(**MENU)

        # Summon

        wait_until('tutorial_summon_main_screen_prompt')
        wait(3)

        touch(**MENU)                                               # Menu Button
        touch(x=540, y=680)                                         # Summon Button
        wait_until('tutorial_10x_button')
        touch(x=640, y=600)                                         # Select 10x Summon
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
        wait_until('setup_party_prompt_8')
        touch(x=100, y=75)   
        wait(4)
        touch(x=100, y=75)           

        # Final Battle - Non-deterministic                          

        wait_until('mission_select_3')
        touch(x=640, y=430)                                         # Mission Select 1
        touch(x=1000, y=200)                                        # Mission Select 2
        touch(x=1000, y=200)
        touch(x=500, y=300)                                         # Select Support
        touch(**MENU)                                               # Start Button

        wait_until('skip_8')
        skip_scene()

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
        touch(x=320, y=650)                                         # Do Not Request

        wait_until('skip_9')
        skip_scene()

        result = wait_until('login_bonus', maxTries=20)
        if result is not None:
            touch(**CLOSE)

            #while True:
            #    if image_is_on_screen('bonuses_received'):
            #        break
            #    touch(**CLOSE)

        touch(x=100, y=75)                                          # Close Button
        wait(1)

        touch(x=440, y=700)                                         # Gift Box
        wait_until('receive_all_gifts_button')
        touch(x=1100, y=250)                                        # Receive All
        
        #click_until('lock')
        #touch(x=50, y=75)                                           # Close
        #click_until('lock')
        #touch(x=50, y=75)                                           # Close

        wait_until('all_gifts_received')
        touch(x=110, y=90)                                          # Close Prompt

        # Multi Summon

        # wait_until('mission_select_protag')
        touch(**MENU)                                               # Menu Button
        touch(x=540, y=680)                                         # Summon Button

        result = wait_until('first_multi_summon_info_prompt', maxTries=150)
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
            wait_until('1x_summon_button')
            touch(x=450, y=600)                                     # 1x Summon

            result_1 = wait_until('not_enough_quartz',
                                'enough_quartz')

            if result_1 == 1:                                       # More Summons
                touch(x=830, y=600)                                 # Confirm Summon
                wait(5)                                             # CV is too fast
                
                result_2 = click_until('lock',
                                       'lock_enabled',
                                       'summon_screen_close',
                                       'summon_screen_close_details')
                if (result_2 == 0) or (result_2 == 1):
                    touch(x=50, y=75)                               # Close
                elif result_2 == 3:
                    touch(1247, 61)                                 # Close

                    result_2 = wait_until('lock', 'lock_enabled', maxTries=15)
                    if (result_2 == 0) or (result_2 == 1):
                        touch(x=50, y=75)                               # Close

            else:                                                   # No More Summons
                touch(x=440, y=600)
                break

        # Take Screenshots

        touch(**MENU)
        touch(x=175, y=675)                                         # Formation
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
        
        result = wait_until('ce_prompt', maxTries=150)
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

            wait_until('my_room_prompt')
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

            wait(5)

            if not image_is_on_screen('transfer_number_issues_successfully'):
                # We failed to issue a bind code.
                touch(**HOME_BUTTON)
                close_app()
                touch(**GO_ICON)
                wait_until('tm')
                touch(**GO_ICON)
                wait_until('relaunch_screen')
                touch(x=1250, y= 65)                                # Close Welcome Screen
                wait_until('protag')
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
