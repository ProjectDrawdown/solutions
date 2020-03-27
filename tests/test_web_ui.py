import subprocess
import urllib

import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from webdrivermanager import GeckoDriverManager


@pytest.fixture(scope='session')
def driver():
    geckodriver_executable_path = GeckoDriverManager().download_and_install()[1]
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path=geckodriver_executable_path, options=options)
    yield driver
    driver.quit()

@pytest.fixture(scope='session')
def voila():
    args=['jupyter', 'notebook', '--VoilaConfiguration.enable_nbextensions=True', '--no-browser', '--Voila.log_level=logging.DEBUG']
    jup = subprocess.Popen(args=args, shell=False, bufsize=1, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, close_fds=True)
    urlparts = None
    for line in jup.stdout:
        line = line.decode('utf-8', errors='ignore').strip()
        if line.startswith('http://localhost'):
            urlparts = urllib.parse.urlparse(line.strip())
            break
    newpath = urlparts.path + 'voila/render/VoilaDrawdown.ipynb'
    urlparts = urlparts._replace(path=newpath)
    yield urllib.parse.urlunparse(urlparts)
    jup.kill()

@pytest.mark.slow
def test_voila_started(driver, voila):
    driver.get(voila)
    driver.implicitly_wait(20)
    assert "Drawdown" in driver.title
    elem = driver.find_element_by_xpath('//div[contains(text(), "Solution")]')
    assert elem
