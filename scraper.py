from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (NoSuchElementException, 
    StaleElementReferenceException, InvalidSelectorException, 
    ElementNotInteractableException, ElementClickInterceptedException, 
    WebDriverException, NoSuchWindowException, InvalidArgumentException,
    TimeoutException)
import pandas as pd
import time
import datetime
import filter, parse_settings, scraper_linkedin

start = datetime.datetime.now()
timestart_prefix = start.strftime("%y-%m-%d_%H-%M-%S")

def print_message(message):
    print(f"[MESSAGE]\t{message}", file=outlog)

def print_warning(warning):
    print(f"[WARNING]\t{warning}", file=outlog)

def print_fail(fail):
    print(f"[FATAL ERROR]\t{fail}", file=outlog)

def print_success(success):
    print(f"[SUCCESS]\t{success}", file=outlog)

def grab_xpaths(xpaths_by_third_party, company_url):
    '''Loops through each url in xpath and returns those contained in the 
    career page url being scraped. This is necessary as there doesn't seem to 
    be an easy way to do this using just .loc'''
    for third_party in xpaths_by_third_party['url']:
        if third_party in company_url:
            return list(xpaths.loc[xpaths['url'] == third_party].values)
    else:
        return []

def scrape_element(element_name, xpath, attr, index):
    '''Scrapes the ith element on a page given its xpath'''

    try:
        element = driver.find_element(by=By.XPATH, value=f'({xpath})')
        if attr == 'text':
            return element.text
        elif attr == 'href':
            return element.get_attribute('href')

    # These errors usually mean the xpath has a typo
    except (NoSuchElementException, TypeError, InvalidSelectorException):
        if element_name == 'jobpage':
            return url
        elif element_name == 'title':
            raise TypeError
        else:
            return f"<{element_name.upper()} MISSING?>"

def scrape_page(driver, listing_xpath, title_xpath, city_xpath, postdate_xpath, 
jobpage_xpath, button_xpath, pagecount):
    '''scrapes a page, saves results to a csv, then attempts to move to the 
    next page if it exists, else returns None'''
    
    # Exit immediately if listing_xpath == nan
    if isinstance(listing_xpath, float):
        print_warning(f"Could not scrape\t{company}\t({url})\t"\
            "due to listing_xpath being NA")
        return None

    company_name, titles, locations, postdates, jobpages = (list(), list(), 
        list(), list(), list())

    # Scrape each element, unless there's a type error (i.e. the element is NA)
    for i in range(1, 
        len(driver.find_elements(by=By.XPATH, value=listing_xpath))+1):
        try:
            titles.append(scrape_element(element_name='title', 
                xpath=listing_xpath+f'[{i}]'+title_xpath, 
                attr='text', index=i))
            company_name.append(company)
        except TypeError:
            continue

        try:     
            locations.append(scrape_element(element_name='city', 
                xpath=listing_xpath+f'[{i}]'+city_xpath, 
                attr='text', index=i))
        except TypeError:
            locations.append("<LOCATION NA>")

        try:     
            raw_postdate = scrape_element(element_name='postdate', 
                xpath=listing_xpath+f'[{i}]'+postdate_xpath, attr='text', 
                index=i)
            # Tries to change dates to "Posted # Days Ago" format. If it can't 
            # determine the date format it just appends the raw string.
            try:
                datetime_postdate = pd.to_datetime(raw_postdate)
                assert(isinstance(datetime_postdate, 
                    pd._libs.tslibs.nattype.NaTType))
                datetime_postdate = datetime_postdate.to_pydatetime()
                day_delta = (datetime.datetime.today()-datetime_postdate).days
                if day_delta == 0:
                    clean_postdate = "Posted Today"
                elif day_delta == 1:
                    clean_postdate = "Posted Yesterday"
                elif day_delta >= 30:
                    clean_postdate = "Posted 30+ Days Ago"
                else:
                    clean_postdate = f"Posted {day_delta} Days Ago"
                postdates.append(clean_postdate)
            except Exception as e:
                if 'Today' in raw_postdate:
                    raw_postdate = "Posted Today"
                elif 'Yesterday' in raw_postdate:
                    raw_postdate = "Posted Yesterday"
                elif raw_postdate[0:1].strip() == '1':
                    raw_postdate = "Posted Yesterday"
                elif raw_postdate[0].isdigit():
                    raw_postdate = f"Posted "\
                        f"{raw_postdate[0:1].strip()} Days Ago"
                postdates.append(raw_postdate) 
        except TypeError:
            postdates.append("<POSTDATE NA>")

        try:
            jobpages.append(scrape_element(element_name='jobpage', 
                xpath=listing_xpath+f'[{i}]'+jobpage_xpath, 
                attr='href', index=i))
        except TypeError:
            jobpages.append(url)
    
    # Click button. If button is a view more button, clear the lists to avoid 
    # double-scraping. Then scrape next page
    try: 
        previous_page_html = driver.page_source
        button = driver.find_element(By.XPATH, button_xpath)
        view_more_flag = False
        if ('VIEW' in button.text.upper() or 'SHOW' in button.text.upper() 
        or 'MORE' in button.text.upper()):
            company_name, titles, locations, postdates, jobpages = (list(), 
                list(), list(), list(), list())
            view_more_flag = True
        button.click()
        time.sleep(settings['SLEEP'])
        next_page_html = driver.page_source
        assert next_page_html != previous_page_html
        pagecount += 1 if not view_more_flag else 0
        scrape_page(driver, listing_xpath, title_xpath, city_xpath, 
            postdate_xpath, jobpage_xpath, button_xpath, pagecount)
    # Move on if html of next page equals html of previous page 
    # (i.e. clicking the button did nothing)
    # or if button doesn't exist (i.e. last page)
    except (AssertionError, NoSuchElementException, 
    ElementNotInteractableException, InvalidArgumentException) as e:
        print_message(f"Scraped {pagecount} pages of:\t"\
            f"{company}\t({url}).\t{type(e)}")
        return None

    # Some buttons aren't actually html buttons but links to the next page
    # MAKE SURE THIS WORKS CORRECTLY WITH VIEW MORE
    # except ElementNotInteractableException as e:
    #     try:
    #         next_page_url = 'files://' + button.get_attribute('href')
    #         driver.get(next_page_url)
    #         next_page_html = driver.page_source
    #         assert(next_page_html != previous_page_html)
    #         scrape_page(driver, listing_xpath, title_xpath, city_xpath, 
    #         postdate_xpath, jobpage_xpath, button_xpath, pagecount)
    #     except Exception as e:
    #         print(type(e), e, sep=' ')
    #         print_message(f"Scraped {pagecount} pages of {company} ({url})")
    #         return None
        
    # If page-clicking error occurs, wait 10 seconds and try again.
    except (StaleElementReferenceException, 
    ElementClickInterceptedException):
        try:
            time.sleep(10)
            button.click()
            time.sleep(settings['SLEEP'])
            next_page_html = driver.page_source
            assert next_page_html != previous_page_html
            pagecount += 1 if not view_more_flag else 0
            scrape_page(driver, listing_xpath, title_xpath, city_xpath, 
            postdate_xpath, jobpage_xpath, button_xpath, pagecount)
        # If same failure occurs after 10 seconds, give up.
        except AssertionError:
            print_message(f"Scraped {pagecount} pages of:\t"\
                f"{company}\t({url}).\t{type(e)}")
            return None
        except (StaleElementReferenceException, 
        ElementClickInterceptedException) as e:
            print_warning(f"Exited prematurely on page {pagecount} of:\t"\
                f"{company}\t({url}).\tThis probably means the\t"\
                f"SLEEP variable was set too low.\t{type(e)}")
            return None
    except Exception as e:
        print_message(f'{company} {type(e)}')
        return None 
    finally:
        if all((company_name, titles, locations, postdates, jobpages)):
            listing_dict['company'].extend(company_name)
            listing_dict['title'].extend(titles)
            listing_dict['location'].extend(locations)
            listing_dict['postdate'].extend(postdates)
            listing_dict['jobpage'].extend(jobpages)
        outlog.flush() 
        return None

if __name__ == '__main__': 
    try:
        settings = parse_settings.parse_settings()
        outlog = open(f'output/{timestart_prefix}_out.log', 'a', 
            encoding='utf-8')

        # Imports the company and url columns from companies.csv, 
        # and all the columns of xpaths.csv
        url_csv = pd.read_csv(settings['URL_CSV'])
        companies, urls = url_csv[['company', 'url']].T.values
        xpaths = pd.read_csv(settings['XPATH_CSV'])
        
        listing_dict = {'company': [],
            'title': [],
            'location': [],
            'postdate': [],
            'jobpage': []}

        unfamiliar_dict = {'company': [],
            'city': [],
            'state': [],
            'territory': []}

        # Setting up selenium webdriver settings
        options = webdriver.ChromeOptions()
        options.binary_location = settings['CHROME_BIN']
        if settings['HEADLESS'].lower() == 'true':
            options = options.add_argument('--headless=new')
        service = webdriver.ChromeService(executable_path=
            settings['CHROMEDRIVER_BIN'])
        driver = webdriver.Chrome(service=service, options=options)

        # Visit each company's job opening page, scroll to the bottom
        for i, (company, url) in enumerate(zip(companies, urls)):
            driver.get(url)
            driver.implicitly_wait(settings['SLEEP']*5)

            scroll_string = "window.scrollTo(0, document.body.scrollHeight);"
            driver.execute_script(scroll_string)

            # See if any url stems in xpaths.csv are in the url of the company
            possible_xpaths_list = grab_xpaths(xpaths, url)
            if not possible_xpaths_list:
                print_warning(f"Unfamiliar pattern for:\t{company}\t({url})\t"\
                    "Perhaps there are typos in xpaths.csv?")
                # This dict optionally put into linkedin afterwards
                ufd_list = url_csv.iloc[i].tolist()
                unfamiliar_dict['company'].append(ufd_list[0])
                unfamiliar_dict['city'].append(ufd_list[1])
                unfamiliar_dict['state'].append(ufd_list[2])
                unfamiliar_dict['territory'].append(ufd_list[3])
                continue
            
            # For each pattern try to scrape the page
            for possible_xpaths in possible_xpaths_list:
                time.sleep(settings['SLEEP'])#*5)
                try:
                    scrape_page(driver, *possible_xpaths[2:8], 1)
                except TimeoutException:
                    print('timeout during ', company)
                    continue
            if i % 10 == 0:
                df = pd.DataFrame(listing_dict)
                df.to_csv(f'output/{timestart_prefix}_jobs.csv', mode='a', 
                    index=False, header=False if i else True)
                listing_dict = {'company': [],
                                'title': [],
                                'location': [],
                                'postdate': [],
                                'jobpage': []}
        print_success("Scraper finished normally.")

    except FileNotFoundError as e:
        print_fail(f"One or more files in settings.ini \
            does not exist as written.")
        raise e
    except (WebDriverException, NoSuchWindowException, KeyboardInterrupt) as e:
        print_fail(f"Scraper interrupted during:\t{company}\t({url})\t"\
            f"due to {type(e)}. Program either manually closed by user or "\
            "crashed unexpectedly.")
        raise e
    except Exception as e:
        print_fail(f"Scraper exited prematurely during:\t{company}\t({url})\t"\
            f"due to {type(e)}: {str(e)}")
        raise e

    finally:
        try:
            driver.quit()  
        except Exception as e:
            print_warning(f"Failed to quit driver due to {type(e)}. "\
            "This probably means it was never created in the first place, "\
            "i.e. the program failed before it was made.")
        try:
            df = pd.DataFrame(listing_dict)
            df.to_csv(f'output\\{timestart_prefix}_jobs.csv', 
                mode='a', index=False, header=False)
        except Exception as e:
            print_warning(f"Failed to produce output csv due to {type(e)}. "\
                "This probably means it was never created in the first "\
                "place, i.e. the program failed before it was made.")
        finally:
            end = datetime.datetime.now()
            print_message(f"Scraper ran for "\
                f"{(end-start).total_seconds()/60} minutes")
            outlog.flush()

    if (settings['LINKEDIN_FLAG'].lower() == 'true' 
    and settings['LINKEDIN_CSV']):
        unfamiliar_df = pd.DataFrame(unfamiliar_dict)
        linkedin_start = datetime.datetime.now()
        try:
            linkedin_df = scraper_linkedin.linkedin(unfamiliar_df)
            linkedin_df.to_csv(f'output\\{timestart_prefix}_jobs.csv', 
                mode='a', index=False, header=True)
            print_success(f"LinkedIn listings successfully appended.")
        except Exception as e:
            print_fail(f'Appending LinkedIn listings failed due to {type(e)}')
        finally:
            linkedin_end = datetime.datetime.now()
            print_message(f"Scraper ran for "\
                f"{(linkedin_end-linkedin_start).total_seconds()/60} minutes")

    if settings['FILTER_FLAG'].lower() == 'true':
        unfiltered_df = pd.read_csv(f'output\\{timestart_prefix}_jobs.csv')
        print(unfiltered_df)
        try:
            filter.filter(unfiltered_df, timestart_prefix, 
                settings['TITLE_WHITELIST'], settings['TITLE_BLACKLIST'], 
                outlog, url_csv)
        except Exception as e:
            print_fail(f'Filter failed due to {type(e)}')

    outlog.close()