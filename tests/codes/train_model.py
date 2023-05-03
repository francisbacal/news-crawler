import sklearn.ensemble as ek
import joblib, pandas as pd
from sklearn import tree, linear_model
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectFromModel
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix
from sklearn.pipeline import make_pipeline
from sklearn import preprocessing
from sklearn import svm
from sklearn.linear_model import LogisticRegression

from newscrawler.model import df, featureSet, extract_features

for i in range(len(df)):
    features = extract_features(df['path'].loc[i], df['type'].loc[i])
    featureSet.loc[i] = features

featureSet.groupby(featureSet['type']).size()

X = featureSet.drop(['path','type'],axis=1).values
y = featureSet['type'].values

print(X,y)


model = { "DecisionTree":tree.DecisionTreeClassifier(max_depth=10),
         "RandomForest":ek.RandomForestClassifier(n_estimators=50),
         "Adaboost":ek.AdaBoostClassifier(n_estimators=50),
         "GradientBoosting":ek.GradientBoostingClassifier(n_estimators=50),
         "GNB":GaussianNB()
}

X_train, X_test, y_train, y_test = train_test_split(X, y ,test_size=0.5)

results = {}
for algo in model:
    clf = model[algo]
    clf.fit(X_train,y_train)
    score = clf.score(X_test,y_test)
    results[algo] = score
print(results)

winner = max(results, key=results.get)
print(winner)

clf = model[winner]
res = clf.predict(X)
mt = confusion_matrix(y, res)
print("False positive rate : %f %%" % ((mt[0][1] / float(sum(mt[0])))*100))
print('False negative rate : %f %%' % ( (mt[1][0] / float(sum(mt[1]))*100)))

#---------- SAVE MODEL ---------#
filename = 'newscrawler/model/sav/model.sav'
joblib.dump(clf, filename)