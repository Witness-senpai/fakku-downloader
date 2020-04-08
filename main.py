import argparse
from downloader import (FDownloader,
                        program_exit,
                        TIMEOUT,
                        URLS_FILE,
                        COOKIES_FILE,
                    )


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-f",
        "--file_urls",
        type=str,
        default=URLS_FILE,
        help=f".txt file that contains list of urls for download if \
            key [--input_type] == file. By default -- {URLS_FILE}")
    argparser.add_argument(
        "-c",
        "--cookies_file",
        type=str,
        default=COOKIES_FILE,
        help=f"Bynary file that contains saved cookies for authentication. \
            By default -- {COOKIES_FILE}")         
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
    argparser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=TIMEOUT,
        help=f"Timeout in seconds for pauses beetween downloading pages \
            Increase this argument if quality of pages is bad. By default -- {TIMEOUT} sec")
    args = argparser.parse_args()

    try:
        with open(args.file_urls, 'r') as f:
            pass
    except FileNotFoundError:

        print(f'File {args.file_urls} are not exist in folder. \n  \
            Create him and write into list of manga, or for set urls \n  \
            and downloading via console use key [--input_type]')
        program_exit()
    loader = FDownloader(
        urls_file=args.file_urls,
        cookies_file=args.cookies_file,
        login=args.login,
        password=args.password,
        timeout=args.timeout,
    )

    try:
        with open(args.cookies_file, 'rb') as f:
            pass
    except FileNotFoundError:
        print('\nCookies file are not detected. Please, authenticate login ' + \
            'in next step and generate cookie for next runs.')
        loader.init_browser(headless=False, auth=True)   
    else:
        print(f'\nUsing cookies: {args.cookies_file}')
        loader.init_browser(headless=True, auth=False)
    loader.load_all()

if __name__ == '__main__':
    main()