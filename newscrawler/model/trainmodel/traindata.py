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

from ..modeldata import ModelData
from ...exceptions import *

class TrainData(ModelData):
  """
  Generate a classifier model based on trained data set
    @params:    data      -     type of model to be generated. Accepts "article" or "section" as string value.
  """
  def __init__(self, data=None):
    print(data)
    if not data or not isinstance(data, str):
      raise trainingError("Invalid passed argument, data.")
    
    if data not in ["article", "section"]:
      raise trainingError("Invalid training data")

    self.data = data
    ModelData.__init__(self, data)
    self.run()

  def run(self):
    for i in range(len(self.df)):
      features = self.extract_features(self.df['path'].loc[i], self.df['type'].loc[i])
      self.featureSet.loc[i] = features

    self.featureSet.groupby(self.featureSet['type']).size()
    print(self.featureSet.head(10))

    X = self.featureSet.drop(['path','type'],axis=1).values
    y = self.featureSet['type'].values

    # model = { "DecisionTree":tree.DecisionTreeClassifier(max_depth=10),
    #         "RandomForest":ek.RandomForestClassifier(n_estimators=50),
    #         "Adaboost":ek.AdaBoostClassifier(n_estimators=50),
    #         "GradientBoosting":ek.GradientBoostingClassifier(n_estimators=50),
    #         "GNB":GaussianNB()
    # }

    X_train, X_test, y_train, y_test = train_test_split(X, y ,test_size=0.2)

    results = {}
    # for algo in model:
    #     clf = model[algo]
    #     clf.fit(X_train,y_train)
    #     score = clf.score(X_test,y_test)
    #     results[algo] = score
    # print(results)

    # winner = max(results, key=results.get)
    # print(winner)
    clf = ek.RandomForestClassifier(n_estimators=50)
    clf.fit(X_train,y_train)
    score = clf.score(X_test,y_test)
    print(score)
    # clf = model[algo]
    res = clf.predict(X)
    mt = confusion_matrix(y, res)
    print("False positive rate : %f %%" % ((mt[0][1] / float(sum(mt[0])))*100))
    print('False negative rate : %f %%' % ( (mt[1][0] / float(sum(mt[1]))*100)))

    #---------- SAVE MODEL ---------#
    if self.data == "article":
      filename = 'newscrawler/model/sav/articlemodel.sav'
    else:
      filename = 'newscrawler/model/sav/sectionmodel.sav'
    print(f"Model saved at {filename}")
    joblib.dump(clf, filename)