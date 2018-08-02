import requests
import xlsxwriter
import time
from datetime import date, timedelta


import bs4 as bs
import datetime as dt
import os
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like

import pandas_datareader.data as web
import fix_yahoo_finance
import pickle
import requests
import csv


start = time.time()


api_username = 'cbc83d2f7fa545f8306b353323e65153'
api_password = 'b7c7bae66b7ed20b22af4a79de4708c1'
base_url = 'https://api.intrinio.com'


# https://api.intrinio.com/financials/standardized?ticker=AAPL&statement=income_statement&type=FY

start_date = '2007-01-01'

d1 = date(2007, 1, 1)  # start date
d2 = date(2018, 5, 28)  # end date

delta = d2 - d1         # timedelta
listofdates = []
for i in range(delta.days + 1):
    listofdates.append(str(d1 + timedelta(days=i)))


def getCalls():
    request_url = base_url + "/usage/current"
    query_params = {
        'access_code' : 'com_fin_data'
    }
    response = requests.get(request_url, params=query_params, auth=(api_username, api_password))
    if response.status_code == 401:
        print("Unauthorized! Check your username and password."); exit()
    data = response.json()['current']
    return data

def getLim():
    request_url = base_url + "/usage/current"
    query_params = {
        'access_code' : 'com_fin_data'
    }
    response = requests.get(request_url, params=query_params, auth=(api_username, api_password))
    if response.status_code == 401:
        print("Unauthorized! Check your username and password."); exit()
    data = response.json()['limit']
    return data

def getED(a,b):
    x = a[0]
    y = b[0]
    c = x.split('-')
    d = y.split('-')
    result = ''
    if c[0] < d[0]:
        result = a
    elif c[0] > d[0]:
        result = b
    else:
        if c[1] < d[1]:
            result = a
        elif c[1] > d[1]:
            result = b
        else:
            if c[2] < d[2]:
                result = a
            elif c[2] > d[2]:
                result = b
            else:
                result = a
    return result


def getED2(x,y):
    c = x.split('-')
    d = y.split('-')
    result = ''
    if c[0] < d[0]:
        result = a
    elif c[0] > d[0]:
        result = b
    else:
        if c[1] < d[1]:
            result = a
        elif c[1] > d[1]:
            result = b
        else:
            if c[2] < d[2]:
                result = a
            elif c[2] > d[2]:
                result = b
            else:
                result = a
    return result

def getSic(ticker):
    request_url = base_url + "/data_point"
    query_params = {
        'ticker': ticker,
        'item': 'sic',
    }
    
    response = requests.get(request_url, params=query_params, auth=(api_username, api_password))
    if response.status_code == 401:
        print("Unauthorized! Check your username and password."); exit()
    data = response.json()['value']
    return data

def getCSize(ticker):
    request_url = base_url + "/data_point"
    query_params = {
        'ticker': ticker,
        'item': 'employees',
    }
    
    response = requests.get(request_url, params=query_params, auth=(api_username, api_password))
    if response.status_code == 401:
        print("Unauthorized! Check your username and password."); exit()
    data = response.json()['value']
    return data


def getMC(tkr):
    request_url = base_url + "/historical_data"
    query_params = {
        'ticker' : tkr,
        'item' : 'marketcap',
        'start_date' : start_date,
        'page_number' : '01'
    }
    response = requests.get(request_url, params=query_params, auth=(api_username, api_password))
    if response.status_code == 401:
        print("Unauthorized! Check your username and password."); exit()
    np = response.json()['total_pages']
    data = response.json()['data']
    values = []
    dates = []
    page = 2
    for row in data:
        cp = row["value"]
        values.append(cp)
        dt = row["date"]
        dates.append(dt)
    while page <= np:
        query_params = {
            'ticker' : tkr,
            'item' : 'marketcap',
            'start_date' : start_date,
            'page_number' : str(page)
        }
        page = page + 1
        response = requests.get(request_url, params=query_params, auth=(api_username, api_password))
        data = response.json()['data']
        for row in data:
            cp = row["value"]
            dt = row["date"]
            values.append(cp)
            dates.append(dt)

    values.reverse()
    dates.reverse()
    return (values,dates)

def getAV(tkr):
    request_url = base_url + "/historical_data"
    query_params = {
        'ticker' : tkr,
        'item' : 'adj_volume',
        'start_date' : start_date,
        'page_number' : '01'
    }
    response = requests.get(request_url, params=query_params, auth=(api_username, api_password))
    if response.status_code == 401:
        print("Unauthorized! Check your username and password."); exit()
    np = response.json()['total_pages']
    data = response.json()['data']
    values = []
    dates = []
    page = 2
    for row in data:
        cp = row["value"]
        values.append(cp)
        dt = row["date"]
        dates.append(dt)
    while page <= np:
        query_params = {
            'ticker' : tkr,
            'item' : 'adj_volume',
            'start_date' : start_date,
            'page_number' : str(page)
        }
        page = page + 1
        response = requests.get(request_url, params=query_params, auth=(api_username, api_password))
        data = response.json()['data']
        for row in data:
            cp = row["value"]
            dt = row["date"]
            values.append(cp)
            dates.append(dt)

    values.reverse()
    dates.reverse()
    return (values,dates)


def compMC(val):
    if val == "na" or val == "nm" or val == "Na":
        return "NA"
    elif val < (1000 * 1000000):
        return "S"
    elif val < (10000 * 1000000):
        return "M"
    else:
        return "L"


def calcSSMA(list):
    sum = 0
    if (len(list) < 50):
        return 'NA'
    for elem in list:
        sum = sum + elem
    res = sum / (len(list))
    return str(res)

def calcLSMA(list):
    sum = 0
    if (len(list) < 200):
        return 'NA'
    for elem in list:
        sum = sum + elem
    res = sum / (len(list))
    return res

def calcSEMA(x, list, idx, nS, p):
    if (len(list) < nS):
        return 'NA'
    k = 2/(nS+1)
    prev = 0
    if list[idx] != 'NA':
        prev = float(list[idx])
    else:
        prev = float(p)
    res = k * prev + (1-k) * x
    pSema = res
    return str(res)

def calcLEMA(x, list, idx, nL, p):
    if (len(list) < nL):
        return 'NA'
    k = 2/(nL+1)
    prev = 0
    if list[idx] != 'NA':
        prev = float(list[idx])
    else:
        prev = float(p)
    res = k * prev + (1-k) * x
    pLema = res
    return str(res)

def infCalc(tkr):
    request_url = base_url + "/historical_data"
    query_params = {
        'ticker' : tkr,
        'item' : 'adj_close_price',
        'start_date' : start_date,
        'page_number' : '01'
    }
    response = requests.get(request_url, params=query_params, auth=(api_username, api_password))
    if response.status_code == 401:
        print("Unauthorized! Check your username and password."); exit()
    np = response.json()['total_pages']
    data = response.json()['data']
    values = []
    dates = []
    page = 2
    for row in data:
        cp = row["value"]
        values.append(cp)
        dt = row["date"]
        dates.append(dt)
    while page <= np:
        query_params = {
            'ticker' : tkr,
            'item' : 'adj_close_price',
            'start_date' : start_date,
            'page_number' : str(page)
        }
        page = page + 1
        response = requests.get(request_url, params=query_params, auth=(api_username, api_password))
        data = response.json()['data']
        for row in data:
            cp = row["value"]
            dt = row["date"]
            values.append(cp)
            dates.append(dt)

    values.reverse()
    dates.reverse()
    nS = 50
    nL = 200
    shortArray = []
    longArray = []
    ssmaList = []
    lsmaList = []
    semaList = []
    lemaList = []
    
    pSema = 0
    pLema = 0
    pSema2 = 0
    pLema2 = 0
    
    i = -1
    #print (tkr + ' ' + str(len(values)))
    for elem in values:
        # print(elem)
        if len(shortArray) < nS:
            shortArray.append(elem)
        else:
            shortArray.pop(0)
            shortArray.append(elem)
        
        if len(longArray) < nL:
            longArray.append(elem)
        else:
            longArray.pop(0)
            longArray.append(elem)
        
        ssma = calcSSMA(shortArray)
        ssmaList.append(ssma)
        
        lsma = calcLSMA(longArray)
        lsmaList.append(lsma)
        
        pSema2 = pSema
        pLema2 = pLema
        pSema = ssma
        pLema = lsma
    
        
        sema = calcSEMA(elem, semaList, i, nS, pSema2)
        semaList.append(sema)
        
        lema = calcLEMA(elem, lemaList, i, nL, pLema2)
        lemaList.append(lema)
        

        i = i + 1
    return (ssmaList, lsmaList, semaList, lemaList, dates, values)




workbook = xlsxwriter.Workbook('result.xlsx')
worksheet = workbook.add_worksheet()
bold = workbook.add_format({'bold':True})
worksheet.set_column('A:A', 18)
worksheet.set_column('B:B', 32)
worksheet.set_column('D:D', 15)
worksheet.set_column('E:E', 15)
worksheet.set_column('F:F', 15)
worksheet.set_column('G:G', 18)
worksheet.set_column('H:H', 18)
worksheet.set_column('I:I', 22)
worksheet.set_column('J:J', 22)
worksheet.set_column('K:K', 22)
worksheet.set_column('L:L', 22)



worksheet.write('A1','DATE',bold)
worksheet.write('B1','Company name',bold)
worksheet.write('C1','Ticker',bold)
worksheet.write('D1', 'Market Cap', bold)
worksheet.write('E1', 'Company Size', bold)
worksheet.write('F1', 'SIC Code', bold)
worksheet.write('G1', 'Adj Closing Price', bold)
worksheet.write('H1', 'adj volume', bold)
worksheet.write('I1', 'SMA 50', bold)
worksheet.write('J1', 'SMA 200', bold)
worksheet.write('K1', 'EMA 50', bold)
worksheet.write('L1', 'EMA 200', bold)

c = 1
def holisym(company, tkr, count, DD):
            vlist1,dlist1 = getMC(tkr)
            vlist2,dlist2 = getAV(tkr)
            ssmaList, lsmaList, semaList, lemaList,dlist3,vlist3 = infCalc(tkr)
            dtl = getED(dlist1,dlist2)
            dtlist = getED(dtl,dlist3)
            sic =  getSic(tkr)
            mcidx = 0
            avidx = 0
            cpidx = 0
            for z in listofdates:
                if z in dlist1 or z in dlist2 or z in dlist3:
                    if z in dlist1 and z not in dlist2:
                        mcidx = mcidx + 1
                    else:
                        f = z.split('-')
                        g = int(z[0:4]);
                        DD[g % 2007] = DD[g % 2007] + 1
                        worksheet.write(count, 0, z)
                        worksheet.write(count, 1, company)
                        worksheet.write(count, 2, tkr)
                        if (z == dlist1[mcidx]):
                            worksheet.write(count, 3, vlist1[mcidx])
                            worksheet.write(count, 4, compMC(vlist1[mcidx]))
                            mcidx = mcidx + 1
                        else:
                            worksheet.write(count, 3, "NA")
                            worksheet.write(count, 4, "NA")
                        worksheet.write(count, 5, sic)
                        if (z == dlist2[avidx]):
                            worksheet.write(count, 7, vlist2[avidx])
                            avidx = avidx + 1
                        else:
                            worksheet.write(count, 7, "NA")
                        if (z == dlist3[cpidx]):
                                worksheet.write(count, 6, vlist3[cpidx])
                                worksheet.write(count, 8, ssmaList[cpidx])
                                worksheet.write(count, 9, lsmaList[cpidx])
                                worksheet.write(count, 10, semaList[cpidx])
                                worksheet.write(count, 11, lemaList[cpidx])
                                cpidx = cpidx + 1
                        else:
                                worksheet.write(count, 6, "NA")
                                worksheet.write(count, 8, "NA")
                                worksheet.write(count, 9, "NA")
                                worksheet.write(count, 10, "NA")
                                worksheet.write(count, 11, "NA")
                        count = count+1
            return count

AD = [0,0,0,0,0,0,0,0,0,0,0,0]
ID = [0,0,0,0,0,0,0,0,0,0,0,0]
GD = [0,0,0,0,0,0,0,0,0,0,0,0]

d = holisym("APPLE","AAPL",c,AD)
e = holisym("INTL BUSINESS MACHINES","IBM", d, ID)
f = holisym("GENERAL MTRS CO","GM", e, GD)


workbook.close()

end = time.time()

elapsed = end - start

print("This program took " + str(round(elapsed,2)) + " seconds to run")
print ("The numbers of API calls used today is: " + str(getCalls()))
print("Today's limit is: " + str(getLim()))
