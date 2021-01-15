# NEWS SITE CRAWLER #

Crawls news website for sections and articles links by using a prediction/classifier made with Sklearn RandomForest library.
Trained models/classifier for both section and article were generated to help classify what type a parsed url/link is.



[![Python 3.8.5](https://img.shields.io/badge/python-3.8.5-blue.svg)](https://www.python.org/downloads/release/python-385/)

## Install ##

**Clone the repository**
--NO REPO YET

**Recommended to create virtualenv**
Use any name for your virtualenv

```bash
virtualenv venv
```

**Activate virtualenv:**

For Mac OS/ Linux

```bash
source venv/bin/activate
```

For Windows

```bash
source venv/Scripts/activate
```

**Install dependencies**
Dependencies are in the requirements.txt

```bash
pip3 install -r requirements.txt
```

## Training Model ##

Model for both article and section are already generated.
In case dataset of either two were updated models or classifier should also be retrained.
Simply run ***'train.py'*** passing argument ***"article"*** or ***"section"***

***Code Snippet:***

```bash
python3 train.py article
```


## Section crawler ##

Not yet done.
See root folder sections_crawler.py

***Code Snippet:***

```bash
python3 section_crawler.py
```

## Article crawler ##

Not yet done.
See root folder articles_crawler.py

***Code Snippet:***

```bash
python3 articles_crawler.py
```