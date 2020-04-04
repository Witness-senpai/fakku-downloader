import argparse
from downloader import FDownloader, program_exit


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-f",
        "--file_urls",
        type=str,
        default='urls.txt',
        help=".txt file that contains list of urls for download if ' + \
            key [--input_type] == file. By default -- urls.txt")   
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
        print('Error: login and password via keys [-l] and [-p] are necessary for download.')
        program_exit()
    else:
        try:
            with open(args.file_urls, 'r') as f:
                pass
        except IOError:
            print(f'File {args.file_urls} are not exist in folder. \n' + \
                'Create him and write into list of manga, or for set urls \n' + \
                'and downloading via console use key [--input_type]')
            program_exit()
    loader = FDownloader(args.file_urls)
    loader.load_all()

if __name__ == '__main__':
    main()