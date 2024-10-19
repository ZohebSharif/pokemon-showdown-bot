import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re

def remove_html_tags(html_content):
    # Regular expression to match HTML tags
    clean_text = re.sub('<.*?>', '\n', html_content)
    return clean_text
def get_log(driver, link):
    # open replay
    print(link)
    driver.get(link)

    # Locate the skip to end button
    buttons = driver.find_elements(By.CLASS_NAME, 'button-last')

    # skip to last turn
    buttons[1].click()

    # get battle log from html
    out_file = open('./battle_log.txt', 'a')

    # get format
    # Step 1: Find the div that contains the "Format" text (assumed to be within the parent div)
    parent_div = driver.find_element(By.CLASS_NAME, 'inner.message-log')

    # Step 2: Extract the inner HTML of the parent div
    html_content = parent_div.get_attribute('innerHTML')

    start_idx = html_content.find("Format")
    out_file.write(html_content[start_idx : html_content.find("</small>", start_idx)] + "\n")
    out_file.write(html_content[html_content.find("<strong>", start_idx) + len("<strong>") : html_content.find("</strong>", start_idx)] + "\n")

    battle_log = remove_html_tags(html_content[html_content.find("Battle started", start_idx) : html_content.find(" won the battle!", start_idx) + len(" won the battle!")])
    out_file.write(battle_log)

    out_file.close()


# Set up the browser and go to replays
driver = webdriver.Chrome()
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
        get_log(driver=driver, link=href)
        seen.add(href)

# You can also close the browser when done
input("Press enter to continue.")
os.remove('./battle_log.txt')
driver.quit()