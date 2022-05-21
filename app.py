import time
import traceback
import psycopg2
import requests
import schedule
from bs4 import BeautifulSoup
from capmonster_python import RecaptchaV2Task
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium_stealth import stealth
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from datetime import datetime

service = Service("C:/chromedriver/chromedriver.exe")
url = "https://www.kv.ee/?act=search.simple&last_deal_type=20&company_id=237&orderby=cdwl&deal_type=20&dt_select=20&company_id_check=237&county=1&search_type=new&parish=1061"
reCaptcha_xpath = "//div[@class='g-recaptcha g-recaptcha-center']"


class RecaptchaV2Selenium:
    def __init__(self, _client_key, driver, kv_url):
        self.captcha = RecaptchaV2Task(_client_key)
        self.browser = driver
        self.website_url = kv_url

    def _get_site_key(self):
        site_key = self.browser.find_element(By.XPATH, reCaptcha_xpath).get_attribute(
            "data-sitekey")
        print(site_key)
        return site_key

    def _solve_recaptcha(self):
        task_id = self.captcha.create_task(website_url=self.website_url,
                                           website_key=self._get_site_key(),
                                           no_cache=True)
        solved_captcha = self.captcha.join_task_result(task_id=task_id, maximum_time=240).get("gRecaptchaResponse")
        print(solved_captcha)

        return solved_captcha

    def submit_form(self):
        self.browser.execute_script("""document.querySelector('[name="g-recaptcha-response"]').innerText='{}'""".format(
            self._solve_recaptcha()))


def clear_email_count():
    open("emailscount.txt", "w").close()


def add_email_count():
    file1 = open("emailscount.txt", "a")
    file1.write("S")
    file1.close()


def read_email_count():
    file = open("emailscount.txt", "r")
    data = file.read().replace(" ", "")
    number_of_emails = len(data)

    return number_of_emails


def scrap():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-first-run")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=service, options=options)

    stealth(driver,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/101.0.4951.67 Safari/537.36",
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    driver.get(url)
    page = driver.page_source
    soup = BeautifulSoup(page, features="lxml")
    table_property = soup.find("div", id="res")
    table_rows = table_property.find_all("tr", attrs={'class': 'object-type-apartment object-item'})
    real_estate = []
    print("GETTING ESTATE ID's...\n")
    for row in table_rows:
        for link in row.find_all('a', attrs={'class': 'object-title-a text-truncate'}):
            link_id = link['href']
            id_array = link_id.split("/")[3][:-5].split('-')[-1]
            real_estate.append(id_array)

    driver.quit()

    return real_estate


def check_real_estate():
    button_send_message_xpath = "//div[@class='inner']//div[@class='object-button']"
    button_accept_cookies_xpath = "//div[@id='onetrust-consent-sdk']//button[@id='onetrust-accept-btn-handler']"
    booked_xpath = "//tr[@class='hide-on-mobile hide-on-tablet']/th"
    title_xpath = "//div[@class='hgroup large']//h1"
    deactivated_xpath = "//div[@class='object-passive-notice']"
    text_xpath = "//div[@class='broker-form-fields-full']/textarea[@id='brokerf-txtarea']"
    email_xpath = "//input[@id='broker-email']"
    telephone_xpath = "//input[@type='tel']"
    sellers_number_xpath = "//div[@class='broker-contact-info broker-contact-collapsable']/ul/li"
    sellers_name_xpath = "//div[@class='article-broker-info-container broker-contact-content broker-contact-private " \
                         "']//div[@class='broker-info']//div[@class='broker-name']"
    address_xpath = "//form/input[@class='input-wide input-field']"
    price_xpath = "//div[@class='object-price']/strong"
    
    bot = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" 
    client_telegram_id = "XXXXXXXXXX"
    client_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    my_telegram_id = "XXXXXXXXXXXX"
    counter = 0

    def fill_form(book_type, wdriver, estate_url):
        textbox = wdriver.find_element(By.XPATH, text_xpath)
        email = wdriver.find_element(By.XPATH, email_xpath)
        telephone = wdriver.find_element(By.XPATH, telephone_xpath)
        element = wait.until(EC.presence_of_element_located((By.XPATH, reCaptcha_xpath))).is_displayed()
        message_sent_xpath = "//div[@class='mail-sent-box']"
        send_button_xpath = "//button[@id='brokerf_submit']"

        time.sleep(1)

        email.send_keys("XXXXXXXXXXXXXXXXXXXXXX")
        time.sleep(1)
        telephone.send_keys("+372 XXXXXXXX")
        time.sleep(1)
        textbox.clear()
        time.sleep(3)

        if book_type == 'sell':
            with open('PRODAZHA.txt', encoding="utf8") as f:
                lines = f.read()
                driver.execute_script("arguments[0].value = arguments[1]", textbox, lines)

        elif book_type == 'rent':
            with open('ARENDA.txt', encoding="utf8") as f:
                lines = f.read()
                driver.execute_script("arguments[0].value = arguments[1]", textbox, lines)

        if element:
            RecaptchaV2Selenium(client_key, wdriver, estate_url).submit_form()
            print("**************************************DONE SOLVING**************************************")
            time.sleep(5)
            driver.find_element(By.XPATH, send_button_xpath).click()
            wait_confirm = WebDriverWait(wdriver, 30)
            message_confirm = wait_confirm.until(
                EC.visibility_of_element_located((By.XPATH, message_sent_xpath))).is_displayed()
            if message_confirm:
                print(">>>> ADDING ID TO DATABASE <<<<\n")
                real_estate_db.execute('INSERT INTO real_estate (estate_id) VALUES (%s);', [str(item)])
                connection.commit()
                return True
            else:
                send_message(my_telegram_id, "FAILED TO SEND FILLED FORM")
                send_message(client_telegram_id, "FAILED TO SEND FILLED FORM")
                return False

    def send_message(chat_id, text):
        # send telegram message
        parameters = {'chat_id': chat_id, 'text': text}
        requests.post(bot + 'sendMessage', data=parameters)

    def iselement(browser, xpath):
        try:
            browser.find_element(By.XPATH, xpath)
            return True
        except exceptions.NoSuchElementException:
            return False

    print("CONNECTING TO DATABASE.\n")

    estate_list = []

    try:
        database_url = 'postgres://uzzjqgth:p06TGymS7Npwx8tHHwqSV5HzfjcukDDL@rogue.db.elephantsql.com/uzzjqgth'
        connection = psycopg2.connect(database_url, sslmode='require')
        real_estate_db = connection.cursor()
        real_estate_db.execute(
            'CREATE TABLE IF NOT EXISTS real_estate (id SERIAL PRIMARY KEY, estate_id TEXT NOT NULL)')
        print("GETTING PAGE SOURCE..\n")
        real_estates = scrap()
        query = 'SELECT * FROM real_estate'
        real_estate_db.execute(query)
        records = real_estate_db.fetchall()
        reversed_real_estates = list(reversed(real_estates))

        # Check list
        print("REAL ESTATE LIST = " + str(reversed_real_estates) + "\n")

        for row in records:
            estate_list.append([row[0], row[1]])

        # Check db
        print("REAL ESTATE DATABASE = " + str(estate_list) + "\n")
        print("COMPARING REAL ESTATES....\n")

        for item in reversed_real_estates:
            real_estate_db.execute('SELECT estate_id FROM real_estate WHERE estate_id = %s', [str(item)])
            if len(real_estate_db.fetchall()) != 1:
                print("> A NEW ESTATE HAS BEEN FOUND <\n")

                kv_url = 'https://www.kv.ee/' + str(item)
                options = webdriver.ChromeOptions()
                options.add_argument("--start-maximized")
                driver = uc.Chrome(options=options, use_subprocess=True)
                driver.get(kv_url)

                # broker_name = driver.find_element(By.XPATH, broker_name_xpath).text
                booked_check = driver.find_element(By.XPATH, booked_xpath).text
                title = driver.find_element(By.XPATH, title_xpath).text

                # print(broker_name)
                print(booked_check)
                print(title)
                
                wait = WebDriverWait(driver, 120)
                element_cookie = iselement(driver, button_accept_cookies_xpath)

                if element_cookie:
                    wait.until(EC.element_to_be_clickable((By.XPATH, button_accept_cookies_xpath))).click()

                # print("check " + str(iselement(driver, deactivated_xpath)))

                if iselement(driver, deactivated_xpath):
                    print("**** TYPE IS DEACTIVATED ****\n")
                    time.sleep(3)
                    driver.quit()
                    real_estate_db.execute('INSERT INTO real_estate (estate_id) VALUES (%s);', [str(item)])
                    connection.commit()
                    continue
                else:
                    if "(Broneeritud)" in booked_check:
                        print("**** BOOKED, SKIPPING ****\n")
                        time.sleep(3)
                        driver.quit()
                        real_estate_db.execute('INSERT INTO real_estate (estate_id) VALUES (%s);', [str(item)])
                        connection.commit()
                        print("**** DONE ****\n")
                    elif "(Broneeritud)" not in booked_check:

                        sellers_number = "Не имеется"
                        sellers_name = "Боится"
                        address = "Не имеется"
                        price = "Надо обкашлить"
                        google_maps = "Не имеется"
                        dt = "Нет"

                        print(">> DETERMINING SELL TYPE <<\n")
                        if "Anda" in title:
                            print(">>> TYPE IS RENTAL <<<\n")
                            print(">>>> SENDING RENTAL TYPE SITE MESSAGE <<<<\n")
                            wait.until(EC.presence_of_element_located((By.XPATH, button_send_message_xpath))).click()

                            # sellers number, name, address, price
                            if iselement(driver, sellers_number_xpath):
                                number = driver.find_element(By.XPATH, sellers_number_xpath).text
                                if "+3" not in number:
                                    sellers_number = "+372" + number
                                else:
                                    sellers_number = number
                            if iselement(driver, sellers_name_xpath):
                                sellers_name = driver.find_element(By.XPATH, sellers_name_xpath).text
                            if iselement(driver, address_xpath):
                                address = driver.find_element(By.XPATH, address_xpath).get_attribute("value")
                                google_maps = "https://maps.google.com/maps?q={}".format(
                                    address.strip().replace(" ", ""))
                            if iselement(driver, price_xpath):
                                price = driver.find_element(By.XPATH, price_xpath).text

                            time.sleep(3)

                            # fill form
                            message_counter = fill_form('rent', driver, kv_url)
                            if message_counter:
                                dt = datetime.now()
                                add_email_count()
                                counter = read_email_count()

                            print(">>>> SENDING TELEGRAM MESSAGE <<<<\n")

                            # send telegram message
                            message = "BING CHILLING!\U0001F976\U0001F976\U0001F976\n\nНовое объявление об аренде: " + \
                                      kv_url + "\n\n" + "Счетчик: " + str(counter) + "\n\n" + "Время отправки: " + \
                                      str(dt) + "\n\n" + "$$$: " + price + "\n" + "Имя кента: " + sellers_name + "\n" \
                                      + "Локация хаты: " + address + "\n" + "Номер кента: " + \
                                      sellers_number.replace(" ", "").strip() + "\n\n" + "Гугл мапа: " + google_maps

                            send_message(client_telegram_id, message)
                            send_message(my_telegram_id, message)

                            driver.quit()

                            print(">>>>> DONE <<<<<\n")

                        elif "Müüa" in title:
                            print(">>> TYPE IS SELL <<<\n")
                            print(">>>> SENDING SELL TYPE SITE MESSAGE <<<<\n")
                            wait.until(EC.presence_of_element_located((By.XPATH, button_send_message_xpath))).click()

                            # sellers number
                            if iselement(driver, sellers_number_xpath):
                                number = driver.find_element(By.XPATH, sellers_number_xpath).text
                                if "+3" not in number:
                                    sellers_number = "+372" + number
                                else:
                                    sellers_number = number
                            if iselement(driver, sellers_name_xpath):
                                sellers_name = driver.find_element(By.XPATH, sellers_name_xpath).text
                            if iselement(driver, address_xpath):
                                address = driver.find_element(By.XPATH, address_xpath).get_attribute("value")
                                google_maps = "https://maps.google.com/maps?q={}".format(
                                    address.strip().replace(" ", ""))
                            if iselement(driver, price_xpath):
                                price = driver.find_element(By.XPATH, price_xpath).text

                            time.sleep(3)

                            # fill form
                            message_counter = fill_form('sell', driver, kv_url)
                            if message_counter:
                                dt = datetime.now()
                                add_email_count()
                                counter = read_email_count()

                            print(">>>> SENDING SELL TYPE TELEGRAM MESSAGE <<<<\n")
                            # send telegram message
                            message = "BING CHILLING!\U0001F976\U0001F976\U0001F976\n\nНовое объявление о продаже: " + \
                                      kv_url + "\n\n" + "Счетчик: " + str(counter) + "\n\n" + "Время отправки: " \
                                      + str(dt) + "\n\n" + "$$$: " + price + "\n" + "Имя кента: " + sellers_name + "\n"\
                                      + "Локация хаты: " + address + "\n" + "Номер кента: " + \
                                      sellers_number.replace(" ", "").strip() + "\n\n" + "Гугл мапа: " + google_maps

                            send_message(client_telegram_id, message)
                            send_message(my_telegram_id, message)

                            driver.quit()

                            print(">>>>> DONE <<<<<\n")

            else:
                continue

        real_estate_db.close()

    except Exception:
        print("******************** FAILED ********************\n")
        send_message(client_telegram_id, "ERROR")
        send_message(my_telegram_id, "ERROR")
        print(traceback.format_exc())


def nest_data():
    try:
        database_url = 'postgres://uzzjqgth:p06TGymS7Npwx8tHHwqSV5HzfjcukDDL@rogue.db.elephantsql.com/uzzjqgth'
        connection = psycopg2.connect(database_url, sslmode='require')
        real_estate_db = connection.cursor()
        print("DELETING DATA\n")
        real_estate_db.execute('DROP TABLE real_estate')
        print("CREATING TABLE\n")
        real_estate_db.execute('CREATE TABLE real_estate (id SERIAL PRIMARY KEY, estate_id TEXT NOT NULL)')
        print("GETTING PAGE SOURCE..\n")
        real_estates = scrap()
        reversed_real_estates = list(reversed(real_estates))

        # Check list
        print("REAL ESTATE LIST = " + str(reversed_real_estates) + "\n")

        for item in reversed_real_estates:
            real_estate_db.execute('SELECT estate_id FROM real_estate WHERE estate_id = %s', [str(item)])
            if len(real_estate_db.fetchall()) != 1:
                real_estate_db.execute('INSERT INTO real_estate (estate_id) VALUES (%s);', [str(item)])
                connection.commit()

        print("**** DATA NESTED ****")
        real_estate_db.close()

        try:
            connection = psycopg2.connect(database_url, sslmode='require')
            real_estate_db = connection.cursor()
            query = 'SELECT * FROM real_estate'
            real_estate_db.execute(query)
            records = real_estate_db.fetchall()
            estate_list = []
            for row in records:
                estate_list.append([row[0], row[1]])

            print(estate_list)

        except Exception:
            print("******************** FAILED TO CHECK ********************\n")
            print(traceback.format_exc())

    except Exception:
        print("******************** FAILED TO NEST ********************\n")
        print(traceback.format_exc())


check_real_estate()
# nest_data()


schedule.every(15).minutes.do(check_real_estate)
schedule.every().monday.do(clear_email_count)
schedule.every(30).days.do(nest_data)

while True:
    schedule.run_pending()
    time.sleep(1)
