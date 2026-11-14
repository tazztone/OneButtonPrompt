import csv
import random
import os
import shutil

_CSV_CACHE = {}
_ARTIST_CATEGORY_CACHE = {}
_ARTIST_DESC_CACHE = {}


def _file_stat(path):
    if path and os.path.isfile(path):
        return (True, os.stat(path).st_mtime_ns)
    return (False, 0)

def random_read_from_csv(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Script directory
    full_path = os.path.join(script_dir, "./csvfiles/" )
    with open(full_path + filename + ".csv", "r",encoding="utf8") as csv_file:
            csv_reader = csv.reader(csv_file)
            output = (random.choice([line[0] for line in csv_reader]))
    return output

def add_from_csv(completeprompt, csvfilename, addcomma, prefix, suffix):
        randomreadfromcsv = random_read_from_csv(csvfilename)
        #print(csvfilename+ ": " + randomreadfromcsv)
        addtoprompt = prefix + " " + randomreadfromcsv + " " + suffix
        if(addcomma == 1):
                return ", ".join([completeprompt,addtoprompt])
        return " ".join([completeprompt,addtoprompt])

def _read_rows_from_file(filepath, delimiter, listoflistmode, skipheader, gender, lowerandstrip):
        rows = []
        with open(filepath, "r", newline="", encoding="utf8") as file:
                reader = csv.reader(file, delimiter=delimiter)
                if skipheader:
                        next(reader, None)
                if listoflistmode:
                        return list(reader)
                for row in reader:
                        if not row:
                                continue
                        if (
                                gender != "all" and (row[1] == gender or row[1] == "genderless" or row[1] == "both")
                                or gender == "all"
                        ):
                                rows.append(row[0].lower().strip() if lowerandstrip == 1 else row[0])
        return rows


def csv_to_list(csvfilename, antilist=[], directory="./csvfiles/", lowerandstrip=0, delimiter=";", listoflistmode=False, skipheader=False, gender="all", insanitylevel=-1, bypass_subsets=False, rng=None, copy_list=True):
        replacing = False
        orig_csvfilename = csvfilename
        userfilesdirectory = "./userfiles/"
        userfilereplacename = csvfilename + "_replace.csv"
        lightfilename = csvfilename + "_light.csv"
        mediumfilename = csvfilename + "_medium.csv"
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(script_dir, directory)
        userfilesfolder = os.path.join(script_dir, userfilesdirectory)
        resolved_directory = directory

        is_standard_dir = directory in ("./csvfiles/", "./csvfiles/special_lists/", "./csvfiles/templates/")
        replace_path = os.path.join(userfilesfolder, userfilereplacename) if is_standard_dir else None

        # check if there is a replace file
        if is_standard_dir:
                if replace_path and os.path.isfile(replace_path):
                        full_path = userfilesfolder
                        resolved_directory = userfilesdirectory
                        csvfilename = csvfilename + "_replace"
                        replacing = True

                # Go check for light or medium files if there is no override and there is an insanitylevel
                if not replacing and not bypass_subsets and insanitylevel > 0:
                        _rng = rng if rng is not None else random
                        if insanitylevel < 4 and os.path.isfile(os.path.join(full_path, lightfilename)):
                                csvfilename = csvfilename + "_light"
                                replacing = True
                        # under 7, then only SOMETIMES take the full list
                        elif insanitylevel < 7 and _rng.randint(0, 13) < 12 and os.path.isfile(os.path.join(full_path, mediumfilename)):
                                csvfilename = csvfilename + "_medium"
                                replacing = True

        csv_path = os.path.join(full_path, csvfilename + ".csv")
        txt_path = os.path.join(full_path, csvfilename + ".txt")
        addon_dir_eligible = directory in ("./csvfiles/", "./csvfiles/special_lists/")
        addon_path = os.path.join(userfilesfolder, orig_csvfilename + "_addon.csv") if addon_dir_eligible else None

        cache_key = (
                resolved_directory,
                csvfilename,
                lowerandstrip,
                delimiter,
                listoflistmode,
                skipheader,
                gender,
                _file_stat(csv_path),
                _file_stat(txt_path),
                _file_stat(addon_path),
                _file_stat(replace_path),
        )

        cached = _CSV_CACHE.get(cache_key)
        if cached is None:
                csvlist = []
                if os.path.isfile(csv_path):
                        csvlist.extend(_read_rows_from_file(csv_path, delimiter, listoflistmode, skipheader, gender, lowerandstrip))
                if os.path.isfile(txt_path):
                        csvlist.extend(_read_rows_from_file(txt_path, delimiter, listoflistmode, skipheader, gender, lowerandstrip))
                if addon_path and os.path.isfile(addon_path):
                        addon_rows = _read_rows_from_file(addon_path, delimiter, listoflistmode, skipheader, gender, lowerandstrip)
                        if listoflistmode:
                                csvlist.append(addon_rows)
                        else:
                                csvlist.extend(addon_rows)

                # remove duplicates, but check only for lowercase stuff
                if not listoflistmode:
                        deduplicated_list = []
                        lowercase_elements = set()
                        for element in csvlist:
                                lowercase_element = element.lower()
                                if lowercase_element not in lowercase_elements:
                                        lowercase_elements.add(lowercase_element)
                                        deduplicated_list.append(element)
                else:
                        deduplicated_list = csvlist

                cached = tuple(deduplicated_list)
                _CSV_CACHE[cache_key] = cached

        if antilist and not listoflistmode:
                anti_set = frozenset(antilist)
                filtered = [el for el in cached if el.lower().strip() not in anti_set]
                return filtered if copy_list else tuple(filtered)

        return list(cached) if copy_list else cached

def artist_category_by_category_csv_to_list(csvfilename,artist):
        csvlist = []
        mediumlist = []
        descriptionlist = []
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(script_dir, "./csvfiles/" )
        with open(full_path + csvfilename + ".csv", "r", newline="",encoding="utf8") as file:
                reader = csv.DictReader(file, delimiter=",")
                for row in reader:
                        if(row["Artist"] == artist):
                                csvlist.append(row["Tags"])
                                mediumlist.append(row["Medium"])
                                descriptionlist.append(row["Description"])
        return csvlist, mediumlist, descriptionlist

def artist_category_csv_to_list(csvfilename,category):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, "./csvfiles/", csvfilename + ".csv")
        cache_key = (csvfilename, category, _file_stat(filepath))
        cached = _ARTIST_CATEGORY_CACHE.get(cache_key)
        if cached is None:
                csvlist = []
                with open(filepath, "r", newline="", encoding="utf8") as file:
                        reader = csv.DictReader(file, delimiter=",")
                        for row in reader:
                                if row[category] == "1":
                                        csvlist.append(row["Artist"])
                cached = tuple(csvlist)
                _ARTIST_CATEGORY_CACHE[cache_key] = cached
        return list(cached)

def artist_descriptions_csv_to_list(csvfilename):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, "./csvfiles/", csvfilename + ".csv")
        cache_key = (csvfilename, _file_stat(filepath))
        cached = _ARTIST_DESC_CACHE.get(cache_key)
        if cached is None:
                csvlist = []
                with open(filepath, "r", newline="", encoding="utf8") as file:
                        reader = csv.DictReader(file, delimiter=",")
                        for row in reader:
                                csvlist.append(row["Description"])
                cached = tuple(csvlist)
                _ARTIST_DESC_CACHE[cache_key] = cached
        return list(cached)

def load_config_csv(suffix=""):
        csvlist = []
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_path_config_file = os.path.join(script_dir, "./userfiles/" )
        full_path_default_config_file = os.path.join(script_dir, "./csvfiles/config/" )
        if(suffix != ""):
                config_file = full_path_config_file + 'config_' + suffix + '.csv'
                default_config_file = full_path_default_config_file + 'default_config_' + suffix + '.csv'
        else:
                config_file = full_path_config_file + 'config.csv'
                default_config_file = full_path_default_config_file + 'default_config.csv'

        if not os.path.exists(config_file):
                shutil.copy2(default_config_file, config_file)
                print("Config file created.")


        with open(config_file, "r", newline="",encoding="utf8") as file:
                reader = csv.DictReader(file, delimiter=";")
                csvlist = [list(row.values()) for row in reader if not any(value.startswith('#') for value in row.values())]
        return csvlist

def load_negative_list():
        primerlist = []
        negativelist = []
        primeraddonlist = []
        negativeaddonlist = []

        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        full_path_default_negative_file = os.path.join(script_dir, "./csvfiles/special_lists/" )
        negative_file = full_path_default_negative_file + 'negativewords.csv'

        full_path_replace_negative_file = os.path.join(script_dir, "./userfiles/" )
        replace_negative_file = full_path_replace_negative_file + 'negativewords_replace.csv'

        full_path_addon_negative_file = os.path.join(script_dir, "./userfiles/" )
        addon_negative_file = full_path_addon_negative_file + 'negativewords_addon.csv'


        if(os.path.isfile(replace_negative_file)):
                negative_file = replace_negative_file

        with open(negative_file, "r", newline="",encoding="utf8") as file:
                reader = csv.DictReader(file, delimiter=";")
                primerlist = [row["primer"] for row in reader]
        with open(negative_file, "r", newline="",encoding="utf8") as file:
                reader = csv.DictReader(file, delimiter=";")
                negativelist = [row["negative"] for row in reader]


        if(os.path.isfile(addon_negative_file)):
                with open(addon_negative_file, "r", newline="",encoding="utf8") as file:
                        reader = csv.DictReader(file, delimiter=";")
                        primeraddonlist = [row["primer"] for row in reader]
                with open(addon_negative_file, "r", newline="",encoding="utf8") as file:
                        reader = csv.DictReader(file, delimiter=";")
                        negativeaddonlist = [row["negative"] for row in reader]
        
        primerlist += primeraddonlist
        negativelist += negativeaddonlist


        return primerlist, negativelist

def load_all_artist_and_category():
        artistlist = []
        categorylist = []
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        full_path_default_artist_file = os.path.join(script_dir, "./csvfiles/" )
        artist_file = full_path_default_artist_file + 'artists_and_category.csv'

        with open(artist_file, "r", newline="",encoding="utf8") as file:
                reader = csv.DictReader(file, delimiter=",")
                artistlist = [row["Artist"] for row in reader]
        with open(artist_file, "r", newline="",encoding="utf8") as file:
                reader = csv.DictReader(file, delimiter=",")
                categorylist = [row["Tags"] for row in reader]

        return artistlist, categorylist

def sort_and_dedupe_csv_file():
        tokenlist = csv_to_list(csvfilename="tokens",skipheader=False)
        tokenlist = sorted(set(tokenlist))
        newlist = []
        for i in tokenlist:
                j = i.lower()
                result = all(c == i[0] for c in i)
                if result:
                        print("String {} have all characters same".format(i))
                else:
                        newlist.append(j)
        
        
        newlist = sorted(set(newlist))

        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        full_path = os.path.join(script_dir, "./csvfiles/special_lists/tokenwriter.csv" )
        with open(full_path, 'w', encoding="utf8") as fp:
                for item in newlist:
                        # write each item on a new line
                        fp.write("%s\n" % item)


# sort_and_dedupe_csv_file()

