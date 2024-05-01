import time
import numpy
import pandas as pd
from selenium import webdriver

# The Keys class provide keys in the keyboard like RETURN, F1, ALT etc.
from selenium.webdriver.common.keys import Keys

# The By class is used to locate elements within a document.
from selenium.webdriver.common.by import By

# Wait for data to be loaded
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# checking if an element exist
from selenium.common.exceptions import NoSuchElementException, TimeoutException

options = webdriver.ChromeOptions()

# Do not use GUI
options.add_argument("headless")

options.add_argument("--disable-extensions")

# 사람처럼 보이게 하는 옵션들
options.add_argument("--disable-gpu")  # 가속 사용 x
options.add_argument("lang=ko_KR")  # 가짜 플러그인 탑재
options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
)  # user-agent 이름 설정

# debug console log
options.add_argument("--log-level=3")
# To enable .click() in headless mode
options.add_argument("--window-size=1024,800")

with webdriver.Chrome(options=options) as driver:

    # 17 개 지역
    # [서울, 부산, 인천, 대전, 광주, 대구, 울산, 세종, 경기,
    # 강원, 충북, 충남, 전북, 전남, 경북, 경남, 제주]

    # 수도권 : 서울, 인천, 세종, 경기
    # 수도권 외 광역시: 부산, 대구, 광주, 대전, 울산
    # 그 외 지방: 강원, 충북, 충남, 전북, 전남, 경북, 경남, 제주

    ######## 지역코드(혹은 ID) & 지역명 수집 ########
    driver.get("https://job.incruit.com/entry/")

    # Setup wait for later
    wait = WebDriverWait(driver, 30)

    regions = driver.find_elements(By.XPATH, '//*[@id="dropFirstDown1"]/div[2]/ul/li')

    rgnID_NAME = {}

    for region in regions:
        # region ID 는 웹 사이트 '지역' 드롭다운 메뉴 순서대로.
        rgnID = region.find_element(By.CSS_SELECTOR, "input").get_attribute(
            "data-item-val"
        )
        rgnName = region.find_element(By.CSS_SELECTOR, "input").get_attribute(
            "data-item-name"
        )
        rgnID_NAME[rgnID] = rgnName

    ######## 본격적인 크롤링 ########

    rgnIDs = [*rgnID_NAME]
    rgnIDs_count = len(rgnIDs)
    features = [
        "region",
        "cpname",
        "title",
        "career",
        "education",
        "jobtype",
        "cptype",
        "sales",
        "employees",
        "aversalary",
        "capital",
        "pros",
    ]
    df = pd.DataFrame(columns=features)

    iter = 1
    for rgnID in rgnIDs:
        # progress rate
        print("{0} ({1} / {2})".format(rgnID_NAME[rgnID], iter, rgnIDs_count))
        iter += 1

        pages = 4
        # 1..pages
        for page in range(1, pages + 1):

            driver.get(
                "https://job.incruit.com/entry/?rgn2={0}&page={1}".format(rgnID, page)
            )

            # 지역명
            rgnName = rgnID_NAME[rgnID]

            # 60 lines per page
            lines = driver.find_elements(
                By.XPATH, '//*[@id="incruit_contents"]/div/div/div[4]/div[1]/div[2]/ul'
            )

            linesPerPage = 60
            for i in range(linesPerPage):
                # progress rate
                if (i + 1) % 10 == 0:
                    print(
                        f" {(i+1) + linesPerPage * (page - 1)} / {linesPerPage * pages}"
                    )

                #### 고용 정보 ####
                # company name cpname
                cpname = (
                    lines[i]
                    .find_element(
                        By.CSS_SELECTOR, "li > div.cell_first > div.cl_top > a"
                    )
                    .text
                )
                # title
                title = (
                    lines[i]
                    .find_element(By.CSS_SELECTOR, "li > div.cell_mid > div.cl_top > a")
                    .text
                )
                # 경력
                career = (
                    lines[i]
                    .find_element(
                        By.CSS_SELECTOR,
                        "li > div.cell_mid > div.cl_md > span:nth-child(1)",
                    )
                    .text
                )
                # 학력
                education = (
                    lines[i]
                    .find_element(
                        By.CSS_SELECTOR,
                        "li > div.cell_mid > div.cl_md > span:nth-child(2)",
                    )
                    .text
                )
                # 고용형태
                jobType = (
                    lines[i]
                    .find_element(
                        By.CSS_SELECTOR,
                        "li > div.cell_mid > div.cl_md > span:nth-child(4)",
                    )
                    .text
                )
                # 입사추천태그('입사지원하면 좋은 이유')
                pros = []

                ############ 기업 정보 ############

                # Store the ID of the original windows
                original_window = driver.current_window_handle

                # Click the link of company info
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "li > div.cell_first > div.cl_top > a")
                    )
                ).click()

                # Wait for the new tab
                wait.until(EC.number_of_windows_to_be(2))
                # Find a new windows and switch to
                for window_handle in driver.window_handles:
                    if window_handle != original_window:
                        driver.switch_to.window(window_handle)
                        break

                # 기업명, 기업유형, 대표, 설립일, 매출, 사원수, 평균연봉, 자본금, 업종
                try:
                    detail = wait.until(
                        EC.presence_of_element_located(
                            (
                                By.XPATH,
                                '//*[@id="company_warp"]/div[1]/div/div/div/div/div/div',
                            )
                        )
                    )
                except (NoSuchElementException, TimeoutException):
                    detail = wait.until(
                        EC.presence_of_element_located(
                            (
                                By.XPATH,
                                '//*[@id="company_warp"]/div[1]/div/div/div[3]/div/div/div',
                            )
                        )
                    )

                # 0 기업명, 1 기업규모, 2 대표자, 3 설립일, 4 매출액, 5 사원수, 6 평균연봉, 7 자본금, 8 업종
                rows = detail.find_elements(By.CSS_SELECTOR, "ul")
                aversalaryIsNull = True
                for row in rows:
                    elems = row.find_elements(By.CSS_SELECTOR, "li")
                    for elem in elems:
                        # 기업규모, 매출액, 사원수, 평균연봉, 자본금
                        elem_text = elem.find_element(By.CSS_SELECTOR, "strong").text

                        if elem_text == "기업규모":
                            cptype = elem.find_element(By.CSS_SELECTOR, "span > a").text
                        elif elem_text == "매출액":
                            # '-' 값으로 채워진 경우 존재
                            sales = elem.find_element(By.CSS_SELECTOR, "span").text
                        elif elem_text == "사원수":
                            employees = elem.find_element(By.CSS_SELECTOR, "span").text
                        elif elem_text == "평균연봉":
                            # ** 아예 항목이 없는 경우 존재 **
                            aversalary = elem.find_element(By.CSS_SELECTOR, "span").text
                            aversalaryIsNull = False
                        elif elem_text == "자본금":
                            # '-' 값으로 채워진 경우 존재
                            capital = elem.find_element(By.CSS_SELECTOR, "span").text

                if aversalaryIsNull:
                    aversalary = "-"

                try:
                    newty = driver.find_element(
                        By.CSS_SELECTOR,
                        "#company_warp > div:nth-child(4) > div > div.newty",
                    )
                # '입사 지원하면 좋은 이유' element 위치(XPATH)가 조금씩 다른 문제를 예외처리를 통해 일일이 조정
                except NoSuchElementException:
                    # print("NoSuchElementException: #company_warp > div:nth-child(4) > div > div.newty")
                    try:
                        newty = driver.find_element(
                            By.CSS_SELECTOR,
                            "#company_warp > div:nth-child(3) > div > div.newty",
                        )
                    # div.newty, '입사지원하면 좋은 이유' 항목이 아예 등록되지 않은 경우
                    except NoSuchElementException:
                        # print("NoSuchElementException: #company_warp.")
                        pass
                finally:
                    try:
                        pros2 = newty.find_elements(
                            By.CSS_SELECTOR, "div > div > div > div > ul > li"
                        )

                        for pro in pros2:
                            # print(
                            #     driver.execute_script(
                            #         "return arguments[0].innerText",
                            #         pro.find_element(By.CSS_SELECTOR, "a > strong"),
                            #     )
                            # )
                            pros.append(
                                driver.execute_script(
                                    "return arguments[0].innerText",
                                    pro.find_element(By.CSS_SELECTOR, "a > strong"),
                                )
                            )
                    except NoSuchElementException:
                        # newty IS NULL. 즉, div.newty (입사지원하면 좋은 이유) 가 아에 없는 경우
                        # List<string> pros : empty list 로 냅둠.
                        pass

                # features = ['region', 'cpname', 'title', 'career', 'education',
                #             'jobtype', 'cptype', 'sales', 'employees' 'aversalary',
                #             'capital', 'pros']

                pros_str = "-".join([pro for pro in pros])

                # 데이터 취합

                values = [
                    rgnName,
                    cpname,
                    title,
                    career,
                    education,
                    jobType,
                    cptype,
                    sales,
                    employees,
                    aversalary,
                    capital,
                    pros_str,
                ]

                new_row = dict(zip(features, values))

                # print(new_row)

                # 기존 dataframe 의 새 row 로 추가
                df = pd.concat(
                    [df, pd.DataFrame.from_dict([new_row])], ignore_index=True
                )

                # close current tap
                driver.close()
                wait.until(EC.number_of_windows_to_be(1))
                # switch back to original window(or tap)
                driver.switch_to.window(original_window)

    df.to_csv("raw_data.csv", encoding="utf-8-sig")
