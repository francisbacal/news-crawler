from api import *
import pytest

def test_gen_payload_country():
  countries = ["singapore"]

  payload = generate_payload(countries)

  assert payload['country'] == {"$in": ["Singapore"]}

def test_gen_payload_country_raises_key_error():
  """
  If input country is not in country names list, should remove key country in payload
  """
  payload = generate_payload("all")

  with pytest.raises(KeyError):
    payload['country']