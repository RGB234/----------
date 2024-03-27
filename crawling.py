import time
import numpy
from selenium import webdriver
# The Keys class provide keys in the keyboard like RETURN, F1, ALT etc.
from selenium.webdriver.common.keys import Keys
# The By class is used to locate elements within a document.
from selenium.webdriver.common.by import By
# Wait for data to be loaded
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


options = webdriver.ChromeOptions()
# Do not use GUI
# options.add_argument("headless")
options.add_argument('--disable-extensions')
options.add_argument('--disable-gpu')
options.add_argument("--log-level=3")

with webdriver.Chrome(options=options) as driver:

# 17 개 지역
# [서울, 부산, 인천, 대전, 광주, 대구, 울산, 세종, 경기, 
# 강운, 충북, 충남, 전북, 전남, 경북, 경남, 제주]

# ul/li[{1~17}]/input
# <input type="checkbox" name="rgn2_list" id="rgn2_list_27" class="shb-chk" data-item-val="27" 
# data-item-name="세종" data-item-upstr="대한민국" value="&amp;rgn2=27">
# https://job.incruit.com/entry/?rgn2=27

######## 지역코드(혹은 ID) : 지역명 수집 ########
    driver.get("https://job.incruit.com/entry/")

    # Setup wait for later
    wait = WebDriverWait(driver, 10)

    regions = driver.find_elements(By.XPATH, "//*[@id=\"dropFirstDown1\"]/div[2]/ul/li")

    rgnID_NAME = {}

    for region in regions:
        # region ID 는 웹 사이트 '지역' 드롭다운 메뉴 순서대로. 일단 정렬x
        rgnID = region.find_element(By.CSS_SELECTOR, "input").get_attribute("data-item-val")
        rgnName = region.find_element(By.CSS_SELECTOR, "input").get_attribute("data-item-name")
        rgnID_NAME[rgnID] = rgnName

    ######## 본격적인 크롤링 ########

    # rgnIDs = rgnID_NAME.keys()
        
    # 울산
    driver.get("https://job.incruit.com/entry/?rgn2=17")

    # 60 lines per page
    lines = driver.find_elements(By.XPATH, "//*[@id=\"incruit_contents\"]/div/div/div[4]/div[1]/div[2]/ul")

    # company name cpname
    cpname = lines[0].find_element(By.XPATH, "//*[@id=\"incruit_contents\"]/div/div/div[4]/div[1]/div[2]/ul[1]/li/div[1]/div[1]/a").text

    # title
    title = lines[0].find_element(By.XPATH, "//*[@id=\"incruit_contents\"]/div/div/div[4]/div[1]/div[2]/ul[1]/li/div[2]/div[1]/a").text

    # 경력
    coreer = lines[0].find_element(By.XPATH, "//*[@id=\"incruit_contents\"]/div/div/div[4]/div[1]/div[2]/ul[1]/li/div[2]/div[2]/span[1]").text

    # 학력
    education = lines[0].find_element(By.XPATH, "//*[@id=\"incruit_contents\"]/div/div/div[4]/div[1]/div[2]/ul[1]/li/div[2]/div[2]/span[2]").text

    # 고용형태
    jobType = lines[0].find_element(By.XPATH, "//*[@id=\"incruit_contents\"]/div/div/div[4]/div[1]/div[2]/ul[1]/li/div[2]/div[2]/span[4]").text

    strengths_ = lines[0].find_elements(By.XPATH, "//*[@id=\"incruit_contents\"]/div/div/div[4]/div[1]/div[2]/ul[1]/li/div[1]/div[2]/a")
    for strength_ in strengths_:
        print(strength_.text)

    print(cpname, title, coreer, education, jobType)

    #### 기업 정보 ####

    # Store the ID of the original windows
    original_window = driver.current_window_handle

    # Check we don't have other windows open already
    assert len(driver.window_handles) == 1

    # Click the link of company info
    lines[0].find_element(By.XPATH, "//*[@id=\"incruit_contents\"]/div/div/div[4]/div[1]/div[2]/ul[1]/li/div[1]/div[1]/a").click()

    # Wait for the new tab
    wait.until(EC.number_of_windows_to_be(2))

    time.sleep(3)

    # Find a new windows and switch to
    for window_handle in driver.window_handles:
        if window_handle != original_window:
            driver.switch_to.window(window_handle)
            break

    try:
        detail = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"company_warp\"]/div[1]/div/div/div/div/div/div")))
    except:
        detail = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"company_warp\"]/div[1]/div/div/div[3]/div/div/div")))
    finally:
        idx = 0
        rows = detail.find_elements(By.CSS_SELECTOR, "ul")
        for row in rows:
            elems = row.find_elements(By.CSS_SELECTOR, "li > span")
            for elem in elems:
                print(idx)
                print(elem.text)
                idx += 1
    
    pros = driver.find_elements(By.XPATH, "//*[@id=\"company_warp\"]/div[4]/div/div[1]/div/div/div/div/ul/li")
    for pro in pros:
        print(pro.find_element(By.CSS_SELECTOR, "li > a > strong").text)


    driver.close()

    time.sleep(3)

# //*[@id="company_warp"]/div[1]/div/div/div[3]/div/div/div
    
# //*[@id="company_warp"]/div[1]/div/div/div/div/div/div


####################################################

# for local in locations:
#     # 지역 선택 드롭다운 메뉴 클릭
#     dropDown = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"dropFirstList1\"]")))
#     # dropDown = driver.find_element(By.XPATH, "//*[@id=\"dropFirstList1\"]")
#     driver.execute_script("arguments[0].click();", dropDown)
#     time.sleep(5)

#     # 지역 선택
#     checkBox = WebDriverWait(local, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id=\"dropFirstDown1\"]/div[2]/ul/li[{0}]/label".format(local_idx))))
#     # checkBox = local.find_element(By.CSS_SELECTOR, "label > span")
#     driver.execute_script("arguments[0].click();", checkBox)
#     local_idx += 1

#     # 검색
#     searchBox = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#SearchResultCount")))
#     # searchBox = driver.find_element(By.CSS_SELECTOR, "#SearchResultCount")
#     driver.execute_script("arguments[0].click();", searchBox)
#     time.sleep(5)

#     # 지역 선택 초기화
#     refresh = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#incruit_contents > div > div > div.shb_body > div > div > div > div.shb-search-output > div.shb-search-output-btn.entry > button")))
#     # driver.find_element(By.CSS_SELECTOR, "#incruit_contents > div > div > div.shb_body > div > div > div > div.shb-search-output > div.shb-search-output-btn.entry > button").send_keys(Keys.ENTER)
#     driver.execute_script("arguments[0].click();", refresh)
    