import os
import datetime
import re

def createDirNow(path: str='D:/Python/VatValidator/media'):
    now = str(datetime.datetime.now())
    rightNow = now.split(' ')[0]
    pathWithDir = path + '/' + str(rightNow)
    if os.path.isdir(pathWithDir):
        print('Directory in this path already exists')
    else:
        os.mkdir(pathWithDir)
    return pathWithDir

def createDir(path):
    if os.path.isdir(path):
        print('Directory in this path already exists')
    else:
        os.mkdir(path)
    return path

def isNipValidable(nip: str):
    countryMap = {
        'AT': r'^U\d{8}',
        'BE': r'^0\d{9}',
        'BG': r'^\d{9, 10}',
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
