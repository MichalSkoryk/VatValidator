from datetime import datetime
import os
from typing import Dict

from helpers.Logger import Logger
from utils import Nip

class FileHandler:
    def __init__(self, path: str, pathToSource: str, logger: Logger):
        '''
        Class that manages files and directories

        :param path: path where directory with output files will be created
        :param pathToSource: path to file with nips numbers
        :param logger: logger used to log information
        '''
        self.pathToSave = path
        today = datetime.now()
        self.dateName = today.strftime("%Y-%m-%d")
        self.dateTimeName = today.strftime("%Y%m%d_%H%M")
        self.logger = logger
        self.pathToSource = pathToSource
        self.headers = ['Nip with country', 'Country', 'Nip number', 'Validation state', 'Message',
                        'Name', 'Address line 1', 'Address line 2', 'CheckData', 'CheckTime',
                        'Screenshot']

    def createMainDir(self):
        '''
        Creates directory where all created files will be
        '''
        self.logger.info(f"Create directory {self.pathToSave}")
        path = self.pathWithMainDirectory()
        self.pathToSave = path
        if os.path.isdir(path):
            print('Directory in this path already exists')
        else:
            os.mkdir(path)

    def createScreenshotsDir(self):
        '''
        Creates directory where screenshots should be
        '''
        path = self.pathToScreenshotFolder()
        self.logger.info(f"Create directory {path}")
        if os.path.isdir(path):
            print('Directory in this path already exists')
        else:
            os.mkdir(path)

    def pathWithMainDirectory(self) -> str:
        '''
        Creates path with main directory

        :return: absolute path with main directory
        '''
        return '/'.join((self.pathToSave, self.dateName))

    def pathToScreenshotFolder(self):
        '''
        Creates path to screenshot folder

        :return: absolute path with screenshot folder
        '''
        screenshotsFolderName = self.dateTimeName + "_screenshots"
        return '/'.join((self.pathToSave, screenshotsFolderName))

    def pathToSaveFile(self, type: str = 'csv', prefix: str = 'NIP') -> str:
        '''
        Creates path to file with data

        :param type: type of file
        :param prefix: prefix of name
        :return: path to file with data
        '''
        name = f"{prefix}{self.dateTimeName}.{type}"
        return '/'.join((self.pathToSave, name))

    def createSaveFile(self):
        '''
        Create file for data on nips and write headers in first line
        '''
        print(self.pathToSaveFile())
        with open(self.pathToSaveFile(), 'w', encoding='utf-8') as saveFile:
            saveFile.write(';'.join(self.headers))

    def writeToCsv(self, data: Dict[str, Nip]):
        '''
        Enters data to file with data on nips

        :param data: dictionary with nips data
        '''
        self.logger.info("Write to csv file")
        with open(self.pathToSaveFile(), 'a', encoding='utf-8') as csvFile:
            for nip in data:
                line = data[nip].formatToCsvLine(self.pathToScreenshotFolder())
                csvFile.write(line)

    def dumpLoggerFile(self):
        '''
        Writes logged information to file
        '''
        with open(self.pathToSaveFile("txt", "Log"), 'w', encoding='utf-8') as file:
            file.write(self.logger.get())
        self.logger.info('Log file created')
