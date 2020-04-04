import argparse
from downloader import FDownloader

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-i",
        "--input_type",
        type=str,
        default='file',
        help="Type of urls input. From .txt file (write <file>) or ' + \
            via console argument (write <console>). By default -- file")
    argparser.add_argument(
        "-f",
        "--file_urls",
        type=str,
        default='urls.txt',
        help=".txt file that contains list of urls for download if ' + \
            key [--input_type] == file. By default -- urls.txt")
    argparser.add_argument(
        "-u",
        "--urls_list",
        type=str,
        default=None,
        help="List of urls for download if key [--input_type] == console. ' + \
            By default - None.")    
    argparser.add_argument(
        "-l",
        "--login",
        type=str,
        default=None,
        help="Login or email for authentication")
    argparser.add_argument(
        "-p",
        "--password",
        type=str,
        default=None,
        help="Password for authentication")
    args = argparser.parse_args()

    if args.login is None or args.password is None:
        print('Error: login and password via keys [-l] and [-i] are necessary for download.')
    if args.input_type == 'console' and args.urls_list is None:
        print('Error: you must write urls with key [-f] if you are using [-i] == <console>')

if __name__ == '__main__':
    main()