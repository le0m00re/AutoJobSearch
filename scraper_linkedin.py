#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 09:08:44 2024

@author: jasonbrooner
"""


import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import datetime
import parse_settings

def linkedin(unscraped_list,outlog):
    try:
        start = datetime.datetime.now()
        timestart_prefix = start.strftime("%y-%m-%d_%H-%M-%S")

        options = Options()
        options.add_experimental_option("detach", True)
        #options.add_argument("--headless")

        driver = webdriver.Chrome(options=options)
        driver.get("https://www.linkedin.com/")

        # Switch to the iframe - add other two options for login
        wait = WebDriverWait(driver, 1800)
        auth = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'https://www.linkedin.com/login')]")))

        # Click the Google sign-in button
        auth.click()

        # Now you can interact with elements inside the iframe
        #popup_window = wait.until(EC.number_of_windows_to_be(2))  # Assuming pop-up opens a new window
        #driver.switch_to.window(driver.window_handles[1])
        input_element = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='form__input--floating mt-24']/input[@id='username']"))) #find class by inspecting source code
        input_element.click()
        input_element.send_keys("hgibotemail@yahoo.com") #input text and click key
        time.sleep(2)
        input_element = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='form__input--floating mt-24']/input[@id='password']"))) #find class by inspecting source code
        input_element.click()
        input_element.send_keys("HarrisonGroupInc1976!" + Keys.ENTER)

        # After interacting with elements inside the iframe, switch back to the default content
        #wait.until(EC.number_of_windows_to_be(1))
        #driver.switch_to.window(driver.window_handles[0])

        link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='https://www.linkedin.com/jobs/?']")))
        link.click()

        careerpages = input("Input name of csv file that contains the sector's companies: ")
        careerpages = pd.read_csv(careerpages)
        state_dict = {
            'AL': 'Alabama',
            'AK': 'Alaska',
            'AZ': 'Arizona',
            'AR': 'Arkansas',
            'CA': 'California',
            'CO': 'Colorado',
            'CT': 'Connecticut',
            'DE': 'Delaware',
            'FL': 'Florida',
            'GA': 'Georgia',
            'HI': 'Hawaii',
            'ID': 'Idaho',
            'IL': 'Illinois',
            'IN': 'Indiana',
            'IA': 'Iowa',
            'KS': 'Kansas',
            'KY': 'Kentucky',
            'LA': 'Louisiana',
            'ME': 'Maine',
            'MD': 'Maryland',
            'MA': 'Massachusetts',
            'MI': 'Michigan',
            'MN': 'Minnesota',
            'MS': 'Mississippi',
            'MO': 'Missouri',
            'MT': 'Montana',
            'NE': 'Nebraska',
            'NV': 'Nevada',
            'NH': 'New Hampshire',
            'NJ': 'New Jersey',
            'NM': 'New Mexico',
            'NY': 'New York',
            'NC': 'North Carolina',
            'ND': 'North Dakota',
            'OH': 'Ohio',
            'OK': 'Oklahoma',
            'OR': 'Oregon',
            'PA': 'Pennsylvania',
            'RI': 'Rhode Island',
            'SC': 'South Carolina',
            'SD': 'South Dakota',
            'TN': 'Tennessee',
            'TX': 'Texas',
            'UT': 'Utah',
            'VT': 'Vermont',
            'VA': 'Virginia',
            'WA': 'Washington',
            'WV': 'West Virginia',
            'WI': 'Wisconsin',
            'WY': 'Wyoming'
        }
        careerpages['state'] = careerpages['state'].map(state_dict)

        columns = ['company', 'title', 'location', 'postdate', 'jobpage']
        linkedin_jobs = pd.DataFrame(columns=columns)

        for index, row in careerpages.iterrows():
            company_name = row["company"]
            city = row["city"]  # Assuming the column name for city is "City" in careerpages dataframe
            state = row["state"]  # Assuming the column name for state is "State" in careerpages dataframe
            region = row["territory"]
            input_element = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@class='jobs-search-box__text-input jobs-search-box__keyboard-text-input jobs-search-global-typeahead__input']")))
            input_element.click()
            input_element.send_keys(Keys.COMMAND + 'a')  # Use 'a' to select all text
            input_element.send_keys(Keys.BACKSPACE)
            input_element.send_keys(company_name)
            input_element.send_keys()
            input_element = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='relative']/input[@aria-label='City, state, or zip code']")))
            
            input_element.send_keys(Keys.COMMAND + 'a')  # Use 'a' to select all text
            input_element.send_keys(Keys.BACKSPACE)
            input_element.send_keys(city + ", " + state)
            time.sleep(0.5)
            try:
                    input_element.send_keys(Keys.RETURN)  
                    time.sleep(3)
                    header = driver.find_element(By.XPATH, "//div[@class='jobs-search-results-list__title-heading']//h1").get_attribute("title")
            except:
                    input_element.send_keys(Keys.COMMAND + 'a')
                    input_element.send_keys(Keys.BACKSPACE)
                    input_element.send_keys(region + ", " + state)
                    input_element.send_keys(Keys.RETURN)  
                    time.sleep(3)
                    header = driver.find_element(By.XPATH, "//div[@class='jobs-search-results-list__title-heading']//h1").get_attribute("title")
                     
            if header != "Jobs you may be interested in":
                time.sleep(1)
                jobs = wait.until(EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class, 'scaffold-layout__list-container')]/li")))
                jobs = driver.find_elements(By.XPATH, "//ul[contains(@class, 'scaffold-layout__list-container')]/li")
                for job in jobs:
                    try:
                        job.click()
                    except StaleElementReferenceException:
                        time.sleep(10)
                        try:
                            job.click()
                        except StaleElementReferenceException:
                            continue
                    time.sleep(1)
                    try:
                            company_element = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class = 'artdeco-entity-lockup__title ember-view t-20']/a")))
                            company = company_element.text                    
                            title = driver.find_element(By.XPATH, "//div[contains(@class, 'job-details-jobs-unified-top-card__container--two-pane')]//h1/a").text
                            location = driver.find_element(By.XPATH, "//div[@class = 'job-details-jobs-unified-top-card__primary-description-container']//span[1]").text
                            postdate = driver.find_element(By.XPATH, "//div[@class = 'job-details-jobs-unified-top-card__primary-description-container']//span[3]/span").text
                            jobpage = driver.find_element(By.XPATH, "//div[contains(@class, 'job-details-jobs-unified-top-card__container--two-pane')]//h1/a").get_attribute("href")
                        
        # Create a new DataFrame with the row you want to append
                            new_row = pd.DataFrame([{
                                'company': company,
                                'title': title,
                                'location': location,
                                'postdate': postdate,
                                'jobpage': jobpage}])
                            print(new_row)
        # Concatenate the existing DataFrame with the new row
                            linkedin_jobs = pd.concat([linkedin_jobs, new_row], ignore_index=True)
                                   
                    except Exception as e:
                            print(f"Error while processing job element: {e}")
                            time.sleep(1)
                            link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='https://www.linkedin.com/jobs/?']")))
                            link.click()
                
                try:
                    pages = driver.find_elements(By.XPATH, "//button[@aria-label = 'View next page']")
                    for page in pages:
                            page.click()
                            jobs = wait.until(EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class, 'scaffold-layout__list-container')]/li")))
                            jobs = driver.find_elements(By.XPATH, "//ul[contains(@class, 'scaffold-layout__list-container')]/li")
                            for job in jobs:
                                job.click()
                                time.sleep(1)
                                try:
                                    company_element = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class = 'artdeco-entity-lockup__title ember-view t-20']/a")))
                                    company = company_element.text                            
                                    title = driver.find_element(By.XPATH, "//div[contains(@class, 'job-details-jobs-unified-top-card__container--two-pane')]//h1/a").text
                                    location = driver.find_element(By.XPATH, "//div[@class = 'job-details-jobs-unified-top-card__primary-description-container']//span[1]").text
                                    postdate = driver.find_element(By.XPATH, "//div[@class = 'job-details-jobs-unified-top-card__primary-description-container']//span[3]/span").text
                                    jobpage = driver.find_element(By.XPATH, "//div[contains(@class, 'job-details-jobs-unified-top-card__container--two-pane')]//h1/a").get_attribute("href")

                # Create a new DataFrame with the row you want to append
                                    new_row = pd.DataFrame([{
                                        'company': company,
                                        'title': title,
                                        'location': location,
                                        'postdate': postdate,
                                        'jobpage': jobpage}])

                # Concatenate the existing DataFrame with the new row
                                    linkedin_jobs = pd.concat([linkedin_jobs, new_row], ignore_index=True)
                                    
                                except Exception as e:
                                    print(f"Error while processing job element: {e}")
                                    time.sleep(1)
                                    link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='https://www.linkedin.com/jobs/?']")))
                                    link.click()
                                    
                except:
                    link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='https://www.linkedin.com/jobs/?']")))
                    link.click()
                           
            else:
                time.sleep(1)
                link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='https://www.linkedin.com/jobs/?']")))
                link.click()
                
                                    
            link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='https://www.linkedin.com/jobs/?']")))
            link.click()

    finally:
        driver.quit()
        end = datetime.datetime.now()
        return linkedin_jobs, 

if __name__ == '__main__':
    start = datetime.datetime.now()
    timestart_prefix = start.strftime("%y-%m-%d_%H-%M-%S")
    outlog = open(f'output/{timestart_prefix}_linkedin.log', 'a', 
        encoding='utf-8')
    settings = parse_settings.parse_settings()
    linkedin_df, linkedin_duration = linkedin(settings['LINKEDIN_CSV'], outlog)
    print(linkedin_df)
    print(f'Ran for {linkedin_duration.total_seconds()/60} minutes')
