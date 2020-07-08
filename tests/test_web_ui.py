import shutil
import subprocess
import urllib

import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from webdrivermanager import GeckoDriverManager


@pytest.fixture(scope='session')
def driver():
    geckodriver_executable_path = shutil.which('geckodriver')
    if geckodriver_executable_path is None:
        geckodriver_executable_path = GeckoDriverManager().download_and_install()[1]
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path=geckodriver_executable_path, options=options)
    yield driver
    driver.quit()

@pytest.fixture(scope='session')
def voila():
    args=['jupyter', 'notebook', '--VoilaConfiguration.enable_nbextensions=True', '--no-browser',
            '--Voila.log_level=logging.DEBUG']
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
def test_voila_basic_function(driver, voila):
    driver.get(voila)
    driver.implicitly_wait(60)
    assert "Drawdown" in driver.title
    elem = driver.find_element_by_xpath('//div[contains(text(), "Solution")]')
    assert elem

    # Check that the tab bar is present and that the Overview tab is there.
    tabs = driver.find_element_by_class_name('web_ui_tab_bar')
    assert tabs
    assert tabs.find_element_by_xpath('//div[contains(text(), "Overview")]')


@pytest.mark.slow
def test_voila_RRS(driver, voila):
    driver.get(voila)
    # Rendering the solution takes about 30 seconds on a Macbook Pro, could
    # take longer on a heavily loaded continuous integration server
    driver.implicitly_wait(240)

    # click the checkbox to render the solution
    checkboxdiv = driver.find_element_by_class_name('checkbox_solarpvutil')
    assert checkboxdiv
    checkbox = checkboxdiv.find_element_by_tag_name("input")
    assert checkbox
    assert checkbox.get_attribute("type") == "checkbox"
    checkbox.click()

    # Check that the tab bar now contains the tabs for a solution
    tabs = driver.find_element_by_class_name('web_ui_tab_bar')
    assert tabs
    assert tabs.find_element_by_xpath('//div[contains(text(), "Summary")]')
    assert tabs.find_element_by_xpath('//div[contains(text(), "Model")]')
    assert tabs.find_element_by_xpath('//div[contains(text(), "Variable Meta-Analysis")]')
    assert tabs.find_element_by_xpath('//div[contains(text(), "Adoption Data")]')
    assert tabs.find_element_by_xpath('//div[contains(text(), "TAM Data")]')
    assert tabs.find_element_by_xpath('//div[contains(text(), "First Cost")]')
    assert tabs.find_element_by_xpath('//div[contains(text(), "Operating Cost")]')
    assert tabs.find_element_by_xpath('//div[contains(text(), "Emissions")]')


@pytest.mark.slow
def test_voila_LAND(driver, voila):
    driver.get(voila)
    # Rendering the solution takes about 30 seconds on a Macbook Pro, could
    # take longer on a heavily loaded continuous integration server
    driver.implicitly_wait(240)

    # click the checkbox to render the solution
    checkboxdiv = driver.find_element_by_class_name('checkbox_silvopasture')
    assert checkboxdiv
    checkbox = checkboxdiv.find_element_by_tag_name("input")
    assert checkbox
    assert checkbox.get_attribute("type") == "checkbox"
    checkbox.click()

    # Check that the tab bar now contains the tabs for a solution
    tabs = driver.find_element_by_class_name('web_ui_tab_bar')
    assert tabs
    assert tabs.find_element_by_xpath('//div[contains(text(), "Summary")]')
    assert tabs.find_element_by_xpath('//div[contains(text(), "Model")]')
    assert tabs.find_element_by_xpath('//div[contains(text(), "Variable Meta-Analysis")]')
    assert tabs.find_element_by_xpath('//div[contains(text(), "Adoption Data")]')
    assert tabs.find_element_by_xpath('//div[contains(text(), "AEZ Data")]')
    assert tabs.find_element_by_xpath('//div[contains(text(), "First Cost")]')
    assert tabs.find_element_by_xpath('//div[contains(text(), "Operating Cost")]')
    assert tabs.find_element_by_xpath('//div[contains(text(), "Emissions")]')
