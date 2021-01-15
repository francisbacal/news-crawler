import pytest
from newscrawler.helpers import *
from newscrawler.links import pageLinks
from newscrawler.model import clf, extract_features


def test_model_section_category():
  """
  Test for url category == section
  """
  # link = 'https://www.philstar.com/the-philippine-star'
  link = 'http://www.philstar.com/pilipino-star-ngayon/probinsiya'
  assert get_path_type(link, clf) == 'section'

def test_extract_features_subdirectory_count():
  """
  extracted features data set:
    ['path', 'path length', 'include', 'exclude', 'double slash count', 'sub directory count', 'length of query', 'type']
  """
  path_1 = '/the-philippine-star'
  path_2 = '/lifestyle/shopping-guide'
  feat_1 = extract_features(path_1, 'oth')
  feat_2 = extract_features(path_2, 'oth')

  assert (feat_1[5] == 1 and feat_2[5] == 2)