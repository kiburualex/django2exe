# # should be deleted on once call of makemigrations

import os, subprocess
import json

class Database:
    def __init__(self):
        self.project_dir_name = 'app'

    def makeMigrationsAndmigrate(self):
        self.processconfiguration()
        try:
            subprocess.call(['python','..\\' + self.project_dir_name + '\manage.pyc','makemigrations'], shell=True)
            subprocess.call(['python','..\\' + self.project_dir_name + '\manage.pyc','migrate',], shell=True)
        except Exception, e:
            print (e)

    def processconfiguration(self):
        config_file_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'config','config.json'))
        try:
            with open(config_file_path) as data_file:    
                data = json.load(data_file)
                django_app_data = data["application"]
                self.project_dir_name = django_app_data["project_dir_name"]
        except Exception as e:
            print (e)


