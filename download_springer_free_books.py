#!/usr/bin/python
# -*- coding: utf-8 -*-

""" download_springer_free_books.py This script downloads the books graciously provided for free by Springer during the Covid-19 sanitary crisis"""

__author__ = "Paul Cottalorda"
__copyright__ = "Copyright 2020"

from pandas import read_excel, DataFrame
import pandas
from urllib3 import PoolManager 
from bs4 import BeautifulSoup
from typing import List, Dict
import argparse
from argparse import Namespace
import wget
import os
import json
import sys

#===---------------------------------------------------------------------------
#===--------------- Utility functions -----------------------------------------
#===---------------------------------------------------------------------------

def quote(s : str) -> str :
    return '"' + s + '"'

def fetch_book( book_title : str
              , url : str
              , local_folder : str
              , args : Namespace
              , manager : PoolManager
              , erroneous_frames : List[Dict[str, str]]
              ) -> None :
    """ The function queries the book url, analyzes it and if there are download links
       available it downloads the PDF and ePub (except if specified otherwise in the command line)
    """ 
    print('Book name:', book_title)
    print('Url:', url)
 
    try:
        html = manager.request('GET', url)
        hostname = 'http://link.springer.com'
        soup = BeautifulSoup(html.data, 'lxml')

        if not args.no_pdf : 
            pdf_links = set([hostname + x['href'] for x in soup.find_all('a') if x.get('data-track-action') == 'Book download - pdf'])
            if len(pdf_links) == 0 :
                raise Exception('No pdf link found! 1 expected. It can occur if the book is no longer available for free, please check the book on Springer\'s website')
            elif len(pdf_links) == 1 :
                pdf_link = pdf_links.pop()
                pdf_folder = os.path.join(local_folder, 'Downloaded books', 'Books')
                pdf_filename = os.path.join(pdf_folder, book_title + '.pdf')
                print('Downloading pdf at', quote(pdf_link), 'in', quote(pdf_filename))
                if not args.dry :
                    os.makedirs(pdf_folder, exist_ok=True)
                    wget.download(pdf_link, out = pdf_filename)
                    print() 
            else :
                raise Exception('Multiple pdf links found! 1 expected.')

        if not args.no_ebook :
            epub_links = set([hostname + x['href'] for x in soup.find_all('a') if x.get('data-track-action') == 'Book download - ePub'])
            if len(epub_links) == 0 :
                print('No ePub link found.')
            elif len(epub_links) == 1 :
                epub_link = epub_links.pop()
                epub_folder = os.path.join(local_folder, 'Downloaded books', 'eBooks')
                epub_filename = os.path.join(epub_folder, book_title + '.epub')
                print('Downloading epub at', '"' + epub_link + '"', 'in', '"' + epub_filename + '"')
                if not args.dry :
                    os.makedirs(epub_folder, exist_ok=True)
                    wget.download(epub_link, out = epub_filename)
                    print() 
            else :
                raise Exception('Multiple ePub links found! 0 or 1 expected.')

    except Exception as e :
        print('Error:', e, file = sys.stderr)
        print('Sadly, we were unable to download the book', quote(book_title), file = sys.stderr)
        error_data = { 'title'         : book_title
                     , 'url'           : url
                     , 'error_message' : str(e)}
        erroneous_frames.append(error_data)


def compute_book_name(book_info : pandas.core.frame.pandas) -> str :
    """ Uses the book entry in the excel sheet to deduce a proper name for the book.
        The book name is constituted of the book title, followed by the edition
        (if any) and the year of print.
        The name is also modified to be saveable i.e. forbitten character in file
        names are replaced with hyphens
    """
    book_name = book_info._1.replace('\\', '-')
    book_name = book_name.replace('/', '-')
    book_name = book_name.replace(':', ' -')
    book_name = book_name.replace('*', '-')
    book_name = book_name.replace('?', '-')
    book_name = book_name.replace('<', '-')
    book_name = book_name.replace('>', '-')
    book_name = book_name.replace('|', '-')
    book_name = book_name.strip()
    edition = book_info.Edition
    return (book_name + ', ' + edition).strip()

#===---------------------------------------------------------------------------
#===--------------- Script body -----------------------------------------------
#===---------------------------------------------------------------------------

def main() :

    parser = argparse.ArgumentParser(description = 'This script downloads the books graciously provided for free by Springer during '
                                                   'the Covid-19 sanitary crisis. It uses the Excel file provided with the script as '
                                                   'reference for the books to download in a folder named "Downloaded books" in the '
                                                   'script folder. By default both PDF and eBook version are downloaded.\n'
                                                   'If you don\'t want the whole library, you can remove the corresponding entries in '
                                                   'the Excel file.\n'
                                                   'At the end of the run, if errors have been encountered, an error_report.json file is saved '
                                                   'in the script repository listing the books that couldn\'t be downloaded. In this case '
                                                   'a launch with --repair will retry to download those files.')
    parser.add_argument('--no-ebook', action = 'store_true', help = 'Disables the download of eBooks', dest = 'no_ebook')
    parser.add_argument('--no-pdf', action = 'store_true', help = 'Disables the download of PDFs', dest = 'no_pdf')
    parser.add_argument('--dry-run', action = 'store_true', help = 'Simulates the execution of the program but nothing is created or downloaded', dest='dry')
    parser.add_argument('--repair', action = 'store_true', help = 'Retries to download the failed entries from a previous run')

    args : Namespace = parser.parse_args()

    local_folder : str = os.path.dirname(os.path.abspath(__file__))
    error_report_path : str = os.path.join(local_folder, 'error_report.json')
    excel_sheet_path : str = os.path.join(local_folder, 'Springer books list.xlsx')
    manager : PoolManager = PoolManager()
    erroneous_entries : List[Dict[str, str]] = []

    if args.repair :
        if os.path.isfile(error_report_path) :
            with open(error_report_path, 'r') as f:
                try:
                    error_list = json.load(f)
                    if isinstance(error_list, list) :
                        for error_dic in error_list :
                            print('===------------------------------')
                            fetch_book(error_dic['title'], error_dic['url'], local_folder, args, manager, erroneous_entries)
                        print('===------------------------------')
                    else:
                        raise Exception('The error report seems corrupted, we suggest you to relaunch a download of fix the report') 
                except KeyError:
                    raise Exception('The error report seems corrupted, we suggest you to relaunch a download of fix the report') 
                except Exception:
                    raise
    else:
        try:
            print('===--- Parsing', quote(excel_sheet_path))
            dataframe : DataFrame = read_excel(excel_sheet_path)

            for book_info in dataframe.itertuples():
                row_index: int = book_info.Index
                print('===------------------------------')
                try:
                    book_name: str = compute_book_name(book_info)
                    url: str = book_info.OpenURL
                    fetch_book(book_name, url, local_folder, args, manager, erroneous_entries)
                except Exception as e:
                    print('Error:', e, file = sys.stderr)
                    print('This is likely due to a corrupt entry in the Excel file, please check its correctness. The row number concerned is', row_index + 2, file = sys.stderr)
           
            print('===------------------------------')
            
        except Exception as e:
            print('Error:', e, file = sys.stderr)
            print('This is likely due to a problem with the Excel file given, please check its correctness', file = sys.stderr)

    if erroneous_entries and not args.dry : 
        with open(error_report_path, 'w') as f :
            json.dump(erroneous_entries, f)
    
    if args.repair and not erroneous_entries and not args.dry:
        if os.path.isfile(error_report_path):
            os.remove(error_report_path)
        


if __name__ == '__main__':
    main()
