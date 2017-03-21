# udacity-multi-user-blog


The goal of this project is to create a simple multi-user blog along the lines of "Medium".

Users should be able to create an account with login/logout functionality, and create/edit/delete posts and comments.

Checkout the live version of this project at https://udacity-multi-user-blog-162006.appspot.com

Usage

Clone the repository:

git clone https://github.com/chezze911/udacity-multi-user-blog

Add the repository as an application in your Google App Engine Launcher

Create a file called secret.txt in your project's root directory with the following format:

 secret = "ENTER_A_SECRET_KEY_HERE"

Get into the project folder in the terminal window:  

cd udacity-multi-user-blog

then run:

dev_appserver.py .

This will render a local version of the site. To access the site: https://localhost:8080.

To check the instance: https://localhost:8000



Setting up your computer (if necessary):

Install Python if necessary.

Install Google App Engine SDK.

Open GoogleAppEngineLauncher.

Sign Up for a Google App Engine Account.

Create a new project in Google’s Developer Console using a unique name.

Create a new project from the file menu and choose this project's folder.

Deploy this project by pressing deploy in GoogleAppEngineLauncher.

When developing locally, click “Run” in GoogleAppEngineLauncher and visit localhost:Port in your favorite browser, where Port is the number listed in GoogleAppEngineLauncher’s table under the column Port.
