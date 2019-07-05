# If you just need to print all the badges I suggest using make_all_badges.py
# not that you can't use this, but this isn't efficient for multi-printing and you don't need all the bells and whistles anyway
# unless you're trying to print a slightly modified version of a badge vs what the spreadsheet would dictate
# e.g. if someone gets to the registration desk and says "actually I spelled my own name wrong, can you fix it", then this is your script
import sys, os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from make_badge import make_badge
from get_badge_spreadsheet import get_badge_spreadsheet

# CSV with registration info
# reg_file = "NAM - Delegate test badges.csv"
reg_file = "NAM - Delegate Registrations 3rd June.csv"
# reg_file = "NAM_Delegate_test_badges_meals_lunches.csv"


# list of email addresses of LOC members (who get a special badge flag)
loc_list = "NAM_loc_list.csv"

# list of names of RAS council members (who get a special badge flag)
# The RAS didn't seem forthcoming with a list of email addresses so let's just hope a name search works
# this list is structured like council_first_name,council_surname
council_list = "RAS_council_list.csv"


# if updated info is present it's a dictionary with keys corresponding to items in the particular row of reg_info you want replaced
def make_one_badge(name_on_badge, reg_file=reg_file, loc_list=loc_list, council_list=council_list, updated_info=None, all_new_badge=False):

    if not all_new_badge:
        # reads spreadsheets, matches up lists for banner info, returns a dataframe
        reg_info = get_badge_spreadsheet(reg_file=reg_file, loc_list=loc_list, council_list=council_list)



        # extract just the badges we want (Name on Badge is unique for the above default spreadsheet, if it's not for you then this might not work)
        reg_this = reg_info[reg_info['Name on Badge'] == name_on_badge]

        if len(reg_this) < 1:
            return "BADGE NAME %s NOT FOUND, not saved" % name_on_badge
        elif len(reg_this) > 1:
            print("WARNING: More than one badge found with name %s, something is weird (%d)" % (name_on_badge, len(reg_this)))


        # .squeeze() makes the row of the dataframe into a Series, which is what make_badge needs
        # don't just do reg_this.squeeze() because then it's a copy of a slice of a dataframe and pandas gets cross
        reg = reg_info[reg_info['Name on Badge'] == name_on_badge].squeeze()


        # e.g. if reg_info has ['Name on Badge'] == 'Patrick Stweart' and he wants to fix that plus also have a bus pass, then
        # updated_info = {'Name on Badge' : 'Patrick Stewart', Travel' : 'Free local bus travel'}
        # and if you also want to make sure that "Stewart" prints in bigger font as is usual, add 'Delegate Surname' : 'Stewart' as well
        # then when you pass that dictionary to this, it will update the info in the Series before it makes the badge
        # note it won't update the spreadsheet file so that will still be wrong
        if updated_info is not None:
            for thekey in updated_info.keys():
                reg[thekey] = updated_info[thekey]

    else:
        # this is never gonna work but let's see what happens
        reg = pd.Series(updated_info)



    the_badge, the_filename, errormsg = make_badge(reg, make_pdf=False, both_sides=True, verbose=True)

    the_filename_new = the_filename.replace(".pdf", "_updated.pdf")
    the_badge[0].save(the_filename_new, save_all=True, append_images=the_badge[1:], resolution=300)

    print("Badge printed to %s" % the_filename_new)

    return the_filename_new





# if this is a command-line call etc., pass things to the reduce_survey function

if __name__ == '__main__':

    try:
        namestr   = sys.argv[1]
    except:
        print("Usage: python %s name=\"Name on Badge\" [optional arguments]" % sys.argv[0])
        print("   name is the CURRENT name on the badge (so we can find it in the spreadsheet)")
        print("   If no optional arguments are specified, this will just print a badge using the spreadsheet info.")
        print("   Optional arguments:")
        print("   name_new=\"New Name on Badge\"")
        print("   surname=\"New Surname\" (so that end of name_new or name prints in larger font)")
        print("   pronoun=\"New pronouns\"")
        print("   affiliation=\"New Affiliation\"")
        print("   bus_pass=1/0    to add/remove the bus pass icon (1 for add, 0 for remove)")
        print("   castle=1/0      to add/remove the castle tour icon")
        print("   pie=1/0         to add/remove the pie & quiz icon")
        print("   dinner=1/0      to add/remove the awards dinner icon")
        print("   council=1/0     to add/remove the RAS Council banner")
        print("   press=1/0       to add/remove the Press banner")
        print("   loc=1/0         to add/remove the LOC banner")
        print("   all_days=1/0    to make it a full-conference registration or individual days")
        print("   monday=1/0      to add day-registration for day 1")
        print("   tuesday=1/0     to add day-registration for day 2")
        print("   wednesday=1/0   to add day-registration for day 3")
        print("   thursday=1/0    to add day-registration for day 4")
        #print("   NOTE that press badges are currently generated separately from this script.")
        print("\n   Dinner menu items, lunch choices etc. aren't binding from the badge so can't be reprinted at this time.")
        exit(0)

    arg = namestr.split('=')
    name_on_badge = arg[1].replace('"', '')
    updated_info = {}
    all_new_badge = False
    is_press=False

    # check for other command-line arguments
    if len(sys.argv) > 2:
        # if there are additional arguments, loop through them
        for i_arg, argstr in enumerate(sys.argv[2:]):
            arg = argstr.split('=')

            if arg[0]   == "name_new":
                updated_info['Name on Badge'] = arg[1].replace('"','')
            elif arg[0] == "surname":
                updated_info['Delegate Surname'] = arg[1].replace('"','')
            elif arg[0].lower().startswith("pronoun"):
                updated_info['Preferred Pronouns'] = arg[1].replace('"','')
            elif arg[0].lower().startswith("affil"):
                updated_info['Affiliation'] = arg[1].replace('"','')
            elif arg[0].lower().startswith("starter"):
                updated_info['Starter'] = arg[1].replace('"','')
            elif arg[0].lower().startswith("main"):
                updated_info['Main'] = arg[1].replace('"','')
            elif arg[0].lower().startswith("dessert"):
                updated_info['Dessert'] = arg[1].replace('"','')
            elif arg[0].lower().startswith("bus"):
                if int(arg[1]) == 1:
                    updated_info['Travel'] = 'Free local bus travel'
                else:
                    updated_info['Travel'] = 'Neither'
            elif arg[0].startswith("castle"):
                if int(arg[1]) == 1:
                    updated_info['Lancaster Castle 01.07.2019'] = 1.0
                else:
                    updated_info['Lancaster Castle 01.07.2019'] = 2.0
            elif arg[0].startswith("pie"):
                if int(arg[1]) == 1:
                    updated_info['Pie & Quiz 02.07.2019'] = 1.0
                else:
                    updated_info['Pie & Quiz 02.07.2019'] = 0.0
            elif "dinner" in arg[0]:
                if int(arg[1]) == 1:
                    updated_info['RAS Award Dinner 03.07.2019'] = 1.0
                else:
                    updated_info['RAS Award Dinner 03.07.2019'] = 0.0
            elif "council" in arg[0]:
                if int(arg[1]) == 1:
                    updated_info['is_council'] = True
                else:
                    updated_info['is_council'] = False
            elif "loc" in arg[0]:
                if int(arg[1]) == 1:
                    updated_info['is_loc'] = True
                else:
                    updated_info['is_loc'] = False
            elif "press" in arg[0]:
                if int(arg[1]) == 1:
                    updated_info['is_press'] = True
                else:
                    updated_info['is_press'] = False
            elif "monday" in arg[0]:
                if int(arg[1]) == 1:
                    updated_info['Attending 1st'] = 1
                else:
                    updated_info['Attending 1st'] = 0
            elif "tuesday" in arg[0]:
                if int(arg[1]) == 1:
                    updated_info['Attending 2nd'] = 1
                else:
                    updated_info['Attending 2nd'] = 0
            elif "wednesday" in arg[0]:
                if int(arg[1]) == 1:
                    updated_info['Attending 3rd'] = 1
                else:
                    updated_info['Attending 3rd'] = 0
            elif "thursday" in arg[0]:
                if int(arg[1]) == 1:
                    updated_info['Attending 4th'] = 1
                else:
                    updated_info['Attending 4th'] = 0
            elif "all_days" in arg[0]:
                if int(arg[1]) == 1:
                    updated_info['Full - Rate 4'] = 1
                else:
                    updated_info['Full - Rate 4'] = 0
            elif "--all_new" in arg[0]:
                all_new_badge = True


    # check to see if we actually updated anything
    if len(updated_info.keys()) < 1:
        updated_info = None
    else:
        # check how many days are registered, if any
        n_days=0
        dayreg_keys = ['Attending 1st', 'Attending 2nd', 'Attending 3rd', 'Attending 4th']
        for daykey in dayreg_keys:
            if daykey in updated_info.keys():
                n_days += updated_info[daykey]
        if n_days > 0:
            updated_info['How many days?'] = n_days

        if all_new_badge:
            # now we need to fill the rest of the series with blank values just so the make_badge function doesn't crash
            for thekey in ['RAS Awards Dinner Guest', 'RAS Awards Guest Name', 'Guest Starter', 'Guest Main', 'Guest Dessert', 'Full - Rate 1', 'Full - Rate 2', 'Full - Rate 3']:
                updated_info[thekey] = ''

            for thekey in ['Outreach Lunch - Tue', 'Publishing Lunch - Wed', 'Diversity Lunch - Mon', 'Exoplanet Lunch - Thur', 'Careers Lunch - Thur', 'Joint MIST/UKSP Lunch - Wed', 'RAS Award Dinner 03.07.2019']:
                updated_info[thekey] = 0

            # only fill these keys if they aren't already filled
            for thekey in ['How many days?', 'Attending 1st', 'Attending 2nd', 'Attending 3rd', 'Attending 4th', 'Full - Rate 4', 'Lancaster Castle 01.07.2019', 'Pie & Quiz 02.07.2019']:
                if not thekey in updated_info.keys():
                    updated_info[thekey] = 0

            for thekey in ['is_loc', 'is_council', 'is_press']:
                if not thekey in updated_info.keys():
                    updated_info[thekey] = False

            for thekey in ['Delegate First Name', 'Delegate Surname', 'Preferred Pronouns', 'Travel', 'Starter', 'Main', 'Dessert']:
                if not thekey in updated_info.keys():
                    updated_info[thekey] = ''

    # go for it
    make_one_badge(name_on_badge, updated_info=updated_info, all_new_badge=all_new_badge)







