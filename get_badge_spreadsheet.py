import sys, os
import pandas as pd


# CSV with registration info
# reg_file = "NAM - Delegate test badges.csv"
reg_file_default = "NAM - Delegate Registrations 3rd June.csv"
# reg_file = "NAM_Delegate_test_badges_meals_lunches.csv"


# list of email addresses of LOC members (who get a special badge flag)
loc_list_default = "NAM_loc_list.csv"

# list of names of RAS council members (who get a special badge flag)
# The RAS didn't seem forthcoming with a list of email addresses so let's just hope a name search works
# this list is structured like council_first_name,council_surname
council_list_default = "RAS_council_list.csv"


def get_badge_spreadsheet(reg_file=reg_file_default, loc_list=loc_list_default, council_list=council_list_default):


	loc_info = pd.read_csv(loc_list)
	council_info = pd.read_csv(council_list)

	reg_info_in = pd.read_csv(reg_file)
	# In [3]: reg_info_in.columns
	# Out[3]: 
	# Index(['﻿Order Number', 'Delegate First Name', 'Delegate Surname',
	#        'Billing Address ', 'Billing Postcode', 'Telephone', 'Email',
	#        'Full - Rate 1', 'Full - Rate 2', 'Full - Rate 3', 'Full - Rate 4',
	#        'Day Rate 1', 'Day Rate 2', 'Day Rate 3', 'Day Rate 4',
	#        'How many days?', 'Attending 1st ', 'Attending 2nd ', 'Attending 3rd',
	#        'Attending 4th', 'Diversity Lunch - Mon', 'Outreach Lunch - Tue ',
	#        'Joint MIST/UKSP Lunch - Wed', 'Publishing Lunch - Wed',
	#        'Careers Lunch - Thur', 'Exoplanet Lunch - Thur',
	#        'Dietary Requirements', 'Disability Requirements', 'B&B 30.06.2019',
	#        'Evening Meal 30.06.2019', 'B&B 01.07.2019', 'Evening meal 01.07.2019',
	#        'B&B 02.07.2019', 'Evening meal 02.07.2019', 'B&B 03.07.2019',
	#        'Evening meal 03.07.2019', 'B&B 04.07.2019',
	#        'Lancaster Castle 01.07.2019', 'Pie & Quiz 02.07.2019',
	#        'RAS Award Dinner 03.07.2019', 'Starter', 'Main', 'Dessert',
	#        'RAS Awards Dinner Guest ', 'RAS Awards Guest Name ', 'Guest Starter',
	#        'Guest Main ', 'Guest Dessert', 'Name on Badge ', 'Preferred Pronouns',
	#        'Affiliation ', 'Abstract ID', 'RAS Membership Number', 'Travel',
	#        'Name of person booking'],
	#       dtype='object')


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

