import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re

chrome_options = Options()
chrome_options.add_argument("--headless")  # Enable headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (useful for headless mode)
chrome_options.add_argument("--disable-extensions")  # Disable browser extensions
chrome_options.add_argument("--disable-plugins")     # Disable plugins
chrome_options.add_argument("--disable-images")      # Disable loading images
chrome_options.add_argument("--disable-javascript")  # Disable JavaScript if not needed

TIMEOUT = 20

def remove_html_tags(html_content):
    # Regular expression to match HTML tags
    clean_text = re.sub('<.*?>', '\n', html_content)
    return clean_text
def get_log(link, reset):
    # open replay
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(TIMEOUT)
        driver.get(link)
   
        # Locate the skip to end button
        buttons = driver.find_elements(By.CLASS_NAME, 'button-last')
    except:
        print(f"skipping {link}")
        return


    # skip to last turn
    if(len(buttons) == 2):
        buttons[1].click()
    else:
        print(f"can't find buttons for {link}")
        return

    # get battle log from html
    out_file = open('./battle_log.txt', 'a')

    # get format
    # Step 1: Find the div that contains the "Format" text (assumed to be within the parent div)
    try:
        parent_div = driver.find_element(By.CLASS_NAME, 'inner.message-log')
    except:
        print(f"can't find parent div for {link}")
        return

    # Step 2: Extract the inner HTML of the parent div
    html_content = parent_div.get_attribute('innerHTML')

    start_idx = html_content.find("Format")
    out_file.write(html_content[start_idx : html_content.find("</small>", start_idx)] + "\n")
    out_file.write(html_content[html_content.find("<strong>", start_idx) + len("<strong>") : html_content.find("</strong>", start_idx)] + "\n")

    battle_log = remove_html_tags(html_content[html_content.find("Battle started", start_idx) : html_content.find(" won the battle!", start_idx) + len(" won the battle!")])
    out_file.write(battle_log)

    out_file.close()

    # process log

    if(reset):
        os.remove('./battle_log.txt')
    driver.quit()
    print("success!")


# Set up the browser and go to replays
driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(TIMEOUT)
driver.get('https://replay.pokemonshowdown.com/?format=%5BGen%201%5D%20Random%20Battle')

# don't rewatch seen replays
seen = set()

# go to one replay
link_list = driver.find_element(By.CLASS_NAME, 'linklist')
links = link_list.find_elements(By.TAG_NAME, 'li')

for link in links:
    a_tag = link.find_element(By.TAG_NAME, 'a')
    href = a_tag.get_attribute('href')

    if(href not in seen):
        get_log(link=href, reset=True)
        seen.add(href)

# You can also close the browser when done
input("Press enter to continue.")
driver.quit()