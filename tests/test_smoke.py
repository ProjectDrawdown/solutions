import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from webdrivermanager import GeckoDriverManager


@pytest.fixture(scope="session")
def driver():
    geckodriver_executable_path = GeckoDriverManager().download_and_install()[1]
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path=geckodriver_executable_path, options=options)
    yield driver
    driver.close()


def test_voila_started(driver):
    driver.get("http://localhost:8866/")
    driver.implicitly_wait(20)
    assert "Drawdown" in driver.title
    elem = driver.find_element_by_xpath('//div[contains(text(), "Solution")]')
    assert elem

