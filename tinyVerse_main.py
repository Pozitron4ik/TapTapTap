import requests
import os
import math
import time
import logging
import json
import numpy as np
import random
from forall import *
from baseClass import base
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

class TelegramBotAutomation(base):
    def tap100(self):
        try:
            check = self.wait_for_element(By.XPATH,
                                        '/html/body/div[2]/div[1]/div/div[4]/a[2]/span'
                                        )
            logging.info(f"Account {self.serial_number}: tap status: {check.text}")
            if check.text == "Collect stardust":
                self.wait_for_element(By.XPATH, 
                                      '/html/body/div[2]/div[1]/div/div[4]/a[2]'
                                      ).click()
                logging.info(f"Account {self.serial_number}: 100% tap")
                self.sleep(2, 5)
        except Exception as e:
            logging.info(f"Account {self.serial_number}: error while tapping")

    def adjust_for_error(self, value):
        if value <= 1:
            return value
        elif value < 10:
            return value - 4
        elif value < 100:
            return value - 20
        elif value < 1000:
            return value - 50
        else: return value - 110

    def interpolation(self, target_f):
        slider_values = [0, 1, 100, 150, 219, 350, 500, 513, 600, 700, 800, 900, 1000]
        f_values = [100, 101, 199, 249, 317, 447 , 843, 1116, 1585, 3219, 5248, 9010, 10000]

        # Интерполировать значение слайдера для заданного f(target_f)
        
        interpolator = np.interp(target_f, f_values, slider_values)

        return self.adjust_for_error(int(interpolator))  # Возвращаем целое значение

    def slide(self):
        try:
            slider = self.wait_for_element(By.XPATH,
                                           '/html/body/div[2]/div[3]/div[2]/div/div[1]/div[2]/div/div/input'
                                           )
            value = int(self.wait_for_element(By.XPATH,
                                          '/html/body/div[2]/div[3]/div[2]/div/div[1]/div[1]/label/b'
                                          ).text)
            logging.info(f"Account {self.serial_number}: initial value: {value}")
            if value<100:return
            new_val = self.interpolation(value-1)
            logging.info(f"Account {self.serial_number}: interpolation: {new_val}")
            self.driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));", slider, new_val
                                    )
            logging.info(f"Account {self.serial_number}: slide ok")
            self.sleep(2, 4)
        except Exception as e:
            logging.info(f"Account {self.serial_number}: error in slide")

    def addstars(self):
        success = False
        try:
            addbut = self.wait_for_element(By.XPATH,
                                           '/html/body/div[2]/div[1]/div/div[4]/a[1]'
                                           )
            addbut.click()
            logging.info(f"Account {self.serial_number}: clicked add stars")
            success = True
            self.sleep(2, 4)
        except Exception as e:
            success = False
            logging.info(f"Account {self.serial_number}: cant click add stars")
        
        if success:
            self.slide()
            try:
                collect = self.wait_for_element(By.XPATH, 
                                                '/html/body/div[2]/div[3]/div[2]/div/div[1]/div[2]/button'
                                                )
                collect.click()
                logging.info(f"Account {self.serial_number}: collected")
                self.sleep(2, 4)
            except Exception as e:
                success = False
                logging.info(f"Account {self.serial_number}: cant collect")


    
def read_accounts_from_file():
    with open('accounts_tinyVerse.txt', 'r') as file:
        return [line.strip() for line in file.readlines()]


def write_accounts_to_file(accounts):
    with open('accounts_tinyVerse.txt', 'w') as file:
        for account in accounts:
            file.write(f"{account}\n")


def process_accounts():
    last_processed_account = None

    while True:

        accounts = read_accounts_from_file()
        random.shuffle(accounts)
        write_accounts_to_file(accounts)
        i = 0
        while i < len(accounts):
            remove_empty_lines('locked_accounts.txt')
            remove_key_lines('locked_accounts.txt', 'TINY')

            retry_count = 0
            i += 1
            success = False
            if is_account_locked(accounts[i - 1]):
                if i == len(accounts):
                    retry_count = 3
                else:
                    accounts.append(accounts[i - 1])
                    accounts.pop(i - 1)
                    print(accounts)
                    i -= 1
                # здесь выход в новую итерацию цикла со следующего элемента

            else:

                while retry_count < 3 and not success:
                    lock_account(accounts[i - 1], 'TINY')
                    bot = TelegramBotAutomation(accounts[i - 1])
                    bot.scrshot = 0  # 0 for no screenshots
                    try:
                        delete_oldScreens()
                        bot.navigate_to_bot()
                        bot.send_message('https://t.me/tinyverslfg')
                        bot.click_link('t.me/tverse/?startapp')
                        time.sleep(1)
                        bot.tap100()
                        bot.addstars()
                        time.sleep(10)

                        logging.info(f"Account {accounts[i - 1]}: Processing completed successfully.")
                        success = True
                    except Exception as e:
                        logging.warning(f"Account {accounts[i - 1]}: Error occurred on attempt {retry_count + 1}: {e}")
                        retry_count += 1
                    finally:
                        logging.info("-------------END-----------")
                        bot.browser_manager.close_browser()
                        logging.info("-------------END-----------")
                        unlock_account(accounts[i - 1], "TINY")
                        sleep_time = random.randrange(5, 15)
                        logging.info(f"Sleeping for {sleep_time} seconds.")
                        time.sleep(sleep_time)

                    if retry_count >= 3:
                        logging.warning(f"Account {accounts[i - 1]}: Failed after 3 attempts.")

            if not success:
                logging.warning(f"Account {accounts[i - 1]}: Moving to next account after 3 failed attempts.")

        logging.info("All accounts processed. Waiting 2 hours before restarting.")

        for hour in range(2):
            logging.info(f"Waiting... {2 - hour} hours left till restart.")
            time.sleep(60 * 60)

        logging.info("Shuffling accounts for the next cycle.")


if __name__ == "__main__":
    process_accounts()