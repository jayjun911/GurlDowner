# GurlDowner
It downloads individual files from Google Drive URLs one by one, using selenium. 

## Requirement
- python 3.x
- pip install selenium
- use matching chromedriver

## Execution
- GurlDowner.py [-h] [-d DOWNLOAD_PATH] [-hide] input_file

-h : help
-d : (optional) download path
-hide : (optional) running in headless mode 
-input_file : (required) text file that contains google drive download url

eg) python GurlDowner.py input.txt -d c:\tmp -hide 

## Note

- input file can contain non-url description. downloader skips if line doesn't start with 'http' thus, you can comment out url with any chars such as # or -

- for not existing files, it generates failed.txt. for timed out item, generates separate timed_out.txt

- timeout is set to 1 min, that's when no further download progress is observed for 1 min. 
