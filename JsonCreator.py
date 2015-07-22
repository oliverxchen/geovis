import csv
import math

class JsonCreator:
    def __init__(self):
        self.early_csv = 'input_data/1971-1980.csv'
        self.late_csv = 'input_data/1991-2000.csv'
        self.loc_count_csv = 'output_data/counts.csv'
        self.json_file = '../oliverxchen.github.io/globe/twitter_vs_temp.json'
        self.colors = dict()
        self.__fill_colors()

        self.magnitudes = dict()
        self.__fill_magnitudes()

    def __fill_colors(self):
        early_temp = self.__get_temp(self.early_csv)
        late_temp = self.__get_temp(self.late_csv)

        for key in early_temp:
            if key in late_temp:
                self.colors[key] = late_temp[key] - early_temp[key]

        max_temp = max(self.colors.values())
        min_temp = min(self.colors.values())

        for key in self.colors:
            self.colors[key] = 0 + (self.colors[key] - min_temp) / (max_temp - min_temp) * 3

    def __get_temp(self, filename):
        temp = dict()

        with open(filename, 'rU') as temp_reader:
            temp_csv = csv.reader(temp_reader)
            lat_counter = 0
            for row in temp_csv:
                lat = 89.75 - lat_counter * 0.5
                lng_counter = 0
                for value in row:
                    lng = -179.75 + lng_counter * 0.5
                    if value != '-999':
                        temp[(lat, lng)] = float(value)
                    lng_counter += 1
                lat_counter += 1

        return temp


    def __fill_magnitudes(self):
        with open(self.loc_count_csv, 'r') as count_reader:
            csv_count = csv.DictReader(count_reader)
            for row in csv_count:
                lat = float(row['lat'])
                lng = float(row['long'])
                val = float(row['count'])
                self.magnitudes[(lat, lng)] = math.log(1 + val)

        max_logcount = max(self.magnitudes.values())
        for key in self.magnitudes:
            self.magnitudes[key] = 0.5 * self.magnitudes[key] / max_logcount

    def write_json(self):
        with open(self.json_file, 'w') as json_writer:
            json_writer.write('[["data",[')
            is_first = True
            for key in self.colors:
                if key in self.magnitudes:
                    if not is_first:
                        json_writer.write(',')
                    else:
                        is_first = False
                    json_writer.write('%s,%s,%s,%s' % (key[0], key[1], round(self.magnitudes[key], 2), round(self.colors[key], 2)))

                # else:
                #     if not is_first:
                #         json_writer.write(',')
                #     else:
                #         is_first = False
                #     json_writer.write('%s,%s,%s,%s' % (key[0], key[1], 0, round(self.colors[key], 2)))

            json_writer.write(']]]')


def main():
    jc = JsonCreator()
    jc.write_json()


if __name__ == '__main__':
    main()