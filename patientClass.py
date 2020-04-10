import pandas as pd
import os
import re, string


def get_Patient_Distribute_Text(msg):

    Datelist = re.findall(r'\b\d+\b', msg)
    if len(Datelist)>=2:
        filename = getfilename(Datelist)
        if filename == '':
            return 1
        else:
            df = patientDisByDate(msg, filename)
            return str(df)

    if "in" in msg:
        df = patientDisByRegion(msg)
        return str(df)

    df = patientDisNew()
    # pd.set_option('display.max_rows', 50)
    message = "The latest data in my database is only updated to March 27！\n\n"
    df = message + str(df)
    return df


def getfilename(list):
    if int(list[-2]) >= 1 and int(list[-2]) <= 12 and int(list[-1]) >= 1 and int(list[-1]) <= 31:
        if len(list[-2]) == 1:
            list[-2] = "0" + list[-2]
        if len(list[-1]) == 1:
            list[-1] = "0" + list[-1]
        filename = "covid20_daily_reports/" + list[-2] + "-" + list[-1] + "-2020.csv"
        return filename


# All countries' patient distribute in 03.27
def patientDisNew():

    filename = "covid20_daily_reports/03-27-2020.csv"
    isExists = os.path.exists(filename)
    if not isExists:
        return 1

    df = pd.read_csv(filename)
    pd.set_option('max_colwidth', 10)
    df = df[['Confirmed', 'Deaths', 'Recovered']].groupby(df['Country_Region']).sum()
    df.columns = ['Confirmed', 'Deaths', 'Healed']
    return df


# Get patient distribute according to date
def patientDisByDate(msg, filename):

    isExists = os.path.exists(filename)
    if not isExists:
        return 1

    df = pd.read_csv(filename)
    pd.set_option('max_colwidth', 10)
    strCol = ' '.join(df.columns.values)

    if "Country/Region" in strCol:
        df = getFirstConditionValue(msg, df)
    else:
        df = getSecondConditionValue(msg, df)

    return df

# 1.22 - 3.22 csv files
def getFirstConditionValue(msg, df):
    if "China" in msg or "china" in msg:
        df = df.loc[df.iloc[:, 1].isin(['Mainland China', 'Hong Kong', 'Taiwan'])]
        df = df[['Province/State', 'Confirmed', 'Deaths', 'Recovered']]
        df.columns = ['Province', 'Confirmed', 'Deaths', 'Healed']
        df.set_index(["Province"], inplace=True)
        return df

    if "about" in msg:
        list = msg.split(' ')
        n = list.index('about')
        df = df.loc[df.iloc[:, 1].isin([list[n + 1]])]
        if df.empty == True:
            return 1

        df = df[['Province/State', 'Confirmed', 'Deaths', 'Recovered']]
        df.columns = ['Region', 'Confirmed', 'Deaths', 'Healed']
        df.set_index(["Region"], inplace=True)
        return df

    if "country" in msg:
        df = df[['Confirmed', 'Deaths', 'Recovered']].groupby(df['Country/Region']).sum()
        df.columns = ['Confirmed', 'Deaths', 'Healed']
        return df

# 3.23 - 3.27 csv files
def getSecondConditionValue(msg, df):

    if "China" in msg or "china" in msg:
        df = df.loc[df.iloc[:, 3].isin(['China', 'Hong Kong', 'Taiwan*'])]
        df = df[['Province_State', 'Confirmed', 'Deaths', 'Recovered']]
        df.columns = ['Province', 'Confirmed', 'Deaths', 'Healed']
        df.set_index(["Province"], inplace=True)
        return df

    if "about" in msg:
        list = msg.split(' ')
        n = list.index('about')
        df = df.loc[df.iloc[:, 3].isin([list[n + 1]])]
        if df.empty == True:
            return 1

        df = df[['Province_State', 'Confirmed', 'Deaths', 'Recovered']]
        df.columns = ['Region', 'Confirmed', 'Deaths', 'Healed']
        df.set_index(["Region"], inplace=True)
        return df

    if "country" in msg:
        df = df[['Confirmed', 'Deaths', 'Recovered']].groupby(df['Country_Region']).sum()
        df.columns = ['Confirmed', 'Deaths', 'Healed']
        return df


# Get patient distribute according to region
def patientDisByRegion(msg):

    exclude = set(string.punctuation)
    msg = ''.join(ch for ch in msg if ch not in exclude)

    list = msg.split(' ')
    n = list.index('in')

    regionlist = []
    for i in range(n+1, len(list)):
        list[i] = list[i].capitalize()
        regionlist.append(list[i])
    strProvince = ' '.join(regionlist)
    # strProvince = ' '.join(list[i] for i in range(n+1, len(list)))

    df1 = pd.read_csv("covid20_time_report/time_series_19-covid-Confirmed_archived_0325.csv")
    df1 = df1.loc[df1.iloc[:, 0] == strProvince]
    if df1.empty == True:
        # print("We don't have data!")
        return 2

    df1 = pd.melt(df1)

    df2 = pd.read_csv("covid20_time_report/time_series_19-covid-Deaths_archived_0325.csv")
    df2 = df2.loc[df2.iloc[:, 0] == strProvince]
    df2 = pd.melt(df2)

    df3 = pd.read_csv("covid20_time_report/time_series_19-covid-Recovered_archived_0325.csv")
    df3 = df3.loc[df3.iloc[:, 0] == strProvince]
    df3 = pd.melt(df3)

    df = pd.merge(df1, df2, on='variable')
    df = pd.merge(df, df3, on='variable')

    df = df.drop([0, 1, 2, 3], axis=0, inplace=False)
    df.columns = ['Date', 'Confirmed', 'Deaths', 'Healed']
    df.set_index(["Date"], inplace=True)
    return df