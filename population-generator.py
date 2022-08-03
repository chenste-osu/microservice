import sys
from subprocess import call
import requests as req
import csv

key = '675a9a066ee3188c71ef659107e5c520579218fe'

stateList = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 
            'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 
            'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'] 

stateFIPSDict = {"AK": "02", "AL": "01", "AR": "05", "AZ": "04", "CA": "06", "CO": "08", "CT": "09", "DC": "11", "DE": "10",
            "FL": "12", "GA": "13", "HI": "15", "IA": "19", "ID": "16", "IL": "17", "IN": "18", "KS": "20", "KY": "21",
            "LA": "22", "MA": "25", "MD": "24", "ME": "23", "MI": "26", "MN": "27", "MO": "29", "MS": "28", "MT": "30",
            "NC": "37", "ND": "38", "NE": "31", "NH": "33", "NJ": "34", "NM": "35", "NV": "32", "NY": "36", "OH": "39",
            "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45", "SD": "46", "TN": "47", "TX": "48", "UT": "49",
            "VA": "51", "VT": "50", "WA": "53", "WI": "55", "WV": "54", "WY": "56"} 

stateFullName = {"AK": "Alaska", "AL": "Alabama", "AR": "Arkansas", "AZ": "Arizona", "CA": "California",
                "CO": "Colorado", "CT": "Connecticut", "DC": "District of Columbia",
                "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "IA": "Iowa",
                "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "KS": "Kansas", "KY": "Kentucky",
                "LA": "Louisiana", "MA": "Massachusetts", "MD": "Maryland", "ME": "Maine", "MI": "Michigan",
                "MN": "Minnesota", "MO": "Missouri", "MS": "Mississippi", "MT": "Montana",
                "NC": "North Carolina", "ND": "North Dakota", "NE": "Nebraska", "NH": "New Hampshire",
                "NJ": "New Jersey", "NM": "New Mexico", "NV": "Nevada", "NY": "New York", "OH": "Ohio",
                "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
                "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
                "VA": "Virginia", "VT": "Vermont", "WA": "Washington", "WI": "Wisconsin",
                "WV": "West Virginia", "WY": "Wyoming"}

yearList = [2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019]

def getPopulation(stateInput, yearInput):
    '''
    This method makes the API call to api.census.gov by concatenating the specified year and state into an URL.
    Returns the population size.
    '''
    url = str("https://api.census.gov/data/" + str(yearInput) + "/acs/acs1?get=NAME,B01003_001E&for=state:" + stateFIPSDict[stateInput] + "&key=" + key)
    response = req.get(url)
    result = response.json()
    popSize = result[1][1]
    return popSize

def writeOutput(dataList):
    '''Write data to output.csv'''
    with open('output.csv', 'w', newline='') as file: 
        writer = csv.writer(file)
        writer.writerow(["input_year","input_state","output_population_size"])
        writer.writerow([str(dataList[1]), str(dataList[0]), str(dataList[2])])

if len(sys.argv)>= 2: #This if-else checks if there is a second argument.
    csvFilearg = sys.argv[1]
    #Parse CSV file:
    with open(csvFilearg) as csvFile: 
        csvData = csv.reader(csvFile)
        next(csvData, None)
        for row in csvData: #Parse the 2nd row of the CSV file. Save the year and state data.
            yearInput = str(row[0])
            stateInput = str(row[1])
        result = getPopulation(stateInput, yearInput) #Get the population size by making an API call.

        #Create output.csv:
        if csvFile == "con-pop-request.csv":
            with open('con-pop-reply.csv', 'w', newline='') as file: 
                writer = csv.writer(file)
                writer.writerow(["input_year","input_state","output_population_size"])
                writer.writerow([str(yearInput), str(stateInput), str(size)])
            print('Output written to con-pop-reply.csv')
        
        else:
            dataList = [stateInput, yearInput, result]
            writeOutput(dataList)
    
else: #If there is no .csv argument, render the GUI.
    import tkinter as tk

    #Start tkinter GUI:
    window = tk.Tk()
    window.geometry("400x400")
    label = tk.Label(text="Population Generator")
    label.pack()

    #Dropdown for selecting US state:
    state = tk.StringVar(window)
    state.set('Select a State')
    dropdown1 = tk.OptionMenu(window, state, *stateList)
    dropdown1.pack()

    #Dropdown for selecting census year:
    year = tk.StringVar(window)
    year.set('Select a census year')
    dropdown2 = tk.OptionMenu(window, year, *yearList)
    dropdown2.pack()

    #Functions for button press:
    def updateOutputGUI(dataList, content = False):
        '''Function that updates the GUI to display the population size and writes results to output.csv after the program receives API response'''
        outputArea["text"] = 'Population: '
        outputArea["text"] += str(dataList[2])
        if content is not False:
            contentOutputArea["text"] = 'Information: \n'
            contentOutputArea["text"] += content
        writeOutput(dataList)

    def getPopulationButton():
        '''Function to make an API call when the user clicks the 'Get Population Data' button. '''
        stateInput = state.get()
        yearInput = year.get()
        if state != 'Select a State' and year != 'Select a census year': 
            result = getPopulation(stateInput, yearInput)
            dataList = [stateInput, yearInput, result]
            updateOutputGUI(dataList)

    def getContentButton():
        '''Function to make an API call when the user clicks the 'Get Population Data' button. '''
        stateInput = state.get()
        yearInput = year.get()
        reqString = str(stateFullName[stateInput])+';'+str(yearInput)
        requestContent(stateInput, yearInput, reqString)

    def requestContent(stateInput, yearInput, inputString):
        if state != 'Select a State' and year != 'Select a census year':
            with open('pop-con-request.csv', 'w', newline='') as file: 
                writer = csv.writer(file)
                writer.writerow(["input_keywords"])
                writer.writerow([inputString])
            call(["python", "content-generator.py", "pop-con-request.csv"])
            parseResponse(stateInput, yearInput)

    def parseResponse(stateInput, yearInput):
        with open('pop-con-reply.csv') as replyFile: 
            csvData = csv.reader(replyFile)
            next(csvData, None)
            for row in csvData: #Parse the 2nd row of the CSV file. Save the year and state data.
                content = str(row[1][1:-1])
        result = getPopulation(stateInput, yearInput)
        dataList=[stateInput, yearInput, result]
        updateOutputGUI(dataList, content)

    #Request population button:
    button = tk.Button(window, text="Get Population Size ONLY", command=getPopulationButton)
    button.pack()

    #Request content for selected State and Year:
    button = tk.Button(window, text="Get Population size AND Generate a paragraph with your selected State/Year", wraplength=400, command=getContentButton)
    button.pack()

    #Output area for GUI:
    outputArea = tk.Label(window, text = 'Population: ')
    outputArea.pack()

    contentOutputArea = tk.Label(window, wraplength=400)
    contentOutputArea.pack()

    window.mainloop()
