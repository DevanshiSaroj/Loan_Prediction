# -*- coding: utf-8 -*-
"""LOAN_PREDICTION.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1yjdXXg1Gm_TSXuipvqybDzPltqWyf5v7
"""

import pandas as pd
import numpy as np

df=pd.read_csv("/content/Loan payments data.csv")

df.head()

df.info()

df.describe()

df.isnull().sum()

# Handling Missing Values
df['paid_off_time'].fillna('Not Paid Off', inplace=True)
df['past_due_days'].fillna(0, inplace=True)

# Convert 'Not Paid Off' and 'NaT' to NaN for paid_off_time column
df['paid_off_time'] = df['paid_off_time'].replace(['Not Paid Off', pd.NaT], pd.NaT)

# Convert 'paid_off_time' column to datetime objects
df['paid_off_time'] = pd.to_datetime(df['paid_off_time'], errors='coerce')

# Replace remaining null values in 'paid_off_time' with the minimum date in the dataset
# print(df['paid_off_time'].min().info)
min_date = df['paid_off_time'].min()
df['paid_off_time'].fillna(min_date, inplace=True)

# Now, convert the 'paid_off_time' column to datetime
df['paid_off_time'] = pd.to_datetime(df['paid_off_time'])

# Check for null values again
print(df.isnull().sum())

# Check numerical columns
numerical_columns = df.select_dtypes(include=['float64', 'int64']).columns
print("Numerical Columns:")
print(numerical_columns)

# Check categorical columns
categorical_columns = df.select_dtypes(include=['object']).columns
print("\nCategorical Columns:")
print(categorical_columns)

# Convert 'effective_date' and 'due_date' columns to datetime objects
df['effective_date'] = pd.to_datetime(df['effective_date'])
df['due_date'] = pd.to_datetime(df['due_date'])

# Calculate 'loan_term_days'
df['loan_term_days'] = (df['due_date'] - df['effective_date']).dt.days

# Now 'loan_term_days' should be available in your DataFrame
print(df['loan_term_days'])

# Define a function to remove outliers based on IQR method
def remove_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df_outliers_removed = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    return df_outliers_removed

# Remove outliers from numerical columns
numerical_columns = ['Principal', 'terms', 'past_due_days', 'age', 'loan_term_days']
for column in numerical_columns:
    df = remove_outliers(df, column)

# Check the shape of the dataframe after removing outliers
print("Shape of dataframe after removing outliers:", df.shape)

# Define a function to identify and remove outliers based on IQR method
def identify_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    return outliers

# Identify outliers for numerical columns
numerical_columns = ['Principal', 'terms', 'past_due_days', 'age', 'loan_term_days']
all_outliers = pd.DataFrame()
for column in numerical_columns:
    outliers = identify_outliers(df, column)
    all_outliers = pd.concat([all_outliers, outliers])

# Print out the outliers
print("Outliers:")
print(all_outliers)

import matplotlib.pyplot as plt  # Import Matplotlib

# Define numerical columns
numerical_columns = ['Principal', 'terms', 'past_due_days', 'age', 'loan_term_days']

# Create boxplots for numerical columns
plt.figure(figsize=(10, 6))
df[numerical_columns].boxplot()
plt.title('Boxplot of Numerical Columns')
plt.xlabel('Columns')
plt.ylabel('Values')
plt.xticks(rotation=45)
plt.show()

# Univariate Analysis (Histograms)
import matplotlib.pyplot as plt

plt.hist(df['Principal'], bins=20)
plt.xlabel('Principal')
plt.ylabel('Frequency')
plt.title('Distribution of Principal')
plt.show()

# Bivariate Analysis (Bar Plots)
import seaborn as sns

sns.countplot(x='loan_status', data=df)
plt.xlabel('Loan Status')
plt.ylabel('Count')
plt.title('Distribution of Loan Status')
plt.show()

# Multivariate Analysis (Pair Plots)
sns.pairplot(df[['Principal', 'age', 'loan_status']], hue='loan_status')
plt.show()

# Create New Features
df['loan_term_days'] = (df['due_date'] - df['effective_date']).dt.days

# Normalize Numerical Features (Min-Max Scaling)
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
df[['Principal', 'age', 'loan_term_days']] = scaler.fit_transform(df[['Principal', 'age', 'loan_term_days']])

df.dtypes

# Convert datetime columns to string (object) type
df['effective_date'] = df['effective_date'].astype(str)
df['due_date'] = df['due_date'].astype(str)
df['paid_off_time'] = df['paid_off_time'].astype(str)

# Now the datetime columns are converted to object type
print(df.dtypes)

# Convert datetime columns to timestamps
df['effective_date_timestamp'] = df['effective_date'].apply(lambda x: pd.Timestamp(x).timestamp())
df['due_date_timestamp'] = df['due_date'].apply(lambda x: pd.Timestamp(x).timestamp())
df['paid_off_time_timestamp'] = df['paid_off_time'].apply(lambda x: pd.Timestamp(x).timestamp())

# Now the datetime columns are converted to timestamps
print(df.dtypes)

# Create 'loan_status_binary' column based on 'loan_status'
df['loan_status_binary'] = (df['loan_status'] == 'PAIDOFF').astype(int)

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Define numerical and categorical features
numerical_features = ['Principal', 'terms', 'past_due_days', 'age', 'loan_term_days', 'effective_date_timestamp', 'due_date_timestamp', 'paid_off_time_timestamp']
categorical_features = ['education', 'Gender']

# Preprocessing for numerical features
numerical_transformer = Pipeline(steps=[
    ('scaler', StandardScaler())
])

# Preprocessing for categorical features
categorical_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# Bundle preprocessing for numerical and categorical features
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numerical_transformer, numerical_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# Define model
model = Pipeline(steps=[('preprocessor', preprocessor),
                        ('classifier', LogisticRegression())])

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(df[numerical_features + categorical_features],
                                                    df['loan_status_binary'],
                                                    test_size=0.2,
                                                    random_state=42)

# Train the model
model.fit(X_train, y_train)

# Predict on test data
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)

import numpy as np
import matplotlib.pyplot as plt

# Extract feature names
feature_names = numerical_features + categorical_features

# Extract coefficients and intercept from the trained logistic regression model
coefficients = model.named_steps['classifier'].coef_[0]
intercept = model.named_steps['classifier'].intercept_[0]

# Create a dictionary mapping feature names to coefficients
feature_coefficients = dict(zip(feature_names, coefficients))

# Sort feature coefficients by absolute value
sorted_coefficients = sorted(feature_coefficients.items(), key=lambda x: np.abs(x[1]), reverse=True)

# Print feature importance
print("Feature Importance:")
for feature, coef in sorted_coefficients:
    print(f"{feature}: {coef:.4f}")

# Plot feature importance
plt.figure(figsize=(10, 6))
plt.barh(range(len(sorted_coefficients)), [coef for _, coef in sorted_coefficients], align='center')
plt.yticks(range(len(sorted_coefficients)), [feature for feature, _ in sorted_coefficients])
plt.xlabel('Coefficient Value')
plt.ylabel('Feature')
plt.title('Feature Importance for Logistic Regression Model')
plt.show()

# Predict probabilities for the test data
y_pred_proba = model.predict_proba(X_test)[:, 1]

# Plot predicted probabilities
plt.figure(figsize=(10, 6))
plt.hist(y_pred_proba, bins=20)
plt.xlabel('Predicted Probability')
plt.ylabel('Frequency')
plt.title('Distribution of Predicted Probabilities')
plt.show()

from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

# Calculate precision
precision = precision_score(y_test, y_pred)

# Calculate recall
recall = recall_score(y_test, y_pred)

# Calculate F1-score
f1 = f1_score(y_test, y_pred)

# Calculate ROC-AUC score (only applicable for binary classification)
roc_auc = roc_auc_score(y_test, y_pred_proba)

print("Precision:", precision)
print("Recall:", recall)
print("F1-score:", f1)
print("ROC-AUC score:", roc_auc)

from sklearn.model_selection import cross_val_score

# Perform cross-validation
cv_scores = cross_val_score(model, X_train, y_train, cv=5)

print("Cross-validation scores:", cv_scores)
print("Mean cross-validation score:", np.mean(cv_scores))

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV  # Import GridSearchCV

# Define numerical and categorical features
numerical_features = ['Principal', 'terms', 'past_due_days', 'age', 'loan_term_days', 'effective_date_timestamp', 'due_date_timestamp', 'paid_off_time_timestamp']
categorical_features = ['education', 'Gender']

# Preprocessing for numerical features
numerical_transformer = Pipeline(steps=[
    ('scaler', StandardScaler())
])

# Preprocessing for categorical features
categorical_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# Bundle preprocessing for numerical and categorical features
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numerical_transformer, numerical_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# Define model
model = Pipeline(steps=[('preprocessor', preprocessor),
                        ('classifier', LogisticRegression())])

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(df[numerical_features + categorical_features],
                                                    df['loan_status_binary'],
                                                    test_size=0.2,
                                                    random_state=42)

# Perform grid search
param_grid = {
    'classifier__C': [0.1, 1.0, 10.0],  # Regularization parameter for logistic regression
    'classifier__penalty': ['l2'],  # Penalty norm for logistic regression compatible with lbfgs solver
}

grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)

# Get best hyperparameters
best_params = grid_search.best_params_
print("Best hyperparameters:", best_params)

# Get best cross-validation score
best_score = grid_search.best_score_
print("Best cross-validation score:", best_score)

