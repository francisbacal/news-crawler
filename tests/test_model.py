import pytest, joblib
from newscrawler.helpers import *
from newscrawler.links import pageLinks
from newscrawler import ModelData




def test_model_section_category():
  """
  Test for url category == section
  """
  modelData = ModelData("section")
  # link = 'https://www.philstar.com/the-philippine-star'
  link = 'http://www.philstar.com/pilipino-star-ngayon/probinsiya'
  
  
  clf = joblib.load('newscrawler/model/sav/sectionmodel.sav')
  url_type =get_path_type(link, clf)
  assert url_type == 'section'