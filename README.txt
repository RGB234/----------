raw_data.csv : crawling.py 로 크롤링한 데이터. 정확히는 각 지역별로 raw_data_{지역}.csv 파일을 저장한 후 이를 하나로 통합한 csv 파일.
data_beforeScaling.csv : data.csv 에서 1차적으로 전처리 후, 피처 스케일링 적용 이전 세이브포인트
data.csv: data_beforeScaling.csv 에서 피처 스케일링까지 적용한 데이터

data_balanced.csv : data.csv 에서 undersampling 한 데이터
data_remaining.csv : data.csv 에서 data_balanced.csv 를 추출(선택)하고 남은 데이터

tree_class0.png, tree_class1.png, tree_class2.png : 튜닝된 xgboostClassifier 모델에서 생성한 각 클래스별 최종트리.
