import os.path, argparse
from GurlDownSelenium import GurlDownSelenium


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str, help="download list file")
    parser.add_argument("-d", "--download_path", type=str, help="specify download directory")
    parser.add_argument("-hide", "--headless", action='store_true', help="headless option")
    parser.add_argument("-s", "--skip", type=str, help="skips first N entries")
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print("Input file not found: {0}".format(args.input_file))
        exit(0)

    if args.download_path and not os.path.exists(args.download_path):
        print("Download location \'{0}\' doesn't exist!".format(args.download_path))
        exit(0)

    print("Input File: {0}".format(args.input_file))
    print("Download Location: {0}".format(args.download_path))

    gurl_loader = GurlDownSelenium(args.headless)
    gurl_loader.set_download_location(args.download_path)

    f = open(args.input_file)
    gdrive_urls = f.readlines()

    gdrive_urls = [x for x in gdrive_urls if x.startswith('http')]
    total_length = len(gdrive_urls)
    current_index = 1
    if args.skip is not None:
        skip_counter = int(args.skip)

    for url_link in gdrive_urls:

        if skip_counter > 0:
            current_index = current_index + 1
            skip_counter = skip_counter - 1
            continue
        print("Downloading {0} out of {1}.... {2}".format(current_index, total_length, url_link.rstrip('\n\r')))
        gurl_loader.set_url(url_link).download_file()
        current_index = current_index + 1


    print("\n\rDownload Completed!")
    gurl_loader.save_log()


if __name__ == "__main__":
    main()

