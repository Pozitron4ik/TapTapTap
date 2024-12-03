import requests
import os
import time
import logging
import json
import random
from forall import *
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')

class BrowserManager:


    def __init__(self, serial_number):
        self.serial_number = serial_number
        self.driver = None
    
    def check_browser_status(self):
        try:
            response = requests.get(
                'http://local.adspower.net:50325/api/v1/browser/active',
                params={'serial_number': self.serial_number}
            )
            data = response.json()
            if data['code'] == 0 and data['data']['status'] == 'Active':
                logging.info(f"Account {self.serial_number}: Browser is already active.")
                return True
            else:
                return False
        except Exception as e:
            logging.exception(f"Account {self.serial_number}: Exception in checking browser status: {str(e)}")
            return False

    def start_browser(self):
        try:
            if self.check_browser_status():
                logging.info(f"Account {self.serial_number}: Browser already open. Closing the existing browser.")
                self.close_browser()
                time.sleep(5)

            script_dir = os.path.dirname(os.path.abspath(__file__))
            requestly_extension_path = os.path.join(script_dir, 'blum_unlocker_extension')

            launch_args = json.dumps(["--headless=new", f"--load-extension={requestly_extension_path}"])

            request_url = (
                f'http://local.adspower.net:50325/api/v1/browser/start?'
                f'serial_number={self.serial_number}&ip_tab=1&headless=1&launch_args={launch_args}'
            )

            response = requests.get(request_url)
            data = response.json()
            if data['code'] == 0:
                selenium_address = data['data']['ws']['selenium']
                webdriver_path = data['data']['webdriver']
                chrome_options = Options()
                chrome_options.add_experimental_option("debuggerAddress", selenium_address)

                service = Service(executable_path=webdriver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.set_window_size(600, 720)
                logging.info(f"Account {self.serial_number}: Browser started successfully.")
                return True
            else:
                logging.warning(f"Account {self.serial_number}: Failed to start the browser. Error: {data['msg']}")
                return False
        except Exception as e:
            logging.exception(f"Account {self.serial_number}: Exception in starting browser: {str(e)}")
            return False

    def close_browser(self):
        try:
            if self.driver:
                try:
                    self.driver.close()
                    self.driver.quit()
                    self.driver = None  
                    logging.info(f"Account {self.serial_number}: Browser closed successfully.")
                except WebDriverException as e:
                    logging.info(f"Account {self.serial_number}: exception, Browser should be closed now")
        except Exception as e:
            logging.exception(f"Account {self.serial_number}: General Exception occurred when trying to close the browser: {str(e)}")
        finally:
            try:
                response = requests.get(
                    'http://local.adspower.net:50325/api/v1/browser/stop',
                    params={'serial_number': self.serial_number}
                )
                data = response.json()
                if data['code'] == 0:
                    logging.info(f"Account {self.serial_number}: Browser closed successfully.")
                else:
                    logging.info(f"Account {self.serial_number}: exception, Browser should be closed now")
            except Exception as e:
                logging.exception(f"Account {self.serial_number}: Exception occurred when trying to close the browser: {str(e)}")

class TelegramBotAutomation:
    def __init__(self, serial_number):
        self.serial_number = serial_number
        self.browser_manager = BrowserManager(serial_number)
        logging.info(f"Initializing automation for account {serial_number}")
        self.browser_manager.start_browser()
        self.driver = self.browser_manager.driver

    def sleep(self, a, b):
        sleep_time = random.randrange(a, b)
        logging.info(f"Account {self.serial_number}: {sleep_time}sec sleep...")
        time.sleep(sleep_time)

    def navigate_to_bot(self):
        try:
            self.driver.get('https://web.telegram.org/k/')
            logging.info(f"Account {self.serial_number}: Navigated to Telegram web.")
        except Exception as e:
            logging.exception(f"Account {self.serial_number}: Exception in navigating to Telegram bot: {str(e)}")
            self.browser_manager.close_browser()

    def send_message(self, message):
        chat_input_area = self.wait_for_element(By.XPATH, '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/input[1]')
        chat_input_area.click()
        chat_input_area.send_keys(message)

        search_area = self.wait_for_element(By.XPATH, '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[2]/div[2]/div[1]/div[1]/div[1]/div[2]/ul[1]/a[1]/div[1]')
        search_area.click()
        logging.info(f"Account {self.serial_number}: Group searched.")

    def click_link(self):
        link = self.wait_for_element(By.CSS_SELECTOR, "a[href*='https://t.me/herewalletbot/app']")
        link.click()
        
        #После последней обновы 31.08.24 закомментил
        #launch_click = self.wait_for_element(By.XPATH, "//body/div[@class='popup popup-peer popup-confirmation active']/div[@class='popup-container z-depth-1']/div[@class='popup-buttons']/button[1]/div[1]")
        #launch_click.click()
        logging.info(f"Account {self.serial_number}: HOT STARTED")
        sleep_time = random.randrange(6, 12)
        logging.info(f"Sleeping for {sleep_time} seconds.")
        time.sleep(sleep_time)
        if self.scrshot:
            self.driver.save_screenshot(f'screen{self.scrshot}.png')
            self.scrshot += 1
        if not self.switch_to_iframe():
            logging.info(f"Account {self.serial_number}: No iframes found")
            return

    def youtube(self, message):
        try:
            watchVid = self.wait_for_element(By.XPATH,
                        '/html/body/div[4]/div/div[2]/div/div/div[2]/button'
                                             )
            watchVid.click()
            self.sleep(7, 10)
            logging.info(f"Account {self.serial_number}: clicked watch video")
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
        except Exception as e:
            logging.info(f"Account {self.serial_number}: {str(e)}")
        try:
            sendPhrase = self.wait_for_element(By.XPATH,
                        '/html/body/div[4]/div/div[2]/div/div/div[2]/button[1]'
                                               )
            sendPhrase.click()
            self.sleep(1, 2)
            logging.info(f"Account {self.serial_number}: clicked send phrase")
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
        except Exception as e:
            logging.info(f"Account {self.serial_number}: {str(e)}")
        try:
            inputField = self.wait_for_element(By.XPATH, '//*[@id="root"]/div/div/div[1]/label//input')
            inputField.send_keys(message)
            self.sleep(1, 2)
            logging.info(f"Account {self.serial_number}: entered message '{message}'")
            
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
        except Exception as e:
            logging.info(f"Account {self.serial_number}: {str(e)}")
        try:
            send = self.wait_for_element(By.XPATH,
                                '//*[@id="root"]/div/div/div[2]/button'
                                         )
            self.driver.execute_script("arguments[0].scrollIntoView();", send)
            send.click()
            self.sleep(15, 20)
            logging.info(f"Account {self.serial_number}: send")
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
        except Exception as e:
            logging.info(f"Account {self.serial_number}: {str(e)}")
        
    

    def switch_to_iframe(self):
        self.driver.switch_to.default_content()
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            self.driver.switch_to.frame(iframes[0])
            return True
        return False

    
    def storage(self):
        try:
            storageBut = self.wait_for_element(By.XPATH,
                            '//*[@id="root"]/div/div/div[1]/div/div/div[4]/div[2]'
                                            )
            self.driver.execute_script("arguments[0].scrollIntoView();", storageBut)
            storageBut.click()
            self.sleep(2, 5)
            logging.info(f"Account {self.serial_number}: clicked storage")
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
        except Exception as e:
            logging.info(f"Account {self.serial_number}: {str(e)}")


    def news(self):
        try:
            newsBut = self.wait_for_element(By.XPATH,
                                            '//*[@id="root"]/div/div/div[2]/div/div[3]/div/div[2]/div[2]/button'
                                            )
            newsBut.click()
            self.sleep(2, 5)
            logging.info(f"Account {self.serial_number}: clicked news")
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
        except Exception as e:
            logging.info(f"Account {self.serial_number}: no news")
            

    def claim(self):
        try:
            claimBut = self.wait_for_element(By.XPATH,
                            '//*[@id="root"]/div/div/div[2]/div/div[3]/div/div[2]/div[2]/button'
                                            )
            self.driver.execute_script("arguments[0].scrollIntoView();", claimBut)
            claimBut.click()
            self.sleep(2, 5)
            logging.info(f"Account {self.serial_number}: claimed")
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
        except Exception as e:
            logging.info(f"Account {self.serial_number}: {str(e)}")
        

    def back(self):
        self.driver.switch_to.default_content()
        self.wait_for_element(By.XPATH,
                    '/html/body/div[6]/div/div[1]/button[1]'
                              ).click()
        time.sleep(2)
        if self.scrshot:
            self.driver.save_screenshot(f'screen{self.scrshot}.png')
            self.scrshot += 1
        self.switch_to_iframe()
        

    
  
    def wait_for_element(self, by, value, timeout=10):
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )

    def wait_for_elements(self, by, value, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_all_elements_located((by, value))
        )

   
    def wallet(self):
        stage = 0
        try:
            walletBut = self.wait_for_element(By.XPATH,
                                  '/html/body/div[4]/div/div[2]/div/div[2]/div[1]/div[1]'
                                  )
            walletBut.click()
            logging.info(f"Account {self.serial_number}: pressed wallet")
            stage+=1
            self.sleep(2, 5)
        except Exception as e:
            logging.info(f"Account {self.serial_number}: {str(e)}")
        if stage:
            try:
                claim = self.wait_for_element(By.XPATH,
                                              '/html/body/div[4]/div/div[2]/div/div[2]/div[1]/div[1]'
                                              )
                claim.click()
                logging.info(f"Account {self.serial_number}: pressed claim")
                self.sleep(3, 5)
            except Exception as e:
                logging.info(f"Account {self.serial_number}: {str(e)}")
        
        
            

def read_accounts_from_file():
    with open('accounts_hot.txt', 'r') as file:
        return [line.strip() for line in file.readlines()]

def write_accounts_to_file(accounts):
    with open('accounts_hot.txt', 'w') as file:
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
            remove_key_lines('locked_accounts.txt', 'HOT')
            
            retry_count = 0
            i+=1
            success = False
            if is_account_locked(accounts[i-1]):
                if i == len(accounts):
                    retry_count = 3            
                else:
                    accounts.append(accounts[i-1])
                    accounts.pop(i-1)
                    print(accounts)
                    i-=1
                #здесь выход в новую итерацию цикла со следующего элемента
            
            else:
                
                while retry_count < 3 and not success:
                    lock_account(accounts[i-1], 'HOT' )
                    bot = TelegramBotAutomation(accounts[i-1])
                    bot.scrshot = 1 #0 for no screenshots
                    try:
                        delete_oldScreens()
                        bot.navigate_to_bot()
                        bot.send_message("https://t.me/dhjsdfgs333")
                        bot.click_link()
                        time.sleep(10)
                        bot.storage()
                        bot.news()
                        bot.claim()
                      #  bot.youtube("profit")
                       # bot.wallet() uncomment maybe
                        

                        logging.info(f"Account {accounts[i-1]}: Processing completed successfully.")
                        success = True  
                    except Exception as e:
                        logging.warning(f"Account {accounts[i-1]}: Error occurred on attempt {retry_count + 1}: {e}")
                        retry_count += 1  
                    finally:
                        logging.info("-------------END-----------")
                        bot.browser_manager.close_browser()
                        logging.info("-------------END-----------")
                        unlock_account(accounts[i-1], "HOT")
                        sleep_time = random.randrange(5, 15)
                        logging.info(f"Sleeping for {sleep_time} seconds.")
                        time.sleep(sleep_time)
                    
                    if retry_count >= 3:
                        logging.warning(f"Account {accounts[i-1]}: Failed after 3 attempts.")
                

            if not success:
                logging.warning(f"Account {accounts[i-1]}: Moving to next account after 3 failed attempts.")
                

            

        

        logging.info("All accounts processed. Waiting 2 hours before restarting.")

        for hour in range(2):
            logging.info(f"Waiting... {2 - hour} hours left till restart.")
            time.sleep(60 * 60)  

        
        logging.info("Shuffling accounts for the next cycle.")

if __name__ == "__main__":
    process_accounts()
