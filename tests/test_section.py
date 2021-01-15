from newscrawler import pageLinks

def test_cleaned_section():
  links = pageLinks(testing=True)
  sections = ['https://www.philstar.com/the-philippine-star/contact-us', 'http://www.philstar.com/pilipino-star-ngayon/probinsiya']
  cleaned = list(links.getSectionLinks(links=sections))

  assert cleaned == ['http://www.philstar.com/pilipino-star-ngayon/probinsiya']