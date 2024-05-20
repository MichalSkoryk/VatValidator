from time import sleep
from typing import Dict

import pyautogui
import selenium.webdriver

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.common import NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException

from fileHandling.FileHandler import FileHandler
from helpers.Logger import Logger
from utils import State, Nip


def downloadPdfForNipNumber(driver, country: str, nip: str, logger: Logger, fileHandler: FileHandler):
    '''
    Sends data to the online service and takes screenshot of the result

    :param driver: selenium webdriver used for web browser management
    :param country: country of nip
    :param nip: nip number
    :param logger: logger used to log information
    :param fileHandler: fileHandler used to manage files
    '''
    # close cookies topic
    try:
        driver.implicitly_wait(1)
        driver.find_element(By.CLASS_NAME, 'ecl-message__close').click()
    except :
        print('Could not find Important Disclaimer close button')

    wait = WebDriverWait(driver, timeout=2, poll_frequency=0.5 ,ignored_exceptions=[
        NoSuchElementException,ElementNotInteractableException, StaleElementReferenceException])
    wait.until(lambda d: driver.find_element(By.CLASS_NAME, 'center-form').is_displayed())

    centrumForm = driver.find_element(By.CLASS_NAME, 'center-form')

    # choose select element
    select_element = driver.find_element(By.ID, 'select-country')
    select = Select(select_element)
    select.select_by_value(country)

    # find nip input
    centrumFormChildren = centrumForm.find_elements(By.TAG_NAME,'div')
    secondDiv = centrumFormChildren[3]
    nipInput = secondDiv.find_element(By.TAG_NAME, 'input')

    # enter nip number
    nipInput.send_keys(nip)

    # find submit button
    submitBtnDiv = centrumForm.find_element(By.CLASS_NAME, 'button-right')
    submitBtn = submitBtnDiv.find_element(By.TAG_NAME, 'button')
    # scroll to see submitBtn
    driver.execute_script("window.scrollBy(0, 500)")

    submitBtn.click()

    # wait for site to
    wait = WebDriverWait(driver, timeout=2, poll_frequency=0.5, ignored_exceptions=[
        NoSuchElementException,ElementNotInteractableException, StaleElementReferenceException])
    wait.until(lambda d: driver.find_element(By.CLASS_NAME, 'text-result').is_displayed())
    resultText = driver.find_element(By.CLASS_NAME, 'text-result')

    if(resultText.text[:3] != 'Yes'):
        logger.info(f'Something wrong on screen {nip}.png')

    #scroll down for better view
    driver.execute_script("window.scrollBy(0, 250)")
    sleep(0.25)
    pyautogui.screenshot(f'{fileHandler.pathToScreenshotFolder()}/{nip}.png')

def downloadPdfForNips(nips: Dict[str, Nip], logger: Logger, fileHandler: FileHandler):
    '''
    Starts web browser engine and prepares it for operations

    :param nips: dictionary with validated nips
    :param logger: logger used for logging files
    :param fileHandler: fileHandler used for managing files
    '''
    # webdriver options
    url = 'https://ec.europa.eu/taxation_customs/vies/#/vat-validation'
    options = webdriver.EdgeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("lang=en-US")
    driver = webdriver.ChromiumEdge(options=options)
    driver.get(url)

    # accept cookies
    wait = WebDriverWait(driver, timeout=2,  poll_frequency=0.5 ,ignored_exceptions=[
        NoSuchElementException,ElementNotInteractableException, StaleElementReferenceException])
    wait.until(lambda d:  driver.find_element(By.CLASS_NAME, 'ecl-message__close').is_displayed())

    acceptCookies = driver.find_element(By.LINK_TEXT, 'Accept only essential cookies')
    acceptCookies.click()
    sleep(2)

    counter = 0
    nipsLength = len(nips)

    for nip in nips:
        # check one nip
        if nips[nip].state == State.VALID:
            counter += 1
            logger.info(f'{counter}/{nipsLength} {nip}')
            try:
                downloadPdfForNipNumber(driver, nips[nip].country, nips[
                    nip].number, logger, fileHandler)
            except TimeoutError:
                driver.refresh()
                driver.implicitly_wait(2)
                print(f'nip country: {nips[nip].country} nip number: {nips[nip].number}')
                downloadPdfForNipNumber(driver, nips[nip].country, nips[
                    nip].number, logger, fileHandler)

            # press back button to comeback to form
            backButton = driver.find_element(By.CLASS_NAME, 'ecl-button--secondary')
            backButton.click()

    driver.quit()