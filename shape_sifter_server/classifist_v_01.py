# Current Status:
# Works to get part info when supplied a part name
# Does not do much else
# Does however, load the config file, and we are ready to build the sorting function

import datetime
import pandas
import shape_sifter_tools

# initMM
# initBB
# initTaxi
# load CFG
# begin

# loop
# check for part from MM
# Check for message from BB
# check for config change

# Check MM
# read from MM
# check if value has changed
# get part info from cfg file
# compare part info against each bin, from 1 to x


# converter for config file data frame
df_config_converters = {
    'bin_number': str,
    'sort_type': str,
    'sort_data': str
                    }

# converter for parts list data frame
df_part_db_converters = {
    'category_number': str,
    'category_name': str,
    'part_number': str,
    'part_name': str,
    'part_weight': float,
    'part_dimensions': str,
    'other_data': str
                    }

# load config file into a pandas data frame
ss_config = pandas.read_csv('ssConfig.csv', sep=',', encoding='ANSI', engine='python', error_bad_lines=0, na_values='?', converters=df_config_converters)

# load partslist file into a pandas data frame
ss_part_db = pandas.read_csv('partlist.csv', sep=',', encoding='ANSI', engine='python', error_bad_lines=0, na_values='?', converters=df_part_db_converters)



# This function returns the attributes of a part in a string
# Needs to be changed to some more useful datatype, like an array, perhaps.
# workingPartNum is read from the MM and compared to the last part, and dropped if it is different
# We will need to change this to accomodate timestamps in the future.
# If we dont use timestamps, consecutive parts of the same number will be dropped.

readPartNum = "3004"
prevPartNum = "0"

#print('{0:%Y-%m-%d %H:%M:%S:%f}'.format(datetime.datetime.now()))

# run the part info retrieval
# returns a DF containing part info
workingPartArray = shape_sifter_tools.classifist(readPartNum, ss_config, ss_part_db)

print("function complete")
print(workingPartArray)

print('{0: %H:%M:%S:%f}'.format(datetime.datetime.now()))
