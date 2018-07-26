## Convert the app.py python file to app.exe


### Setting Up:

	- install pyinstaller using: pip install pyinstall

	- type command pyinstaller --onefile --windowed <your_script_name>.py
		This will create a standalone executable in the dist directory of your script folder. 
		Don’t worry, if the folder doesn’t exist it will create one automatically.
		— onefile - Tells PyInstaller to create only one file. 
			    If you don’t specify this, the libraries will be distributed as separate files  
                            along with the executable.
		— windowed- Tells PyInstaller to hide the console.
	- copy the .exe file just created and paste it in the root folder
