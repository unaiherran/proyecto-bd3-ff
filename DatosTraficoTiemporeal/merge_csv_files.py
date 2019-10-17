import glob
import logging
import os
import pandas as pd

logging.basicConfig(level=logging.INFO, filemode='a', format='%(asctime)s - %(message)s')

if __name__ == "__main__":
    logging.info('Merging realtime traffic data ...')
    os.chdir("csv")

    logging.info('Searching csv files ...')
    extension = 'csv'
    all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
    logging.info(f'Found {len(all_filenames)} files')

    logging.info('Mergering ...')
    # combine all files in the list
    combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames])

    logging.info('Processing ...')

    combined_csv['fecha'] = pd.to_datetime(combined_csv['fecha'])
    combined_csv['dia_semana'] = combined_csv['fecha'].dt.dayofweek
    combined_csv['mes'] = combined_csv['fecha'].dt.month
    combined_csv['hora'] = combined_csv['fecha'].dt.hour.map(str) + combined_csv['fecha'].dt.minute.apply(
        lambda x: '{0:0>2}'.format(x))

    # export to csv
    logging.info('Writing ...')
    combined_csv.to_csv("combined_csv.csv", index=False, encoding='utf-8-sig')

