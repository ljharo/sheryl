# others
import os
import json
import logging
from time import sleep
from dotenv import load_dotenv

# selenium
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains

# sqlalhemy
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import select
from datetime import datetime, timedelta

# own imports
from .models import Base, Reaction, User

logging.basicConfig(filename='data/log.txt', encoding='utf-8',
                    format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)


def send_message(driver, user_id):
    # Send message
    driver.get(f'https://www.facebook.com/messages/t/{user_id}')
    sleep(10)
    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    textbox = WebDriverWait(
        driver, 60).until(expected_conditions.element_to_be_clickable(
            (By.XPATH, '//div[@role="textbox"]')))
    textbox.send_keys("Hi! How can I help you")
    textbox.send_keys(Keys.ENTER)
    sleep(10)
    logging.info("Message sent")


# Database engine and initialization
engine = create_engine("sqlite:///data/db.sqlite", echo=True)
Base.metadata.create_all(engine)

# We load the environment variables
load_dotenv()
EMAIL = os.environ.get('EMAIL')
PASSWORD = os.environ.get('PASSWORD')


# Create driver
logging.info("Process started")
options = uc.ChromeOptions()
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
options.add_experimental_option('prefs', {'intl.accept_languages': 'es'})
driver = uc.Chrome(headless=True, options=options)
logging.info("Driver created")

# Log in
driver.get('https://www.facebook.com/')
WebDriverWait(
    driver, 60).until(expected_conditions.presence_of_element_located(
        (By.ID, 'email'))).send_keys(EMAIL)
driver.find_element(By.ID, 'pass').send_keys(PASSWORD)
WebDriverWait(
    driver, 60).until(expected_conditions.element_to_be_clickable(
        (By.XPATH, '//button[@type="submit"]'))).click()
WebDriverWait(
    driver, 60).until(expected_conditions.presence_of_element_located(
        (By.XPATH, '//span[text()="Grupos"]')))
logging.info("Logged in")

# Open group
driver.set_window_size(1600, 8000)
driver.get('https://www.facebook.com/profile.php?id=100067031089582')
sleep(10)
ActionChains(driver).send_keys(Keys.ESCAPE).perform()
sleep(60)

# Hover over reaction images
images = driver.find_elements(By.XPATH, '//img[@height="18"]')
for image in images:
    ActionChains(driver).move_to_element(image).perform()
    sleep(5)
# Hover over comments indicators
comments_to_hover = driver.find_elements(
    By.XPATH, '//span[contains(text(), "comentarios")]')
for comment in comments_to_hover:
    ActionChains(driver).move_to_element(comment).perform()
    sleep(5)

# Get the user's data from the browser network interactions
logs = driver.get_log("performance")
events = [json.loads(entry['message'])['message'] for entry in logs]
events = [event for event in events if 'method' in event and 'Network.response' in event['method']]
bodies = []

for event in events:
    try:
        body = driver.execute_cdp_cmd('Network.getResponseBody', {
                                      'requestId': event["params"]["requestId"]})
        body["body"] = json.loads(body["body"])
        if 'feedback' in body["body"]["data"] and ('reactors' in body["body"]["data"]["feedback"] or 'commenters' in body["body"]["data"]["feedback"]):
            bodies.append(body)
    except ValueError as e:
        print(e)

reactions = set()
for body in bodies:
    if 'reactors' in body["body"]["data"]["feedback"]:
        for node in body["body"]["data"]["feedback"]["reactors"]["nodes"]:
            reactions.add((node["id"], node["name"],
                          body['body']['data']['feedback']['id']))
    if 'commenters' in body["body"]["data"]["feedback"]:
        for edge in body["body"]["data"]["feedback"]["commenters"]["edges"]:
            reactions.add((edge["node"]["id"], edge["node"]["name"],
                          body['body']['data']['feedback']['id']))

logging.info("Found %d reactions", len(reactions))

with Session(engine) as session:
    for reaction in reactions:
        reaction_object = Reaction(user_id=reaction[0], post_id=reaction[2])
        user_object = User(user_id=reaction[0], name=reaction[1])
        logging.info("Processing reaction from user %s", user_object.name)

        stmt = select(Reaction).where(Reaction.user_id == reaction_object.user_id).where(
            Reaction.post_id == reaction_object.post_id)
        found_reaction = session.scalars(stmt).one_or_none()

        if found_reaction is None:
            logging.info("This is a new reaction")
            session.add(reaction_object)
            session.commit()

            stmt = select(User).where(User.user_id == user_object.user_id)
            found_user = session.scalars(stmt).one_or_none()

            if found_user:
                logging.info("User has reacted before")
                if found_user.last_message < datetime.now() - timedelta(days=180):
                    send_message(driver, found_user.user_id)
                    found_user.last_message = datetime.now()
                    session.commit()
            else:
                logging.info("User has not reacted before")
                send_message(driver, user_object.user_id)
                user_object.last_message = datetime.now()
                session.add(user_object)
                session.commit()


driver.quit()
