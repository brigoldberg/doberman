# Downloading Tools

### bulk_downloader.py

Inputs a file of ticker symbols.  Script will check if the ticker symbol is already 
in the HDF5 file.  If the ticker is not a key in the HDF5 file, it will be downloaded.

Future version will have date range checking of HDF5 tickers.


### downloader.py

Downloads an individual ticker symbol to CSV file and imports key/data to a HDF5 file.


### list_hdf_keys.py

Lists all keys in a HDF5 file.


### read_ohlc.py

Prints the first and last OHLC record for a ticker symbol.
