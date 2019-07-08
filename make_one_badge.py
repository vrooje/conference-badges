# If you just need to print all the badges I suggest using make_all_badges.py
# not that you can't use this, but this isn't efficient for multi-printing and you don't need all the bells and whistles anyway
# unless you're trying to print a slightly modified version of a badge vs what the spreadsheet would dictate
# e.g. if someone gets to the registration desk and says "actually I spelled my own name wrong, can you fix it", then this is your script
import sys, os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from make_badge import make_badge
from get_badge_spreadsheet import get_badge_spreadsheet, get_default_files, get_spreadsheet_colnames


reg_file, loc_list, council_list = get_default_files()

thecols = get_spreadsheet_colnames()

# we're using a lot of columns below but these in particular several times
# so doing this just makes the code a little bit easier to read
nameonbadge_col = thecols['nameonbadge_col']
surname_col     = thecols['surname_col']


# if updated info is present it's a dictionary with keys corresponding to items in the particular row of reg_info you want replaced
def make_one_badge(name_on_badge, reg_file=reg_file, loc_list=loc_list, council_list=council_list, updated_info=None, all_new_badge=False):

    if not all_new_badge:
        # reads spreadsheets, matches up lists for banner info, returns a dataframe
        reg_info = get_badge_spreadsheet(reg_file=reg_file, loc_list=loc_list, council_list=council_list)



        # extract just the badges we want (Name on Badge is unique for the above default spreadsheet, if it's not for you then this might not work)
        reg_this = reg_info[reg_info[nameonbadge_col] == name_on_badge]

        if len(reg_this) < 1:
            return "BADGE NAME %s NOT FOUND, not saved" % name_on_badge
        elif len(reg_this) > 1:
            print("WARNING: More than one badge found with name %s, something is weird (%d)" % (name_on_badge, len(reg_this)))


        # .squeeze() makes the row of the dataframe into a Series, which is what make_badge needs
        # don't just do reg_this.squeeze() because then it's a copy of a slice of a dataframe and pandas gets cross
        reg = reg_info[reg_info[nameonbadge_col] == name_on_badge].squeeze()


        # e.g. if reg_info has [nameonbadge_col] == 'Patrick Stweart' and he wants to fix that plus also have a bus pass, then
        # updated_info = {nameonbadge_col : 'Patrick Stewart', Travel' : 'Free local bus travel'}
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
                updated_info[nameonbadge_col] = arg[1].replace('"','')
            elif arg[0] == "surname":
                updated_info[surname_col] = arg[1].replace('"','')
            elif arg[0].lower().startswith("pronoun"):
                updated_info[thecols['pronouns_col']] = arg[1].replace('"','')
            elif arg[0].lower().startswith("affil"):
                updated_info[thecols['affiliation_col']] = arg[1].replace('"','')
            elif arg[0].lower().startswith("starter"):
                updated_info[thecols['starter_col']] = arg[1].replace('"','')
            elif arg[0].lower().startswith("main"):
                updated_info[thecols['main_col']] = arg[1].replace('"','')
            elif arg[0].lower().startswith("dessert"):
                updated_info[thecols['dessert_col']] = arg[1].replace('"','')
            elif arg[0].lower().startswith("bus"):
                if int(arg[1]) == 1:
                    updated_info[thecols['travelpref_col']] = 'Free local bus travel'
                else:
                    updated_info[thecols['travelpref_col']] = 'Neither'
            elif arg[0].startswith("castle"):
                if int(arg[1]) == 1:
                    updated_info[thecols['castle_col']] = 1.0
                else:
                    updated_info[thecols['castle_col']] = 2.0
            elif arg[0].startswith("pie"):
                if int(arg[1]) == 1:
                    updated_info[thecols['pie_col']] = 1.0
                else:
                    updated_info[thecols['pie_col']] = 0.0
            elif "dinner" in arg[0]:
                if int(arg[1]) == 1:
                    updated_info[thecols['dinner_col']] = 1.0
                else:
                    updated_info[thecols['dinner_col']] = 0.0
            elif "council" in arg[0]:
                if int(arg[1]) == 1:
                    updated_info[thecols['council_col']] = True
                else:
                    updated_info[thecols['council_col']] = False
            elif "loc" in arg[0]:
                if int(arg[1]) == 1:
                    updated_info[thecols['loc_col']] = True
                else:
                    updated_info[thecols['loc_col']] = False
            elif "press" in arg[0]:
                if int(arg[1]) == 1:
                    updated_info[thecols['press_col']] = True
                else:
                    updated_info[thecols['press_col']] = False
            elif "monday" in arg[0]:
                if int(arg[1]) == 1:
                    updated_info[thecols['dayattend_cols'][0]] = 1
                else:
                    updated_info[thecols['dayattend_cols'][0]] = 0
            elif "tuesday" in arg[0]:
                if int(arg[1]) == 1:
                    updated_info[thecols['dayattend_cols'][1]] = 1
                else:
                    updated_info[thecols['dayattend_cols'][1]] = 0
            elif "wednesday" in arg[0]:
                if int(arg[1]) == 1:
                    updated_info[thecols['dayattend_cols'][2]] = 1
                else:
                    updated_info[thecols['dayattend_cols'][2]] = 0
            elif "thursday" in arg[0]:
                if int(arg[1]) == 1:
                    updated_info[thecols['dayattend_cols'][3]] = 1
                else:
                    updated_info[thecols['dayattend_cols'][3]] = 0
            elif "all_days" in arg[0]:
                if int(arg[1]) == 1:
                    updated_info[thecols['fullrate_cols'][3]] = 1
                else:
                    updated_info[thecols['fullrate_cols'][3]] = 0
            elif "--all_new" in arg[0]:
                all_new_badge = True


    # check to see if we actually updated anything
    if len(updated_info.keys()) < 1:
        updated_info = None
    else:
        # check how many days are registered, if any
        n_days=0
        dayreg_keys = [thecols['dayattend_cols'][0], thecols['dayattend_cols'][1], thecols['dayattend_cols'][2], thecols['dayattend_cols'][3]]
        for daykey in dayreg_keys:
            if daykey in updated_info.keys():
                n_days += updated_info[daykey]
        if n_days > 0:
            updated_info[thecols['daycount_col']] = n_days

        if all_new_badge:
            # now we need to fill the rest of the series with blank values just so the make_badge function doesn't crash

            strcols = thecols['guestname_cols'].copy()
            strcols.extend([thecols['guest_col']])
            strcols.extend(thecols['gueststarter_cols'])
            strcols.extend(thecols['guestmain_cols'])
            strcols.extend(thecols['guestdessert_cols'])
            strcols.extend(thecols['fullrate_cols'][:-1])
            for thekey in strcols:
                updated_info[thekey] = ''

            intcols = thecols['lunch_cols'].copy()
            intcols.extend([thecols['dinner_col']]) 
            for thekey in intcols:
                updated_info[thekey] = 0

            # only fill these keys if they aren't already filled
            for thekey in [thecols['daycount_col'], thecols['dayattend_cols'][0], thecols['dayattend_cols'][1], thecols['dayattend_cols'][2], thecols['dayattend_cols'][3], thecols['fullrate_cols'][3], thecols['castle_col'], thecols['pie_col']]:
                if not thekey in updated_info.keys():
                    updated_info[thekey] = 0

            for thekey in [thecols['loc_col'], thecols['council_col'], thecols['press_col']]:
                if not thekey in updated_info.keys():
                    updated_info[thekey] = False

            for thekey in [thecols['givenname_col'], surname_col, thecols['pronouns_col'], thecols['travelpref_col'], thecols['starter_col'], thecols['main_col'], thecols['dessert_col']]:
                if not thekey in updated_info.keys():
                    updated_info[thekey] = ''

    # go for it
    make_one_badge(name_on_badge, updated_info=updated_info, all_new_badge=all_new_badge)







