# -*- coding: utf-8 -*-
"""AP_LAB_PROJECT_IMPLEMENTATION_TEST.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1uo3vp458dPtkJpxyPRUJ6nL-86YVp90A
"""

# Commented out IPython magic to ensure Python compatibility.

#IMPORTS

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
# %matplotlib inline

from matplotlib.pylab import rcParams
rcParams['figure.figsize']=20,10
from keras.models import Sequential
from keras.layers import LSTM,Dropout,Dense


from sklearn.preprocessing import MinMaxScaler

#Reading the dataset
df=pd.read_csv("NSE-TATA.csv")
df.dropna() #(IMPROVEMENT)
df.head()

#Analyzig the closing prices from dataframe
df["Date"]=pd.to_datetime(df.Date,format="%Y-%m-%d")
df.index=df['Date']

plt.figure(figsize=(16,8))
plt.plot(df["Close"],label='Close Price history')

# Sort the dataset on date time and filter “Date” and “Close” columns:
data=df.sort_index(ascending=True,axis=0)
new_dataset=pd.DataFrame(index=range(0,len(df)),columns=['Date','Close'])

for i in range(0,len(data)):
    new_dataset["Date"][i]=data['Date'][i]
    new_dataset["Close"][i]=data["Close"][i]

#Normalize the new filtered dataset
scaler=MinMaxScaler(feature_range=(0,1))
final_dataset=new_dataset[['Close']].values #(IMPROVEMENT)

train_data=final_dataset[0:987,:]
valid_data=final_dataset[987:,:]

new_dataset.index=new_dataset.Date
new_dataset.drop("Date",axis=1,inplace=True)
scaler=MinMaxScaler(feature_range=(0,1))
scaled_data=scaler.fit_transform(final_dataset)

x_train_data,y_train_data=[],[]

for i in range(60,len(train_data)):
    x_train_data.append(scaled_data[i-60:i,0])
    y_train_data.append(scaled_data[i,0])

x_train_data,y_train_data=np.array(x_train_data),np.array(y_train_data)

x_train_data=np.reshape(x_train_data,(x_train_data.shape[0],x_train_data.shape[1],1))

#Build and train the LSTM model
lstm_model=Sequential()
lstm_model.add(LSTM(units=50,return_sequences=True,input_shape=(x_train_data.shape[1],1)))
lstm_model.add(LSTM(units=50))
lstm_model.add(Dense(1))

inputs_data=new_dataset[len(new_dataset)-len(valid_data)-60:].values
inputs_data=inputs_data.reshape(-1,1)
inputs_data=scaler.transform(inputs_data)

lstm_model.compile(loss='mean_squared_error',optimizer='adam')
from keras.callbacks import EarlyStopping
early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
lstm_model.fit(x_train_data, y_train_data, epochs=50, batch_size=32, verbose=2, validation_split=0.2, callbacks=[early_stopping])

# Take a sample of a dataset to make stock price predictions using the LSTM model:
X_test=[]
for i in range(60,inputs_data.shape[0]):
    X_test.append(inputs_data[i-60:i,0])
X_test=np.array(X_test)

X_test=np.reshape(X_test,(X_test.shape[0],X_test.shape[1],1))
predicted_closing_price=lstm_model.predict(X_test)
predicted_closing_price=scaler.inverse_transform(predicted_closing_price)

#Save the LSTM MODEL
lstm_model.save("saved_model.h5")

# Visualize the predicted stock costs with actual stock costs:
train_data=new_dataset[:987]
valid_data=new_dataset[987:]
valid_data['Predictions']=predicted_closing_price
plt.plot(train_data["Close"])
plt.plot(valid_data[['Close',"Predictions"]])

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

#CHECKING FOR EFFICIENCY
# Calculate evaluation metrics
mse = mean_squared_error(valid_data["Close"], valid_data["Predictions"])
rmse = np.sqrt(mse)  # Root Mean Squared Error
mae = mean_absolute_error(valid_data["Close"], valid_data["Predictions"])
r2 = r2_score(valid_data["Close"], valid_data["Predictions"])

# Print the metrics
print(f"Mean Squared Error (MSE): {mse:.4f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
print(f"Mean Absolute Error (MAE): {mae:.4f}")
print(f"R-Squared (R²) Score: {r2:.4f}")

# Plot the actual vs. predicted values
plt.figure(figsize=(14,6))
plt.plot(valid_data["Close"], label="Actual Prices", color="blue")
plt.plot(valid_data["Predictions"], label="Predicted Prices", color="red", linestyle="dashed")
plt.title("Actual vs. Predicted Stock Prices")
plt.xlabel("Time")
plt.ylabel("Stock Price")
plt.legend()
plt.show()

# Plot residual errors (Actual - Predicted)
plt.figure(figsize=(12,6))
plt.scatter(valid_data["Close"], valid_data["Close"] - valid_data["Predictions"], color="purple")
plt.axhline(y=0, color="black", linestyle="dashed")
plt.title("Residual Errors")
plt.xlabel("Actual Prices")
plt.ylabel("Residuals (Actual - Predicted)")
plt.show()