import numpy as py
import pandas as pd
import json
import pickle
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import RandomOverSampler
from sklearn.metrics import classification_report
cols = ["Age at enrollment","Gender","Scholarship holder","Curricular units 1st sem (enrolled)","Curricular units 1st sem (approved)","Curricular units 1st sem (grade)","Curricular units 2nd sem (enrolled)","Curricular units 2nd sem (approved)","Curricular units 2nd sem (grade)","Debtor","Tuition fees up to date","Target"]
df=pd.read_csv("data.csv",sep=";",usecols=cols)
df["Target"] = (df["Target"] == "Dropout").astype(int) # 1 is DropOut, 0 is Enrolled/Graduate
df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)
train = df_shuffled.iloc[:int(0.6 * len(df))]
test = df_shuffled.iloc[int(0.6 * len(df)):int(0.8 * len(df))]
valid = df_shuffled.iloc[int(0.8 * len(df)):]
binary_features = ["Gender", "Scholarship holder", "Debtor"]
continuous_features = [
    "Age at enrollment", "Curricular units 1st sem (enrolled)", "Curricular units 1st sem (approved)", "Curricular units 1st sem (grade)",
    "Curricular units 2nd sem (enrolled)", "Curricular units 2nd sem (approved)", "Curricular units 2nd sem (grade)",
    "Tuition fees up to date"
]
std=StandardScaler()
def scale(dataframe, oversampling=False, fit_scaler=False, scaler_path="scaler.pkl"):
    X_bin = dataframe[binary_features].values
    X_cont = dataframe[continuous_features].values
    y = dataframe["Target"].values

    if fit_scaler:
        X_cont = std.fit_transform(X_cont)
        with open(scaler_path, "wb") as f:
            pickle.dump(std, f)
    else:
        with open(scaler_path, "rb") as f:
            loaded_scaler = pickle.load(f)
            X_cont = loaded_scaler.transform(X_cont)
    X = py.hstack((X_cont, X_bin))
    if oversampling:
        ros = RandomOverSampler()
        X, y = ros.fit_resample(X, y)

    data = py.hstack((X, y.reshape(-1, 1)))
    return data, X, y
train,X_train,Y_train=scale(train,True,True)
test,X_test,Y_test=scale(test,False,False)
Valid,X_valid,Y_valid=scale(valid,False,False)
class LogisticRegression:
  def __init__(self,learnrate,iteration):
    self.learnrate=learnrate
    self.iteration=iteration
  def sigmoid(self, z):
    p=1/(1+py.exp(-z))
    return p
  def fit(self,X,y):
    self.m,self.n=X.shape
    self.w=py.zeros(self.n)
    self.b=0
    for _ in range(self.iteration):
      z=py.dot(X,self.w)+self.b
      y_pred=self.sigmoid(z)
      #lossfunction
      dw=(1/self.m)*py.dot(X.T,(y_pred-y))
      db=(1/self.m)*sum(y_pred-y)
      #reduce w and b
      self.w-=self.learnrate*dw
      self.b-=self.learnrate*db
  def predict_prob(self, X):
      z = py.dot(X, self.w) + self.b
      return self.sigmoid(z)
  def predict(self,X):
    prob = self.predict_prob(X)
    return [1 if i>0.5 else 0 for i in prob]
logs=LogisticRegression(0.01,5000)
logs.fit(X_train,Y_train)
with open("logistic_model.pkl", "wb") as f:
    pickle.dump(logs, f)
with open("logistic_model.pkl", "rb") as f:
   loaded_model = pickle.load(f)
y_pred=loaded_model.predict(X_test)
print(classification_report(Y_test,y_pred))
feature_order = continuous_features + binary_features
with open("scaler.pkl", "rb") as f:
    loaded_scaler = pickle.load(f)
with open("logistic_model.pkl", "rb") as f:
    loaded_model = pickle.load(f)
def predict_from_backend(student_dict):
    features = [student_dict[feat] for feat in feature_order]
    features = py.array(features).reshape(1, -1)
    continuous_idx = list(range(len(continuous_features)))
    features_scaled = features.astype(float).copy()
    features_scaled[:, continuous_idx] = loaded_scaler.transform(features[:, continuous_idx])
    prob = loaded_model.sigmoid(py.dot(features_scaled, loaded_model.w) + loaded_model.b)[0]
    prediction = 1 if prob > 0.5 else 0
    prediction_label = "Dropout" if prediction == 1 else "Enrolled/Graduate"
    response = {
        "Risk_Score": round(float(prob), 2),
        "Prediction_Label": prediction_label,
        "Recommendations": (
            ["Attend mentoring sessions", "Seek academic counseling"]
            if prediction == 1 else
            ["Keep up the good work!"]
        )
    }
    return json.dumps(response, indent=4)
#Example
sample_dropout = {
    "Age at enrollment": 19,
    "Gender": 0,
    "Scholarship holder": 0,
    "Curricular units 1st sem (enrolled)": 6,
    "Curricular units 1st sem (approved)": 2,
    "Curricular units 1st sem (grade)": 8.0,   
    "Curricular units 2nd sem (enrolled)": 6,
    "Curricular units 2nd sem (approved)": 1,
    "Curricular units 2nd sem (grade)": 7.5,  
    "Debtor": 1,                            
    "Tuition fees up to date": 0              
}

print(predict_from_backend(sample_dropout))