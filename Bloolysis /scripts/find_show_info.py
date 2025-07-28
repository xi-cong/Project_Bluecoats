# we will find the all the year and location available front the inital DCI.org page 

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

DATA_DIR = "data"

# this function scarpes all urls for shows since 2013 and writes them into a csv file 
# only needs to be run when new shows are updated
def scrape_dci_recaps_selenium():
    options = Options()
    options.add_argument("--headless")  # Remove this if you want to see browser
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    all_shows = []

    base_url = "https://www.dci.org/scores/?location=All&season={}&pageno={}"

    years = [str(y) for y in range(2025, 2012, -1)]

    for year in years:
        print(f"🔍 Scraping year {year}")
        for page in range(1, 12):
            print(f"  → Page {page}", end="... ")
            url = base_url.format(year, page)
            driver.get(url)
            time.sleep(1.5)  # Give JavaScript time to load

            links = driver.find_elements(By.CSS_SELECTOR, 'a.arrow-btn')
            if not links:
                print("No links found.")
                break

            recap_links = [link.get_attribute('href').replace("final-scores", "recap") for link in links] #type:ignore
            all_shows.extend(recap_links)
            print(f"{len(recap_links)} links.")

    driver.quit()

    print(f"fetched {len(all_shows)} shows")
    # Save to CSV
    df = pd.DataFrame(all_shows)
    df.to_csv(f"{DATA_DIR}/all_shows_url.csv", index=False, header=['url'])
    print("✅ Done! Recap URLs saved to all_shows_url.csv")
    return all_shows
# write "all_shows_url.csv"

# This function extra the important cells from each html of the show
def extrat_valid_cells(url_show):
    # url_show = "https://www.dci.org/scores/recap/2024-dci-southeastern-championship/"
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
        # print(levels)

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

# This function loops through each url in each column of the url csv 
# This function parsers all the show information and create a flat list of list 
# List = [show date, show location, corp, and corp score recap dateframe]
def build_show_score_list():
    # df_all_shows = pd.read_csv("all_shows_url.csv")
    # url_little_rock = df_all_shows["2025"][3]
    with open(f"{DATA_DIR}/all_shows_url.csv") as file:
        reader  = csv.reader(file)
        list_all_shows = list(reader)[1:]

    list_all_show_scores = []
    list_error_show_scores = []


    for i, url_show in enumerate(list_all_shows):
            # print(f"📅 Fetching {i} show(s) from {column}...")
            url_show = url_show[0]
            valid_cells = extrat_valid_cells(url_show) # call function that extract the right cells

            resp = requests.get(str(url_show), headers={"User-Agent": "Mozilla/5.0"}).text
            soup = BeautifulSoup(resp, "html.parser")
            show_time_location = soup.select_one("div.score-date-location.justify-center")

            if not show_time_location:
                print(f"⚠️ Skipping — no show time/location found at: {url_show}")
                continue

            show_time_location = show_time_location.get_text(separator="|", strip=True) #type:ignore
            show_time = show_time_location.split("|")[0]
            show_location = show_time_location.split("|")[1]

            if len(valid_cells) > 3:
                list_all_show_scores.append(valid_cells)
                print(f"✅ successfully extracted scores at {show_location} on {show_time}")
            elif len(valid_cells) == 2:
                print(f"⛔️ error 1: no world class at {show_location} on {show_time}")
            else:
                list_error_show_scores.append(valid_cells)
                print(f"🚫error 2: something went wrong at {show_location} on {show_time}: {url_show}")

    print("🥂🥂🥂 all done!!!")

    # pprint(list_all_show_scores)
    df = pd.DataFrame(list_all_show_scores)
    df_error2 = pd.DataFrame(list_error_show_scores)
    # print(df.head())
    # print(len(list_all_show_scores))
    df.to_csv(f"{DATA_DIR}/all_shows_score_recap.csv", index=False, header=False)
    # df_error2.to_csv("all_error_score_recap.csv", index=False)
# write "all_shows_score_recap.csv"

# build_show_score_dict()

def clean_csv():
    df = pd.read_csv(f"{DATA_DIR}/all_shows_score_recap.csv")
    # df = df.drop(df.columns[0], axis=1)
    df.columns = ["Date", "Location", "Corp", "Score Recap"]
    df.to_csv(f"{DATA_DIR}/all_shows_score_recap.csv", index=False)

# clean_csv()

def find_error_shows():
    df = pd.read_csv(f"{DATA_DIR}/all_shows_score_recap.csv")
    error_rows = df[df["Corp"].astype(str).str.match(r"^\d")]
    print(error_rows)
    error_rows.to_csv(f"{DATA_DIR}/error shows.csv")

# find_error_shows()

def build_show_cols(list_show_scores):

    show_dict = {}
    show_date = list_show_scores[0]
    show_location = list_show_scores[1]
    show_geneffect_cols = list_show_scores[2]
    show_visual_cols = list_show_scores[3]
    show_music_cols = list_show_scores[4]
    return [show_date, show_location]

# This function write the corp from shows to individual corp score recap in each show 
# This function write the df into score by show&corp csv 
def build_show_score_df():
    with open(f"{DATA_DIR}/all_shows_score_recap.csv") as rfile:
        reader = csv.reader(rfile)
        all_scores = list(reader)[1:]
    
    # all_scores = [[line for line in row if line.strip()] for row in all_scores]
    # list_show_scores = all_scores[21] # use the 2024 final as example list 
    # list_show_scores = [element for element in list_show_scores if element !=""] # removes the extra "" with no data
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
        list_show_scores = [element for element in list_show_scores if element !=""] # removes the extra "" with no data
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
                    # corp_geneffect = list_corp_scores[list_index+1].split("|")[-2]
                    # corp_visual = list_corp_scores[list_index+2].split("|")[-2]
                    # corp_music = list_corp_scores[list_index+3].split("|")[-2]
                    # corp_subtotal = list_corp_scores[list_index+4].split("|")[-2]
                    # corp_total = list_corp_scores[list_index+5].split("|")[-2]
                    for info in corp_scores[1:]:
                        corp_output.append(info.split("|")[-2])
                        corp_output.append(info.split("|")[-1])
                    # print(corp_output)
                    output = list(skeleton_list) + list(corp_output)
                    # print(output)
                    if len(output) != len(columns):
                        print(f"⚠️ Skipping {corp} on {skeleton_list[0]}, {skeleton_list[1]} — {len(output)} values vs {len(columns)} columns")
                        continue 
                    list_outputs.append(output)
                except:
                    error_count += 1
    
    print(f"{error_count} corp score missing")

    df = pd.DataFrame(list_outputs, columns=columns)
    df.to_csv(f"{DATA_DIR}/score_by_show&corp.csv", index=False)
    display(df.head())
# write "score_by_show&corp.csv"

def find_bluecoats():
    df_og = pd.read_csv(f"{DATA_DIR}/score_by_show.csv")
    bluecoats_df = df_og[df_og["Corp Name"] == "Bluecoats"]
    bluecoats_df.to_csv(f"{DATA_DIR}/bluecoats_shows.csv")

# Update lastest game 
def find_lastest_shows_links():
    print("🔄 running find_lastest_show_links")

    with open(f"{DATA_DIR}/all_shows_url.csv") as fin:
        list_all_shows_url = fin.readlines()

    options = Options()
    options.add_argument("--headless")  # Remove this if you want to see browser
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    all_shows = {}

    base_url = "https://www.dci.org/scores/?location=All&season={}&pageno={}"

    years = [str(y) for y in range(2025, 2012, -1)]

    for year in years:
        print(f"🔍 Scraping year {year}")
        all_shows[year] = []
        for page in range(1, 12):
            print(f"  → Page {page}", end="... ")
            url = base_url.format(year, page)
            driver.get(url)
            time.sleep(1.5)  # Give JavaScript time to load

            links = driver.find_elements(By.CSS_SELECTOR, 'a.arrow-btn')
            if not links:
                print("No links found.")
                break

            recap_links = [link.get_attribute('href').replace("final-scores", "recap") for link in links] #type:ignore
            lastest_links = []
            for i, link in enumerate(recap_links): 
                if link.strip().rstrip('/') == list_all_shows_url[1].strip().rstrip('/'):
                    lastest_links = recap_links[:i]
                    if len(lastest_links) > 0:
                        # update url csv
                        try:
                            df_original= pd.read_csv(f"{DATA_DIR}/all_shows_url.csv")
                            urls = df_original["url"].tolist()
                            urls = lastest_links + urls
                            df_new = pd.DataFrame(urls, columns=["url"])
                            df_new.to_csv(f"{DATA_DIR}/all_shows_url.csv", index=False)

                            return lastest_links
                        except:
                            df_original= pd.read_csv(f"{DATA_DIR}/all_shows_url.csv")
                            urls = df_original["0"].tolist()
                            urls = lastest_links + urls
                            df_new = pd.DataFrame(urls, columns=["url"])
                            df_new.to_csv(f"{DATA_DIR}/all_shows_url.csv", index=False)

                            return lastest_links
                        
                    else: 
                        print("∅ no lastest show to update")
                        return []
            
            # all_shows[year].extend(recap_links)
            # print(f"{len(recap_links)} links.")

    driver.quit()

    # Save to CSV
    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in all_shows.items()]))
    df.to_csv(f"{DATA_DIR}/all_shows_url.csv", index=False)
    print("✅ Done! Recap URLs saved to all_shows_url.csv")
    return all_shows

def build_lastest_show_score_list():
    print("⮑ to find_latest_show_list")
    list_lastest_show = find_lastest_shows_links()
    print("🔄 running build_latest_show_list")
    # url_little_rock = df_all_shows["2025"][3]

    list_all_show_scores = []
    list_error_show_scores = []


    for i, url_show in enumerate(list_lastest_show):
            # print(f"📅 Fetching {i} show(s) from {column}...")
            if pd.isna(url_show):
                continue  # Skip empty or invalid entries
            
            
            valid_cells = extrat_valid_cells(url_show) # call function that extract the right cells

            resp = requests.get(url_show, headers={"User-Agent": "Mozilla/5.0"}).text
            soup = BeautifulSoup(resp, "html.parser")
            show_time_location = soup.select_one("div.score-date-location.justify-center")

            if not show_time_location:
                print(f"⚠️ Skipping — no show time/location found at: {url_show}")
                continue

            show_time_location = show_time_location.get_text(separator="|", strip=True) #type:ignore
            show_time = show_time_location.split("|")[0]
            show_location = show_time_location.split("|")[1]

            if len(valid_cells) > 3:
                list_all_show_scores.append(valid_cells)
                print(f"☑️ successfully fetched shows at {show_location} on {show_time}")
            elif len(valid_cells) == 2:
                print(f"⛔️ error 1: no world class at {show_location} on {show_time}")
            else:
                list_error_show_scores.append(valid_cells)
                print(f"🚫error 2: something went wrong at {show_location} on {show_time}: {url_show}")
            

    with open(f"{DATA_DIR}/all_shows_score_recap.csv", newline='') as f:
        reader = csv.reader(f)
        old_rows = list(reader)
    list_all_show_scores = list_all_show_scores + old_rows
    df_new = pd.DataFrame(list_all_show_scores)
    df_new.to_csv(f"{DATA_DIR}/all_shows_score_recap.csv", index=False, header=False)
    print(f"✅ updated score_recap.csv")

    print("🥂🥂🥂 all done!!!")

    return list_all_show_scores

def build_lastest_show_score_df():
    print("⮑ to build lastest show score list")

    list_lastest_scores = build_lastest_show_score_list()
    print("🔄 running build lastest show score df")
    
    # list_show_scores = all_scores[21] # use the 2024 final as example list 
    # list_show_scores = [element for element in list_show_scores if element !=""] # removes the extra "" with no data
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

    for list_show_scores in list_lastest_scores:
        list_show_scores = [element for element in list_show_scores if element !=""] # removes the extra "" with no data
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
                # corp_geneffect = list_corp_scores[list_index+1].split("|")[-2]
                # corp_visual = list_corp_scores[list_index+2].split("|")[-2]
                # corp_music = list_corp_scores[list_index+3].split("|")[-2]
                # corp_subtotal = list_corp_scores[list_index+4].split("|")[-2]
                # corp_total = list_corp_scores[list_index+5].split("|")[-2]
                for info in corp_scores[1:]:
                    corp_output.append(info.split("|")[-2])
                    corp_output.append(info.split("|")[-1])
                # print(corp_output)
                output = list(skeleton_list) + list(corp_output)
                # print(output)
                if len(output) != len(columns):
                    print(f"⚠️ Skipping {corp} on {skeleton_list[0]}, {skeleton_list[1]} — {len(output)} values vs {len(columns)} columns")
                    continue 
                list_outputs.append(output)
            except:
                print(skeleton_list+[corp_name])
                error_count += 1
    
    print(f"🚨 {error_count} corp score missing")

    df = pd.read_csv(f"{DATA_DIR}/score_by_show&corp.csv")
    new_df = pd.DataFrame(list_outputs, columns=df.columns)

    # Prepend to the existing df
    df = pd.concat([new_df, df], ignore_index=True)
    df.to_csv(f"{DATA_DIR}/score_by_show.csv", index=False)

# build_lastest_show_score_df()









