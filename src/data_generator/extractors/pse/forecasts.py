import glob
import os
from datetime import datetime
from time import sleep

import openpyxl
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

from src.data_generator.extractors.pse.base_extractor import BasePseDataExtractor

_TEMPORARY_RESOURCES_PATH = os.path.join(os.path.abspath(os.curdir), r'resources\temporary')
_DATA_URL = r'https://www.pse.pl/dane-systemowe/plany-pracy-kse/plan-koordynacyjny-5-letni' \
            r'/wielkosci-podstawowe'
_DOWNLOAD_BUTTON_PATH = '//li[contains(@onclick,"insta_download_xlsx()")]'
_DATE_BUTTON_PATH = '//li[contains(@class,"vui-param")]'
_START_DATE_INPUT_PATH = '//input[contains(@name,"data_od")]'
_END_DATE_INPUT_PATH = '//input[contains(@name,"data_do")]'
_CONFIRM_DATE_BUTTON_PATH = '//button[contains(@class,"btn btn-primary apply")]'
_MONTH_SELECT_PATH = '//select[contains(@class,"ui-datepicker-month")]'
_YEAR_SELECT_PATH = '//select[contains(@class,"ui-datepicker-year")]'

__all__ = ('ForecastsExtractor',)


class ForecastsExtractor(BasePseDataExtractor):
    def extract(self, date: datetime) -> pd.DataFrame:
        if date.year < 2021:
            data = super().extract(date=date)
        else:
            self.__clear_local_directory()
            self.__download_data_to_local_directory(date=date)
            data = self.__read_data_from_temporary_resources()
        return data

    def _get_data_name(self) -> str:
        return 'PL_WPKD'

    def __read_data_from_temporary_resources(self) -> pd.DataFrame:
        files = glob.glob('\\'.join([_TEMPORARY_RESOURCES_PATH, '*']))
        if len(files) == 1:
            workbook = openpyxl.load_workbook(files[0])
            raw_data = workbook.active.values
            data = pd.DataFrame(raw_data)
            data.columns = data.iloc[0]
            data = data.iloc[3:]
            return data
        else:
            raise ValueError(f'{len(files)} files in the directory')

    def __select_date(self, driver: webdriver.Chrome, date: datetime) -> None:
        WebDriverWait(driver, 600).until(
            expected_conditions.element_to_be_clickable((By.XPATH, _START_DATE_INPUT_PATH))
        )

        month = str(date.month-1)
        year = str(date.year)
        day = date.day
        day_path = f'//td[contains(@data-handler,"selectDay")]/a[contains(text(), "{day}")]'

        for element_path in [_START_DATE_INPUT_PATH, _END_DATE_INPUT_PATH]:
            driver.find_element_by_xpath(element_path).click()
            Select(driver.find_element_by_xpath(_MONTH_SELECT_PATH)).select_by_value(month)
            Select(driver.find_element_by_xpath(_YEAR_SELECT_PATH)).select_by_value(year)
            driver.find_element_by_xpath(day_path).click()

    def __download_data_to_local_directory(self, date: datetime) -> None:
        driver = self.__create_webserver_driver()
        try:
            driver.get(_DATA_URL)
            WebDriverWait(driver, 600).until(
                expected_conditions.element_to_be_clickable((By.XPATH, _DATE_BUTTON_PATH))
            )

            driver.find_element_by_xpath(_DATE_BUTTON_PATH).click()
            self.__select_date(driver=driver, date=date)
            driver.find_element_by_xpath(_CONFIRM_DATE_BUTTON_PATH).click()

            WebDriverWait(driver, 600).until(
                expected_conditions.element_to_be_clickable((By.XPATH, _DOWNLOAD_BUTTON_PATH))
            )
            driver.find_element_by_xpath(_DOWNLOAD_BUTTON_PATH).click()
        except TimeoutException as e:
            print(e)
            raise
        finally:
            i = 0
            sleep(10)
            while not self.__check_if_file_downloaded():
                sleep(10)
                i += 10
                if i >= 30:
                    print('PSE downloading process has failed')
                    print('Retrying')
                    self.__download_data_to_local_directory(date=date)
            print('Closing the web driver')
            driver.close()
            driver.quit()

    def __create_webserver_driver(self) -> webdriver.Chrome:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": _TEMPORARY_RESOURCES_PATH,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False
        })
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def __clear_local_directory(self) -> None:
        files = glob.glob('\\'.join([_TEMPORARY_RESOURCES_PATH, '*']))
        for f in files:
            os.remove(f)

    def __check_if_file_downloaded(self) -> bool:
        if glob.glob('\\'.join([_TEMPORARY_RESOURCES_PATH, '*'])):
            print('File downloaded')
            return True


if __name__ == '__main__':
    data_ = ForecastsExtractor().extract(date=datetime(2021, 1, 11))
