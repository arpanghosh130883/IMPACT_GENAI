import os

PROJECT_ROOT_DIR = os.getcwd()
print('PROJECT_ROOT_DIR: ', PROJECT_ROOT_DIR)
APPS_DIR = os.path.dirname(os.path.abspath(__file__))
COMMON_APP_FILES_DIR =  os.path.join(APPS_DIR, "common_app_files")
APP_MEDIA_DIR =  os.path.join(COMMON_APP_FILES_DIR, "media")