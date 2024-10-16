# nfl-stats-scraping
Project to scrape and clean NFL data.

# Installation
TODO: currently the environment is kind of messed up, I think there's a mix of conda and pip installs.  I couldn't get conda requirements to work (the packages were private?) so I'm using pip inside a conda environment right now which is probably dumb.  I had to manually install a few packages with pip. But, might just use Poetry or something or Dockerize it?

## Linux Install
Followed a few different tutorials.  Not sure what actually worked.

https://stackoverflow.com/questions/68283578/how-can-i-run-selenium-on-linux

You can't use sudo on Amazon Linux distro, and you have to use yum instead of apt-get.  You also can't activate super user using "su" because there is not password set.  So I logged in from the AWS console with Instance Connect and setting user as root.  This allowed me to run super user commands.

So in the answer above, I used the following for step (1) for the install: https://www.cyberciti.biz/faq/howto-install-google-chrome-on-redhat-rhel-fedora-centos-linux/.

Alas, it is still not working:
> https://www.cyberciti.biz/faq/howto-install-google-chrome-on-redhat-rhel-fedora-centos-linux/

Other issues: I had hard-coded the chrome executable path and once I reinstalled a different version it worked once I started using which() again.  

Browser and Driver versions need to be compatible.

http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_CHROME_VERSION_amd64.deb

Replace "CHROME_VERSION" with valid version.  Found this version for 95, which was what the error message said the driver required: 95.0.4638.54

http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_95.0.4638.54_amd64.deb


Let's try to combine this with the link I found in the other tutorial: 
wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm

https://dl.google.com/linux/direct/google-chrome-stable_95.0.4638.54_x86_64.rpm

For drivers, it looks like you can go here: https://chromedriver.storage.googleapis.com/

This shows all of the versions available to download with https://chromedriver.storage.googleapis.com/CHROME_VERSION/chromedriver_linux64.zip

There's these version archivers that might help: https://www.slimjet.com/chrome/google-chrome-old-version.php