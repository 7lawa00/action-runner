from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def run_selenium_action_demo():
    """Simple Selenium demo that opens example.com and captures title."""
    try:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.set_window_size(1200, 800)
        driver.get('https://example.com')
        title = driver.title
        driver.quit()
        return {'ok': True, 'title': title}
    except Exception as e:
        return {'ok': False, 'error': str(e)}
