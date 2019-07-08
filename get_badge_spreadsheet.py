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

# just so other programs can pull these default filenames from here instead of having to define them themselves
def get_default_files():
    return reg_file_default, loc_list_default, council_list_default



# define column names here and only here
# this isn't just reading a spreadsheet and getting a list of colnames
# it's which of those colnames is needed for which tasks
# which are numbers, which are strings, that sort of thing.
def get_spreadsheet_colnames():

    thecols = {

        'orderno_col'     : '﻿Order Number',
        'givenname_col'   : 'Delegate First Name',
        'surname_col'     : 'Delegate Surname',
        'email_col'       : 'Email',
        'nameonbadge_col' : 'Name on Badge',
        'pronouns_col'    : 'Preferred Pronouns',
        'affiliation_col' : 'Affiliation',
        'travelpref_col'  : 'Travel',

        'castle_col'      : 'Lancaster Castle 01.07.2019',
        'pie_col'         : 'Pie & Quiz 02.07.2019',
        'pieguest_col'    : 'Pie & Quiz Guest Name',
        'dinner_col'      : 'RAS Award Dinner 03.07.2019',
        'starter_col'     : 'Starter',
        'main_col'        : 'Main',
        'dessert_col'     : 'Dessert',
        'guest_col'       : 'RAS Awards Dinner Guest',

        'daycount_col'    : 'How many days?',


        'loc_col'         : 'is_loc',
        'council_col'     : 'is_council',
        'locemail_col'    : 'loc_email',
        'councilname_col' : 'council_surname',

        'press_col'       : 'is_press',


        'fullrate_cols'          : ['Full - Rate 1', 'Full - Rate 2', 'Full - Rate 3', 'Full - Rate 4'],
        'dayrate_cols'           : ['Day Rate 1', 'Day Rate 2', 'Day Rate 3', 'Day Rate 4'],
        'dayattend_cols'         : ['Attending 1st', 'Attending 2nd', 'Attending 3rd', 'Attending 4th'],
        'lunch_cols'             : ['Diversity Lunch - Mon', 'Outreach Lunch - Tue',
           'Joint MIST/UKSP Lunch - Wed', 'Publishing Lunch - Wed',
           'Careers Lunch - Thur', 'Exoplanet Lunch - Thur'],
        'requirements_cols'      : ['Dietary Requirements', 'Disability Requirements'],
        'guestname_cols'         : ['RAS Awards Guest Name', 'RAS Awards Guest 2 Name', 'RAS Awards Guest 3 Name', 
            'RAS Awards Guest 4 Name', 'RAS Awards Guest 5 Name'],
        # apparently we didn't have any further disability requirements cols for guests? also apparently there's a typo in that column header
        # it didn't matter -- that info was used by conference services but not printed on badges so isn't relevant here
        'guestrequirements_cols' : ['Disability Requirments Guest', 
            'Dietary Requirements Guest', 'Dietary Requirements Guest 2', 'Dietary Requirements Guest 3', 
            'Dietary Requirements Guest 4', 'Dietary Requirements Guest 5'],
        'gueststarter_cols'      : ['Guest Starter', 'Guest 2 Starter', 'Guest 3 Starter', 'Guest 4 Starter', 'Guest 5 Starter'],
        'guestmain_cols'         : ['Guest Main', 'Guest 2 Main ', 'Guest 3 Main ', 'Guest 4 Main', 'Guest 5 Main'],
        'guestdessert_cols'      : ['Guest Dessert', 'Guest 2 Dessert', 'Guest 3 Dessert', 'Guest 4 Dessert', 'Guest 5 Dessert']
       
    }

    return thecols




def get_badge_spreadsheet(reg_file=reg_file_default, loc_list=loc_list_default, council_list=council_list_default):


    loc_info = pd.read_csv(loc_list)
    council_info = pd.read_csv(council_list)

    reg_info_in = pd.read_csv(reg_file)


    thecols = get_spreadsheet_colnames()


    # remove leading and trailing spaces from column names because those will drive me up the wall and break everything
    colnames_nosp = [q.strip() for q in reg_info_in.columns]
    reg_info_in.columns = colnames_nosp

    # match up council_members
    reg_info_temp = pd.merge(reg_info_in, council_info, how="left", left_on=thecols['surname_col'], right_on=thecols['councilname_col'])

    # match up LOC members
    reg_info = pd.merge(reg_info_temp, loc_info, how="left", left_on=thecols['email_col'], right_on=thecols['locemail_col'])
    # non-matches are NaN by default so fill with empty string to prevent crashing on next line
    reg_info[thecols['locemail_col']].fillna(value='', inplace=True)
    reg_info[thecols['councilname_col']].fillna(value='', inplace=True)

    reg_info[thecols['loc_col']]     = [len(q) > 1 for q in reg_info[thecols['locemail_col']]]
    reg_info[thecols['council_col']] = [len(q) > 1 for q in reg_info[thecols['councilname_col']]]

    return reg_info

