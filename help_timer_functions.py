# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 17:59:04 2021

@author: Anja
"""

import time 
import unittest
from datetime import timedelta
import pandas as pd

def unixTimeMillis(dt):
    ''' Convert datetime to unix timestamp '''
    return int(time.mktime(dt.timetuple()))


def unixToDatetime(unix):
    ''' Convert unix timestamp to datetime. '''
    return pd.to_datetime(unix, unit='s', origin='unix').round('1d')

def getMarks(start, end, N=20):
    ''' 
    start: Time in datetime format
    end: time in datetime format
    N: how many marks
    
    Returns the marks for labeling. 
    Every Nth value will be used.
    '''
    start_unix = unixTimeMillis(start)
    end_unix = unixTimeMillis(end)

    range_dates = range(start_unix,end_unix,int((end_unix-start_unix)/N))
    result = {date: {'label': str(unixToDatetime(date))[:10],
                    'style': {'color': 'lightblue'}} for date in range_dates}

    return result

class TestDateConversion(unittest.TestCase):
    
    def test_unixConversion(self):
        g = pd.to_datetime('2021-06-23', format="%Y-%m-%d")
        self.assertEqual(g, unixToDatetime(unixTimeMillis(g)))

    def test_unixConversionHours(self):
        g = pd.to_datetime('2021-06-23', format="%Y-%m-%d")
        h = g+timedelta(hours=2)
        self.assertEqual(g, unixToDatetime(unixTimeMillis(h)))


    def test_getMarks_len(self):
        end = pd.to_datetime('2021-06-23', format="%Y-%m-%d")
        start = pd.to_datetime('2020-06-23', format="%Y-%m-%d")
        self.assertEqual(20, len(getMarks(start, end, 20)))

if __name__ == '__main__':
    unittest.main(argv=[''], verbosity=1, exit=False)
