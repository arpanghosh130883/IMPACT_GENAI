import os
from project_path import PROJECT_ROOT_DIR, APPS_DIR, APP_MEDIA_DIR

_media_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "media")

LOGO_FILE_PATH = os.path.join(APP_MEDIA_DIR, "modulr_logo_transparent.png")
FAVICON_FILE_PATH = os.path.join(APP_MEDIA_DIR, "modulr_favicon.png")
RECORD_AND_TRANSCRIBE = os.path.join(APP_MEDIA_DIR, "modulr_record_and_transcribe.png")