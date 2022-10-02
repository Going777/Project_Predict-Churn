# -*- coding: utf-8 -*-
"""AI_03_김정원_Project2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/bluewhale0528/Section2_Project/blob/main/AI_03_%E1%84%80%E1%85%B5%E1%86%B7%E1%84%8C%E1%85%A5%E1%86%BC%E1%84%8B%E1%85%AF%E1%86%AB_Project2.ipynb

# Project2. 통신사 고객 이탈여부를 예측해보자

* 데이터 선정이유

: 어떤 산업에서든 고객 유치도 중요하지만 기존 고객을 계속해서 유지하는 것 역시 중요하다. 이러한 문제에 있어 어떤 변수가 이탈율에 영향을 미치는지 알아보기 위해 해당 통신사 고객 이탈여부 데이터셋을 선택하게 되었다.

* 문제 정의

: 고객의 통신사 이탈 여부를 예측하는 문제 => `이진분류문제`

* BaseLine Model
: 분류 문제이기 때문에 최빈값으로 예측하는 모델을 기준모델로 삼음
"""

!sudo apt-get install -y fonts-nanum
!sudo fc-cache -fv
!rm ~/.cache/matplotlib -rf

# Commented out IPython magic to ensure Python compatibility.
# # 라이브러리 설치
# %%capture
# import sys
# 
# if 'google.colab' in sys.modules:
#     # Install packages in Colab
#     !pip install category_encoders==2.*
#     !pip install eli5
#     # !pip install pandas-profiling==2.*
#     !pip install pdpbox
#     !pip install shap
#     !pip install xgboost

# 라이브러리 불러오기
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
plt.rc('font', family='NanumBarunGothic')
plt.rc('axes', unicode_minus=False)
from pdpbox.pdp import pdp_isolate, pdp_plot, pdp_interact, pdp_interact_plot
import shap

# from pandas_profiling import ProfileReport
from sklearn.model_selection import train_test_split
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from category_encoders import OneHotEncoder, TargetEncoder
from xgboost import XGBClassifier

import warnings
warnings.filterwarnings('ignore')

"""### Data Description
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
*DeviceProtection : 장치 보호 서비스 사용 여부
*TechSupport : 기술지원 서비스 사용 여부
*StreamingTV : 스트리밍 TV 서비스 사용 여부
*StreamingMovies : 스트리밍 영화 서비스 사용 여부
*Contract : 계약 형태 (Month to Month, One year, Two years)
*PaperlessBilling : 종이영수증 사용 여부 (Yes, No)
*PaymentMethod : 결제 수단 () 
*MonthlyCharges : 월 납부액
*TotalCharges : 전체 기간 납부액
*Churn : 지난달 기준 통신사 이탈 여부 (yes, no)

"""

# 데이터 불러오기
data = pd.read_csv("/content/WA_Fn-UseC_-Telco-Customer-Churn.csv")

# 데이터로부터 패턴을 알아내는 것이 중요하기 때문에, 분석에 customerID 칼럼은 필요없다고 판단 -> 삭제처리
data.drop(columns=["customerID"], inplace=True)

# 컬럼명 소문자로 통일
col_lower = [name.lower() for name in data.columns]
data.columns = col_lower
data.shape

"""## 1. 데이터 전처리
### 1. 데이터 살펴보기
"""

# profile = ProfileReport(train).to_notebook_iframe()

# 데이터 중복행 확인 및 삭제
print(data.duplicated().sum()) # 22개의 중복행 존재
data.drop_duplicates(inplace=True)

# 데이터 타입 확인
data.info()

"""* data description과 비교해봤을 때, totalcharges 칼럼은 숫자형으로 되어 있어야 함 -> 데이터타입 변환 필요"""

sorted(data["totalcharges"].unique())[:10]

"""* totalcharges 칼럼을 바로 숫자형으로 변환하는 것이 불가능 했다. 그 이유는 값 중에 ' '와 같이 스페이스가 들어간 빈칸의 값이 존재했기 때문이다
* 해당 값을 결측값으로 대체하는 과정이 필요하다
"""

data["totalcharges"] = data["totalcharges"].replace(" ", np.nan) # 결측값으로 대체

data["totalcharges"] = data["totalcharges"].astype("float") # 숫자형(float)으로 형변환

# 결측치 확인
data.isnull().sum()

"""* totalcharges 칼럼에 11개의 결측치가 확인된다."""

# 결측치 행 확인
print(data[data["totalcharges"].isnull()].shape[0])
data[data["totalcharges"].isnull()]

"""* 결측치 행을 살펴봤을 때, 공통적으로 tenure칼럼이 0인 것을 확인할 수 있었다
* 아래의 경우, tenure == 0 인 경우를 출력해보았다
"""

print(data[data["tenure"] == 0].shape[0])
data[data["tenure"] == 0]

"""* tenure == 0인 행과 TotalCharge가 결측값인 행이 정확히 일치한다
* 이는 계약 유지기간이 0개월이기 때문에 아직까지는 돈을 지불하지 않은 것으로 예측해볼 수 있다 
* 따라서 TotalCharge 칼럼의 결측값은 0으로 처리하면 될 것 같다
"""

# 결측값 처리
data.totalcharges.fillna(0, inplace=True)

data.isnull().sum().sum() # 결측값 처리 완료

# Category형 칼럼 범주 확인
for col in data.columns:
    if data[col].nunique() <= 10:
        print('{:<16}: {}'.format(col, data[col].unique()))

"""* {Yes, No}와 같이 이진 범주를 가진 칼럼이 대다수
* {No phone/internet service} 범주는 결국 그 서비스를 이용하지 않고 있다는 뜻 => No로 통일
"""

# No phone/internet service 범주 가진 칼럼은 No범주로 바꿔주기
for col in data.columns:
    if data[col].nunique() == 3:
        data[col] = data[col].apply(lambda x: "No" if "service" in x else x)

"""### EDA"""

# Data Leakage 방지 위해 트레인/테스트 셋으로 나누고 분석 (8:2)
train, test = train_test_split(data, train_size=0.8, random_state=2)
print(train.shape, test.shape)
print(train.columns)
train.head(2)

# 타겟 변수
target = "churn"
target_perc = train[target].value_counts(normalize=True)
label = ["No","Yes"]

explode = [0.03] * len(label)
cmap = plt.cm.Spectral
colors = cmap(np.linspace(0, 1.3, 2))

fig, ax = plt.subplots(figsize=(6,6), constrained_layout=True)
ax.pie(target_perc, startangle=-20, counterclock=False,  colors=colors, explode=explode,
        autopct="%.2f%%", textprops={'fontsize': 20, 'weight': 'bold', 'color': 'white'})
ax.set_title("고객 이탈 여부", fontsize=22, weight="bold",loc="center")
plt.legend(label, fontsize=18, bbox_to_anchor=(1, 0.9))
plt.show();

"""* 타겟 변수인 고객 이탈여부를 살펴보면, 이탈한 사람이 약 26.5%, 이탈하지 않은 사람이 약 73.5%로 imbalanced된 데이터이다.
* 추후 분석시 class_weight 조정 또는 업/다운 샘플링을 통해 어느정도 데이터 균형을 맞춰주는 작업이 필요할 것 같다.
"""

# 성별
f, ax = plt.subplots(1,2, figsize=(30,8))
sns.set(font_scale=2)
sns.set_palette("Set2")
sns.set_style("whitegrid")

sns.countplot(train["gender"], ax=ax[0])
sns.countplot(train["gender"], hue=train[target], ax=ax[1]);

"""* 좌측 그림을 살펴보면 수집된 데이터에 성별의 차이는 없어 보인다.
* 우측 그림을 살펴보면 고객 이탈여부에 성별은 그다지 영향을 끼치지 않는 것 같다.
"""

# seniorcitizen(고령자)
f, ax = plt.subplots(1,2, figsize=(30,8))
sns.countplot(train["seniorcitizen"], ax=ax[0])
ax[0].set(ylabel="", xticklabels=["No","Yes"], title="Senior citizen count plot")
sns.countplot(train["seniorcitizen"], hue=train[target], ax=ax[1])
ax[1].set(ylabel="", xticklabels=["No","Yes"], title="Senior citizen count plot by churn");

"""* 데이터상으로 고령자의 데이터는 부족하다.
* 하지만 고령자의 경우 이탈율이 상대적으로 높은 상황이다.
* 데이터 개수가 적어 모델 변수 중요도에서 낮게 나올수도 있으나, 고령화 사회를 접어들고 있는 지금, 이러한 현황은 추후 중요하게 다뤄야할 부분으로 보인다
"""

# 배우자(partner), 부양가족(dependents)
f, ax = plt.subplots(1,2, figsize=(30,8))
sns.countplot(train["partner"], hue=train[target], ax=ax[0])
ax[0].set(ylabel="")
sns.countplot(train["dependents"], hue=train[target], ax=ax[1])
ax[1].set(ylabel="");

"""* 배우자(parter)나 부양가족(dependents)이 있는 경우 이탈율이 상대적으로 낮다."""

# phoneservice, multilines(여러 회신 서비스)
f, ax = plt.subplots(1,2, figsize=(30,8))
sns.countplot(train["phoneservice"], hue=train[target], ax=ax[0])
ax[0].set(ylabel="")
sns.countplot(train["multiplelines"], hue=train[target], ax=ax[1])
ax[1].set(ylabel="");

"""* 대부분 고객들은 폰 서비스를 활용하고 있다
* 비율적으로 봤을 때 여러회선을 사용하고 있는 경우, 조금 이탈율이 낮은 것 같다 => 결합할인을 받고 있을 가능성이 있다
"""

# 인터넷서비스
f,ax = plt.subplots(1,2, figsize=(20,5))
sns.countplot(train["internetservice"], ax=ax[0])
ax[0].set(ylabel="")
sns.countplot(train["internetservice"], hue=train[target], ax=ax[1])
ax[1].set(ylabel="");

"""* 인터넷 서비스 현황을 살펴보면, Fiber optic, DSL 순으로 많이 사용하고 있다
* 하지만 Fiber optic의 경우 이탈비율이 높다 => 고객들이 해당 서비스에 만족하지 못하고 있다
* DSL은 상대적으로 고객들이 만족할만한 인터넷서비스를 제공하고 있는 것으로 보인다
"""

# 온라인 기술관련 서비스(onlinesecurity, onlinebackup, deviceprotection, techsupport)
f,ax = plt.subplots(4,2, figsize=(20,20))
sns.set(font_scale=1.5)
sns.set_palette("Set2")
sns.set_style("whitegrid")

sns.countplot(train["onlinesecurity"], ax=ax[0,0])
ax[0,0].set(ylabel="")
sns.countplot(train["onlinesecurity"], hue=train[target], ax=ax[0,1])
ax[0,1].set(ylabel="")

sns.countplot(train["onlinebackup"], ax=ax[1,0])
ax[1,0].set(ylabel="")
sns.countplot(train["onlinebackup"], hue=train[target], ax=ax[1,1])
ax[1,1].set(ylabel="")

sns.countplot(train["deviceprotection"], ax=ax[2,0])
ax[2,0].set(ylabel="")
sns.countplot(train["deviceprotection"], hue=train[target], ax=ax[2,1])
ax[2,1].set(ylabel="")

sns.countplot(train["techsupport"], ax=ax[3,0])
ax[3,0].set(ylabel="")
sns.countplot(train["techsupport"], hue=train[target], ax=ax[3,1])
ax[3,1].set(ylabel="");

"""* 통신사에서 제공하는 온라인 기술관련 서비스의 각각의 사용률 및 그에 따른 이탈여부의 분포는 거의 비슷하다
* 대체로 해당 서비스를 이용하고 있지 않았고, 이용하는 사람은 이탈할 확률이 좀 더 낮다 -> 온라인 서비스에 만족하고 있다 
"""

# 스트리밍 서비스(streamingTv, streamingMovie)
f,ax = plt.subplots(2,2, figsize=(20,10))

sns.countplot(train["streamingtv"], ax=ax[0,0])
ax[0,0].set(ylabel="")
sns.countplot(train["streamingtv"], hue=train[target], ax=ax[0,1])
ax[0,1].set(ylabel="")

sns.countplot(train["streamingmovies"], ax=ax[1,0], order=["No","Yes"])
ax[1,0].set(ylabel="")
sns.countplot(train["streamingmovies"], hue=train[target], order=["No","Yes"], ax=ax[1,1])
ax[1,1].set(ylabel="");

"""* 스트리밍 서비스를 사용하지 않는 고객의 수가 더 많다
* 스트리밍 서비스를 사용하는 고객의 이탈율이 조금 더 높아 보인다 => 스트리밍 서비스 보완 필요
"""

# contract(계약형태)
f,ax = plt.subplots(1,2, figsize=(20,8))
sns.countplot(train["contract"], ax=ax[0])
ax[0].set(ylabel="")
sns.countplot(train["contract"], hue=train[target], ax=ax[1])
ax[1].set(ylabel="");

"""* 매달 계약하는 고객의 수가 상대적으로 많다
* 장기계약하는 고객일수록 기존 통신사에서 이탈할 확률이 적고, 단기계약하는 고객이수록 이탈할 확률이 높다
* 단기계약 고객을 장기계약할 수 있도록 할 수 있는 유인책을 생각해보아야 한다
"""

# 종이 영수증 사용여부
f,ax = plt.subplots(1,2, figsize=(20,8))
sns.countplot(train["paperlessbilling"], ax=ax[0])
ax[0].set(ylabel="")
sns.countplot(train["paperlessbilling"], hue=train[target], ax=ax[1])
ax[1].set(ylabel="");

"""* paperlessbilling 서비스를 사용한다는 것은 종이영수증을 받지않고, 전자영수증 또는 어플로 처리하겠다는 뜻이다
* 종이영수증을 사용하는 고객들에 비해 사용하지 않는 고객들이 많으나 그만큼 이탈자도 많다 => 해당 서비스의 품질이 좋지 않은 것은 아닌지 검토 필요
"""

# 지불방식
f,ax = plt.subplots(2,1, figsize=(20,10))
sns.countplot(train["paymentmethod"], ax=ax[0])
ax[0].set(ylabel="")
sns.countplot(train["paymentmethod"], hue=train[target], ax=ax[1])
ax[1].set(ylabel="");

"""* Electronic Check방식을 가장 많이 사용하고 있으나, 이탈고객도 가장 많다 => 검토 필요"""

# 계약 유지기간
f,ax = plt.subplots(1,1,figsize=(20,7))
sns.kdeplot(train.tenure[(train["churn"] == 'No') ],
                ax=ax, color="Red", shade = True)
sns.kdeplot(train.tenure[(train["churn"] == 'Yes') ],
                ax =ax, color="Blue", shade= True)
ax.legend(["Not Churn","Churn"],loc='upper right')
ax.set_ylabel('Density')
ax.set_xlabel('Tenure')
ax.set_title("Dist'n of tenure by churn");

"""* 계약 유지 기간이 길어질수록 이탈하는 고객은 확연하게 줄어든다
* 위에서 살펴봤던 계약형태와도 밀접한 관련이 있어보인다
"""

# 월 청구액 / 전체 지불액
f,ax = plt.subplots(2,1,figsize=(20,16))
sns.kdeplot(train.monthlycharges[(train["churn"] == 'No') ],
                ax=ax[0], color="Red", shade = True)
sns.kdeplot(train.monthlycharges[(train["churn"] == 'Yes') ],
                ax =ax[0], color="Blue", shade= True)
ax[0].legend(["Not Churn","Churn"],loc='upper right')
ax[0].set_ylabel('Density')
ax[0].set_xlabel('Monthly Charges')
ax[0].set_title("Dist'n of monthly charges by churn")

sns.kdeplot(train.totalcharges[(train["churn"] == 'No') ],
                ax=ax[1], color="Red", shade = True)
sns.kdeplot(train.totalcharges[(train["churn"] == 'Yes') ],
                ax =ax[1], color="Blue", shade= True)
ax[1].legend(["Not Churn","Churn"],loc='upper right')
ax[1].set_ylabel('Density')
ax[1].set_xlabel('Total Charges')
ax[1].set_title("Dist'n of total charges by churn")

"""* 월 청구액이 많을수록 이탈확률이 높다
* 전체 청구액이 적을수록 이탈확률이 높다 (tenure와 연관되어 보임) => tenure(계약 유지기간)의 값이 작다는 것이 곧 전체 납부액이 적다는 말과 일맥상통

### Feature Engineering
"""

train2 = train.copy()
train2["predict"] = train2["tenure"] * train2["monthlycharges"]
train2[["tenure","monthlycharges","totalcharges","predict"]]

"""* 계약 유지기간(tenure)동안 원래 설정했던 서비스를 변동없이 계속해서 사용했다면 월 납부액은 동일했을 것이다 
* 그렇다면 **`계약 유지기간(tenure) * 월납부액(monthlycharges) = 전채납부액(totalcharges)`**의 식이 성립해야 한다고 생각했다
* 하지만 대부분 위에서 예측한 예상과 동일하지 않았다 -> 달에 따라 고객이 서비스 가입 상품을 바꿨을 수도 있고 프로모션 혜택을 받았을 수도 있을 것 같다
* 따라서 계약기간동안 동일한 월납부액을 냈다는 가정하에 예상금액과 실제 전체 납부액 간의 차이를 나타내 주는 칼럼을 추가해주었다
"""

def engineer(df):
    # 예상 전체 납부액과 실제 전체 납부액의 차이 칼럼 추가
    df["prediceted_diff"] = (df["tenure"] * df["monthlycharges"]) - df["totalcharges"]

    # {yes/no, male/female}범주의 칼럼 1,0으로 인코딩
    for col in df.columns:
        if df[col].nunique() == 2:
            df[col] = df[col].apply(lambda x: 1 if (x=="Yes") or (x=="Male") else 0 if (x=="No") or (x=="Female") else x)

    # 온라인 기술관련 서비스 가입 개수
    df["#security_service"] = df["onlinesecurity"] + df["onlinebackup"] + df["deviceprotection"] + df["techsupport"]

    # 스트리밍 서비스 가입 개수
    df["#streaming_service"] = df["streamingtv"] + df["streamingmovies"]

    return df

train = engineer(train)
test = engineer(test)

"""## 모델링
* 평가지표 : Accuracy, Recall, F1_score, AUC
* 정확도만 가지고 평가하기에는 데이터 불균형으로 인해 우리 예측하고자 하는 타겟(이탈자)을 제대로 예측하지 못하는 경우가 생긴다.
* 때문에 정확도와 더불어 Recall, F1_score, AUC를 함께 고려해 주어야 한다
"""

# 모델 평가지표 출력 함수
def evaluate(model, X, y):
    pred = model.predict(X)
    accuracy = accuracy_score(y, pred)
    recall = recall_score(y, pred)
    auc = roc_auc_score(y, pred)
    f1 = f1_score(y, pred)
    
    print("Accuracy:", accuracy)
    print("F1_score: ", f1)
    print("Recall: ", recall)
    print("AUC: ", auc)
    print("-----------------------------\n")

# 학습/검증셋으로 나누기
train,val = train_test_split(train, train_size=0.8)

# 타겟/독립변수로 나누기
y_train = train[target]
X_train = train.drop(columns=target)

y_val = val[target]
X_val = val.drop(columns=target)

y_test = test[target]
X_test = test.drop(columns=target)

# 인코딩, 스케일링 진행
preprocessing_pipe = Pipeline(
    [("encoder",OneHotEncoder(use_cat_names=True)),
    ("scaler",StandardScaler())])
preprocessing_pipe.fit(X_train)

X_train_pre = preprocessing_pipe.transform(X_train)
X_val_pre = preprocessing_pipe.transform(X_val)

"""### Baseline Model
* 타겟 변수의 최빈값으로 예측하는 모델
"""

from sklearn.metrics import accuracy_score, f1_score, roc_curve, roc_auc_score, auc, confusion_matrix, recall_score

major = y_train.mode()[0] # 최빈값 추출
pred_train = [major] * len(y_train) # 최빈값으로 트레인 데이터셋 예측

pred_val = [major] * len(y_val) # 최빈값으로 검정 데이터셋 예측

print("--- train --------")
print("Accuracy:",accuracy_score(y_train, pred_train)) # 정확도
print("F1_score:",f1_score(y_train, pred_train)) # F1_score
print("Recall:",recall_score(y_train, pred_train)) # F1_score
print("AUC",roc_auc_score(y_train, pred_train)) # ROC-curve의 면적(AUC)

print("--- validation --------")
print("Accuracy:",accuracy_score(y_val, pred_val))
print("F1_score:",f1_score(y_val, pred_val))
print("Recall:",recall_score(y_val, pred_val)) # F1_score
print("AUC",roc_auc_score(y_val, pred_val))

"""* 정확도는 어느정도 높지만, 재현율, F1_score, AUC와 같은 다른 모델 평가 지표에서는 형편없는 성능을 보인다
* 이는 타겟 변수의 데이터 불균형으로부터 비롯된 것으로 보인다
* 해당 부분을 보완하여 모델을 학습시킬 필요가 있다.

### UpSampling
"""

from imblearn.over_sampling import SMOTE

X_train_upsample, y_train_upsample = SMOTE(random_state=42).fit_resample(X_train_pre, y_train)
pd.DataFrame(y_train_upsample).value_counts(normalize=True)

"""* SMOTE방식을 사용하여 데이터 균형을 맞춰주었다

### Logistic Regression Model
"""

logistic1 = LogisticRegression().fit(X_train_upsample, y_train_upsample)

print("[ training ] ")
evaluate(logistic1, X_train_upsample, y_train_upsample)
print("[ validataion ]")
evaluate(logistic1, X_val_pre, y_val)

"""* 따로 하이퍼파라미터 튜닝없이 기본적인 로지스틱회귀모델을 적용했다
* 모델 성능이 나름 괜찮은 것 같다

### RandomForest Classifier Model
"""

from scipy.stats import randint, uniform

rf_pipe = Pipeline([("rf", RandomForestClassifier(random_state=2))])

param_distribs = {
        'rf__n_estimators': randint(low=50, high=500),
        'rf__max_depth': randint(1,30),
        'rf__max_features': uniform(0,1),
    }

clf1 = RandomizedSearchCV(
    rf_pipe,
    param_distributions=param_distribs,
    n_iter=30,
    cv=3,
    scoring="f1",
    verbose=1,
    n_jobs=-1,
    random_state=2)

clf1.fit(X_train_upsample, y_train_upsample)
rf_pipe = clf1.best_estimator_

print("[ training ] ")
evaluate(rf_pipe, X_train_upsample, y_train_upsample)
print("[ validataion ]")
evaluate(rf_pipe, X_val_pre, y_val)

"""* 랜덤포레스트 모델은 하이퍼파라미터 튜닝 후 최적의 파라미터를 적용했지만, 훈련데이터셋에 상당히 과적합된 모델성능을 보여준다

### Xgboost Model
"""

xgb_pipe = Pipeline([("xgb",XGBClassifier(random_state=2, n_jobs=-1))])

param_distribs = {'xgb__n_estimators': randint(low=50, high=500), 
                'xgb__learning_rate': [0.05, 0.1, 0.2],
                'xgb__max_depth' : randint(1,30),
              }


clf2 = RandomizedSearchCV(
    xgb_pipe,
    param_distributions=param_distribs,
    n_iter=30,
    cv=3,
    scoring="f1",
    verbose=1,
    n_jobs=-1,
    random_state=2)

clf2.fit(X_train_upsample, y_train_upsample)
xgb_pipe = clf2.best_estimator_

print("[ training ] ")
evaluate(xgb_pipe, X_train_upsample, y_train_upsample)
print("[ validataion ]")
evaluate(xgb_pipe, X_val_pre, y_val)

"""* 여전히 모델의 과적합이 심하다
* 이전 모델에서보다 일반화 성능이 더 떨어진 모습이다

### LightGBM
"""

from lightgbm import LGBMClassifier

lgbm_pipe = Pipeline([("lgbm", LGBMClassifier(random_state=2, n_jobs=-1, objective="binary"))]    
)

param_distributions = {'lgbm__n_estimators': randint(low=50, high=500), 
              'lgbm__learning_rate': [None, 0.05, 0.1, 0.2],
              'lgbm__max_depth' : randint(1,15),
              'lgbm__num_leaves': randint(1,50),
              'lgbm__max_features': uniform(0,1),
              }


clf3 = RandomizedSearchCV(
    lgbm_pipe,
    param_distributions=param_distributions,
    n_iter=40,
    cv=3,
    scoring="f1",
    verbose=1,
    n_jobs=-1,
    random_state=2)

clf3.fit(X_train_upsample, y_train_upsample)
lgbm_pipe = clf3.best_estimator_

print("[ training ]")
evaluate(lgbm_pipe, X_train_upsample, y_train_upsample)
print("[ validataion ]")
evaluate(lgbm_pipe, X_val_pre, y_val)

"""* LGBM 역시 과적합이 존재하긴 하지만 검정 테스트셋에서도 그렇게 나쁜 성능을 보이진 않고 있다
* 무엇보다 모델이 빨리 돌아가서 시간적인 측면에서 장점이 크다
* LGBM을 최종모델로 선정해보려 한다

"""

X_test_pre = preprocessing_pipe.transform(X_test)

print("[ test ]")
evaluate(lgbm_pipe, X_test_pre, y_test)

"""* test set에서도 검증 데이터셋에서 확인했던 모델 성능과 비슷한 결과를 내주었다
* 어느정도 과적합이 있긴했지만 일반화 성능도 나쁘지는 않은 것 같다
* BaselineModel과 비교했을 때, F1_score, Recall과 같은 지표에서 성능이 굉장히 개선되었다.

## 분석결과 시각화

### 변수 중요도
"""

from eli5.sklearn import PermutationImportance

permuter = PermutationImportance(
    lgbm_pipe.named_steps["lgbm"],
    scoring="f1",
    n_iter=5,
    random_state=2
)

permuter.fit(X_val_pre, y_val)

import eli5
enc = preprocessing_pipe.named_steps["encoder"]
feature_names = enc.get_feature_names()


perm_imp_df = pd.DataFrame()
perm_imp_df["feature"] = feature_names
perm_imp_df["importance"] = permuter.feature_importances_
perm_imp_df = perm_imp_df.sort_values(["importance"],ascending=False)

plt.figure(figsize=(10,10))
sns.barplot(x="importance", y="feature", data=perm_imp_df)
plt.title("Permutation Importance by LGBM");

"""* Feature Engineering으로 만들어낸 변수들이 어느정도 상위에 랭크하고 있다
* 상위랭크 : contract_month_to_month, tenure, internetservice_Fiber optic, contract_two_year, predicted_diff
* 하위랭크 : streamingmovies, seniorcitizenn, contract_one_year, deviceprotection, techsupport, onlinebackup
"""

# 상위랭크(top3)에 위치한 변수들의 영향도를 살펴보자
features = perm_imp_df["feature"].iloc[:3].tolist()
X_test_df = pd.DataFrame(X_test_pre, columns=feature_names)

for feature in features:
    isolated = pdp_isolate(
        model = lgbm_pipe,
        dataset=X_test_df,
        model_features = feature_names,
        feature=feature
        # feature = feature,
        # grid_type = "percentile",
        # num_grid_points = 10
    )
    sns.set(font_scale=2)
    pdp_plot(isolated, feature_name=feature);

"""* EDA 분석에서 분석했던 결과와 거의 동일한 영향을 미치고 있다

## 모델의 한계
* 데이터의 크기가 작아서 과적합될 우려가 있다
* 과적합 문제를 완전히 해결하진 못했다
* 데이터 수급이 굉장히 간단하게 되어 있고, 변수 자체도 정제되어 들어와있는데, 이러한 데이터를 만나기는 쉽지 않다

## 모델의 유용성
* 해당 모델에서 살펴봤던 타겟변수와 피쳐들의 관계에 대한 분석은 추후 고객 유지 방법을 모색할 때 유용한 지표로 사용될 수 있다
"""

