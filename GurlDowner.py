import os
import sys

from GurlDownSelenium import GurlDownSelenium


def main():
    gurlLoader = GurlDownSelenium()
    try:
        f = open(sys.argv[1])
    except IndexError:
        print("Input file name must be specified")
        print("eg) gurlDowner input.txt")
    except FileNotFoundError:
        print("Input file not found: {0}".format(sys.argv[1]))
    gdrive_urls = f.readlines()

    gdrive_urls = [x for x in gdrive_urls if x.startswith('https:')]
    total_length = len(gdrive_urls)
    current_index = 1
    for url_link in gdrive_urls:
        print("Downloading {0} out of {1}.... {2}".format(current_index, total_length, url_link.rstrip('\n\r')))
        gurlLoader.set_url(url_link).download_file()
        current_index = current_index + 1


if __name__ == "__main__":
    main()

