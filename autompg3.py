import os
import sys
import csv
import re
from collections import namedtuple
from collections import defaultdict
import logging
import requests
import argparse
import matplotlib.pyplot as plt

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#file handler

fh = logging.FileHandler('autompg3.log', 'w')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

class AutoMPG:
    def __init__(self, make, model, year, mpg):
        self.make = make
        self.model = model
        self.year = year
        self.mpg = mpg

    def __repr__(self):
        return f'AutoMPG("{self.make}", "{self.model}", {self.year}, {self.mpg})'

    def __str__(self):
        return f'{self.make} {self.model} ({self.year}) - {self.mpg} mpg'

    def __eq__(self, other):
        if not isinstance(other, AutoMPG):
            return NotImplemented
        return (self.make, self.model, self.year, self.mpg) == (other.make, other.model, other.year, other.mpg)

    def __lt__(self, other):
        if not isinstance(other, AutoMPG):
            return NotImplemented
        return (self.make, self.model, self.year, self.mpg) < (other.make, other.model, other.year, other.mpg)

    def __hash__(self):
        return hash(self.make, self.model, self.year, self.mpg)

class AutoMPGData:
    def __init__(self):
        logging.debug('Starting __init__ in autoMPGData class')
        self.data = []
        self._load_data()

    def __iter__(self):
        return iter(self.data)

    def _load_data(self):
        logging.debug('Checking if original file exists')
        if not os.path.exists('auto-mpg.data.txt'):
            self._get_data()

        logging.debug('Start _load_data...')
        if not os.path.exists('auto-mpg.clean.txt'):
            self._clean_data()
            logger.debug('A new file was created')

        Record = namedtuple('Record',
                            ['mpg', 'cylinders', 'displacement', 'horsepower', 'weight', 'acceleration', 'year',
                             'origin', 'car_names'])

        make_dict = {
            'chevroelt': 'chevrolet',
            'chevy': 'chevrolet',
            'maxda': 'mazda',
            'mercedesbenz': 'mercedes',
            'toyouta': 'toyota',
            'vokswagen': 'volkswagen',
            'vw': 'volkswagen'
        }

        with open('auto-mpg.clean.txt', 'r') as file:
            reader = csv.reader(file, delimiter =' ', skipinitialspace=True)
            for row in reader:
                record = Record(*row)
                make, *model = record.car_names.split()
                model = " ".join(model)
                # clean make data
                logger.debug('The beginning of cleaning make data')
                if make in make_dict:
                    make = make_dict[make]
                logger.debug('End of cleaning make data')
                self.data.append(AutoMPG(make, model, int(record.year), float(record.mpg)))
        logging.debug('Ending _load_data...')

    def _clean_data(self):
        logging.debug('Starting _clean_data...')
        with open('auto-mpg.data.txt', 'r') as file:
            with open('auto-mpg.clean.txt', 'w') as out:
                for line in file:
                    line = line.expandtabs()
                    cleaned_line = re.sub(' +', ' ', line)
                    out.write(cleaned_line)
        logging.debug('Ending _clean_data...')

    def sort_by_default(self):
        list.sort(self.data)

    def sort_by_year(self):
        return list.sort(self.data, key = lambda carYear: (carYear.year, carYear.make, carYear.model, carYear.mpg))

    def sort_by_mpg(self):
        return list.sort(self.data, key = lambda carMPG: (carMPG.mpg, carMPG.make, carMPG.model, carMPG.year))

    def mpg_by_year(self):
        mpgs_by_year = defaultdict(list)
        for car in self.data:
            mpgs_by_year[car.year].append(car.mpg)
        return {year: sum(mpgs) / len(mpgs) for year, mpgs in mpgs_by_year.items()}

    def mpg_by_make(self):
        mpgs_by_make = defaultdict(list)
        for car in self.data:
            mpgs_by_make[car.make].append(car.mpg)
        return {make: sum(mpgs) / len(mpgs) for make, mpgs in mpgs_by_make.items()}


    def _get_data(self):
        logger.debug('Data is being retrieved from website')
        url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data'
        data = requests.get(url)
        with open('auto-mpg.data.txt', 'wb') as file:
            file.write(data.content)
        logger.debug('Data has been written to file')

def main():
    parser = argparse.ArgumentParser(description='Analyze Auto MPG data set, format exampple is "python autompg3.py print --sort year --plot"')
    parser.add_argument('command', choices=['print', 'mpg_by_year', 'mpg_by_make'], help='Command to execute')
    parser.add_argument('-s', '--sort', help='Sort order', choices=['year', 'mpg', 'default'])
    parser.add_argument('-o', '--ofile', dest='ofile', help='Name of output file, if not specified, output is sent to stdout')
    parser.add_argument('-p', '--plot', dest='plot', action='store_true', help='Outputs a matplotlib plot')

    args = parser.parse_args()
    auto_data = AutoMPGData()

    if args.command == 'print':

        if args.sort == 'year':
            auto_data.sort_by_year()
        elif args.sort == 'mpg':
            auto_data.sort_by_mpg()
        elif args.ofile:
            with open(args.ofile, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['mpg', 'cylinders', 'displacement', 'horsepower', 'weight', 'acceleration', 'year',
                             'origin', 'make', 'model'])
                for car in auto_data:
                    writer.writerow([car.mpg, car.cylinder, car.displacement, car.horsepower, car.weight, car.acceleration,
                                     car.year, car.origin, car.make, car.model])
        else:
            auto_data.sort_by_default()

        for car in auto_data:
            print(car)

    elif args.command == 'mpg_by_year':
        mpg_by_year = auto_data.mpg_by_year()
        if args.ofile:
            with open(args.ofile, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['year', 'mpg'])
                for year, mpg in sorted(mpg_by_year.items()):
                    writer.writerow([year, mpg])

        else:
            print('MPG by year:')
            for year, mpg in sorted(mpg_by_year.items()):
                print(f'{year}: {mpg:.2f}')

        if args.plot:
            plt.plot(list(mpg_by_year.keys()), list(mpg_by_year.values()))
            plt.xlabel('Year')
            plt.ylabel('Average MPG')
            plt.title('Average MPG by Year')
            plt.show()

    elif args.command == 'mpg_by_make':
        mpg_by_make = auto_data.mpg_by_make()
        if args.ofile:
            with open(args.ofile, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['make', 'model'])
                for make, mpg in sorted(mpg_by_make.items()):
                    writer.writerow([make, mpg])
        else:
            print('MPG by make:')
            for make, mpg in sorted(mpg_by_make.items()):
                print(f'{make}: {mpg:.2f}')

        if args.plot:
            plt.plot(list(mpg_by_make.keys()), list(mpg_by_make.values()))
            plt.xlabel('Make')
            plt.ylabel('Average MPG')
            plt.title('Average MPG by Make')
            plt.show()

main()