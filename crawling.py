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

options.add_argument("--ignore-certificate-errors-spki-list")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--ignore-ssl-errors")
# To enable .click() in headless mode
options.add_argument("--window-size=1024,800")

# 지역당 몇 개의 페이지를 크롤링할지
PAGES = 3
# 한 페이지당 몇 개의 모집공고를 크롤링할지
LINES = 60
# 크롤링을 시작할 지역 (1~17)
STARTINGPOINT = 5

with webdriver.Chrome(options=options) as driver:

    # 17 개 지역
    # [서울, 부산, 인천, 대전, 광주, 대구, 울산, 세종, 경기, 강원,
    # 충북, 충남, 전북, 전남, 경북, 경남, 제주]

    # 수도권 : 서울, 인천, 세종, 경기
    # 수도권 외 광역시: 부산, 대구, 광주, 대전, 울산
    # 그 외 지방: 강원, 충북, 충남, 전북, 전남, 경북, 경남, 제주

    ######## 지역코드(혹은 ID) & 지역명 수집 ########
    driver.get("https://job.incruit.com/entry/")

    # Setup wait for later
    wait = WebDriverWait(driver, 30)
    regions = driver.find_elements(By.XPATH, '//*[@id="dropFirstDown1"]/div[2]/ul/li')

    # {region ID : Name}
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

    # the keys of rgnID_NAME dictionary
    rgnIDs = [*rgnID_NAME]
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
    # df = pd.DataFrame(columns=features)

    print(rgnID_NAME)

    # [지역별로 반복]
    iter = 1
    for order in range(len(rgnIDs)):
        df = pd.DataFrame(columns=features)
        # 에러로 인해 크롤링이 중간에 중단되었을 경우,
        # crawling_startingpoint 를 조정하여 수동으로 특정 지역부터 크롤링을 시작할 수 있다.
        # 17개 지역
        # {'11': '서울', '12': '부산', '14': '인천', '16': '대전', '15': '광주',
        # '13': '대구', '17': '울산', '27': '세종', '18': '경기', '19': '강원특별자치도',
        # '20': '충북', '21': '충남', '22': '전북특별자치도', '23': '전남', '24': '경북',
        # '25': '경남', '26': '제주'}

        # ex) '대구' 지역에서 중단되었을 경우, 위 딕셔너리에서 '대구' 는 6번째. '대구' 의 rgnID 는 rgnIDs[5]
        # 따라서 crawling_startingpoint 를 6으로 하면 서울~광주까지는 크롤링하지 않고 패스.
        crawling_startingpoint = STARTINGPOINT
        if order < crawling_startingpoint - 1:
            iter = crawling_startingpoint
            continue

        rgnID = rgnIDs[order]

        # progress rate
        print("{0} ({1} / {2})".format(rgnID_NAME[rgnID], iter, len(rgnIDs)))
        iter += 1

        # [페이지마다 반복]
        pages = PAGES
        # 1..pages
        for page in range(1, pages + 1):
            driver.get(
                "https://job.incruit.com/entry/?rgn2={0}&page={1}".format(rgnID, page)
            )

            # 지역명
            rgnName = rgnID_NAME[rgnID]

            # 60 lines per page
            lines = driver.find_elements(
                By.XPATH,
                '//*[@id="incruit_contents"]/div/div/div[4]/div[1]/div[2]/ul',
            )

            linesPerPage = LINES
            for i in range(linesPerPage):
                try:
                    # progress rate
                    if (i + 1) % 10 == 0:
                        print(
                            f" {(i+1) + linesPerPage * (page - 1)} / {linesPerPage * pages}"
                        )

                    #### 고용 정보 ####
                    # company name
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
                        .find_element(
                            By.CSS_SELECTOR, "li > div.cell_mid > div.cl_top > a"
                        )
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

                    ############ 기업 정보 ############

                    # Store the ID of the original windows
                    original_window = driver.current_window_handle

                    # Check we don't have other windows open already
                    assert len(driver.window_handles) == 1

                    # Click the link of company info
                    cpInfoLink = wait.until(
                        EC.element_to_be_clickable(
                            lines[i].find_element(
                                By.CSS_SELECTOR, "li > div.cell_first > div.cl_top > a"
                            )
                        )
                    )

                    cpInfoLink.click()

                    # Wait for the new tab
                    wait.until(EC.number_of_windows_to_be(2))

                    # Find a new windows and switch to
                    for window_handle in driver.window_handles:
                        if window_handle != original_window:
                            driver.switch_to.window(window_handle)
                            break

                    # 기업명, 기업유형, 대표, 설립일, 매출, 사원수, 평균연봉, 자본금, 업종
                    # detail = driver.find_element(
                    #     By.CSS_SELECTOR,
                    #     ".head_company_detail > div",
                    # )
                    detail = wait.until(
                        EC.presence_of_element_located(
                            (
                                By.CSS_SELECTOR,
                                ".head_company_detail > div",
                            )
                        )
                    )

                    # 0 기업명, 1 기업규모, 2 대표자, 3 설립일, 4 매출액, 5 사원수, 6 평균연봉, 7 자본금, 8 업종
                    # cptype = "-"
                    sales = "-"
                    employees = "-"
                    aversalary = "-"
                    capital = "-"

                    rows = detail.find_elements(By.CSS_SELECTOR, "ul")
                    # aversalaryIsNull = True
                    for row in rows:
                        elems = row.find_elements(By.CSS_SELECTOR, "li")
                        for elem in elems:
                            # 기업규모, 매출액, 사원수, 평균연봉, 자본금
                            elem_text = elem.find_element(
                                By.CSS_SELECTOR, "strong"
                            ).text

                            if elem_text == "기업규모":
                                cptype = elem.find_element(By.CSS_SELECTOR, "span").text
                            elif elem_text == "매출액":
                                # '-' 값으로 채워진 경우 존재
                                sales = elem.find_element(By.CSS_SELECTOR, "span").text
                            elif elem_text == "사원수":
                                employees = elem.find_element(
                                    By.CSS_SELECTOR, "span"
                                ).text
                            elif elem_text == "평균연봉":
                                # ** 아예 항목이 없는 경우 존재 **
                                aversalary = elem.find_element(
                                    By.CSS_SELECTOR, "span"
                                ).text
                                # aversalaryIsNull = False
                            elif elem_text == "자본금":
                                # '-' 값으로 채워진 경우 존재
                                capital = elem.find_element(
                                    By.CSS_SELECTOR, "span"
                                ).text

                    # 입사추천태그('입사지원하면 좋은 이유')
                    pros = []
                    try:
                        newty = driver.find_element(
                            By.CSS_SELECTOR,
                            "#company_warp > div:nth-child(4) > div > div.newty",
                        )
                    # '입사 지원하면 좋은 이유' element XPATH가 조금씩 다른 문제를 예외처리를 통해 일일이 조정
                    except NoSuchElementException:
                        # print("NoSuchElementException: #company_warp > div:nth-child(4) > div > div.newty")
                        try:
                            newty = driver.find_element(
                                By.CSS_SELECTOR,
                                "#company_warp > div:nth-child(3) > div > div.newty",
                            )
                        # div.newty 이 아예 없는 경우 ('입사지원하면 좋은 이유' 항목 미등록)
                        except NoSuchElementException:
                            # print("NoSuchElementException: #company_warp.")
                            pass
                    finally:
                        try:
                            pros2 = newty.find_elements(
                                By.CSS_SELECTOR, "div > div > div > div > ul > li"
                            )

                            for pro in pros2:
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

                except (TimeoutException, NoSuchElementException):
                    print(
                        "exception (TimeoutException or NoSuchElementException) occured"
                    )
                    # cool down
                    driver.implicitly_wait(5)
                    df.to_csv(
                        f"raw_data_{rgnID_NAME[rgnID]}_temp.csv", encoding="utf-8-sig"
                    )

                    # 열린 탭들 정리
                    if len(driver.window_handles) != 1:
                        print(
                            f"the number of all windows: ", len(driver.window_handles)
                        )
                        original_window = driver.window_handles[0]
                        for window in driver.window_handles:
                            if window != original_window:
                                driver.switch_to.window(window)
                                driver.close()
                                driver.switch_to.window(original_window)
                        print(
                            f"After clearing dummy windows - the number of all windows: ",
                            len(driver.window_handles),
                        )
                    print("progress resumed")
                    continue

        df.to_csv(f"raw_data_{rgnID_NAME[rgnID]}.csv", encoding="utf-8-sig")

    df.to_csv("raw_data.csv", encoding="utf-8-sig")
