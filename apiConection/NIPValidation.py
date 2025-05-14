import json
import re
import requests

from typing import Dict
from helpers.Logger import Logger
from fileHandling.FileHandler import FileHandler
from utils import State, Nip

class NipCheck:
    def __init__(self, fileManager: FileHandler, logger: Logger):
        '''
        Class with functions checking if nip is valid

        :param FileManager fileManager: FileHandler used to perform operations on files
        :param Logger logger: logger used to log information
        '''
        self.checkStatusUrl = "https://ec.europa.eu/taxation_customs/vies/rest-api/check-status"
        self.checkNipUrl = "https://ec.europa.eu/taxation_customs/vies/rest-api/check-vat-number"
        self.logger = logger
        self.fileManager = fileManager

    def checkStatus(self):
        """
        Checks if service is available
        :return:
        bool:vow
        dict:countries
        """
        payload = {}
        headers = {}
        response = requests.request("GET", self.checkStatusUrl, headers=headers, data=payload)
        # response to json
        responseObj = json.loads(response.text)
        #list of countries available for check
        countries = { country['countryCode'] for country in responseObj['countries'] if
                      country['availability'] == 'Available'}

        vow = responseObj['vow']['available']

        return vow, countries

    def sendRequest(self, country, vatNumber) -> dict:
        """
        Sends request to service for information on vatNumber in chosen country

        :param str country: country of nip
        :param str vatNumber: nip number valid for chosen country
        :return: information from service in dictionary
        """
        url = self.checkNipUrl

        payload = json.dumps({
            "countryCode": country,
            "vatNumber": vatNumber
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        responseObj = json.loads(response.text)
        return responseObj


    def isVatNumberValid(self, country: str, vatNumber: str) -> tuple:
        """
        Checks if vatNumber exists and is valid

        :param country: country of nip
        :param vatNumber: nip number valid for chosen country
        :return: Tuple with information of nip number from service
        """
        try:
            responseObj = self.sendRequest(country, vatNumber)
        except:
            print('Error in request occured')
            return State.ERROR, 'Request could not be send, try to repeat action later', '', '', ''

        # default none values
        if not responseObj.get('actionSucceed', True):
            return State.ERROR, 'Could not connect with server check its availability', '', '', ''

        return State.VALID if responseObj['valid'] else State.NOT_VALID, '', responseObj['name'], \
               responseObj['address'], responseObj['requestDate']

    def checkIfNumbersAreValid(self, nips: Dict[str, Nip]) -> Dict[str, Nip]:
        """
        Function gets information for each validate nip in nips

        :param nips: dictionary of nips to check
        :return: dictionary of valid nips with information on them
        """
        for nip in nips.keys():
            # print(f'{nip} {nips[nip]["valid"]}', end=' ')
            if nips[nip].state == State.READY_FOR_CHECK:
                self.logger.info(f'Request for {nip} send')
                state, message, ownerName, addressLine, date = self.isVatNumberValid(nips[nip].country,
                                                                   nips[nip].number)
                nips[nip].state = state
                nips[nip].message = message
                nips[nip].ownerName = ownerName
                nips[nip].address = addressLine
                nips[nip].requestDateTime = date
            else:
                nips[nip].ownerName = ''
                nips[nip].address = ''
                nips[nip].requestDateTime = ''
        return nips

    def isNipBuildCorrectly(self, nip: str) -> bool:
        """
        Checks locally if nip is valid for it's country

        :param nip: nip number with prefix of country code
        :return: true if nip is build correctly or false
        """
        countryMap = {
            'AT': r'^U\d{8}',
            'BE': r'^0\d{9}',
            'BG': r'^\d{9,10}', # fortmat good why not working?
            'HR': r'^\d{11}',
            'CY': r'^\d{8}[A-Z]',
            'CZ': r'^\d{8,10}',
            'DK': r'^\d{8}',
            'EE': r'^\d{9}',
            'FI': r'^\d{8}',
            'FR': r'^[0-9ABCDEFGHJKLMNPRSTUWVXYZ]{2}\d{8}',
            'EL': r'^\d{9}',
            'ES': r'^[A-Z0-9]\d{7}[A-Z0-9]',
            'NL': r'^\d{9}B\d{2}',
            'IE': r'^\d[A-Z0-9+*]\d{5}[A-Z]',
            'LT': r'^\d{9}(?:\d{3})',
            'LU': r'^\d{8}',
            'LV': r'^\d{11}',
            'MT': r'^\d{8}',
            'DE': r'^\d{9}',
            'PL': r'^\d{10}',
            'PT': r'^\d{9}',
            'RO': r'^\d{2,10}',
            'SK': r'^\d{10}',
            'SI': r'^\d{8}',
            'SE': r'^\d{12}',
            'HU': r'^\d{8}',
            'IT': r'^\d{11}'
        }

        nipsCountry = nip[:2]
        if nipsCountry not in countryMap.keys():
            return False
        if re.compile(countryMap[nipsCountry]).match(nip[2:]):
            return True
        return False

    def validateNips(self) -> Dict[str, Nip]:
        '''
        Validates nips locally and online if possible

        :return: dictionary of Valid nips for optional screenshot confirmation
        '''
        chunkSize = 50
        counter = 0
        validNips = {}
        nips = {}
        self.fileManager.createMainDir()
        self.fileManager.createSaveFile()

        self.logger.info("Opening file")
        with open(self.fileManager.pathToSource, 'r',  newline='', encoding='utf-8') as sourceFile:
            self.logger.info("NIP format verification")
            for notFormattedRow in sourceFile.readlines():
                counter += 1
                row = notFormattedRow.strip('\n\r').replace(' ', '')
                nips[row] = Nip(row)

                if self.isNipBuildCorrectly(row):
                    nips[row].state = State.READY_FOR_CHECK
                    self.logger.info(f'{row} Approved for validation')
                else:
                    nips[row].state = State.ERROR
                    nips[row].message = 'Wrong format for this country or country not in UE'
                    self.logger.info(f'{row} Validation Error')

                if chunkSize == counter:
                    self.logger.info("Checking nips using API")
                    checkedNips = self.checkIfNumbersAreValid(nips)
                    self.fileManager.writeToCsv(checkedNips)
                    for nip in checkedNips:
                        if checkedNips[nip].state == State.VALID:
                            validNips[nip] = checkedNips[nip]
                    nips = {}
                    counter = 0

            if len(nips) != 0:
                self.logger.info("Checking nips using API")
                checkedNips = self.checkIfNumbersAreValid(nips)
                self.fileManager.writeToCsv(checkedNips)
                for nip in checkedNips:
                    if checkedNips[nip].state == State.VALID:
                        validNips[nip] = checkedNips[nip]
            return validNips
