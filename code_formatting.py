X = df_balanced_drop.iloc[:, 1:]
y = df_balanced_drop["region"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=747
)

# randSearch.best_params_
# Best Parameters :  {'n_estimators': 80, 'max_depth': 4, 'learning_rate': 0.14}

xgb_clf_tuned = XGBClassifier(
    n_estimators=80,
    max_depth=4,
    learning_rate=0.14,
    objective="multi:softmax",
    num_class=3,
    eval_metric=["mlogloss"],
)

xgb_clf_tuned.fit(
    X_train, y_train, eval_set=[(X_train, y_train), (X_test, y_test)], verbose=0
)
results = xgb_clf_tuned.evals_result()
epochs = len(results["validation_0"]["mlogloss"])
x_axis = range(0, epochs)

# xgb_clf 'mlogloss' plot
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(x_axis, results["validation_0"]["mlogloss"], label="Train")
ax.plot(x_axis, results["validation_1"]["mlogloss"], label="Test")
ax.legend()
plt.xlabel("epoch")
plt.ylabel("mlogloss")
plt.title("RandomSearchCV XGB Clf")
plt.show()
