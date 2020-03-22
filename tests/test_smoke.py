import time

import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


@pytest.fixture(scope="session")
def driver():
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path='bin/geckodriver', options=options)
    yield driver
    driver.close()


def test_voila_started(driver):
    driver.get("http://localhost:8866/")
    time.sleep(10)
    assert "Drawdown" in driver.title
    elem = driver.find_element_by_xpath('//div[contains(text(), "Solution")]')
    assert elem

