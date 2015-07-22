# coding=utf-8
import csv
import Levenshtein as lev

class GeoCode:
    def __init__(self):
        self.threshhold_jw = 0.93
        self.raw_location_file = 'input_data/locations.csv'
        self.city_list_file = 'input_data/cities15000.txt'
        self.country_list_file = 'input_data/countries.csv'
        self.output_file = 'output_data/matches_2.csv'

        self.countries = dict()
        self.iso_countries = dict()
        self.__init_countries()
        self.country_list = self.countries.keys()

        self.cities = dict()
        self.__init_cities()
        self.city_list = self.cities.keys()

    def __init_countries(self):
        with open(self.country_list_file, 'r') as country_reader:
            country_reader.readline()
            country_csv = csv.reader(country_reader)
            for row in country_csv:
                if len(row[1]) == 0:
                    continue
                name = self.__standarize_string(row[3])
                lattitude = float(row[1])
                longitude = float(row[2])
                self.countries[name] = (lattitude, longitude)
                self.iso_countries[row[0]] = name

    def __init_cities(self):
        with open(self.city_list_file, 'r') as city_reader:
            city_csv = csv.reader(city_reader, delimiter='\t')
            for row in city_csv:
                name = self.__standarize_string(row[1])
                ascii_name = self.__standarize_string(row[2])
                iso_country = row[8]
                if iso_country not in self.iso_countries:
                    country = ''
                else:
                    country = self.iso_countries[iso_country]

                latitude = float(row[4])
                longitude = float(row[5])

                # hack: this ignores that you can have different cities with the same name
                # (in different states/countries). Latest city will overwrite earlier cities
                self.cities[name] = (country, latitude, longitude)
                if ascii_name != name:
                    self.cities[ascii_name] = (country, latitude, longitude)

    # replace multiple spaces with single space
    # change to all lower case
    # remove leading and trailing spaces
    @staticmethod
    def __standarize_string(input):
        return " ".join(input.split()).lower().strip()

    def __best_city_match(self, raw):
        max_jw = 0
        max_city = ''
        for city in self.city_list:
            jw = lev.jaro_winkler(city, raw)
            if jw > max_jw:
                max_jw = jw
                max_city = city

        if max_jw > self.threshhold_jw:
            country, latitude, longitude = self.cities[max_city]
            return max_city, country, latitude, longitude
        else:
            return None, None, None, None

    def __best_country_match(self, raw):
        max_jw = 0
        max_country = ''
        for country in self.country_list:
            jw = lev.jaro_winkler(country, raw)
            if jw > max_jw:
                max_jw = jw
                max_country = country

        if max_jw > self.threshhold_jw:
            latitude, longitude = self.countries[max_country]
            return max_country, max_country, latitude, longitude
        else:
            return None, None, None, None

    def match_from_file(self):
        loc_match = dict()
        loc_count = dict()

        with open(self.raw_location_file, 'rU') as raw_reader:
            raw_reader.readline()
            csv_raw = csv.reader(raw_reader)
            line_counter = 0
            inter_batch_counter = 0
            for row in csv_raw:
                line_counter += 1
                inter_batch_counter += 1
                if len(row) == 0:
                    continue

                raw_location = self.__standarize_string(row[0])
                if raw_location in loc_match:
                    loc_count[raw_location] += 1
                else:
                    loc_match[raw_location] = self.__match_standardized_string(raw_location)
                    loc_count[raw_location] = 1

                if inter_batch_counter >= 1000:
                    print line_counter
                    inter_batch_counter = 0

        self.__write_matches(loc_match, loc_count)

    def __write_matches(self, loc_match, loc_count):
        alphabetized = sorted(loc_count.keys())

        with open(self.output_file, 'w') as output_writer:
            output_writer.write('input string, place, country, latitude, longitude, count\n')
            for raw in alphabetized:
                count = loc_count[raw]
                place, country, latitude, longitude = loc_match[raw]
                if place is None:
                    place = ''
                if country is None:
                    country = ''
                if latitude is None:
                    latitude = ''
                if longitude is None:
                    longitude = ''
                output_writer.write('"%s","%s","%s",%s,%s,%s\n' % (raw, place, country, latitude, longitude, count))

    def __match_standardized_string(self, raw_location):

        latitude = None
        longitude = None
        country = None
        place = None

        if raw_location.startswith("Üt:"):
            latlong = raw_location[4:].split(',')
            try:
                latitude = float(latlong[0])
                longitude = float(latlong[1])
            except:
                print "Üt: match failed: " + raw_location
        else:
            tokens = raw_location.split(',')
            n_tokens = len(tokens)

            # check if single token is a country name (takes precedence over cities)
            if n_tokens == 1:
                place, country, latitude, longitude = self.__best_country_match(tokens[0])
            # check if they have directly input the lat/long in decimal format.
            elif n_tokens == 2:
                try:
                    latitude = float(tokens[0])
                    longitude = float(tokens[1])
                except:
                    latitude = None
                    longitude = None

            # if it doesn't match a country and isn't decimal format latlong, just check the first token
            # Improvements: check other tokens, validate with country, check alternate names, etc
            if latitude is None:
                place, country, latitude, longitude = self.__best_city_match(tokens[0])

            # if no city match could be found, try countries in the last token
            if latitude is None:
                place, country, latitude, longitude = self.__best_country_match(tokens[n_tokens-1])

        return place, country, latitude, longitude


def main():
    gc = GeoCode()
    gc.match_from_file()


if __name__ == '__main__':
    main()
