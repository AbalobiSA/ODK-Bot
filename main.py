import sys
import os

import time as sleeper
import argparse

import xml.etree.ElementTree

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

try:
    import secrets
    ASK_CREDENTIALS = False
except:
    ASK_CREDENTIALS = True

# Should exception messages be printed
PRINT_EXCEPTIONS = True

# The time to wait before the webdriver decides that the element does not exist
_wait_time = 60.0

GLOBAL_USER_ARRAY = []


def main():
    """
    Main method
    :return: None
    """

    driver = None
    
    if ASK_CREDENTIALS:
        print 'No secrets.py file found, asking credentials:'
        _username, _password = ask_credentials()
    else:
        _username = secrets.USERNAME
        _password = secrets.PASSWORD

    if globals()['_filetype'] == 'xml':
        accounts = parse_xml()
    elif globals()['_filetype'] == 'csv':
        accounts = parse_csv()
    else:
        print 'Filetype not supported'
        sys.exit(1)

    try:
        # Get webdriver
        driver = get_driver()
        
        # Open Abalobi ODK page
        url = "https://%s:%s@abalobi-fisher.appspot.com/Aggregate.html#admin/permission///" % (_username, _password)
        driver.get(url)

        sleeper.sleep(5.0)
        num_rows = get_number_of_rows(driver)

        for row in xrange(1, num_rows + 1):
            username = get_row_username(driver, row)
            
            if username in accounts:
                print 'Account "%s" found in accounts supplied in "accounts.csv". Updating password...' % username
                
                press_row_button(driver, row)
                sleeper.sleep(2.5)
                enter_popup_password(driver, accounts[username])
            else:
                print 'Account "%s" not found in accounts supplied in "accounts.csv". Skipping updating of password...' % username
                
    except Exception as e:
        if PRINT_EXCEPTIONS:
            print e
        else:
            print 'Something went wrong during execution'
    
    # Finally stop the driver and close all browser windows
    if driver is not None:
        try:
            close_driver(driver)
        except Exception as e:
            if PRINT_EXCEPTIONS:
                print e
            else:
                print 'Something went wrong while closing'
    
    print '=========='
    print 'Bye Bye :)'


def get_driver():
    """
    Get a FireFox webdriver instance
    :return: A webdriver instance
    """

    print "Initializing the webdriver"

    if globals()['_browser'] == 'phantom':
        if sys.platform == "linux" or sys.platform == "linux2":
            # linux
            print 'You are running Linux'
            driver = webdriver.PhantomJS(executable_path="./phantomjs")
        elif sys.platform == "win32":
            # Windows...
            print 'You are running Windows'
            driver = webdriver.PhantomJS(executable_path="./phantomjs.exe")
        else:
            print 'Operating system not supported. Exiting...'
            sys.exit(1)
    elif globals()['_browser'] == 'firefox':
        if sys.platform == "linux" or sys.platform == "linux2":
            # linux
            print 'You are running Linux'
            driver = webdriver.Firefox(executable_path="./geckodriver")
        elif sys.platform == "win32":
            # Windows...
            print 'You are running Windows'
            driver = webdriver.Firefox(executable_path="./geckodriver.exe")
        else:
            print 'Operating system not supported. Exiting...'
            sys.exit(1)
    else:
        print 'Browser not supported. Exiting...'
        sys.exit(1)

    return driver


def close_driver(driver):
    """
    Stop the webdriver and close all web browser windows
    :return: None
    """
    
    print 'Closing and quiting...'
    
    driver.close()
    driver.quit()
    
    
def get_row_username(driver, row):
    """
    Get the username in row 'row'
    :param driver: The webdriver
    :param row: The row number to check
    :return: The username
    """
    
    # print 'Getting row %d username...' % row

    xpath = '//*[@id="mainNav"]/tbody/tr[2]/td/div/div[4]/table/tbody/tr[2]/td/div/div[1]/div/div/table/tbody[1]/tr[%d]/td[2]/div/input' % row
    username = WebDriverWait(driver, _wait_time).until(ec.presence_of_element_located((By.XPATH, xpath))).get_property('value')
    
    # print 'The username found is: %s' % username
    
    return username
    
    
def press_row_button(driver, row):
    """
    Press the "Update Password" button in row 'row'
    :param driver: The webdriver
    :param row: The row to check
    :return: None
    """

    print 'Pressing the "Update Password" button in row %d...' % row

    xpath = '//*[@id="mainNav"]/tbody/tr[2]/td/div/div[4]/table/tbody/tr[2]/td/div/div[1]/div/div/table/tbody[1]/tr[%d]/td[4]/div/button' % row
    WebDriverWait(driver, _wait_time).until(ec.presence_of_element_located((By.XPATH, xpath))).click()
    
    
def enter_popup_password(driver, password):
    """
    Enters the password into the popup
    :param driver: The websriver
    :param password: The password to enter
    :return: None
    """
    
    print 'Entering the password in the popup...'
    
    # Get the popup window password fields and insert password
    p1_xpath = '/html/body/div[5]/div/table/tbody/tr[2]/td[2]/input'
    p1 = WebDriverWait(driver, _wait_time).until(ec.presence_of_element_located((By.XPATH, p1_xpath)))
    p1.send_keys(password)
    
    p2_xpath = '/html/body/div[5]/div/table/tbody/tr[3]/td[2]/input'
    p2 = WebDriverWait(driver, _wait_time).until(ec.presence_of_element_located((By.XPATH, p2_xpath)))
    p2.send_keys(password)
    
    # Wait a bit after entering the password just to be safe
    sleeper.sleep(1.0)
    
    # Press the update button
    button_xpath = '/html/body/div[5]/div/table/tbody/tr[4]/td[1]/button'
    button = WebDriverWait(driver, _wait_time).until(ec.presence_of_element_located((By.XPATH, button_xpath)))
    button.click()
    
    # raw_input('Press any key to continue...')
    
    
def get_number_of_rows(driver):
    """
    Get the number of row in the table ie. the number of accounts
    :param driver: The webdriver
    :return: The number of rows
    """
    
    print 'Finding the number of accounts on page...'
    
    xpath = '//*[@id="mainNav"]/tbody/tr[2]/td/div/div[4]/table/tbody/tr[2]/td/div/div[1]/div/div/table/tbody[1]/*'
    WebDriverWait(driver, _wait_time).until(ec.presence_of_element_located((By.XPATH, xpath)))
    num_rows = len(driver.find_elements_by_xpath(xpath))

    print '%d accounts were found on page' % num_rows
    
    return num_rows


def ask_credentials():
    """
    Ask the user for their username and password
    :return: The username and password
    """
    
    username = raw_input('Please enter your login username: ')
    password = raw_input('Please enter your login password: ')
    
    return username, password
        
        
def parse_xml():
    """
    Parse the accounts.xml file
    :return: A mapping(dictionary) of username to password
    """

    if not os.path.exists(sys.path[0] + '/accounts.xml'):
        print 'The accounts.xml file does not exists. Exiting'
        exit()

    try:
        print "Parsing the accounts.xml..."
    
        # Dictionary containing the username to password mappings
        parsed_accounts = {}
    
        e = xml.etree.ElementTree.parse(sys.path[0] + '/accounts.xml').getroot()
    
        accounts = e.findall('account')
        for account in accounts:
            username = str(account.get('username'))
            password = str(account.get('password'))
        
            parsed_accounts[username] = password
    
        return parsed_accounts
    except Exception as e:
        print 'Something went wrong with parsing XML file. Exiting'
        raise e


def parse_csv():
    """
    Parse the CSV file
    :return: A mapping(dictionary) of username to password
    """
    
    import os
    import sys
    import csv
    
    if not os.path.exists(sys.path[0] + '/test.csv'):
        print 'The test.csv file does not exists. Exiting'
        exit()
    
    try:
        print "Parsing the test.csv file..."
        
        # List containing the username, password and community
        parsed_accounts = {}
        
        heading = True
        
        username_index = -1
        password_index = -1
        
        with open('test.csv', 'r') as f:
            reader = csv.reader(f)
            
            for row in reader:
                # print row
                
                if heading:
                    heading = False
                    
                    username_index = row.index("Username")
                    password_index = row.index("Password")
                else:
                    parsed_accounts[row[username_index]] = row[password_index]
        
        # print parsed_accounts
        
        return parsed_accounts
    except Exception as e:
        print 'Something went wrong with parsing CSV file. Exiting'
        raise e


def parse_argv():
    """

    :return:
    """

    parser = argparse.ArgumentParser(description='Updates user password on ODK', add_help=True, version='1.1')

    parser.add_argument('--browser', '-b', type=str, choices=['firefox', 'phantom'], default='phantom', help='The browser to use')
    parser.add_argument('--input', '-i', type=str, choices=['csv', 'xml'], default='csv', help='The input file-type to use')

    args = parser.parse_args()

    print 'The arguments are =>', args
    print '-' * 25

    globals()['_browser'] = args.browser
    globals()['_filetype'] = args.input


if __name__ == '__main__':
    parse_argv()
    main()
