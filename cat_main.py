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
                self.driver.set_window_size(480, 720)
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

    def navigate_to_bot(self, message):
        try:
            self.driver.get('https://web.telegram.org/a/')
            logging.info(f"Account {self.serial_number}: Navigated to Telegram web.")
            chat_input_area = self.wait_for_element(By.XPATH, 
                                                   # '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/input[1]'
                                                    '//*[@id="telegram-search-input"]'
                                                    )
            chat_input_area.click()
            chat_input_area.send_keys(message)

            time.sleep(1)
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1


            search_area = self.wait_for_element(By.XPATH, 
                            #   '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[2]/div[2]/div[1]/div[1]/div[1]/div[2]/ul[1]/a[1]/div[1]'
                                '//*[@id="LeftColumn-main"]/div[2]/div[2]/div/div[2]/div/div[2]/div/div'
                                                )
            search_area.click()

            logging.info(f"Account {self.serial_number}: bot searched.")

            self.sleep(2, 5)
            
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
            

        except Exception as e:
            logging.exception(f"Account {self.serial_number}: Exception in navigating to Telegram bot: {str(e)}")
            self.browser_manager.close_browser()

    def start_game(self):
        try:
            play = self.wait_for_element(By.XPATH, 
                         '//*[@id="MiddleColumn"]/div[3]/div[2]/div/div[2]/div[1]/div[2]/div/button[1]'
                                  )
            play.click()


            logging.info(f"Account {self.serial_number}: clicked play.")
            self.sleep(5, 9)


            self.switch_to_iframe()
            
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
            
        except Exception as e:
            logging.exception(f"Account {self.serial_number}: {str(e)}")
            self.browser_manager.close_browser()



    def switch_to_iframe(self):
        self.driver.switch_to.default_content()
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            self.driver.switch_to.frame(iframes[0])
            return True
        return False          

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
        

    def avatar(self):
        try:
            avatarBut = self.wait_for_element(By.XPATH,
                                     '//*[@id="root"]/div/div/div[2]/a[4]'
                                              )
            avatarBut.click()
            self.sleep(20, 30)
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
            logging.exception(f"Account {self.serial_number}: clicked avatar")
        except Exception as e:
            logging.exception(f"Account {self.serial_number}: {str(e)}")

    def upgradeCat(self):
        try:
            self.sleep(40, 60)
            upgrade = self.wait_for_element(By.XPATH,
                             '//*[@id="root"]/div/div/div[1]/div[2]/section[2]/a/button'
                                            )
            upgrade.click()
            self.sleep(10, 20)
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
            logging.exception(f"Account {self.serial_number}: clicked upgrade cat")
        except Exception as e:
            logging.exception(f"Account {self.serial_number}: {str(e)}")

    def get_random_cat_image(self):
        
        repo_url = "https://raw.githubusercontent.com/max-mapper/cats/master/cat_photos/"
        
        
        image_files = ['00092f6ec7a911e1be6a12313820455d_7.png',
                    '0475ea02c7da11e18cf91231380fd29b_7.png',
                    '0502a3b2a1e111e18cf91231380fd29b_7.png',
                    '066bdac8c71811e1a38422000a1c8933_7.png',
                    '086b74e22ec411e19e4a12313813ffc0_7.png',
                    '0c375608c71811e1b10e123138105d6b_7.png',
                    '10b80642c7da11e19894123138140d8c_7.png',
                    '12a8d742be7f11e188131231381b5c25_7.png',
                    '16cb636ed3c711e1b62722000a1e8b36_7.png',
                    '185f6434c7a911e18cf91231380fd29b_7.png',
                    '1d3ccf7291c211e18cf91231380fd29b_7.png',
                    '2320b0ae089e11e29e6f22000a1e8b8a_7.png',
                    '25508c1e88ba11e1a87612313804ec91_7.png',
                    '29e2f6eaa03911e19e4a12313813ffc0_7.png',
                    '2f49bd8cbf0911e180d51231380fcd7e_7.png',
                    '33eb19201ed811e1abb01231381b65e3_7.png',
                    '3437df14c7aa11e1aee522000a1e8a5f_7.png',
                    '3ba670686e7111e181bd12313817987b_7.png',
                    '3f65914ca43711e1abb01231382049c1_7.png',
                    '42fe6a682c5011e19e4a12313813ffc0_7.png',
                    '433e375c2cc211e1a87612313804ec91_7.png',
                    '4857e4b0c95a11e19b0622000a1e8a4f_7.png',
                    '4ebcfed0a75911e1b2fe1231380205bf_7.png',
                    '548c8aa491a811e1be6a12313820455d_7.png',
                    '558eadc0c08211e18bb812313804a181_7.png',
                    '55d268706e7111e1989612313815112c_7.png',
                    '5804b25e64d211e18bb812313804a181_7.png',
                    '5c7ac9ec6fa211e1a87612313804ec91_7.png',
                    '628645a4048611e2a2ab22000a1d038e_7.png',
                    '66231dd2d23511e182d912313b0c28f0_7.png',
                    '66250dd8be6011e1aebc1231381b647a_7.png',
                    '67dcb80ab41b11e1aebc1231381b647a_7.png',
                    '6c8b25eea03911e192e91231381b3d7a_7.png',
                    '6cd3d502c03011e180c9123138016265_7.png',
                    '728ba2a4bedc11e1bf341231380f8a12_7.png',
                    '729fe6b6371d11e19896123138142014_7.png',
                    '78fd1f1aca3911e1a39b1231381b7ba1_7.png',
                    '7d7f0184a43711e1b10e123138105d6b_7.png',
                    '813290b864d411e1a87612313804ec91_7.png',
                    '84592b6ebedc11e1989612313815112c_7.png',
                    '84bec45e2b7211e19e4a12313813ffc0_7.png',
                    '853c0926ca3911e1a39b1231381b7ba1_7.png',
                    '87597f406f0811e180d51231380fcd7e_7.png',
                    '8a7a7bc2d76b11e195351231381b651f_7.png',
                    '8f496896661b11e180d51231380fcd7e_7.png',
                    '90d35578a43711e180d51231380fcd7e_7.png',
                    '92df98b46efd11e18bb812313804a181_7.png',
                    '9319d9f6ca3911e1b2fe1231380205bf_7.png',
                    '93c475d0ff4c11e1839c123138192853_7.png',
                    '9796956091a811e181bd12313817987b_7.png',
                    '9b43befc33ea11e19e4a12313813ffc0_7.png',
                    'a227324aa43711e19e4a12313813ffc0_7.png',
                    'ac62bcbcac5111e1b9f1123138140926_7.png',
                    'af6c6f9a1dd411e19e4a12313813ffc0_7.png',
                    'b1d94ca0ca3911e18cf91231380fd29b_7.png',
                    'b3f6a1ae359711e19e4a12313813ffc0_7.png',
                    'b672f508bedc11e1af7612313813f8e8_7.png',
                    'b9028196224511e180c9123138016265_7.png',
                    'b966683e290011e19e4a12313813ffc0_7.png',
                    'bd9c8d0ea75711e1989612313815112c_7.png',
                    'be87b8a0721f11e1b9f1123138140926_7.png',
                    'c47c1ca0ff4c11e1a76e22000a1e8903_7.png',
                    'c9eead403a8c11e19e4a12313813ffc0_7.png',
                    'cab21d2e661b11e18bb812313804a181_7.png',
                    'd27f934ed5f411e19b0622000a1e8a4f_7.png',
                    'de5ad150c19111e1b9f1123138140926_7.png',
                    'e1bca2f66ff711e1a87612313804ec91_7.png',
                    'e66928da64d311e19e4a12313813ffc0_7.png',
                    'e766ea3c434611e180c9123138016265_7.png',
                    'e8f4da56d3c611e18ca012313806b840_7.png',
                    'ebd69cfc2bae11e1abb01231381b65e3_7.png',
                    'ed45f0cc2e7111e19896123138142014_7.png',
                    'f2033f0a6bb311e19e4a12313813ffc0_7.png',
                    'f39a66b2c71711e19894123138140d8c_7.png',
                    'f8558fc44b0c11e180c9123138016265_7.png',
                    'fbe98620432f11e19e4a12313813ffc0_7.png',
                    'kublai0.jpg',
                    'kublai1.jpg',
                    'kublai10.jpg',
                    'kublai100.jpg',
                    'kublai101.jpg',
                    'kublai102.jpg',
                    'kublai103.jpg',
                    'kublai104.jpg',
                    'kublai105.jpg',
                    'kublai106.jpg',
                    'kublai107.jpg',
                    'kublai108.jpg',
                    'kublai109.jpg',
                    'kublai11.jpg',
                    'kublai110.jpg',
                    'kublai111.jpg',
                    'kublai112.jpg',
                    'kublai113.jpg',
                    'kublai114.jpg',
                    'kublai115.jpg',
                    'kublai116.jpg',
                    'kublai117.jpg',
                    'kublai118.jpg',
                    'kublai12.jpg',
                    'kublai13.jpg',
                    'kublai14.jpg',
                    'kublai15.jpg',
                    'kublai16.jpg',
                    'kublai17.jpg',
                    'kublai18.jpg',
                    'kublai19.jpg',
                    'kublai2.jpg',
                    'kublai20.jpg',
                    'kublai21.jpg',
                    'kublai22.jpg',
                    'kublai23.jpg',
                    'kublai24.jpg',
                    'kublai25.jpg',
                    'kublai26.jpg',
                    'kublai27.jpg',
                    'kublai28.jpg',
                    'kublai29.jpg',
                    'kublai3.jpg',
                    'kublai30.jpg',
                    'kublai31.jpg',
                    'kublai32.jpg',
                    'kublai33.jpg',
                    'kublai34.jpg',
                    'kublai35.jpg',
                    'kublai36.jpg',
                    'kublai37.jpg',
                    'kublai38.jpg',
                    'kublai39.jpg',
                    'kublai4.jpg',
                    'kublai40.jpg',
                    'kublai41.jpg',
                    'kublai42.jpg',
                    'kublai43.jpg',
                    'kublai44.jpg',
                    'kublai45.jpg',
                    'kublai46.jpg',
                    'kublai47.jpg',
                    'kublai48.jpg',
                    'kublai49.jpg',
                    'kublai5.jpg',
                    'kublai50.jpg',
                    'kublai51.jpg',
                    'kublai52.jpg',
                    'kublai53.jpg',
                    'kublai54.jpg',
                    'kublai55.jpg',
                    'kublai56.jpg',
                    'kublai57.jpg',
                    'kublai58.jpg',
                    'kublai59.jpg',
                    'kublai6.jpg',
                    'kublai60.jpg',
                    'kublai61.jpg',
                    'kublai62.jpg',
                    'kublai63.jpg',
                    'kublai64.jpg',
                    'kublai65.jpg',
                    'kublai66.jpg',
                    'kublai67.jpg',
                    'kublai68.jpg',
                    'kublai69.jpg',
                    'kublai7.jpg',
                    'kublai70.jpg',
                    'kublai71.jpg',
                    'kublai72.jpg',
                    'kublai73.jpg',
                    'kublai74.jpg',
                    'kublai75.jpg',
                    'kublai76.jpg',
                    'kublai77.jpg',
                    'kublai78.jpg',
                    'kublai79.jpg',
                    'kublai8.jpg',
                    'kublai80.jpg',
                    'kublai81.jpg',
                    'kublai82.jpg',
                    'kublai83.jpg',
                    'kublai84.jpg',
                    'kublai85.jpg',
                    'kublai86.jpg',
                    'kublai87.jpg',
                    'kublai88.jpg',
                    'kublai89.jpg',
                    'kublai9.jpg',
                    'kublai90.jpg',
                    'kublai91.jpg',
                    'kublai92.jpg',
                    'kublai93.jpg',
                    'kublai94.jpg',
                    'kublai95.jpg',
                    'kublai96.jpg',
                    'kublai97.jpg',
                    'kublai98.jpg',
                    'kublai99.jpg']

        save_directory = "randomcats"
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        
        random_image = random.choice(image_files)
        
        # Полный URL изображения
        image_url = repo_url + random_image

        # Путь для сохранения изображения локально
        existing_files = [f for f in os.listdir(save_directory) if f.startswith('cat') and (f.endswith('.png') or f.endswith('.jpg'))]
    
        if existing_files:
            # Извлекаем последний номер из файлов (независимо от расширения)
            last_file_number = max([int(f.replace('cat', '').replace('.png', '').replace('.jpg', '')) for f in existing_files])
            new_file_number = last_file_number + 1
        else:
            new_file_number = 1  

        file_extension = os.path.splitext(random_image)[1]

        # Путь для сохранения изображения локально с уникальным именем и расширением
        local_image_path = os.path.join(save_directory, f"cat{new_file_number}{file_extension}")

        img_data = requests.get(image_url).content
        with open(local_image_path, 'wb') as handler:
            handler.write(img_data)
        
        return local_image_path


    def get_random_cat_image_from_folder(self):
        folder_path = "randomcats"
        
        cat_images = [f for f in os.listdir(folder_path) if f.startswith('cat') and (f.endswith('.png') or f.endswith('.jpg'))]
        
        if not cat_images:
            return None
        
        random_image = random.choice(cat_images)
        
        random_image_path = os.path.join(folder_path, random_image)
        
        return random_image_path




    def sendPic(self):
        try:
            self.get_random_cat_image() #comment this line after /randomcats dir gets large enough
            self.sleep(3, 5)
            picture_path = self.get_random_cat_image_from_folder()
            absolute_picture_path = os.path.abspath(picture_path)
            
            upload_element = self.driver.execute_script(
                "document.querySelector('input[type=\"file\"]').classList.remove('hidden');"
            )

            upload_element = self.wait_for_element(By.CSS_SELECTOR, 'input[type="file"]')
            upload_element.send_keys(absolute_picture_path)


            logging.info(f"Account {self.serial_number}: uploaded pic")
            self.sleep(30, 40)
            
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
                
            
        except Exception as e:
            logging.exception(f"Account {self.serial_number}: {str(e)}")

            
        

  
    def wait_for_element(self, by, value, timeout=10):
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )

    def wait_for_elements(self, by, value, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_all_elements_located((by, value))
        )

   

def read_accounts_from_file():
    with open('accounts_cat.txt', 'r') as file:
        return [line.strip() for line in file.readlines()]

def write_accounts_to_file(accounts):
    with open('accounts_cat.txt', 'w') as file:
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
            remove_key_lines('locked_accounts.txt', 'CAT')
            
            retry_count = 0
            i += 1
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
                    lock_account(accounts[i-1], 'CAT' )
                    bot = TelegramBotAutomation(accounts[i-1])
                    bot.scrshot = 1 #0 for no screenshots
                    try:
                        delete_oldScreens()
                        bot.navigate_to_bot("@catsgang_bot")
                        bot.start_game()
                        bot.avatar()
                        bot.upgradeCat()
                        bot.sendPic()

                        logging.info(f"Account {accounts[i-1]}: Processing completed successfully.")
                        success = True  
                    except Exception as e:
                        logging.warning(f"Account {accounts[i-1]}: Error occurred on attempt {retry_count + 1}: {e}")
                        retry_count += 1  
                    finally:
                        
                        logging.info("-------------END-----------")
                        bot.browser_manager.close_browser()
                        logging.info("-------------END-----------")
                        sleep_time = random.randrange(5, 15)
                        unlock_account(accounts[i-1], "CAT")
                        logging.info(f"Sleeping for {sleep_time} seconds.")
                        time.sleep(sleep_time)

                    
                    if retry_count >= 3:
                        logging.warning(f"Account {accounts[i-1]}: Failed after 3 attempts.")
                        remove_key_lines('locked_accounts.txt', 'CAT')
                

            if not success:
                logging.warning(f"Account {accounts[i-1]}: Moving to next account after 3 failed attempts.")
            
           

            

        

        logging.info("All accounts processed. Waiting 6 hours before restarting.")

        for hour in range(6):
            logging.info(f"Waiting... {6 - hour} hours left till restart.")
            time.sleep(60 * 60)  

        
        logging.info("Shuffling accounts for the next cycle.")

if __name__ == "__main__":
    process_accounts()
