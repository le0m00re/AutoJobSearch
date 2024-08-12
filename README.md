# AutoJobSearch v1.0 -- 2024 August 2
Outputs a csv file of job openings filtered by location and title.

## Installing
The executables can run upon installation. Python does not need to be downloaded, and it comes with its own copy of Chrome.

## Running
To run scraper, simply double-click scraper.exe <br>
Filter runs automatically after scraper by default, or can be run independently by double-clicking filter.exe

## Files and Folders
1. **settings.ini**
Text file with settings for the exe files.

2. **scraper.exe**
Scrapes job postings from a list of websites given by urls.csv according to the patterns given by xpaths.csv, outputs *timestamp*_jobs.csv and *timestamp*_out.log in \output.

3. **urls.csv**
Default input csv for the urls in scraper.exe, has columns for company, city, state, territory, career page, and third party url, if different from career page. For information on what these columns mean and how to fill new companies into them see \tutorials.

4. **xpaths.csv**
Default input csv for the xpaths in scraper.exe, has columns for type of third party, url pattern, and the xpaths for listing, title, location, date posted, job page, and next button, if one exists. For information on what these columns mean, what xpaths are, and how to find them see \tutorials

5. **filter.exe**
Filters a csv of jobs either automatically after scraper.exe or manually from a csv listed in settings.ini <br>
Filters both by location in urls.csv and by titles in whitelist.csv and blacklist.csv, a title not found in either csv is whitelisted implicitly

6. **whitelist.csv**
List of terms that will automatically pass the filter.

7. **blacklist.csv**
List of terms that will automatically be blocked by the filter. Locations can be blacklisted in the same csv by putting the '@' sign before the term

8. **\output**
Folder for output csv and log files from both executables. All output is timestamped with the program's start time 

9. **\dev**
Folder containing source code for the executables as well as copies of Chrome and chromedriver.


10. **\tutorials**
Tutorial videos explaining basic use of the executables.

## Troubleshooting
AutoJobSearch can only run on Windows <br>
Sometimes there are problems running AutoJobSearch on a new computer due to security blocks from Windows <br>
Check \tutorials for basic info on properly running executables <br>
In the case of persistent bugs, crashes, or unexpected output, contact developers at:
* huawei-lee@uiowa.edu
* jason-brooner@uiowa.edu
* leomoore@uiowa.edu

## Information for Developers
AutoJobSearch is written in Python. It uses pandas and selenium, and is converted to exe files by pyinstaller
* Selenium documentation: (https://www.selenium.dev/documentation/)
* PyInstaller documentation: (https://pyinstaller.org/en/stable/)

Selenium uses chromedriver to operate chrome automatically
* Chromedriver installation: (https://googlechromelabs.github.io/chrome-for-testing/)