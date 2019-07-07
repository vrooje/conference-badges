import sys, os
import pandas as pd


# CSV with registration info
reg_file_default = "registration_spreadsheet_example.csv"


# list of email addresses of LOC members (who get a special badge flag)
# it's technically a csv but with 1 column so just 1 email per line, no commas
# but with the first line having column names
loc_list_default = "LOC_list.csv"

# list of names of RAS council members (who get a special badge flag)
# The RAS didn't seem forthcoming with a list of email addresses so let's just hope a name search works
# this list is structured like council_first_name,council_surname
# This is quite specific to this example conference but easily substituted for a list of VIPs etc for yours
#   (in which case you'll also want to edit the banner image that goes with it)
council_list_default = "RAS_council_list.csv"


def get_badge_spreadsheet(reg_file=reg_file_default, loc_list=loc_list_default, council_list=council_list_default):


	loc_info = pd.read_csv(loc_list)
	council_info = pd.read_csv(council_list)

	reg_info_in = pd.read_csv(reg_file)


	# remove leading and trailing spaces from column names because those will drive me up the wall
	colnames_nosp = [q.strip() for q in reg_info_in.columns]
	reg_info_in.columns = colnames_nosp

	# match up council_members
	reg_info_temp = pd.merge(reg_info_in, council_info, how="left", left_on="Delegate Surname", right_on="council_surname")

	# match up LOC members
	reg_info = pd.merge(reg_info_temp, loc_info, how="left", left_on="Email", right_on="loc_email")
	# non-matches are NaN by default so fill with empty string to prevent crashing on next line
	reg_info['loc_email'].fillna(value='', inplace=True)
	reg_info['council_surname'].fillna(value='', inplace=True)

	reg_info['is_loc']     = [len(q) > 1 for q in reg_info.loc_email]
	reg_info['is_council'] = [len(q) > 1 for q in reg_info.council_surname]

	return reg_info

