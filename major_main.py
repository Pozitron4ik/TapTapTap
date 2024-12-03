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

debug = False

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

            if debug:
                launch_args = json.dumps([f"--load-extension={requestly_extension_path}"])
                headless_param = "0"
            else:
                launch_args = json.dumps(["--headless=new", f"--load-extension={requestly_extension_path}"])
                headless_param = "1"

            request_url = (
                f'http://local.adspower.net:50325/api/v1/browser/start?'
                f'serial_number={self.serial_number}&ip_tab=1&headless={headless_param}&launch_args={launch_args}'
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
                self.driver.set_window_size(600, 900)
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
        self.sleep(2, 3)

    def click_link(self):
        link = self.wait_for_element(By.CSS_SELECTOR, "a[href*='t.me/major/start?startapp']")
        link.click()
        
        #После последней обновы 31.08.24 закомментил
        #launch_click = self.wait_for_element(By.XPATH, "//body/div[@class='popup popup-peer popup-confirmation active']/div[@class='popup-container z-depth-1']/div[@class='popup-buttons']/button[1]/div[1]")
        #launch_click.click()
        logging.info(f"Account {self.serial_number}: NAJOR STARTED")
        sleep_time = random.randrange(6, 12)
        logging.info(f"Sleeping for {sleep_time} seconds.")
        time.sleep(sleep_time)
        if not self.switch_to_iframe():
            logging.info(f"Account {self.serial_number}: No iframes found")
            return

    
    

    def switch_to_iframe(self):
        self.driver.switch_to.default_content()
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            self.driver.switch_to.frame(iframes[0])
            return True
        return False

    
    def clickGames(self):
        try:
            games = self.wait_for_element(By.XPATH,
                    '//*[@id="root"]/div/div/div/div/footer/a[2]/div'
                                            )
            games.click()
            self.sleep(2, 4)
            

            logging.info(f"Account {self.serial_number}: pressed games")
            
        except Exception as e:
            logging.info(f"Account {self.serial_number}: {e}")
        
        if self.scrshot:
            self.driver.save_screenshot(f'screen{self.scrshot}.png')
            self.scrshot += 1

    def durov(self, sequence):
        stage = 0

        try:
            play = self.wait_for_element(By.XPATH,
                                         "//span[text()='Puzzle Durov']"
                                         )
            play.click()
            logging.info(f"Account {self.serial_number}: clicked play durov")
            self.sleep(2, 4)
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
            stage+=1
        except Exception as e:
            logging.info(f"Account {self.serial_number}: {str(e), stage}")
        
        if stage:
            
            try:
                faces = [[0, 0, 0, 0],
                         [0, 0, 0, 0],
                         [0, 0, 0, 0],
                         [0, 0, 0, 0]]
                i = 0
                counter = 1
                while i<4:
                    j = 0
                    while j<4:
                        try:
                            faces[i][j] = self.wait_for_element(By.XPATH, 
                            f'/html/body/div[1]/div/div/div/div/div[1]/div[3]/div/div[2]/div[2]/div[{counter}]'
                                                            )
                        except Exception as e:
                            logging.info(f"Account {self.serial_number}: {str(e)} on stage {stage} on element a{i, j}")
                        j+=1
                        counter+=1
                    i+=1
                stage+=1
                logging.info(f"Account {self.serial_number}: matrix initialized")
            except Exception as e:
                logging.info(f"Account {self.serial_number}: {str(e)} on stage {stage}")

            if stage > 1:
                try:
                    step=1
                    while step <= 4:
                        found = False
                        i = 0
                        while i < 4:
                            j = 0
                            while j < 4:
                                self.driver.execute_script("arguments[0].scrollIntoView();", faces[i][j])
                                if step == sequence[i][j]:
                                    faces[i][j].click()
                                    logging.info(f"Account {self.serial_number}: pressed {sequence[i][j]} durov")
                                    self.sleep(1, 3)
                                    if self.scrshot:
                                        self.driver.save_screenshot(f'screen{self.scrshot}.png')
                                        self.scrshot += 1
                                    step += 1
                                    found = True
                                    break  # Exit the inner loop
                                j += 1
                            if found:
                                break  # Exit the outer loop
                            i += 1
                    logging.info(f"Account {self.serial_number}: clicked all durovs")
                    stage += 1

                except Exception as e:
                    logging.info(f"Account {self.serial_number}: {str(e)} on stage {stage}, element{i}{j}")
        
        if stage > 2:
            try:
                check = self.wait_for_element(By.CSS_SELECTOR,
                                '#root > div > div > div > div > div.min-page-content-height > div.p-4.tg-bg.min-h-\[35vh\].rounded-t-lg > div > button'
                                            )
                self.driver.execute_script("arguments[0].scrollIntoView();", check)
                check.click()
                logging.info(f"Account {self.serial_number}: clicked check")
                self.sleep(2, 4)
                if self.scrshot:
                    self.driver.save_screenshot(f'screen{self.scrshot}.png')
                    self.scrshot += 1
            except Exception as e:
                logging.info(f"Account {self.serial_number}: {str(e)} on stage {stage} while checking")





    def takeBonus(self):
        try:
            takebutton = self.wait_for_element(By.CSS_SELECTOR,
                        # '//*[@id="root"]/div/div/div/div/div[2]/div/div[4]/div'
                        # '//*[@id="root"]/div/div/div/div/div[2]/div/div[4]/button'
                          #  '/html/body/div[1]/div/div/div/div/div[2]/div/div[1]'
                           '#root > div > div > div > div > div.top-0.left-0.h-dvh.w-dvw.z-\[2\].fixed > div > div._close_15ei1_7'
                                            )
            takebutton.click()
            self.sleep(1, 3)
            
            logging.info(f"Account {self.serial_number}: took bonus")

            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1

        except Exception as e:
            logging.info(f"Account {self.serial_number}: no bonus")
        
        
    def checkCross(self):
        try:
            cross = self.wait_for_element(By.XPATH, '//*[@id="root"]/div/div/div/div/div[2]/div/div[1]')
            cross.click()
            time.sleep(1)
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
            
            logging.info(f"Account {self.serial_number}: wait until next spin")
            return 1

        except Exception as e:
            return 0


    
    def clickSpin(self):
        logging.info(f"Account {self.serial_number}: trying to spin roulette...")
        try:
            
            play = self.wait_for_element(By.XPATH,
              #  '//*[@id="root"]/div/div/div/div/div[1]/div[3]/div[2]/div/div[2]/div/div[2]/div'
                '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[1]/div[3]/div[1]/div[2]/button[1]'
                                        )
            play.click()
            self.sleep(2, 4)
            logging.info(f"Account {self.serial_number}: clicked play")

            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1

            if self.checkCross():
                return 
            
        except Exception as e:
            logging.info(f"Account {self.serial_number}: {e}")
        
        
        try: 
            spin = self.wait_for_element(By.XPATH,
              # '//*[@id="root"]/div/div/div/div/div[1]/div[3]/div/div[2]/div/div[1]'
               '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]/button[1]'
                                        )
            self.driver.execute_script("arguments[0].scrollIntoView();", spin)
            spin.click()
            logging.info(f"Account {self.serial_number}: clicked spin")
            self.sleep(7, 9)

            
        except Exception as e:
            logging.info(f"Account {self.serial_number}: {e}")


        try:
            activate = self.wait_for_element(By.XPATH,
                               # '//*[@id="root"]/div/div/div/div/div[2]/div/div[3]/div'  
                                '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[3]/button[1]'
                                            )
            
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
            self.driver.execute_script("arguments[0].scrollIntoView();", activate)
            activate.click()
            self.sleep(1, 3)
            logging.info(f"Account {self.serial_number}: actvated bonus")

        except Exception as e:
            logging.info(f"Account {self.serial_number}: {e}")
            
            
    def clickMonetka(self):
        logging.info(f"Account {self.serial_number}: trying to hold monetochka...")
        try:
            play = self.wait_for_element(By.XPATH,
                               # '//*[@id="root"]/div/div/div/div/div[1]/div[3]/div[2]/div/div[1]/div/div[2]/div'
                               
                                        )   
            play.click()
            self.sleep(2, 4)
            logging.info(f"Account {self.serial_number}: clicked play")
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1

            if self.checkCross():
                return


        except Exception as e:
            logging.info(f"Account {self.serial_number}: {e}")
        

        try:
            element = self.wait_for_element(By.CSS_SELECTOR,
                          '#root > div > div > div > div > div.min-page-content-height > div:nth-child(5) > div > div.flex.flex-col.items-center.pt-7.h-full.w-full.pb-14 > div.scale-element.false.max-w-\[305px\].transition-all.duration-300.relative.mt-7 > div:nth-child(3)'
                                            )

            self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mousedown', {bubbles:true,cancelable:true,view:window}));", element)
            tihi_chas = 55+random.randint(0, 4)
            logging.info(f"Account {self.serial_number}: holding this shit for {tihi_chas} sec...")
            # Ожидаем заданное время
            time.sleep(tihi_chas)

            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1

            # С помощью JavaScript инициируем событие mouse up
            self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseup', {bubbles:true,cancelable:true,view:window}));", element)
            logging.info(f"Account {self.serial_number}: success monetka hold")

            time.sleep(60 - tihi_chas + random.randrange(0, 3))
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1

            self.wait_for_element(By.XPATH,
                        '//*[@id="root"]/div/div/div/div/div[2]/div/div[3]/div'
                                  ).click()
            logging.info(f"Account {self.serial_number}: activated bonus")
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
            
        except Exception as e:
            logging.info(f"Account {self.serial_number}: {e}")


    def postStory(self):
        stage = 0
        try:
            earn = self.wait_for_element(By.XPATH,
                            '//*[@id="root"]/div/div/div/div/footer/a[1]/div'
                                         )
            earn.click()
            self.sleep(1, 3)
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
            stage +=1
            logging.info(f"Account {self.serial_number}: clicked earn")
        except Exception as e:
            logging.info(f"Account {self.serial_number}: {e, stage}")
        
        if stage:
            try:
                but1st =  self.wait_for_element(By.XPATH,
                        "//span[text()='Share in Telegram Stories']"           
                                                )
                self.driver.execute_script("arguments[0].scrollIntoView();", but1st)
                but1st.click()
                self.sleep(1, 3)

                if self.scrshot:
                    self.driver.save_screenshot(f'screen{self.scrshot}.png')
                    self.scrshot += 1

                logging.info(f"Account {self.serial_number}: pressed task 'story'")
                stage += 1
            except Exception as e:
                logging.info(f"Account {self.serial_number}: {e, stage}")
        
        if stage > 1:
            try:
                share = self.wait_for_element(By.XPATH,
                                "//span[text()='Share']"
                )
                self.driver.execute_script("arguments[0].scrollIntoView();", share)
                share.click()
                self.sleep(1, 3)
                logging.info(f"Account {self.serial_number}: pressed share")
                stage += 1
            except Exception as e:
                logging.info(f"Account {self.serial_number}: {e, stage}")
        
        if stage > 2:
            try:
                check = self.wait_for_element(By.XPATH,
                            '//*[@id="modal"]/div[3]/div'
                                              )
                self.driver.execute_script("arguments[0].scrollIntoView();", check)
                check.click()
                self.sleep(1, 3)
                logging.info(f"Account {self.serial_number}: pressed check")
                stage += 1
                if self.scrshot:
                    self.driver.save_screenshot(f'screen{self.scrshot}.png')
                    self.scrshot += 1
            except Exception as e:
                logging.info(f"Account {self.serial_number}: {e, stage}")
    
    def switch_tabs(self):
        try:
            # Логирование начала процесса переключения
            logging.info("Начинаем переключение вкладок.")
            
            # Получаем список открытых вкладок
            tabs = self.driver.window_handles
            logging.info(f"Открыто {len(tabs)} вкладок.")

            # Определяем текущую вкладку
            current_tab = self.driver.current_window_handle
            current_index = tabs.index(current_tab)
            
            # Рассчитываем индекс следующей вкладки
            next_index = (current_index + 1) % len(tabs)
            logging.info(f"Переключаемся с вкладки {current_index} на {next_index}.")
            
            # Переключаемся на следующую вкладку
            self.driver.switch_to.window(tabs[next_index])
            
            # Ждём некоторое время, чтобы вкладка могла полностью загрузиться
            time.sleep(1)

            # Делаем скриншот, если включена опция
            if self.scrshot:
                screenshot_name = f'screen{self.scrshot}.png'
                self.driver.save_screenshot(screenshot_name)
                logging.info(f"Сохранен скриншот: {screenshot_name}")
                self.scrshot += 1

            # Ждём перед переключением обратно
            self.sleep(3, 7)

            # Возвращаемся на исходную вкладку
            logging.info("Переключаемся обратно на исходную вкладку.")
            self.driver.switch_to.window(tabs[current_index])

            # Переходим в iframe, если это нужно
            logging.info("Переключаемся на iframe.")
            self.switch_to_iframe()

        except Exception as e:
            # Логируем любые возникшие ошибки
            logging.error(f"Ошибка в аккаунте {self.serial_number}: {e}")




    def shorts(self):
        stage = 0
        try:
            but1st = self.wait_for_element(By.XPATH,
                         "//span[text()='Watch YouTube Shorts']"
                                           )
            
            self.driver.execute_script("arguments[0].scrollIntoView();", but1st)
            but1st.click()
            self.sleep(1, 3)
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
            logging.info(f"Account {self.serial_number}: pressed task 'shorts' ")
            stage += 1
        except Exception as e:
            logging.info(f"Account {self.serial_number}: {e, stage}")
        
        if stage:
            try:
                watch = self.wait_for_element(By.XPATH,
                            '//*[@id="root"]/div/div/div/div/div[2]/div/div[4]/button'
                                              )
                watch.click()

                self.sleep(1, 3)
                stage += 1
                logging.info(f"Account {self.serial_number}: pressed watch")
            except Exception as e:
                logging.info(f"Account {self.serial_number}: {e, stage}")
        
        if stage > 1:
            try:
                self.switch_tabs()
                check = self.wait_for_element(By.XPATH,
                            '//*[@id="modal"]/div[3]/div'
                                              )
                
                self.sleep(5, 8)
                check.click()
                time.sleep(1)
                if self.scrshot:
                    self.driver.save_screenshot(f'screen{self.scrshot}.png')
                    self.scrshot += 1
                logging.info(f"Account {self.serial_number}: pressed сheck")
                stage += 1
            except Exception as e:
                logging.info(f"Account {self.serial_number}: {e, stage}")

    def goats(self):
        stage = 0
        try:
            goatsBut = self.wait_for_element(By.XPATH,
                            "//span[text()='GOATS']"
                                            )
            self.driver.execute_script("arguments[0].scrollIntoView();", goatsBut)
            goatsBut.click()
            self.sleep(2, 4)
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
            stage +=1
        except Exception as e:
            logging.info(f"Account {self.serial_number}: {e, stage}")
    
        if stage:
            try:
                join = self.wait_for_element(By.XPATH,
                              '//*[@id="root"]/div/div/div/div/div[2]/div/div[4]/button'
                                             )
                join.click()
                self.sleep(2, 4)
                if self.scrshot:
                    self.driver.save_screenshot(f'screen{self.scrshot}.png')
                    self.scrshot += 1
                stage +=1
            except Exception as e:
                logging.info(f"Account {self.serial_number}: {e, stage}")
        
        if stage > 1:
            try:
                self.driver.switch_to.default_content()
                launch = self.wait_for_element(By.XPATH, 
                                 '/html/body/div[7]/div/div[2]/button[1]/div'
                                               )
                launch.click()
                self.sleep(2, 4)
                if self.scrshot:
                    self.driver.save_screenshot(f'screen{self.scrshot}.png')
                    self.scrshot += 1
                stage +=1
            except Exception as e:
                logging.info(f"Account {self.serial_number}: {e, stage}")
        
        if stage > 2:
            try:
                major = self.wait_for_element(By.XPATH,
                                              '/html/body/div[6]/div/div[1]/div[1]/div/div[2]/button[1]'
                                              )
                major.click()
                self.sleep(2, 4)
                self.switch_to_iframe()
                if self.scrshot:
                    self.driver.save_screenshot(f'screen{self.scrshot}.png')
                    self.scrshot += 1
                stage +=1
            except Exception as e:
                logging.info(f"Account {self.serial_number}: {e, stage}")
                
        if stage > 3:
            try:
                check = self.wait_for_element(By.XPATH,
                                '//*[@id="modal"]/div[3]/div'
                                              )
                check.click()
                self.sleep(1, 3)
                if self.scrshot:
                    self.driver.save_screenshot(f'screen{self.scrshot}.png')
                    self.scrshot += 1
                stage +=1
            except Exception as e:
                logging.info(f"Account {self.serial_number}: {e, stage}")
                

    def tonChannels(self):
        stage = 0
        try:
            tonchan = self.wait_for_element(By.XPATH,
                   "//span[text()='TON Channels']"
                                  )
            self.driver.execute_script("arguments[0].scrollIntoView();", tonchan)
            tonchan.click()
            self.sleep(1, 3)
            logging.info(f"Account {self.serial_number}: pressed task 'ton channels'")
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
            stage += 1
        except Exception as e:
            logging.info(f"Account {self.serial_number}: {e, stage}")
        
        if stage:
            try:
                subscribe = self.wait_for_element(By.XPATH,
                   "//span[text()='Subscribe']"
                                  )
                self.driver.execute_script("arguments[0].scrollIntoView();", subscribe)
                subscribe.click()
                self.sleep(1, 3)
                logging.info(f"Account {self.serial_number}: pressed subscribe")
                if self.scrshot:
                    self.driver.save_screenshot(f'screen{self.scrshot}.png')
                    self.scrshot += 1
                stage += 1
            except Exception as e:
                logging.info(f"Account {self.serial_number}: {e, stage}")
        
        if stage > 1:
            try:
                self.driver.switch_to.default_content()
                join = self.wait_for_element(By.XPATH, 
                                    '/html/body/div[7]/div/div[3]/button'
                                             )
                join.click()
                self.sleep(1, 2)
                self.switch_to_iframe()
                logging.info(f"Account {self.serial_number}: pressed subscribe")
                if self.scrshot:
                    self.driver.save_screenshot(f'screen{self.scrshot}.png')
                    self.scrshot += 1
                stage += 1
            except Exception as e:
                logging.info(f"Account {self.serial_number}: {e, stage}")

        if stage > 2:
            try:
                check = self.wait_for_element(By.XPATH,
                                    '//*[@id="modal"]/div[3]/div'
                                              )
                self.driver.execute_script("arguments[0].scrollIntoView();", check)
                check.click()
                self.sleep(1, 2)
                logging.info(f"Account {self.serial_number}: pressed check")
                if self.scrshot:
                    self.driver.save_screenshot(f'screen{self.scrshot}.png')
                    self.scrshot += 1
                stage += 1
            except Exception as e:
                logging.info(f"Account {self.serial_number}: {e, stage}")            


    def followMajor(self):
        stage = 0
        try:
            follow = self.wait_for_element(By.XPATH,
                    "//span[text()='Follow Major in Telegram']"
                                        )
            self.driver.execute_script("arguments[0].scrollIntoView();", follow)
            follow.click()
            self.sleep(1, 2)
            logging.info(f"Account {self.serial_number}: pressed task 'follow Major in tg'")
            if self.scrshot:
                self.driver.save_screenshot(f'screen{self.scrshot}.png')
                self.scrshot += 1
            stage += 1
        except Exception as e:
            logging.info(f"Account {self.serial_number}: {e, stage}")

        if stage:
            try:
                check = self.wait_for_element(By.XPATH,
                                           '//*[@id="modal"]/div[3]/div'   
                                              )
                check.click()
                self.sleep(1, 2)
                logging.info(f"Account {self.serial_number}: pressed check")
                if self.scrshot:
                    self.driver.save_screenshot(f'screen{self.scrshot}.png')
                    self.scrshot += 1
            except Exception as e:
                logging.info(f"Account {self.serial_number}: {e, stage}")

        



    def tasks(self):
        self.tonChannels()
        self.followMajor()


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

   

def read_accounts_from_file():
    with open('accounts_major.txt', 'r') as file:
        return [line.strip() for line in file.readlines()]

def write_accounts_to_file(accounts):
    with open('accounts_major.txt', 'w') as file:
        for account in accounts:
            file.write(f"{account}\n")

def process_accounts():
    last_processed_account = None
    
    order = [[4, 0, 0, 0],
             [0, 0, 2, 0],
             [0, 0, 0, 1],
             [0, 3, 0, 0]]

    

    while True:
        

        accounts = read_accounts_from_file()
        random.shuffle(accounts)
        write_accounts_to_file(accounts)
        i = 0
        while i < len(accounts):
            remove_empty_lines('locked_accounts.txt')
            remove_key_lines('locked_accounts.txt', 'NAJOR')
            
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
                    lock_account(accounts[i-1], 'NAJOR' )
                    bot = TelegramBotAutomation(accounts[i-1])
                    bot.scrshot = 0 #0 for no screenshots
                    try:
                        delete_oldScreens()
                        bot.navigate_to_bot()
                        bot.send_message("https://t.me/nazhorikplotnogoooool")
                        bot.click_link()
                        time.sleep(1)
                        
                        bot.takeBonus()
                       #bot.postStory()
                       #bot.tasks()


                        bot.clickGames()
                        bot.clickSpin()
                       #bot.back()
                       #bot.clickGames()
                       #bot.durov(order)

                       # bot.clickGames()
                       # bot.clickMonetka()

                        logging.info(f"Account {accounts[i-1]}: Processing completed successfully.")
                        success = True  
                    except Exception as e:
                        logging.warning(f"Account {accounts[i-1]}: Error occurred on attempt {retry_count + 1}: {e}")
                        retry_count += 1  
                    finally:
                        logging.info("-------------END-----------")
                        bot.browser_manager.close_browser()
                        logging.info("-------------END-----------")
                        unlock_account(accounts[i-1], "NAJOR")
                        sleep_time = random.randrange(5, 15)
                        logging.info(f"Sleeping for {sleep_time} seconds.")
                        time.sleep(sleep_time)
                    
                    if retry_count >= 3:
                        logging.warning(f"Account {accounts[i-1]}: Failed after 3 attempts.")
                

            if not success:
                logging.warning(f"Account {accounts[i-1]}: Moving to next account after 3 failed attempts.")
                

            

        

        logging.info("All accounts processed. Waiting 8 hours before restarting.")

        for hour in range(8):
            logging.info(f"Waiting... {8 - hour} hours left till restart.")
            time.sleep(60 * 60)  

        
        logging.info("Shuffling accounts for the next cycle.")

if __name__ == "__main__":
    process_accounts()