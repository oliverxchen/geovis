import csv
import array


class CountLatLong:
    def __init__(self):
        self.match_file = 'output_data/matches.csv'
        self.count_file = 'output_data/counts.csv'
        self.lat_long_count = dict()
        self.__read_match_file()

    @staticmethod
    def __round_lat_long(input_string):
        output = round((float(input_string) - 0.25) * 2, 0)
        return output / 2 + 0.25

    def __add_to_count(self, lat, lng, count):
        try:
            rounded_lat = self.__round_lat_long(lat)
            rounded_long = self.__round_lat_long(lng)
        except:
            print 'Could not parse: ' + '%s, %s, %s' % (lat, lng, count)
            return

        lat_long = (rounded_lat, rounded_long)

        if lat_long in self.lat_long_count:
            self.lat_long_count[lat_long] += int(count)
        else:
            self.lat_long_count[lat_long] = int(count)

    def __read_match_file(self):
        with open(self.match_file, 'r') as match_reader:
            csv_reader = csv.DictReader(match_reader)
            for row in csv_reader:
                if len(row[' latitude']) == 0:
                    continue
                self.__add_to_count(row[' latitude'], row[' longitude'], row[' count'])

    def write_count_file(self):
        with open(self.count_file, 'w') as count_writer:
            count_writer.write('lat,long,count\n')
            for key in self.lat_long_count:
                count_writer.write('%s,%s,%s\n' % (key[0], key[1], self.lat_long_count[key]))


def main():
    cll = CountLatLong()
    cll.write_count_file()

if __name__ == '__main__':
    main()