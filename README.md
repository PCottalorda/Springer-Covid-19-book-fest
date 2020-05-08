# Springer-Covid-19-book-fest
This repository provides a Python 3 script that allows one to download all the books that Springer made graciously available for free during the Covid-19 sanitary crisis. This offer is not expected to last after July 2020.  

## Prerequisite
This python script requires the following packages that can be installed with pip through
```
pip install pandas urllib3 bs4 typing argparse wget lxml
```

## Usage
To download the script type
```
git clone https://github.com/PCottalorda/Springer-Covid-19-book-fest
cd Springer-Covid-19-book-fest
```
You can filter the books you want by editing the Excel file "Springer books list.xlsx" and removing the undesired rows.

Then, run the script with
```
python download_springer_free_books.py
```
or
```
python3 download_springer_free_books.py
```
depending on the default python version you are running.

We encourage you to check the help before running the script with
```
python download_springer_free_books.py -h
```
You can also launch a dry run i.e. a run that downloads nothing but tries to connect to the springer website and display what the script will do with the command
```
python download_springer_free_books.py --dry-run
```
Springer provides its books in both ePub and PDF format. The files weight around 11 Go, hence the process can take several hours. We provide options if you don't want the ePubs or PDFs but please be careful that some books are only available in PDF.
```
python download_springer_free_books.py --no-ebook
```
```
python download_springer_free_books.py --no-pdf
```

After the run the books are downloaded in a folder called "Downloaded books" in the script folder. If there is a problem during the process or if some books are not available for free anymore, an error report is generated in the script folder. It is a JSON easily readable. You can try to re-download the failed cases with
```
python download_springer_free_books.py --repair
```

Good readings !
