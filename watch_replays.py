import os
import logging
import re
import queue

# selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options


chrome_options = Options()
chrome_options.add_argument("--headless")  # Enable headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (useful for headless mode)
chrome_options.add_argument("--disable-extensions")  # Disable browser extensions
chrome_options.add_argument("--disable-plugins")     # Disable plugins
chrome_options.add_argument("--disable-images")      # Disable loading images
chrome_options.add_argument("--disable-javascript")  # Disable JavaScript if not needed

TIMEOUT = 60

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def remove_html_tags(html_content):
    # Regular expression to match HTML tags
    clean_text = re.sub('<div class="chat chatmessage-collectorely">[*]+</div>', '', html_content)
    clean_text = re.sub('<.*?>', '\n', clean_text)
    
    
    return clean_text
def get_log(link, reset):
    # open replay
    try:
        # Use context management to ensure WebDriver closes properly
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(TIMEOUT)
        driver.get(link)
        
        # Wait for the "button-last" element to be clickable (or present)
        WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'button-last'))
        )
        
        # Locate the skip to end button
        buttons = driver.find_elements(By.CLASS_NAME, 'button-last')
        
        # Check if any buttons were found
        # if buttons:
        #     logger.info(f"Found {len(buttons)} 'button-last' elements.")
        # else:
        #     logger.warning("No 'button-last' buttons found.")
    
    except TimeoutException:
        logger.error(f"Timeout while loading {link}")
        return False
    except NoSuchElementException:
        logger.error(f"No 'button-last' element found on {link}")
        return False
    except Exception as e:
        logger.error(f"An error occurred with {link}: {e}")
        return False


    # skip to last turn
    if buttons:
        buttons[1].click()
    else:
        logger.warning("No 'button-last' buttons found.")
        return False

    # get battle log from html
    out_file = open('./battle_log.txt', 'a')

    # get format
    # Step 1: Find the div that contains the "Format" text (assumed to be within the parent div)
    try:
        parent_div = driver.find_element(By.CLASS_NAME, 'inner.message-log')
    except:
        print(f"can't find parent div for {link}")
        return False

    # Step 2: Extract the inner HTML of the parent div
    html_content = parent_div.get_attribute('innerHTML')

    start_idx = html_content.find("Format")
    out_file.write("\n" + html_content[start_idx : html_content.find("</small>", start_idx)] + "\n")
    out_file.write(html_content[html_content.find("<strong>", start_idx) + len("<strong>") : html_content.find("</strong>", start_idx)] + "\n")

    battle_log = remove_html_tags(html_content[html_content.find("Battle started", start_idx) : html_content.find(" won the battle!", start_idx) + len(" won the battle!")])
    out_file.write(battle_log)

    out_file.close()

    # process log

    if(reset):
        os.remove('./battle_log.txt')
    driver.quit()
    logger.info("success!")

    return True


# Set up the browser and go to replays
driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(TIMEOUT)

while True:
    try:
        driver.get('https://replay.pokemonshowdown.com/?format=%5BGen%201%5D%20Random%20Battle')


        # get list of links to replays
        link_list = driver.find_element(By.CLASS_NAME, 'linklist')
        links = link_list.find_elements(By.TAG_NAME, 'li')

        break
    except TimeoutException:
        logger.warning("Main page timed out. Trying again.")
        continue


# make queue of links
link_q = queue.Queue()

for link in links:
    a_tag = link.find_element(By.TAG_NAME, 'a')
    href = a_tag.get_attribute('href')

    link_q.put(href)
    
driver.quit()

while not link_q.empty():
    # go to one replay
    curr = link_q.get()

    if not get_log(link=curr, reset=False):
        link_q.put(curr)



# You can also close the browser when done
input("Press enter to continue.")