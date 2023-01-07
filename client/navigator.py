from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

nav = None

def initialize_nav():
    
    global nav
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    nav = webdriver.Chrome(options=options)
    
initialize_nav()