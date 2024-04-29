import pandas as pd
from selenium import webdriver

# The By class is used to locate elements within a document.
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException, TimeoutException

options = webdriver.ChromeOptions()
# Do not use GUI
options.add_argument("headless")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
# debug console log
options.add_argument("--log-level=3")
# To enable .click() in headless mode
options.add_argument("--window-size=1024,800")

with webdriver.Chrome(options=options) as driver:
    wait = WebDriverWait(driver, 4)
    df = pd.DataFrame()

    for i in range(1, 34):
        driver.get(
            "https://job.incruit.com/jobdb_list/categoryjob.asp?compcate={:02d}".format(
                i
            )
        )

        try:
            # tag = driver.find_element(By.XPATH, "//*[@id=\"incruit_contents\"]/div[1]/div/div[1]/h2").text
            tag = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="incruit_contents"]/div[1]/div/div[1]/h2')
                )
            )
            print("{} : {}".format(i, tag.text))
            df = pd.concat([df, pd.DataFrame.from_dict([tag.text])], ignore_index=True)
        except TimeoutException:
            pass

    df.to_csv("tags.csv", encoding="utf-8-sig")
