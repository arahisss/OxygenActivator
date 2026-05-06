from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import subprocess
import socket
import random


def _get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def get_driver(logfile_path="chromedriver_and_chrome.log", headless=True, timeout=15):
    options = webdriver.ChromeOptions()
    # if headless:
    #     options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])

    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

    chromedriver_path = ChromeDriverManager().install()
    port = _get_free_port()

    log_fd = open(logfile_path, "a", buffering=1, encoding="utf-8", errors="ignore")

    popen_kwargs = {"stdout": log_fd, "stderr": log_fd}
    if os.name == "nt":
        popen_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    args = [chromedriver_path, f"--port={port}"]

    proc = subprocess.Popen(args, **popen_kwargs)

    started = False
    start_t = time.time()
    while time.time() - start_t < timeout:
        try:
            test_driver = webdriver.Remote(command_executor=f"http://127.0.0.1:{port}", options=options)
            test_driver.quit()
            started = True
            break
        except Exception:
            time.sleep(0.2)

    if not started:
        try:
            proc.kill()
        except Exception:
            pass
        log_fd.close()
        raise RuntimeError("chromedriver не запустился/не отвечает в отведённое время." + os.path.abspath(logfile_path))

    driver = webdriver.Remote(command_executor=f"http://127.0.0.1:{port}", options=options)

    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
    )
    original_quit = driver.quit

    def _quit_and_kill(*args, **kwargs):
        exc = None
        try:
            original_quit(*args, **kwargs)
        except Exception as e:
            exc = e
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        try:
            log_fd.close()
        except Exception:
            pass
        if exc:
            raise exc

    driver.quit = _quit_and_kill

    driver._chromedriver_proc = proc
    driver._chromedriver_log = os.path.abspath(logfile_path)

    return driver


def wait_for_page_complete(driver, timeout=20):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def dismiss_popups(driver):
    close_selectors = [
        "button[aria-label*='close']",
        "button[aria-label*='Close']",
        "button[aria-label*='Закрыть']",
        "button:has(svg[role='img'])",
        "button.close",
        "button[data-testid*='close']",
        ".cookie-consent__close",
        ".modal button.close"
    ]
    for sel in close_selectors:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            for e in els:
                try:
                    e.click()
                    time.sleep(0.3)
                except Exception:
                    pass
        except Exception:
            pass

    try:
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.ESCAPE)
    except Exception:
        pass

    js = """
    document.querySelectorAll('[role=\"dialog\"], .modal, .overlay, .cookie-banner, .cookie-consent').forEach(e=>e.remove());
    """
    try:
        driver.execute_script(js)
    except Exception:
        pass


def waiting_letter(driver, inbox):
    refresh_button = driver.find_element(
        By.CSS_SELECTOR,
        "button svg[data-tooltip-id='arrows-clockwise']"
    ).find_element(By.XPATH, "./..")

    actions = ActionChains(driver)
    actions.move_to_element(refresh_button).perform()

    max_attempts = 10
    attempt = 0
    letter_found = False

    while attempt < max_attempts and not letter_found:
        dismiss_popups(driver)
        attempt += 1
        try:
            time.sleep(3)
            driver.execute_script("arguments[0].click();", refresh_button)

            first_letter = driver.find_element(
                By.XPATH,
                ".//button[.//p[@title='support@oxygenxml.com']]"
            )

            driver.execute_script("arguments[0].scrollIntoView(true);", first_letter)
            driver.execute_script("arguments[0].click();", first_letter)
            letter_found = True
        except Exception as e:
            time.sleep(3)
            continue


def get_email(driver, pbar):
    max_attempts = 10
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        try:
            email_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.border-gray-20 > button > p"))
            )
            email = email_element.text
            if "@" in email and "Генерируем" not in email:
                pbar.update(1)
                return email

            time.sleep(3)
            driver.refresh()
            dismiss_popups(driver)
        except Exception:
            time.sleep(2)
            continue

def click_top_ok_if_present(driver, timeout=5):
    ok_texts = ["OK", "Ok", "ОК", "Ок", "Понятно", "Принять", "Accept", "Agree", "Yes"]
    try:
        btn = WebDriverWait(driver, timeout).until(
            lambda d: next(
                (
                    el for el in d.find_elements(By.XPATH, "//button|//a")
                    if (el.text or "").strip() in ok_texts
                ),
                False
            )
        )
        if btn and btn is not False:
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.5)
            driver.quit()
            return True
    except Exception:
        pass
    return False

def send_mail(email):
    driver = get_driver()
    license_url = 'https://www.oxygenxml.com/xml_editor/register.html'
    driver.get(license_url)

    email_field = driver.find_element(By.ID, "email")
    email_field.clear()
    email_field.send_keys(email)
    time.sleep(random.uniform(2, 4))

    email_field = driver.find_element(By.ID, "name")
    email_field.clear()
    email_field.send_keys("Gans")
    time.sleep(random.uniform(2, 4))

    country_dropdown = Select(driver.find_element(By.ID, "country"))
    country_dropdown.select_by_visible_text("Armenia")
    time.sleep(random.uniform(3, 5))

    actions = ActionChains(driver)
    actions.move_by_offset(100, 200).perform()
    actions.move_by_offset(-50, 100).perform()

    submit_button = driver.find_element(By.ID, "XML_Editor")
    # submit_button.click()
    driver.execute_script("arguments[0].click();", submit_button)
    click_top_ok_if_present(driver)
    WebDriverWait(driver, 10).until(EC.url_changes(license_url))
    driver.quit()


def gen_license_key(pbar):
    url = 'https://internxt.com/ru/temporary-email'
    driver = get_driver()
    pbar.update(1)
    try:
        driver.get(url)
        dismiss_popups(driver)
        pbar.update(1)
        time.sleep(5)
        email = get_email(driver, pbar)

        send_mail(email)
        inbox = driver.find_element(By.ID, "inbox")
        waiting_letter(driver, inbox)
        pbar.update(1)

        time.sleep(3)
        key = inbox.find_element(By.CSS_SELECTOR, "pre")
        return key.text
    except Exception as e:
        pass
    finally:
        driver.quit()