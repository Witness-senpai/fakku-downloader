#!/usr/bin/env python3

import argparse
from pathlib import Path

from downloader import (
    FDownloader,
    program_exit,
    TIMEOUT,
    WAIT,
    URLS_FILE,
    DONE_FILE,
    COOKIES_FILE,
    ROOT_MANGA_DIR,
    MAX,
)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-z",
        "--collection_url",
        type=str,
        default=None,
        help=f"Give a collection URL that will be parsed and loaded into urls.txt \
            The normal operations of downloading manga images will not happen while this \
            parameter is set. \
            By default -- None, process the urls.txt instead",
    )
    argparser.add_argument(
        "-f",
        "--file_urls",
        type=str,
        default=URLS_FILE,
        help=f".txt file that contains list of urls for download \
            By default -- {URLS_FILE}",
    )
    argparser.add_argument(
        "-d",
        "--done_file",
        type=str,
        default=DONE_FILE,
        help=f".txt file that contains list of urls that have been downloaded. \
            This is used to resume in the event that the process stops midway. \
            By default -- {DONE_FILE}",
    )
    argparser.add_argument(
        "-c",
        "--cookies_file",
        type=str,
        default=COOKIES_FILE,
        help=f"Binary file that contains saved cookies for authentication. \
            By default -- {COOKIES_FILE}",
    )
    argparser.add_argument(
        "-o",
        "--output_dir",
        type=str,
        default=ROOT_MANGA_DIR,
        help=f"The directory that will be used as the root of the output \
            By default -- {ROOT_MANGA_DIR}",
    )
    argparser.add_argument(
        "-l",
        "--login",
        type=str,
        default=None,
        help="Login or email for authentication",
    )
    argparser.add_argument(
        "-p", "--password", type=str, default=None, help="Password for authentication"
    )
    argparser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=TIMEOUT,
        help=f"Timeout in seconds for loading first manga page. \
            Increase this argument if quality of pages is bad. By default -- {TIMEOUT} sec",
    )
    argparser.add_argument(
        "-w",
        "--wait",
        type=float,
        default=WAIT,
        help=f"Wait time in seconds for pauses beetween downloading pages \
            Increase this argument if you become blocked. By default -- {WAIT} sec",
    )
    argparser.add_argument(
        "-m",
        "--max",
        type=int,
        default=MAX,
        help=f"Max number of volumes to download at once \
            Set this argument if you become blocked. By default -- No limit",
    )
    args = argparser.parse_args()

    file_urls = Path(args.file_urls)
    if args.collection_url:
        Path(args.file_urls).touch()
    elif not file_urls.is_file() or file_urls.stat().st_size == 0:
        print(
            f"File {args.file_urls} does not exist or empty.\n"
            + "Create it and write the list of manga urls first.\n"
            + "Or run this again with the -z parameter with a collection_url to download urls first."
        )
        program_exit()

    # Create empty done.text if it not exists
    if not Path(args.done_file).is_file():
        Path(args.done_file).touch()

    loader = FDownloader(
        urls_file=args.file_urls,
        done_file=args.done_file,
        cookies_file=args.cookies_file,
        root_manga_dir=args.output_dir,
        login=args.login,
        password=args.password,
        timeout=args.timeout,
        wait=args.wait,
        _max=args.max,
    )

    if not Path(args.cookies_file).is_file():
        print(
            f"Cookies file({args.cookies_file}) are not detected. Please, "
            + "login in next step for generate cookie for next runs."
        )
        loader.init_browser(headless=False)
    else:
        print(f"Using cookies file: {args.cookies_file}")
        loader.init_browser(headless=True)

    if args.collection_url:
        loader.load_urls_from_collection(args.collection_url)
    else:
        loader.load_all()


if __name__ == "__main__":
    main()
