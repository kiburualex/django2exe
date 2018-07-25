# Packager is a project to help you distribute your django project as exe

### Credits:

	- https://algotronics.wordpress.com/2015/10/23/dj2exe/

	- WinPython

	- Cefpython3


### Setting Up:

	- Run setup.bat to install django and cefpython3 and other custom requirements in requirements/setup_requirements.txt

	- After successful installation you can delete setup.bat and requirements folder

	- The app folder is a sample django project which you can delete

	- Paste your Django project folder where app folder is placed(it is recommended to compile all .py files to .pyc and delete all .py files, this will protect your source code.If you don't django2exe will compile all .py to .pyc but won't delete your .py files)

	- In the config folder paste the icon you want on the application window

	- Edit the config.json to get it all running

		-project_dir_name -> Name of your django projec folder

		Rest all settings are self-explanatory

	- Install all your pip requirements and migrations using the terminal which can be launched by executing py-dist\scripts\cmd.bat

	- When all done, try launching the your application with launch.bat



### Contents:
	setup.bat and setup_requirements.txt:
		
		- sets up django and cefpython3 using pip.DELETE THESE FILES IN PRODUCTION DISTRIBUTIONS

	launchapp.bat
		
		- script to launch the application with a console to see log errors.DELETE THIS FILE IN PRODUCTION DISTRIBUTIONS

	launchapp.exe
		
		- launchapp.bat converted to exe with invisible console.Rename this to your application name

	app/

		- Just a sample Django project for structure reference

	config/

		- contains icon for application window

		- config.json for settings for the application

	img/

		- contains image for the png splashcreen

	py-dist/

		- The py-dist folder has portable python with some extra packages like pip installed

		- There is also a run.py in py-dist folder which launches the web server and the windows application.It also
		takes care of killing processes on exit

			What run.py does

				- A application is made with pyqt
				- A cef component is placed into the application using cefpython3
				- A manage.pyc runserver process is spawned on port 8000 on localhost
				- cef webkit is made to navigate to 127.0.0.1:8000

				NOTE: IF YOU WANT TO NAVIGATE TO SOME OTHER URL OR WANT TO BIND TO SOME OTHER PORT FEEL FREE TO EDIT run.py

		- There is a migrate.py in py-dist folder which makes migrations and migrates models to the database. Runs only once the gets deleted
		since there is no need to make migrations every time one is running. script backup in the migrate-backup folder

		scripts/

			- env.bat
				setups portable python environment

			- cmd.bat
				setups portable python environment and starts cmd in the environment

			- python
				portable python console
	py-to-exe/

		- contains the app.py file which is to be converterd to app.exe using pyinstaller

	requirements/

		- contains environment requirements for the django app
		- base_requirements.txt
                                base requirements that are a must for the app includes django <=1.11 and cefpython
                                NB: python environment set is python2.7 hence django 2.0 cannot work
		- setup_requirements
				calls the baserequirements.txt and one can add additional requierements depending on
				their application.
