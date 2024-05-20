from datetime import datetime, timedelta
from enum import Enum


class State(Enum):
    VALID = 'VALID'
    NOT_VALID = 'NOT_VALID'
    READY_FOR_CHECK = 'READY_FOR_CHECK'
    ERROR = 'ERROR'

class Nip():
    state: State
    message: str
    number: str
    country: str
    address: str
    requestDateTime: str
    ownerName: str

    def __init__(self, name: str):
        '''
        Representation of nip with all values

        :param name: not separated nip country and number
        '''
        self.country, self.number = name[:2], name[2:]

    def getFullName(self) -> str:
        return self.country + self.number

    def formatToCsvLine(self, pathToScreenshotFolder: str = 'Checked without screenshot') -> str:
        '''
        Function prepares and returns data to write to csv file in one line

        :param pathToScreenshotFolder: path to folder with Screenshots
        :return: all information on nip in csv formatted line
        '''
        addressLines = self.address.split('\n')
        addressLine2 = ''
        if len(addressLines) == 2:
            addressLine1, addressLine2 = addressLines
        elif len(addressLines) == 1:
            addressLine1 = addressLines[0]
        else:
            addressLine1 = addressLines[0]
            addressLine2 = '\t'.join(addressLines[1:])

        try:
            datetimePL = datetime.strptime(self.requestDateTime, '%Y-%m-%dT%H:%M:%S.%fZ') + \
                         timedelta(hours=2)
            date, time = str(datetimePL).split(' ')
            time = time[:8]
        except:
            time, date = '', ''

        pathToScreenshot = f'{pathToScreenshotFolder}/{self.getFullName()}.png' if \
            self.state == State.VALID else 'Not applicable'

        line = '\n' + ';'.join((self.getFullName(), self.country, self.number,
                                self.state.value, self.message, self.ownerName,
                                addressLine1, addressLine2, date, time, pathToScreenshot))

        return line
