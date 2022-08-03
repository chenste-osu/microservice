# CS362 Sprint 3 - Coding Assignment - Content Generator
# Written by Steven Chen


import tkinter as tk
import csv
import sys
import os.path
import time
from subprocess import call
import wikipedia
import requests
from bs4 import BeautifulSoup


class ContentGenerator:
    """class that contains the main functions for the content generator GUI"""

    def __init__(self, master):
        
        self.master = master
        master.title("Content Generator")

        self.p_var = tk.StringVar()
        self.s_var = tk.StringVar()
        self.csv_var = tk.StringVar()
        self.current_text = tk.StringVar()
        self.pop_var = tk.StringVar()

        self.p_label = tk.Label(master, text="Primary Keyword:")
        self.s_label = tk.Label(master, text="Secondary Keyword:")
        self.p_entry = tk.Entry(master, textvariable=self.p_var)
        self.s_entry = tk.Entry(master, textvariable=self.s_var)

        self.io_label = tk.Label(master, text="Input/Output Status:")
        self.csv_result = tk.Label(master, textvariable=self.csv_var, borderwidth=2, relief="flat")

        self.sub_btn = tk.Button(master, text="Submit", command=self.keyword_submit)
        self.save_btn = tk.Button(master, text="Save as .csv", command=self.save_csv)
        self.pop_btn = tk.Button(master, text="Get Recent State Population Data", command=self.pop_submit)

        self.pop_label = tk.Label(master, text="", borderwidth=2, relief="flat")

        self.output_display = tk.Text(master, height=30, width=50, wrap=tk.WORD)

        self.stateDict = {"AK": "Alaska", "AL": "Alabama", "AR": "Arkansas", "AZ": "Arizona", "CA": "California",
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

    def display_text(self, display_text):
        """function takes a string as a parameter and displays it in the GUI text box"""
        self.display_clear()
        self.output_display.insert(tk.END, display_text)

    def display_de_error(self, error_text):
        """displays the error string from the disambiguation error exception thrown by the wikipedia API"""
        self.display_clear()
        self.output_display.insert(tk.END, "Your Primary Keyword wasn't specific enough." + "\n")
        self.output_display.insert(tk.END, error_text)

    def display_clear(self):
        """clears the GUI display textbox"""
        self.output_display.delete("1.0", tk.END)

    def display_csv_result(self, result_string):
        """takes a string and displays that as the csv_result label to indicate the result of the i/o operation"""
        self.csv_var.set(result_string)
        self.csv_result.configure(relief="groove")

    def hide_pop(self):
        """hides the label that contains the population data for the searched state"""
        self.pop_label["text"] = ""
        self.pop_label.configure(relief="flat")

    def hide_csv_result(self):
        """hides the label that contains the result for an input/output operation"""
        self.csv_var.set("")
        self.csv_result.configure(relief="flat")

    def wiki_search(self, primary):
        """uses wikipedia's search to return a list of up to 5 results based on primary keyword"""
        if primary == "New York":
            primary = "New York (State)"
        wiki_results = wikipedia.search(primary, results=5, suggestion=True)

        if not wiki_results[0]:
            self.display_text("Article could not be found based on primary keyword.")
            self.current_text.set("")
            return

        return wiki_results

    def find_article(self, article_title):
        """takes the first result after running the wiki_search function then searches wikipedia for the article page
        and returns the html soup of the requested article"""
        found_page = wikipedia.page(title=article_title, auto_suggest=False)

        target_url = found_page.url
        response = requests.get(target_url)
        soup = BeautifulSoup(response.content, features="lxml")

        # remove all the citation bracket things (example: [4])
        a_tags = soup.find_all("a")
        for a_t in a_tags:
            if "[" and "]" in a_t.text:
                a_t.clear()

        return soup

    def find_paragraph(self, article_soup, primary, secondary):
        """searches the html soup obtained from the find_article function and attempts to find a paragraph containing
        both the primary and secondary keywords"""
        paragraphs = article_soup.find_all("p")

        for p in paragraphs:
            if primary.lower() in p.text.lower() and secondary.lower() in p.text.lower():
                self.display_text(p.text)
                self.current_text.set(p.text)
                return True

        self.display_text("Paragraph could not be found containing the specified keywords.")
        self.current_text.set("")
        return False

    def keyword_submit(self, primary=None, secondary=None):
        """invoked when user presses the submit keyword button.
        looks up the wikipedia article and searches for a paragraph with both primary and secondary keywords
        optionally can pass primary and secondary keyword as parameters"""
        self.display_clear()
        self.hide_csv_result()
        self.hide_pop()

        if primary is None:
            primary = self.p_var.get()
        if secondary is None:
            secondary = self.s_var.get()

        if primary == "":
            self.display_text("Primary keyword is blank.")
            return

        # if primary is a state code, converts it to the full state name
        if primary in self.stateDict:
            primary = self.convert_state_code(primary)

        # gets a list of wiki searches based on primary
        search_results = self.wiki_search(primary)
        if not search_results[0]:
            self.display_text("Article could not be found based on primary keyword.")
            self.current_text.set("")
            return

        # finds the wikipedia article, extracts html soup of article, then finds the paragraph from soup
        try:
            article_soup = self.find_article(search_results[0][0])
            found_p = self.find_paragraph(article_soup, primary, secondary)
            # if "primary" is a state, then requested population data button is shown
            self.check_state(self.p_var.get(), primary, found_p, article_soup)

        except wikipedia.exceptions.DisambiguationError as de:
            self.display_de_error(format(de))

    def start_csv(self):
        """checks for con-input.csv upon starting the GUI.
        if con-input.csv is found, updates the csv_result and enters the keywords from the csv file into the entry boxes
        then submits the keyword query and displays the result"""
        if os.path.isfile("con-input.csv"):
            with open("con-input.csv", "r", encoding="utf-8") as csv_start:
                start_reader = csv.reader(csv_start)
                self.open_csv(start_reader)
                self.display_csv_result("con-input.csv loaded")
        else:
            self.display_csv_result("con-input.csv not found!")

    def open_csv(self, open_reader):
        """takes a csv_reader object as a parameter, parses for the input_keywords and then finds
        the corresponding wikipedia article and paragraph. """
        self.get_keywords(open_reader)
        self.keyword_submit()

    def save_csv(self, executed_filename=None):
        """saves keywords and whatever is in "self.current_text" into a csv file"""
        if executed_filename == "pop-con-request.csv":
            save_filename = "pop-con-reply.csv"
            headers = ["input_keywords", "output_content"]
        else:
            save_filename = "con-output.csv"
            headers = ["input_keywords", "output_content", "population"]

        i_kw = self.p_var.get() + ";" + self.s_var.get()
        o_c = '"' + self.current_text.get() + '"'
        o_p = self.pop_var.get()

        with open(save_filename, "w", encoding="utf-8") as csv_output:
            csv_writer = csv.writer(csv_output, delimiter=",", lineterminator='\n')
            csv_writer.writerow(headers)
            csv_writer.writerow([i_kw, o_c, o_p])

        self.display_csv_result(save_filename + " written")

    def get_keywords(self, keyword_reader):
        """takes a csv reader object as a parameter and extracts the input_keywords.
        updates the corresponding class attributes"""
        row_list = []
        for row in keyword_reader:
            row_list.append(row)

        raw_keywords = row_list[1][0]
        split_keywords = raw_keywords.split(";")

        primary_keyword = split_keywords[0]
        secondary_keyword = split_keywords[1]

        self.p_var.set(primary_keyword)
        self.s_var.set(secondary_keyword)

    def get_population(self, population_reader):
        """takes a csv reader object as a parameter and extracts the population number.
        updates the corresponding class attributes"""
        row_list = []
        for row in population_reader:
            row_list.append(row)

        self.pop_var.set(row_list[1][2])
        self.pop_label["text"] = "Population: " + row_list[1][2]
        self.pop_label.configure(relief="ridge")

    def convert_state_code(self, primary):
        """converts a state code into the full state name"""
        if primary in self.stateDict:
            return self.stateDict[primary]

    def check_state(self, p_var, primary, found_p, article_soup):
        """if the primary keyword is a state code, a button becomes available to get recent population data
        otherwise, the button is removed
        if the paragraph containing the census year is not found, the first paragraph will be displayed instead"""
        if p_var in self.stateDict:
            self.pop_btn.grid(row=0, column=2)
            if not found_p:
                self.find_paragraph(article_soup, primary, "")
            return True
        else:
            self.pop_btn.grid_remove()
            self.pop_var.set("")
            self.hide_pop()
            return False

    def pop_submit(self):
        """invoked when the user clicks the button to request recent population data
        saves "con-pop-request.csv" then runs "python population-generator.py con-pop-request.csv"
        then reads "con-pop-reply.csv" and displays the recent population data"""
        self.save_request()
        call(["python", "population-generator.py", "con-pop-request.csv"])
        time.sleep(2)
        self.open_con_pop()
        self.pop_btn.grid_remove()

    def save_request(self):
        """function is invoked when the user requests population data for a state
        saves the current state (primary keyword) into a csv file compatible with population-generator"""
        headers = ["input_year", "input_state"]
        i_y = "2019"
        i_s = self.p_var.get()

        with open("con-pop-request.csv", "w", encoding="utf-8") as pop_request:
            csv_writer = csv.writer(pop_request, delimiter=",", lineterminator='\n')
            csv_writer.writerow(headers)
            csv_writer.writerow([i_y, i_s])

    def open_con_pop(self):
        """searches for output.csv from population-generator in the same directory which is generated after a request to
        population-generator is made then updates the corresponding class attribute"""
        if os.path.isfile("output.csv"):
            with open("output.csv", "r", encoding="utf-8") as pop_reply:
                pop_reply_reader = csv.reader(pop_reply)
                self.get_population(pop_reply_reader)

        else:
            self.display_csv_result("output.csv not found!")


if __name__ == "__main__":
    root = tk.Tk()

    # command line execution
    if len(sys.argv) >= 2:
        if sys.argv[1] == "con-input.csv" or sys.argv[1] == "pop-con-request.csv":
            congen = ContentGenerator(root)
            with open(sys.argv[1], "r", encoding="utf-8") as csv_input:
                csv_reader = csv.reader(csv_input)
                congen.open_csv(csv_reader)
                congen.save_csv(sys.argv[1])

        else:
            print("This type of input file is not accepted")

    # render GUI
    else:
        root.geometry("650x525")

        congen = ContentGenerator(root)

        # primary keyword label
        congen.p_label.grid(row=0, column=0)
        congen.p_entry.grid(row=0, column=1)
        root.grid_rowconfigure(0, minsize=30)

        # secondary keyword label
        congen.s_label.grid(row=1, column=0)
        congen.s_entry.grid(row=1, column=1)
        root.grid_rowconfigure(1, minsize=30)
        root.grid_columnconfigure(1, minsize=140)

        # population label button
        congen.pop_label.grid(row=1, column=2)

        # keyword submit button
        congen.sub_btn.grid(row=2, column=0)
        root.grid_rowconfigure(2, minsize=30)

        # paragraph text display
        congen.output_display.grid(row=3, column=2)

        # save as csv button
        congen.save_btn.grid(row=4, column=2)
        # i/o show text label
        congen.io_label.grid(row=4, column=0)
        # csv file result label
        congen.csv_result.grid(row=4, column=1)

        # loads con-input.csv upon program start
        congen.start_csv()

        root.mainloop()
