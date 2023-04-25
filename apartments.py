#https://jenningsgroup.com/for-rent/

import requests
from bs4 import BeautifulSoup
import pandas as pd
import pygsheets

gs = pygsheets.authorize(service_file='C:\My Files\projects\creds.json')
data = []

def getDataJennings():
    URL = "https://jenningsgroup.appfolio.com/listings?1671594116509&filters%5Bproperty_list%5D=Website%20-%20All%20Listings&theme_color=%23676767&filters%5Border_by%5D=date_posted&iframe_id=af_iframe_0"
    page = requests.get(URL)

    soup = BeautifulSoup(page.text, "html.parser")

    apartments = soup.findAll("div", class_="listing-item result js-listing-item")
    #apartments = soup.findAll("div", class_="listings js-listings-container")
    #apartments = soup.findAll("div", class_="listing-item__body")
    
    for title in apartments:
        item = {}
        columns = title.findAll("div", class_="detail-box__item")
        

        for result in columns:
            col, res = result.text.strip().split("\n")
            item[col] = res

        if item["Bed / Bath"][0] != "S" and int(item["Bed / Bath"][0]) >= 3:
            if item["Available"] > "8/1/22" and item["Available"] != "Now":
                location = title.find("span", class_="u-pad-rm js-listing-address")
                item["Location"] = location.text.strip() 
                
                item["URL"] = "https://jenningsgroup.appfolio.com" + title.find("a", class_="btn btn-secondary js-link-to-detail")['href']
                data.append(item)
    return data

def getDataAGhousing():

    URL = "https://www.agcampushousing.com/vacancies?city=Eugene&beds=3%2C4%2C5%2B"
    page = requests.get(URL)

    soup = BeautifulSoup(page.text, "html.parser")

    apartments = soup.findAll("div", class_="listings-container")
    print(page.text)
    for title in apartments:
        item = {}
        columns = title.findAll("div", class_="listing-section")
        

        for result in columns:
            col, res = result.text.strip().split("\n")
            item[col] = res

        # if item["Bed / Bath"][0] != "S" and int(item["Bed / Bath"][0]) >= 3:
        #     if item["Available"] > "8/1/22" and item["Available"] != "Now":
        #         location = title.find("span", class_="u-pad-rm js-listing-address")
        #         item["Location"] = location.text.strip() 
                
        #         item["URL"] = "https://jenningsgroup.appfolio.com" + title.find("a", class_="btn btn-secondary js-link-to-detail")['href']
        #         data.append(item)

    return data

def export_dataGS(data):
    sheet = gs.open('apartments')
    worksheet = sheet[0]
    df = pd.DataFrame(data)
    worksheet.set_dataframe(df, (1,1))

def export_dataMS(data):
    df = pd.DataFrame(data)
    df.to_excel(r'C:\My Files\projects\data.xlsx', index=False)

def export_new_dataMS(data):
    path = r'C:\My Files\projects\data.xlsx'
    df_excel = pd.read_excel(path)
    
    new = []
    for item in data:
        if item not in df_excel.values:
            if item['Location'] not in df_excel.values:
                new.append(item)
            #update to a property
        
    df_new = pd.DataFrame(new)

    if not df_new.empty:
        print("new records found")
        frame = pd.concat([df_excel, df_new])
        frame.to_excel(r'C:\My Files\projects\data.xlsx', index=False)
    

if __name__ == '__main__':
    data = getDataJennings()
    export_new_dataMS(data)
    #export_dataMS(data)
