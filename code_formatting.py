# 17개 지역
regions = {
    "11": "서울",
    "12": "부산",
    "14": "인천",
    "16": "대전",
    "15": "광주",
    "13": "대구",
    "17": "울산",
    "27": "세종",
    "18": "경기",
    "19": "강원특별자치도",
    "20": "충북",
    "21": "충남",
    "22": "전북특별자치도",
    "23": "전남",
    "24": "경북",
    "25": "경남",
    "26": "제주",
}


# 수도권 : 서울, 인천, 세종, 경기
# 수도권 외 광역시: 부산, 대구, 광주, 대전, 울산
# 그 외 지방: 강원, 충북, 충남, 전북, 전남, 경북, 경남, 제주

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

for region in regions.values():
    df_subset = pd.read_csv(f"sample data/raw_data_{region}.csv", index_col=0)
    df = pd.concat([df, df_subset])

df = df.reset_index(drop=True)

df.to_csv("raw_data.csv", encoding="utf-8-sig")
