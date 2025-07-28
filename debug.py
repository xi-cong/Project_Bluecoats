import csv
import requests 
from bs4 import BeautifulSoup
import pandas as pd
from pprint import pprint
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from IPython.display import display




def debug1():
    url_show = "https://www.dci.org/scores/recap/2019-dci-world-championship-finals/"
    resp = requests.get(url_show, headers={"User-Agent": "Mozilla/5.0"}).text
    soup = BeautifulSoup(resp, "html.parser")
    show_time_location = soup.select_one("div.score-date-location.justify-center")

    show_time_location = show_time_location.get_text(separator="|", strip=True) #type:ignore
    show_time = show_time_location.split("|")[0]
    show_location = show_time_location.split("|")[1]

            # print(show_location)
            # print(show_time)

            # find the competition levels in this corp
    levels = soup.find_all("h2", class_="h4")
    levels = [level.get_text(strip=True) for level in levels]
            # print(levels)

            # find the flat cells in the table
    recap_tbls = soup.find_all("div", class_="recap-tbl responsive-tbl")
    for recap_tbl in recap_tbls:
        table_cols = recap_tbl.find_all("td")
        flat_cells = [col.get_text(separator="|", strip=True) for col in table_cols] # tempo
        
        mark_index_list=[]
        for index, cell in enumerate(flat_cells):
            output = []
            # print(f"Row {index}: {cell}")
            # if index > 200:
            #     break
            if cell == "Total":
                mark_index_list.append(index)
                print(index)
        


        cols_cells = flat_cells[:mark_index_list[0]]
        corp_cells = flat_cells[mark_index_list[0]+1:]
    
        for index, cell in enumerate(cols_cells):
            if cell.count("|") > 6:
                output.append(cell)    

        for index, cell in enumerate(corp_cells):
            if "|" not in cell and "-" not in cell: # finds corp name
                output.append(cell)
            if cell.count("|") > 6: # finds rows with the concatenated scores
                output.append(cell)
            if cell == "--": # locate sub final and final scores 
                try: 
                    output.append(corp_cells[index-1])
                    output.append(corp_cells[index+1])
                except:
                    output.append(["N/A"])
        
        pprint(output)
        
    print(f"successfully extracted valid cells shows at {show_location} on {show_time}")
    return output

    
    # pprint(output)

# debug1()

def debug2():
    url_show = "https://www.dci.org/scores/recap/2019-dci-world-championship-finals/"
    resp = requests.get(url_show, headers={"User-Agent": "Mozilla/5.0"}).text
    soup = BeautifulSoup(resp, "html.parser")
    show_time_location = soup.select_one("div.score-date-location.justify-center")

    try:
        show_time_location = show_time_location.get_text(separator="|", strip=True) #type:ignore
        show_time = show_time_location.split("|")[0]
        show_location = show_time_location.split("|")[1]

                # print(show_location)
                # print(show_time)

                # find the competition levels in this corp
        levels = soup.find_all("h2", class_="h4")
        levels = [level.get_text(strip=True) for level in levels]
        print(levels)

                # find the flat cells in the table
        recap_tbls = soup.find_all("div", class_="recap-tbl responsive-tbl")

        try:
            output = []
            output.append(show_time)
            output.append(show_location)
            if 'World Class' in levels:
                recap_tbl = recap_tbls[0]
                table_cols = recap_tbl.find_all("td")
                flat_cells = [col.get_text(separator="|", strip=True) for col in table_cols]
                
                mark_index_list=[]
                for index, cell in enumerate(flat_cells):
                    # print(f"Row {index}: {cell}")
                    if cell == "Total":
                        mark_index_list.append(index)

                cols_cells = flat_cells[:mark_index_list[0]]
                corp_cells = flat_cells[mark_index_list[0]+1:]
            
                for index, cell in enumerate(cols_cells):
                    if cell.count("|") > 6:
                        output.append(cell)    

                for index, cell in enumerate(corp_cells):
                    if cell.count("|") > 6:
                        output.append(cell)
                    if "|" not in cell and "-" not in cell:
                        output.append(cell)
                    if cell == "--": # locate sub final and final scores 
                        try: 
                            output.append(corp_cells[index-1])
                            output.append(corp_cells[index+1])
                        except:
                            output.append(["N/A"])
                first_cell = str(output[2])
    
                if "General" not in first_cell:
                    return ["N/A"] # if something goes wrong 
                else:
                    return output # if everything goes right
            else:
                return output # return out put with just time and location
                
            #print(f"successfully extracted valid cells shows at {show_location} on {show_time}")
        except: 
            #print(f"something went wrong at {show_location} on {show_time}")
            return [show_time, show_location, url_show]
        
        
    except: 
        return ["N/A"] # if something goes wrong
    
    # pprint(output)


# print(debug2())

def build_show_cols(list_show_scores):

    show_dict = {}
    show_date = list_show_scores[0]
    show_location = list_show_scores[1]
    show_geneffect_cols = list_show_scores[2]
    show_visual_cols = list_show_scores[3]
    show_music_cols = list_show_scores[4]
    return [show_date, show_location]

def debug3():
    # with open("all_shows_score_recap.csv") as all_scores:
    #     all_scores = list(csv.reader(all_scores))
    
    # list_show_scores = all_scores[21] # use the 2024 final as example list 
    # list_show_scores = [element for element in list_show_scores if element !=""] # removes the extra "" with no data

    all_scores = [['August 10, 2019', 'Indianapolis, IN', 'General Effect|General Effect 1|J. Howell|Rep|Perf|TOT|General Effect 1|M. Stone|Rep|Perf|TOT|General Effect 2|G. Fugett|Rep|Perf|TOT|General Effect 2|N. Jones|Rep|Perf|TOT|TOT', 'Visual|Visual Proficiency|J. Orefice|Cont|Achv|TOT|Visual - Analysis|W. Chumley|Comp|Achv|TOT|Color Guard|J. Sturgeon|CONT|Achv|TOT|TOT', 'Music|Music - Brass|J. Harper|Cont|Achv|TOT|Music - Analysis|J. Davila|Cont|Achv|TOT|Music - Analysis|R. Greenwell|Cont|Achv|TOT|Music - Percussion|J. Prosperie|Cont|Achv|TOT|TOT', 'Blue Devils', '9.900|1|9.800|2|19.700|2|9.900|1|9.900|1|19.800|1|9.800|2|9.800|2|19.600|2|9.750|2|9.750|3|19.500|2|39.300|2', '9.900|1|9.900|1|19.800|1|10.000|1|10.000|1|20.000|1|9.900|2|9.850|2|19.750|2|29.775|1', '9.750|3|9.500|5|19.250|4|9.700|3|9.500|4|19.200|4|9.800|3|9.800|2|19.600|3|9.850|2|10.000|1|19.850|1|29.250|3', '98.325|1', '98.325|1', 'Bluecoats', '9.800|2|10.000|1|19.800|1|9.800|2|9.800|2|19.600|2|9.900|1|9.900|1|19.800|1|9.800|1|9.900|1|19.700|1|39.450|1', '9.800|2|9.800|2|19.600|2|9.900|2|9.900|2|19.800|2|9.700|4|9.800|3|19.500|3|29.450|2', '9.800|2|9.750|2|19.550|2|9.750|2|9.700|2|19.450|2|9.950|1|9.750|3|19.700|2|9.800|3|9.750|3|19.550|3|29.338|1', '98.238|2', '98.238|2', 'Santa Clara Vanguard', '9.500|5|9.650|4|19.150|4|9.650|4|9.750|3|19.400|3|9.600|3|9.500|4|19.100|4|9.550|4|9.650|4|19.200|4|38.425|4', '9.700|3|9.500|5|19.200|4|9.800|3|9.800|3|19.600|3|9.800|3|9.600|4|19.400|4|29.100|3', '9.500|5|9.600|4|19.100|5|9.650|4|9.600|3|19.250|3|9.600|5|9.650|5|19.250|5|9.900|1|9.900|2|19.800|2|29.075|4', '96.600|3', '96.600|3', 'Carolina Crown', '9.700|3|9.700|3|19.400|3|9.400|6|9.650|4|19.050|5|9.500|4|9.700|3|19.200|3|9.600|3|9.800|2|19.400|3|38.525|3', '9.600|4|9.700|3|19.300|3|9.500|6|9.700|4|19.200|5|9.400|7|9.500|5|18.900|6|28.700|5', '9.900|1|9.800|1|19.700|1|9.800|1|9.850|1|19.650|1|9.900|2|9.900|1|19.800|1|9.600|5|9.650|5|19.250|4|29.338|1', '96.563|4', '96.563|4', 'The Cavaliers', '9.600|4|9.500|5|19.100|5|9.700|3|9.600|5|19.300|4|9.400|5|9.300|5|18.700|5|9.500|5|9.550|5|19.050|5|38.075|5', '9.500|5|9.300|6|18.800|6|9.700|4|9.600|5|19.300|4|9.600|5|9.400|6|19.000|5|28.550|6', '9.600|4|9.700|3|19.300|3|9.600|5|9.400|5|19.000|5|9.700|4|9.700|4|19.400|4|9.650|4|9.400|6|19.050|6|28.775|5', '95.400|5', '95.400|5', 'Boston Crusaders', '9.400|6|9.400|6|18.800|6|9.500|5|9.500|6|19.000|6|9.200|6|9.200|6|18.400|6|9.300|7|9.500|6|18.800|6|37.500|6', '9.400|6|9.600|4|19.000|5|9.600|5|9.500|6|19.100|6|10.000|1|9.900|1|19.900|1|29.000|4', '9.400|6|9.400|6|18.800|6|9.300|7|9.250|6|18.550|7|9.400|7|9.600|6|19.000|6|9.200|7|9.200|7|18.400|7|27.988|6', '94.488|6', '94.488|6', 'Blue Knights', '9.300|7|9.300|7|18.600|7|9.300|7|9.200|7|18.500|7|9.100|7|9.050|7|18.150|7|9.400|6|9.200|7|18.600|7|36.925|7', '9.200|8|9.050|8|18.250|8|9.400|7|9.000|10|18.400|8|9.100|9|9.100|8|18.200|9|27.425|9', '9.300|7|9.300|7|18.600|7|9.400|6|9.200|7|18.600|6|9.500|6|9.300|7|18.800|7|9.150|8|8.950|9|18.100|9|27.700|7', '92.050|7', '92.050|7', 'Blue Stars', '9.200|8|9.000|8|18.200|8|9.100|8|9.100|8|18.200|8|8.950|8|8.800|9|17.750|9|9.200|8|9.100|8|18.300|8|36.225|8', '9.100|9|8.800|10|17.900|10|9.300|8|9.400|7|18.700|7|9.500|6|9.200|7|18.700|7|27.650|7', '9.200|8|9.000|8|18.200|8|9.250|8|9.050|9|18.300|8|9.250|8|9.150|9|18.400|8|9.100|9|9.050|8|18.150|8|27.350|9', '91.225|8', '91.225|8', 'The Cadets', '8.800|10|8.900|9|17.700|9|8.600|11|9.000|9|17.600|10|8.800|10|9.000|8|17.800|8|8.900|10|8.800|11|17.700|10|35.400|10', '9.000|10|9.000|9|18.000|9|8.600|12|9.100|9|17.700|11|9.000|10|8.800|11|17.800|11|26.750|10', '9.100|9|8.800|10|17.900|9|9.150|9|9.100|8|18.250|9|9.100|9|9.200|8|18.300|9|9.500|6|9.700|4|19.200|5|27.688|8', '89.838|9', '89.838|9', 'Mandarins', '8.900|9|8.700|11|17.600|10|9.000|9|8.900|10|17.900|9|8.900|9|8.700|10|17.600|10|9.000|9|9.000|9|18.000|9|35.550|9', '9.300|7|9.100|7|18.400|7|9.100|9|9.200|8|18.300|9|9.300|8|9.000|9|18.300|8|27.500|8', '9.000|10|8.700|11|17.700|11|9.100|10|8.800|10|17.900|10|9.000|10|9.100|10|18.100|10|8.500|12|8.300|12|16.800|12|26.250|11', '89.300|10', '89.300|10', 'Crossmen', '8.600|12|8.800|10|17.400|11|8.700|10|8.800|11|17.500|11|8.700|11|8.600|11|17.300|11|8.800|11|8.700|12|17.500|12|34.850|11', '8.900|11|8.600|12|17.500|11|8.900|10|8.900|11|17.800|10|8.900|11|8.950|10|17.850|10|26.575|11', '8.800|12|8.600|12|17.400|12|8.800|12|8.600|12|17.400|12|8.800|12|8.900|11|17.700|11|8.700|11|8.600|11|17.300|11|26.125|12', '87.550|11', '87.550|11', 'Phantom Regiment', '8.700|11|8.600|12|17.300|12|8.500|12|8.700|12|17.200|12|8.600|12|8.500|12|17.100|12|8.700|12|8.900|10|17.600|11|34.600|12', '8.700|12|8.700|11|17.400|12|8.700|11|8.800|12|17.500|12|8.800|12|8.500|12|17.300|12|26.100|12', '8.900|11|8.900|9|17.800|10|9.000|11|8.750|11|17.750|11|8.900|11|8.700|12|17.600|12|8.900|10|8.700|10|17.600|10|26.538|10', '87.238|12', '87.238|12']]

    error_count = 0
    list_outputs = []
    columns = [
        "Show Date", "Show Location", 
        
        "Corp Name",

        # "General Effect 1 - Rep", "General Effect 1 - Rep_rank",
        # "General Effect 1 - Perf", "General Effect 1 - Perf_rank",
        #"General Effect 1 - TOT", "General Effect 1 - TOT_rank",

        # "General Effect 2 - Rep", "General Effect 2 - Rep_rank",
        # "General Effect 2 - Perf", "General Effect 2 - Perf_rank",
        # "General Effect 2 - TOT", "General Effect 2 - TOT_rank",

        "General Effect - TOT", "General Effect - TOT_rank",

        # "Visual Proficiency - Cont", "Visual Proficiency - Cont_rank",
        # "Visual Proficiency - Achv", "Visual Proficiency - Achv_rank",
        # "Visual Proficiency - TOT", "Visual Proficiency - TOT_rank",

        # "Visual Analysis - Comp", "Visual Analysis - Comp_rank",
        # "Visual Analysis - Achv", "Visual Analysis - Achv_rank",
        # "Visual Analysis - TOT", "Visual Analysis - TOT_rank",

        # "Color Guard - CONT", "Color Guard - CONT_rank",
        # "Color Guard - Achv", "Color Guard - Achv_rank",
        # "Color Guard - TOT", "Color Guard - TOT_rank",

        "Visual - TOT", "Visual - TOT_rank",

        # "Brass - Cont", "Brass - Cont_rank",
        # "Brass - Achv", "Brass - Achv_rank",
        # "Brass - TOT", "Brass - TOT_rank",

        # "Music Analysis - Cont", "Music Analysis - Cont_rank",
        # "Music Analysis - Achv", "Music Analysis - Achv_rank",
        # "Music Analysis - TOT", "Music Analysis - TOT_rank",

        # "Percussion - Cont", "Percussion - Cont_rank",
        # "Percussion - Achv", "Percussion - Achv_rank",
        # "Percussion - TOT", "Percussion - TOT_rank",

        "Music - TOT", "Music - TOT_rank",

        "Sub Total", "Sub Total_rank",

        "Total", "Total_rank"
    ]


    for list_show_scores in all_scores:
        pprint(list_show_scores[:3])
        list_show_scores = list([element for element in list_show_scores if element !=""]) # removes the extra "" with no data
        print(list_show_scores)
        skeleton_list = build_show_cols(list_show_scores)

    
        list_corp_scores = list_show_scores[5:] # slice off the columns
        for index, corp in enumerate(list_corp_scores[::6]): # split list of list by corp and locate all the sub score elements in the list
            list_index = index*6
            corp_scores = list_corp_scores[list_index:list_index+6]
            try:
                # corp_scores = "|".join(list_corp_scores[index*6+1:index*6+6]).split("|") # joins all the stats then split them by | to make one big list of everything, which should line up with the columns
                corp_output = []
                corp_name = corp
                corp_output.append(corp_name)
                corp_geneffect = list_corp_scores[list_index+1].split("|")[-2]
                corp_visual = list_corp_scores[list_index+2].split("|")[-2]
                corp_music = list_corp_scores[list_index+3].split("|")[-2]
                corp_subtotal = list_corp_scores[list_index+4].split("|")[-2]
                corp_total = list_corp_scores[list_index+5].split("|")[-2]
                for info in corp_scores[1:]:
                    corp_output.append(info.split("|")[-2])
                    corp_output.append(info.split("|")[-1])
                # print(corp_output)
                output = skeleton_list + corp_output
                # print(output)
                if len(output) != len(columns):
                    print(f"⚠️ Skipping {corp} on {skeleton_list[0]}, {skeleton_list[1]} — {len(output)} values vs {len(columns)} columns")
                    continue 
                list_outputs.append(output)
            except:
                error_count += 1
    
    print(f"{error_count} shows missing")

    df = pd.DataFrame(list_outputs, columns=columns)
    df.to_csv("score_by_show&corp.csv", index=False)
    display(df.head())

# debug3()

def clean1(): 
    df = pd.read_csv("all_shows_score_recap.csv")
    df = df.dropna(axis=1, how='all')
    print(df)
    df.to_csv("all_shows_score_recap.csv", index=False, header=False)

# clean1()