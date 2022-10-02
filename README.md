# Project_Predict Churn
### 📍분석 주제 : 통신사 고객 이탈여부를 예측해보자
* 데이터 선정 이유 : 어떤 산업에서든 고객 유치도 중요하지만 기존 고객을 계속해서 유지하는 것 역시 중요하다. 이러한 문제에 있어 어떤 변수가 이탈율에 영향을 미치는지 알아보기 위해 해당 통신사 고객 이탈여부 데이터셋을 선택하게 되었다.
* 문제 정의 : 고객의 통신사 이탈 여부를 예측하는 문제 => `이진분류문제`
* BaseLine Model : 분류 문제이기 때문에 최빈값으로 예측하는 모델을 기준모델로 삼음
---
### 📍사용 변수
* customerID : 고객 ID
* gender : 고객의 성별 (Male, Female)
* SeniorCitizen : 65세 이상 고객인지 (1:yes, 0:no)
* Partner : 배우자 여부 (yes, no)
* Dependents : 부양가족과 함께 살고 있는지 (yes, no)
* tenure : 계약 유지 기간 (통신사와 함께하고 있는 기간)
* PhoneService : 휴대폰 서비스 사용 여부
* MultiplieLines : 여러 회선 서비스 사용 여부 (yes, no, 전화 서비스 없음)
* InternetService : 인터넷 서비스 여부 (DSL, Fiber optic, No)
* OnlineSecurity : 온라인 보안 서비스 사용 여부
* OnlineBackup : 온라인 백업 서비스 사용 여부
* DeviceProtection : 장치 보호 서비스 사용 여부
* TechSupport : 기술지원 서비스 사용 여부
* StreamingTV : 스트리밍 TV 서비스 사용 여부
* StreamingMovies : 스트리밍 영화 서비스 사용 여부
* Contract : 계약 형태 (Month to Month, One year, Two years)
* PaperlessBilling : 종이영수증 사용 여부 (Yes, No)
* PaymentMethod : 결제 수단 ()
* MonthlyCharges : 월 납부액
* TotalCharges : 전체 기간 납부액
* Churn : 지난달 기준 통신사 이탈 여부 (yes, no)
---
### 📍분석 흐름
1. 데이터 전처리(EDA / Feature Engineering)
2. 모델링
3. 분석 결과 도출
---
### 📍분석 결과
* 평가 지표 : Accuracy, Recall, F1_score, AUC
* 정확도만 가지고 평가하기에는 데이터 불균형으로 인해 우리 예측하고자 하는 타겟(이탈자)을 제대로 예측하지 못하는 경우가 생긴다.
* 때문에 정확도와 더불어 Recall, F1_score, AUC를 함께 고려해 주었다
#### 1) Baseline Model - 타겟 변수의 최빈값으로 예측하는 모델
![image](https://user-images.githubusercontent.com/109488657/193443270-a3bc27a1-e56a-4398-a93a-0cc516c13725.png)
* 정확도는 어느정도 높지만, 재현율, F1_score, AUC와 같은 다른 모델 평가 지표에서는 형편없는 성능을 보인다
* 이는 타겟 변수의 데이터 불균형으로부터 비롯된 것으로 보인다
* 데이터 불균형 부분을 보완하기 위해 `SMOTE 방식을 통해 데이터 균형을 맞춰주었다`

#### 2) Logistic Regression Model
![image](https://user-images.githubusercontent.com/109488657/193443379-f544dd50-74a3-454b-bbfa-5b3ce6da19e6.png)
* 따로 하이퍼파라미터 튜닝없이 기본적인 로지스틱회귀모델을 적용했다
* 모델 성능이 나름 괜찮은 것 같다

#### 3) RandomForest Classifier Model
![image](https://user-images.githubusercontent.com/109488657/193443437-5bb98278-bef3-4d40-b7f4-2b2e46afb43a.png)
* 랜덤포레스트 모델은 하이퍼파라미터 튜닝 후 최적의 파라미터를 적용했지만, 훈련데이터셋에 상당히 과적합된 모델성능을 보여준다

#### 4) Xgboost Model
![image](https://user-images.githubusercontent.com/109488657/193443606-74e0e163-c3d7-46e8-80ff-5af706e300ca.png)
* 여전히 모델의 과적합이 심하다
* 이전 모델에서보다 일반화 성능이 더 떨어진 모습이다

#### 5) LightGBM Model
![image](https://user-images.githubusercontent.com/109488657/193443646-0c8b1802-5dee-4655-b654-d4c081c963ea.png)
* LGBM 역시 과적합이 존재하긴 하지만 검정 테스트셋에서도 그렇게 나쁜 성능을 보이진 않고 있다
* 무엇보다 모델이 빨리 돌아가서 시간적인 측면에서 장점이 크다
* LGBM을 최종모델로 선정 남겨둔 테스트 데이터에 대해 분석을 실시해 보았다.
![image](https://user-images.githubusercontent.com/109488657/193443655-f0546e82-7f97-4eaf-8cb1-211f05be0e02.png)
* test set에서도 검증 데이터셋에서 확인했던 모델 성능과 비슷한 결과를 내주었다
* 어느정도 과적합이 있긴했지만 일반화 성능도 나쁘지는 않은 것 같다
* BaselineModel과 비교했을 때, F1_score, Recall과 같은 지표에서 성능이 굉장히 개선되었다.
---
![image](https://user-images.githubusercontent.com/109488657/193443674-53eab11e-ef68-4eff-befa-53e082fb2b91.png)
* Feature Engineering으로 만들어낸 변수들이 어느정도 상위에 랭크하고 있다
* 상위랭크 : contract_month_to_month, tenure, internetservice_Fiber optic, contract_two_year, predicted_diff
* 하위랭크 : streamingmovies, seniorcitizenn, contract_one_year, deviceprotection, techsupport, onlinebackup
#### 상위랭크 3가지의 변수 영향도를 살펴보았다
**[contract_month_to_month]**
![image](https://user-images.githubusercontent.com/109488657/193443702-0f3f369c-dc00-43d2-89d1-8b07f968bfea.png)
* 장기 계약하는 고객일수록 기존 통신사에서 이탈할 확률이 적다
**[tenure]**
![image](https://user-images.githubusercontent.com/109488657/193443704-d204b2a0-62bc-44e4-bb45-8ee68487d14d.png)
* 계약 유지 기간이 길어질수록 기존 통신사에서 이탈할 확률이 적다
**[internetservice_Fiber optic]**
![image](https://user-images.githubusercontent.com/109488657/193443716-1e6b20b3-e480-4fbd-aaa4-4fb644bf2335.png)
* 인터넷 서비스 중 Fiber optic을 사용하고 있을 경우 이탈할 확률이 적다

=> 통신사에 고객들이 장기 계약할 수 있도록 하는 유인책을 개발해야 하며, Fiber optic 서비스를 개선해야할 필요성이 있다
---
### 📍모델의 한계
* 데이터의 크기가 약 7000여개 정도로 적기 때문에 대부분의 모델 적용시 과적합된 결과가 도출되었다 
* 최종 선정 모델인 LightGBM을 사용했을 때도 과적합 문제를 완전히 해결하진 못했다
* 데이터 수급이 굉장히 간단하게 되어 있고, 변수 자체도 정제되어 들어와있는데, 현실에서 이러한 데이터를 만나기는 쉽지 않다
---
### 📍모델의 유용성
* 해당 모델에서 살펴봤던 타겟변수와 피쳐들의 관계에 대한 분석은 추후 고객 유지 방법을 모색할 때 유용한 지표로 사용될 수 있다
