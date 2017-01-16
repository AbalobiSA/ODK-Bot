# ODK-Bot

**About**

A python script that automatically sets the passwords of users on the ODK Aggregate site.<br>
The passwords for each user is set in the <b>accounts.xml</b> file.

**Requirements**

* Firefox 48 or higher
* <a href="https://github.com/mozilla/geckodriver/releases"><i>Geckoriver</i></a>
* Selenium
* Python 2.7 - Untested on Python 3.x

**Usage**

* Run <b>pip install -r requirements.txt</b> if Selenium is not installed
* Edit the <b>accounts.xml</b> file as desired, specifying the usernames and passwords.
* Supply the login details in <b>secrets.py</b> if desired.
* Run <b>main.py</b>.
* Watch and enjoy.

**Optional: Hardcode your passwords during development**

Create a new file in your local repo: secrets.py and add the following lines:

USERNAME = "login_username"<br>
PASSWORD = "login_password"<br>
Replace the strings with your own username and password

***

**Notes**

The wait and sleep times may have to be changed depending on your internet connection and computer performace.
