import sys, os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from make_badge import make_badge
from get_badge_spreadsheet import get_badge_spreadsheet, get_default_files, get_spreadsheet_colnames


reg_file, loc_list, council_list = get_default_files()

thecols = get_spreadsheet_colnames()

# these are the only 2 columns we'll be using directly below
# so doing this just makes the code a little bit easier to read
nameonbadge_col = thecols['nameonbadge_col']
surname_col     = thecols['surname_col']

# reads spreadsheets, matches up lists for banner info, returns a dataframe
# this was originally just part of this script but I broke it out so I could also have a script to print 1 badge of my choosing
reg_info = get_badge_spreadsheet(reg_file=reg_file, loc_list=loc_list, council_list=council_list)

# checking for duplicate badges by name-on-badge
# by_badgename = reg_info[['Delegate Surname', 'Name on Badge']].groupby('Name on Badge').aggregate('count')
by_badgename = reg_info[[surname_col, nameonbadge_col]].groupby(nameonbadge_col).aggregate('count')

# used to keep a cumulative track of errors and also to print a big file with all badges at the end
imlist = []
errlist = []

print("Printing %d individual badges..." % len(reg_info))
for i, row in enumerate(reg_info.iterrows()):
    # pandas sends the row index and the row contents as a tuple so let's split them
    i_row, reg = row

    if (i > 0) & ((i + 1) % 25 == 0):
        print("... Badge %d of %d" % (i+1, len(reg_info)))
    print("              %s" % reg[nameonbadge_col])
    the_badge, the_filename, errormsg = make_badge(reg, both_sides=False)
    # if i == 0:
    #   break

    # keep a list of just the front of the badges
    imlist.append(the_badge[0])

    # keep track of errors and warnings
    if (len(errormsg) > 0):
        errlist.extend(errormsg)

    # add the badge to a PDF file? 

# print these before trying to make the full PDF because that takes time and you can review these in the meantime
print("There were %d errors and warnings:" % len(errlist))
for msg in errlist:
    print(msg)

if sum(by_badgename['Delegate Surname'] > 1) > 0:
    print("The following names had more than 1 badge associated:")
    print(by_badgename[by_badgename[surname_col] > 1])

# save them all to a single file
# which I thought the printer would want, but turns out, not? Keeping this in though.
# if I were printing them myself I'd print len(reg_info) copies of the back side of the badge
# and then load those into the printer so that the following file could print on the blank side of those pages.
# but I guess professional printers do it a different way
#
print(" ... individual badges printed, now saving a file with all badge front pages")
outputfile_save = "all_badges_front_only.pdf"
imlist[0].save(outputfile_save, save_all=True, append_images=imlist[1:], resolution=300)

print("%d individual badges saved" % len(reg_info))
print(" along with 1 file of all badge front pages at %s." % (outputfile_save))

#bye