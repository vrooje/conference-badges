import sys, os
import pandas as pd, numpy as np
from PIL import Image, ImageDraw, ImageFont
import textwrap
from get_badge_spreadsheet import get_spreadsheet_colnames

#https://stackoverflow.com/questions/27327513/create-pdf-from-a-list-of-images

# make a badge for NAM 2019: 2 pages (1 double-sided)


thecols = get_spreadsheet_colnames()


# paper size in inches 
paper_size = [8.27, 11.69]  #A4

# resolution of image (dots per inch)
dpi = 300

# format as tuple for creating images later
page_pix = (int(dpi*paper_size[0]), int(dpi*paper_size[1]))

# upper left and lower right pixel coords of different page areas:
# Q1 is the badge with name, affiliation, bus pass etc (upper left)
# Q2 is the same badge with name, etc. except with sponsor logos at bottom replacing event icons (upper right)
# Q3 is actually Q3 + Q4, i.e. the lower half of the page

q1_ul   = (0, 0)
q1_lr   = (int(page_pix[0]/2)-1, int(page_pix[1]/2)-1)
q1_ur   = (q1_lr[0], q1_ul[1])
q1_ll   = (q1_ul[0], q1_lr[1])
q1_size = (q1_lr[0] - q1_ul[0], q1_lr[1] - q1_ul[1])

q2_ul   = (int(page_pix[0]/2)  , 0)
q2_lr   = (int(page_pix[0])  , int(page_pix[1]/2)-1)
q2_ur   = (q2_lr[0], q2_ul[1])
q2_ll   = (q2_ul[0], q2_lr[1])
q2_size = (q2_lr[0] - q2_ul[0], q2_lr[1] - q2_ul[1])

q3_ul   = (0                   , int(page_pix[1]/2))
q3_lr   = (int(page_pix[0])-1  , int(page_pix[1])  -1)
q3_size = (q3_lr[0] - q3_ul[0], q3_lr[1] - q3_ul[1])


col_loc     = "#B51700" # dark red
col_press   = "#1DB100" # green
col_student = "#017B76" # dark teal
col_council = "#004D7F" # moderately dark blue
col_mon     = "#00A2FF" # bright blue
col_tues    = "#61D836" # bright green
col_wed     = "#FAE232" # yellow
col_thur    = "#EF5FA7" # bright pink

# regular text is black with red headers, text over banners is white
textcol     = "#000000"
headercol   = "#B51700" # = col_loc
bannercol   = "#FFFFFF"

# this is what my system has for Helvetica Neue
# if this breaks for you check that this font file actually exists in your fonts folder
the_font = "HelveticaNeue.ttc"

# font sizes - taken from the full-res keynote file, as are starting positions
tsize = {
    "given_name"  : 134,
    "surname"     : 178,
    "affiliation" : 94,
    "pronouns"    : 76,
    "header"      : 48,
    "regular"     : 40,
    "header_sm"   : 42,
    "regular_sm"  : 32
}

tstart_y = {
    "given_name"  : 549,
    "surname"     : 710,
    "affiliation" : 1008,
    "pronouns"    : 1145,
}

# set up fonts dictionary
fonts = {}
for thekey in tsize.keys():
    fonts[thekey] = ImageFont.truetype(the_font, tsize[thekey])

font_heights = {}
for thekey in tsize.keys():
    txtsize = fonts[thekey].getsize("Lancaster University")
    font_heights[thekey] = txtsize[1] #+ txtsize[1]/2  #1.5 line spacing


# List of possible postnominals that might require modification to name printing
# Add whatever you want to this list
postnominals = ['FRAS', 'MBE', 'OBE', 'CBE', 'FRS']



# images for various things
# these should be pre-sized & at 300 dpi to show up how you want them to
img_path       = "images/"
badge_path_out = "individual_badges/"

# starter image for the front with logos, cut lines, schedule etc
# basically everything that is static on the badge front is here
front_start_path = img_path + "NAM badges - blank layout front.png"

# the back of the badges is the same for everyone so this is all we should need
back_path        = img_path + "NAM badges - layout back.png"

# we don't need these anymore since we've incorporated them into the above
#logo_main_path   = img_path + "NAM2019FullLockup_badgeprint.png"
#sponsors_front_path = img_path + "sponsor_logo_front_badgeprint.png"
#cut_lines_path = img_path + "cut_lines_badgeprint.png"
#schedule_path  = img_path + "NAM2019_schedule_badgeprint.png"

# banners for different groups
loc_banner_path     = img_path + "banner_label_loc_badgeprint.png"
council_banner_path = img_path + "banner_label_council_badgeprint.png"
press_banner_path   = img_path + "banner_label_press_badgeprint.png"
student_banner_path = img_path + "banner_label_student_badgeprint.png"


loc_line_width = 75  # the width of the lines drawing the rectangles for the LOC boxes



# positions of things
margin_buffer = 60  # about 5 mm in pixels

textwidth_max = q1_size[0] - 2*margin_buffer
textsize_max = (textwidth_max, q1_size[1])

# these positions and sizes are taken from the full-res keynote file
banner_y      = 1298
banner_pos_q1 = (q1_ul[0], banner_y)
banner_pos_q2 = (q2_ul[0], banner_y)

the_days  = ['mon', 'tue', 'wed', 'thu']
day_y     = 1406
day_x = {
    'mon' : 1276,
    'tue' : 1573,
    'wed' : 1869,
    'thu' : 2166
}
day_path = {
    'mon' : img_path + "monday_badgeprint.png",
    'tue' : img_path + "tuesday_badgeprint.png",
    'wed' : img_path + "wednesday_badgeprint.png",
    'thu' : img_path + "thursday_badgeprint.png"    
}

icon_pos = {
    'bus'    : (84, 1544),
    'pie'    : (432, 1555),
    'castle' : (720, 1554),
    'dinner' : (1009, 1549)
}
icon_path = {
    'bus'    : img_path + "bus_icon_badgeprint.png",
    'pie'    : img_path + "pie_icon_badgeprint.png",
    'castle' : img_path + "castle_icon_badgeprint.png",
    'dinner' : img_path + "awards_dinner_icon_badgeprint.png"    
}

# these are not quite from the keynote file but were modified as needed while debugging
dinner_menu_size = (872, 590)
dinner_menu_pos  = (1579, 2225)

lunch_menu_size = (872, 200)
lunch_menu_pos  = (1579, 2825)


# check a given line of text isn't going to overflow in width
# if so, decrease the font size proportionally
def check_font_size(the_text, the_targetsize, this_font, draw_front, multi=False, adjust_startsize=False):
    the_textsize = draw_front.textsize(the_text, font=this_font)
    if the_textsize[0] >= the_targetsize[0] - margin_buffer:
        # there's probably a better way to do this than with a while loop
        # but a simple proportion isn't quite doing it, and anyway
        # this is a variable-width font so it will really depend on the exact string
        while (the_textsize[0] > the_targetsize[0] - margin_buffer):
            #print(the_textsize[0], the_targetsize[0] - margin_buffer, this_font.size)
            new_size = this_font.size - 2
            this_font = ImageFont.truetype(the_font, new_size)
            the_textsize = draw_front.textsize(the_text, font=this_font)
            if this_font.size <= 10:
                break

    else:
        # account for possible multi-line sizing, but otherwise leave it unchanged
        new_size = this_font.size

    # if this will be a multi-line text, decrease the font size just a bit
    if multi & adjust_startsize:
        this_font = ImageFont.truetype(the_font, int(new_size*0.8))

    return this_font




def get_ul_of_centered_size(target_size, input_size):
    # takes a size of an input image that you want to paste into the center of a target area
    # of a different size, and figures out what the start coordinates need to be.
    # sizes are tuples of (x, y).

    # this makes a list, not a tuple
    # not sure that matters to PIL but just in case
    #c = [int((a[i] - b[i])/2) for i in range(len(a))]

    ul_out = [int((target_size[i] - input_size[i])/2) for i in range(len(target_size))]

    # update: it matters to PIL
    return tuple(ul_out)


# takes the desired text, font characteristics, part of badge etc;
# makes sure it's all going to print correctly, modifies as needed
# and returns the parameters the printing should actually use
def get_text_params(thetext, input_font, this_key, draw_front, adjust_startheight=False, adjust_startsize=False, textsize_max=textsize_max, force_oneline=False, qsize=q1_size):
    #the_textsize = draw_front.textsize(thetext, font=input_font)
    this_font = check_font_size(thetext, textsize_max, input_font, draw_front)
    y_start = tstart_y[this_key]

    # the below is a list because if it is True it needs to be a list
    # so the code after returning this function assumes a list
    multiline = [False]

    # If the new font is dramatically smaller we may want to do multi-line text
    # though not if we're explicitly told to keep things on one line
    if (this_font.size < input_font.size * 0.7) & (not force_oneline):
        # have the first line be a little bigger than the second, and break into 2 lines only
        l_break = int(len(thetext)/1.5)
        text_lines = textwrap.wrap(thetext, l_break)
        # figure out a new font size based on wrapping the line
        this_font = check_font_size(text_lines[0], textsize_max, input_font, draw_front, multi=True, adjust_startsize=adjust_startsize)
        if adjust_startheight:
            # start the text a bit higher to compensate for having 2 lines
            y_start = tstart_y[this_key] - int(font_heights[this_key]/2)

        # recenter/reposition each line
        ctr_text_arr = []
        y_pos = y_start
        for this_line in text_lines:
            the_textsize  = draw_front.textsize(this_line, font=this_font)
            ctr_text_this = np.array(get_ul_of_centered_size(qsize, the_textsize))
            ctr_text_arr.append((ctr_text_this[0], y_pos))
            y_pos += the_textsize[1]

        multiline = [True, text_lines, ctr_text_arr]


    the_textsize = draw_front.textsize(thetext, font=this_font)
    ctr_text_tot = np.array(get_ul_of_centered_size(qsize, the_textsize))
    ctr_text_pos = (ctr_text_tot[0], y_start)

    return this_font, ctr_text_pos, multiline




def make_badge(reg, both_sides=True, make_pdf=True, verbose=True):

    '''
    #############################################################################
    ###################  basic data cleaning & verification  ####################
    #############################################################################
    '''

    errormsg = []
    dy_affil = 0

    # this column key apparently has a special character in it because EFF EXCEL 
    # and I don't care if it's 'Order Number' or '\ufeffOrder Number', I just care what the content is
    # and I will instead use the fact that it's the first column
    orderno_col = reg.keys()[0]


    # make sure the series item names (keys) don't have leading or trailing whitespace
    #keynames_2 = [q.strip() for q in reg.keys()]
    #reg.keys = keynames_2
    # LOL NEVERMIND WHY IS IT SO HARD TO RENAME INDICES IN A PANDAS SERIES
    # we'll just have to do it in the dataframe that feeds this instead
    # the above replaces the index object with just a list and I think that will break things below
    # so I'm skipping this until I figure it out later


    # this shouldn't be an issue but let's just make sure
    if pd.isnull(reg[thecols['nameonbadge_col']]):
        print_name = reg[thecols['givenname_col']].strip() + " " + reg[thecols['surname_col']].strip()
    else:
        print_name = reg[thecols['nameonbadge_col']]


    # group columns into things we might need
    fullreg_cols = thecols['fullrate_cols']
    dayreg_cols = [thecols['daycount_col']]
    dayreg_cols.extend(thecols['dayattend_cols'])
    events_cols  = [thecols['castle_col'], thecols['pie_col'], thecols['dinner_col']]
    eventcols_sh = ['castle', 'pie', 'dinner']

    dinner_cols  = [thecols['starter_col'], thecols['main_col'], thecols['dessert_col'], thecols['guest_col']]
    dinner_cols.extend(thecols['guestname_cols'])
    dinner_cols.extend(thecols['gueststarter_cols'])
    dinner_cols.extend(thecols['guestmain_cols'])
    dinner_cols.extend(thecols['guestdessert_cols'])

    # lunch_print  = {
    #     'Diversity Lunch - Mon'       : '(Di)', 
    #     'Outreach Lunch - Tue'        : '(Ou)', 
    #     'Joint MIST/UKSP Lunch - Wed' : '(M/U)', 
    #     'Publishing Lunch - Wed'      : '(Pu)', 
    #     'Careers Lunch - Thur'        : '(Ca)', 
    #     'Exoplanet Lunch - Thur'      : '(Ex)'
    # }

    # translate full lunch names into shorthands to be printed on the badges
    lunch_print  = {
        thecols['lunch_cols'][0] : '(Di)', 
        thecols['lunch_cols'][1] : '(Ou)', 
        thecols['lunch_cols'][2] : '(M/U)', 
        thecols['lunch_cols'][3] : '(Pu)', 
        thecols['lunch_cols'][4] : '(Ca)', 
        thecols['lunch_cols'][5] : '(Ex)'
    }


    # map what's in the spreadsheet to what we'll actually print (we have limited space)
    # this isn't really defined anywhere but here, so make menu changes here as needed
    menu_print = {
        'Watermelon'             : 'Watermelon',
        'Hot Smoked Salmon'      : 'Salmon',
        'Chicken & Leek Terrine' : 'Terrine',
        'Roast Rump of Lamb'     : 'Lamb',
        'Herb Crusted Cod'       : 'Cod',
        'Parsnip Gnocchi'        : 'Gnocchi',
        'Lemon Polenta Cake'     : 'Lemon Cake',
        'Fruit & Berry Salad'    : 'Fruit',
        'Chocolate Mousse'       : 'Mousse'
    }

    # let's fill some NaNs so that we don't have problems later
    thefillcols = [thecols['pronouns_col'], thecols['affiliation_col'], thecols['travelpref_col']]
    reg[thefillcols]  = reg[thefillcols].fillna(value='')
    reg[dinner_cols]  = reg[dinner_cols].fillna( value='')
    reg[fullreg_cols] = reg[fullreg_cols].fillna(value=-1)
    reg[dayreg_cols]  = reg[dayreg_cols].fillna( value=-1)
    #reg[lunch_cols]   = reg[lunch_cols].fillna(  value=-1)
    reg[events_cols]  = reg[events_cols].fillna( value=-1)

    # let's extract some info from the registration csv row

    # are they attending the full conference or just certain days?
    attend_full = False
    for thekey in thecols['fullrate_cols']:
        if reg[thekey] == 1:
            attend_full = True

    if not attend_full:
        # if they're not full registrants they should be day registrants but let's just check
        if pd.isnull(reg[thecols['daycount_col']]):
            attend_day = False
            # if we're here this person is somehow not registered for any days NOR the full conference so we should just not return a badge
            # maybe they're just registered for the dinner? In which case they don't need a badge, they need a dinner ticket
            this_errormsg = "Entry for %s has neither full-conference registration nor any days registered" % reg[thecols['nameonbadge_col']]
            errormsg.append([this_errormsg])
            if verbose:
                print(this_errormsg)
            #return None
        else:
            attend_day = True
            # NOTE if you change the dayreg_cols above this might break too
            which_days = [False, False, False, False]
            for i, col in enumerate(dayreg_cols):
                # ignore the "how many days?" column
                if i > 0:
                    if reg[col] > 0:
                        which_days[i-1] = True

            # it's possible someone could be in here as day-registered for all 4 days
            # in which case that's just a full registration
            if sum(which_days) == 4:
                attend_full = True
                attend_day  = False


    # as defined above this is: castle tour, pie & quiz, dinner
    which_events = [False, False, False]
    for i, the_event in enumerate(events_cols):
        if reg[the_event] > 0:
            which_events[i] = True

    dinner_guest = False
    if type(reg[thecols['guest_col']]) in [float, int]: 
        if reg[thecols['guest_col']] > 0:
            dinner_guest = True
        elif len(reg[thecols['guest_col']]) > 1:
            dinner_guest = True
        else:
            pass

    # fill some NaNs before continuing
    reg[lunch_print.keys()] = reg[lunch_print.keys()].fillna(value=0)
    n_lunch = 0
    which_lunch = []
    for i_lunch, the_lunch in enumerate(lunch_print.keys()):
        #print(reg[the_lunch])
        if reg[the_lunch] > 0:
            n_lunch += 1
            which_lunch.append(True)
        else:
            which_lunch.append(False)



    bus_pass = False
    if "local bus" in reg[thecols['travelpref_col']]:
        bus_pass = True

    # for now - when we get a press list we can do this
    # actually nevermind we decided to just send blank Press-marked badges to the RAS
    # and let them deal with it
    is_press = False
    try:
        if reg[thecols['press_col']] > 0:
            is_press = True
    except:
        pass



    '''
    #############################################################################
    ###################    Construction of front of badge    ####################
    #############################################################################
    '''


    # create the front-side image
    the_front  = Image.new('RGB', page_pix, (255, 255, 255))
    draw_front = ImageDraw.Draw(the_front)

    front_start = Image.open(front_start_path)
    the_front.paste(front_start, (0, 0))


    '''
        If LOC, they need a border
        And put it first so that other stuff will write over it
    '''

    if reg[thecols['loc_col']]:

        # also apparently the LOC members who manually sent in reg info
        # are day-registered for all days instead of just fully registered
        attend_full = True

        loc_offset = int(loc_line_width/2)

        textwidth_max = q1_size[0] - 2*loc_line_width - margin_buffer
        textsize = (textwidth_max, q1_size[1])

        # ugh, apparently I don't have an advanced enough version of PIL to use the width= 
        # with the rectangle drawing. So I'll have to do it as a series of lines. Hurray
        # draw_front.rectangle([q1_ul, q1_lr], fill=None, outline=col_loc, width=20)

        # we could draw a box just by sending lots of coordinates but the joints look weird
        # plus we have to offset from the different boundaries separately
        # so let's draw them individually

        # across the whole top (horizontal)
        this_start = (q1_ul[0], q1_ul[1] + loc_offset)
        this_end   = (q2_ur[0], q2_ur[1] + loc_offset)
        draw_front.line([this_start, this_end], fill=col_loc, width=loc_line_width)

        # across the whole bottom (horizontal)
        this_start = (q1_ll[0], q1_ll[1] - loc_offset)
        this_end   = (q2_lr[0], q2_lr[1] - loc_offset)
        draw_front.line([this_start, this_end], fill=col_loc, width=loc_line_width)

        # LHS (vertical)
        this_start = (q1_ul[0] + loc_offset, q1_ul[1])
        this_end   = (q1_ll[0] + loc_offset, q1_ll[1])
        draw_front.line([this_start, this_end], fill=col_loc, width=loc_line_width)

        # middle left (vertical)
        this_start = (q1_ur[0] - loc_offset, q1_ur[1])
        this_end   = (q1_lr[0] - loc_offset, q1_lr[1])
        draw_front.line([this_start, this_end], fill=col_loc, width=loc_line_width)

        # middle right (vertical)
        this_start = (q2_ul[0] + loc_offset, q2_ul[1])
        this_end   = (q2_ll[0] + loc_offset, q2_ll[1])
        draw_front.line([this_start, this_end], fill=col_loc, width=loc_line_width)

        # RHS (vertical)
        this_start = (q2_ur[0] - loc_offset, q2_ur[1])
        this_end   = (q2_lr[0] - loc_offset, q2_lr[1])
        draw_front.line([this_start, this_end], fill=col_loc, width=loc_line_width)

        # the banners should be pre-made to be the same width as each quadrant
        # if you're changing this you'll have to modify this
        loc_banner = Image.open(loc_banner_path)
        the_front.paste(loc_banner, banner_pos_q1)
        the_front.paste(loc_banner, banner_pos_q2)



    '''
        Banners
    '''

    # it's assumed below that nobody has more than one banner, as these positions overwrite each other

    # RAS Council Banner
    if reg[thecols['council_col']]:
        council_banner = Image.open(council_banner_path)

        # the banners should be pre-made to be the same width as each quadrant
        # if you're changing this you'll have to modify this
        the_front.paste(council_banner, banner_pos_q1)
        the_front.paste(council_banner, banner_pos_q2)


    # Press Banner
    if is_press:
        press_banner = Image.open(press_banner_path)

        # the banners should be pre-made to be the same width as each quadrant
        # if you're changing this you'll have to modify this
        the_front.paste(press_banner, banner_pos_q1)
        the_front.paste(press_banner, banner_pos_q2)


    # Student Banner
    # nevermind, we decided not to do this


    # Day registrations, bus pass and paid events are only on one quadrant of the badge
    # This is out of paranoia in case someone wanted to cut out the dinner-ticket icon on their badge and
    #   give it to someone else; they can still do that but then they won't still have one on the other side
    # Versus names and so on, which are in Q1 and Q2 so the badge is reversible

    '''
        Day Registrations
    '''
    if not attend_full:
        for i_day, is_day in enumerate(which_days):
            if is_day:
                this_day = the_days[i_day]
                day_img = Image.open(day_path[this_day])
                # note the third argument is what PIL uses to extract the transparency mask (preserves transparency)
                the_front.paste(day_img, (day_x[this_day], day_y))


    '''
        Bus pass
    '''
    if bus_pass:
        bus_img = Image.open(icon_path['bus'])
        the_front.paste(bus_img, icon_pos['bus'], bus_img)



    '''
        Events (Pie and Quiz, Castle, Dinner)
    '''
    for i_event, the_event in enumerate(events_cols):
        if reg[the_event] > 0:
            event_short = eventcols_sh[i_event]
            event_img = Image.open(icon_path[event_short])
            # note the third argument is what PIL uses to extract the transparency mask (preserves transparency)
            the_front.paste(event_img, icon_pos[event_short], event_img)



    # thus endeth the part of this that's just pasting images in
    # now we have to write actual text.


    '''
        Name
    '''
    # we ideally want to print the surname in a bigger font
    # but we also asked people to specify the name they wanted on their badges
    # so if we can't easily extract a surname this might get interesting

    # clear leading and trailing spaces before continuing
    first_name    = reg[thecols['givenname_col']].strip()
    surname       = reg[thecols['surname_col']].strip()
    name_on_badge = reg[thecols['nameonbadge_col']].strip()

    if name_on_badge.endswith(surname):
        # cool, then let's drop the surname and print that separately
        first_name_print = name_on_badge[:-len(surname)].strip()

        this_item = first_name_print
        this_key  = 'given_name'
        this_font, ctr_text_pos, multiline = get_text_params(this_item, fonts[this_key], this_key, draw_front, textsize_max=textsize_max)

        if multiline[0]:
            for i_line, this_line in enumerate(multiline[1]):
                # multiline has: [False] if multiple lines not needed,
                # and [True, text_lines, text_start_positions] if it is needed
                # where each of the latter are lists
                ctr_text_pos = multiline[2][i_line]
                draw_front.text(ctr_text_pos, this_line, font=this_font, fill=textcol)
                draw_front.text((ctr_text_pos[0]+q2_ul[0], ctr_text_pos[1]), this_line, font=this_font, fill=textcol)
                #txtsize = this_font.getsize("Lancaster University")

        else:       
            # mirror text in Q1 and Q2 of badge
            draw_front.text(ctr_text_pos, this_item, font=this_font, fill=textcol)
            draw_front.text((ctr_text_pos[0]+q2_ul[0], ctr_text_pos[1]), this_item, font=this_font, fill=textcol)



        this_item = surname
        this_key  = 'surname'
        # This font is way too big to break up into two lines so if the name is too long, just make the font smaller until it's not
        # at NAM2019 this was required for 1 badge, so different behaviour as a result of force_oneline=True is rare
        this_font, ctr_text_pos, multiline = get_text_params(this_item, fonts[this_key], this_key, draw_front, textsize_max=textsize_max, force_oneline=True)

        # mirror text in Q1 and Q2 of badge
        draw_front.text(ctr_text_pos, this_item, font=this_font, fill=textcol)
        draw_front.text((ctr_text_pos[0]+q2_ul[0], ctr_text_pos[1]), this_item, font=this_font, fill=textcol)

    else:
        # we're in uncharted territory
        name_print_simple = True

        # check if the only reason it didn't match was post-nominals
        special_suffix = False
        suffix_text    = ''
        name_on_badge_new = name_on_badge + ''

        # Honestly the sheer amount of code I've had to add for the 2 people who insisted on having their MBE status
        # printed on the badge has to be a metaphor for something

        for postnom in postnominals:
            # add the space just in case someone's name ends in "obe" (etc) and they love all-caps
            ppostnom = ' ' + postnom
            if ppostnom in name_on_badge:
                special_suffix = True
                # remove the postnom from the copy of the name string
                # (we'll create a postnom-only string below)
                name_on_badge_new = name_on_badge_new.replace(ppostnom, '')
            else:
                pass

        if special_suffix:
            # split name_on_badge by ' '
            # while the last item is a postnominal.strip()
            # save that text and remove it from name_on_badge
            # now check if the name_on_badge ends in the surname
            # if it does, great, get text widths of surname_in_big_font + postnominals_in_given_name_font
            # center that text
            # print given_name, new amalgamated surname in different font sizes
            # else: 
            name_sep = name_on_badge.split()
            postnom_on_badge = ''
            # put the postnoms back together in the order in which they're given by the attendee
            for i_p in range(len(name_sep)):
                j_p = len(name_sep) - 1 - i_p
                if name_sep[j_p] in postnominals:
                    postnom_on_badge = name_sep[j_p] + ' ' + postnom_on_badge

            # print(name_on_badge_new)

            if name_on_badge_new.endswith(surname):
                # this means we have a given name + surname + postnominals
                # and we know which is which, so we can do this variable font size thing
                name_print_simple = False
                given_name_new = name_on_badge_new.replace(' ' + surname, '').strip()

                this_item = given_name_new
                this_key  = 'given_name'
                this_font, ctr_text_pos, multiline = get_text_params(this_item, fonts[this_key], this_key, draw_front, textsize_max=textsize_max, force_oneline=True)

                # mirror text in Q1 and Q2 of badge
                draw_front.text(ctr_text_pos, this_item, font=this_font, fill=textcol)
                draw_front.text((ctr_text_pos[0]+q2_ul[0], ctr_text_pos[1]), this_item, font=this_font, fill=textcol)


                # the given name was the easy part; let's now deal with the surname + postnominal 
                # we need to get the size of the postnominal in the anticipated size and then resize the full line
                # assuming it's that proportional size

                next_item = postnom_on_badge
                next_key  = 'given_name'
                pn_size = fonts[next_key].getsize(next_item)

                this_item = surname + ' '
                this_key  = 'surname'
                sn_size = fonts[this_key].getsize(this_item)

                # what is the fractional size of the surname alone, in proportion to surname + postnominals?
                sn_size_f = float(sn_size[0])/float(sn_size[0] + pn_size[0])
                # that's the text width we're going for as a fraction of the max

                # so that's the maximum width we can go for in this case
                textsize_max_sn = (int(textsize_max[0]*sn_size_f), textsize_max[1])

                # resize fonts as needed given the text and max width
                this_font, ctr_text_pos, multiline = get_text_params(this_item, fonts[this_key], this_key, draw_front, textsize_max=textsize_max_sn, force_oneline=True)
                # get the actual size of the text in the new font
                txtsize = this_font.getsize(this_item)

                # we now need to size the postnom font to prevent overspill of a smaller width (by the width of the surname text)
                next_font, next_ctr_text_pos, multiline_next = get_text_params(next_item, fonts[next_key], next_key, draw_front, textsize_max=(textsize_max[0] - txtsize[0], textsize_max[1]), force_oneline=True) 
                txtsize_next = next_font.getsize(next_item)

                # we've now gotten sizes so now we can get positions and place things properly                

                txtwidth_tot = txtsize[0] + txtsize_next[0]
                # get the coordinates-to-center of the combined string
                this_ctr_txt_combined = get_ul_of_centered_size(q1_size, (txtwidth_tot, txtsize[1]))

                # print the surname part
                surname_pos = (this_ctr_txt_combined[0], ctr_text_pos[1])
                draw_front.text(surname_pos, this_item, font=this_font, fill=textcol)
                draw_front.text((surname_pos[0]+q2_ul[0], surname_pos[1]), this_item, font=this_font, fill=textcol)                

                # print the postnominal part
                postnom_pos = (this_ctr_txt_combined[0] + txtsize[0], ctr_text_pos[1] + (txtsize[1] - txtsize_next[1]))
                draw_front.text(postnom_pos, next_item, font=next_font, fill=textcol)
                draw_front.text((postnom_pos[0]+q2_ul[0], postnom_pos[1]), next_item, font=next_font, fill=textcol)                

                # the above might not look right for all edge cases so create a warning message
                this_errormsg = "NOTE: Badge for %s has postnominals, which we've tried to print nicely but this should be manually checked to make sure it looks ok" % name_on_badge
                errormsg.extend([this_errormsg])
                if verbose:
                    print(this_errormsg)

            else:
                # if it's something that doesn't end in a surname even after taking out the special suffixes, 
                # don't try to vary fonts etc, just do the simple printing
                pass


        # if it's not a special suffix let's try one more thing
        # assume they might have "surname, some-other-stuff"
        # e.g. at our conference we had "So-and-so Surname, Artist"
        elif "%s," % surname in name_on_badge:
            

            # cool, we can print a big surname
            name_print_simple = False

            name_sep = name_on_badge.split('%s,' % surname)

            given_name_print = name_sep[0].strip()
            this_item = given_name_print
            this_key  = 'given_name'
            this_font, ctr_text_pos, multiline = get_text_params(this_item, fonts[this_key], this_key, draw_front, textsize_max=textsize_max, force_oneline=True)

            # mirror text in Q1 and Q2 of badge
            draw_front.text(ctr_text_pos, this_item, font=this_font, fill=textcol)
            draw_front.text((ctr_text_pos[0]+q2_ul[0], ctr_text_pos[1]), this_item, font=this_font, fill=textcol)


            this_item = surname
            this_key  = 'surname'

            # the entire point of this is just to get the text height *without* the comma
            this_font, ctr_text_pos, multiline = get_text_params(this_item, fonts[this_key], this_key, draw_front, textsize_max=textsize_max, force_oneline=True)
            # get the size of this font
            txtsize_noc = fonts[this_key].getsize(this_item)
            
            # now do the one we'll print
            this_item = surname + ', '
            this_font, ctr_text_pos, multiline = get_text_params(this_item, fonts[this_key], this_key, draw_front, textsize_max=textsize_max, force_oneline=True)
            # get the size of this font
            txtsize = fonts[this_key].getsize(this_item)

            next_item = name_sep[1].strip()

            next_key  = 'given_name'
            # this is modified because we need to size the font to prevent overspill of a smaller width (by the width of the surname text)
            next_font, next_ctr_text_pos, multiline_next = get_text_params(next_item, fonts[next_key], next_key, draw_front, textsize_max=(textsize_max[0] - txtsize[0], textsize_max[1]), force_oneline=True) 
            txtsize_next = next_font.getsize(next_item)
            txtwidth_tot = txtsize[0] + txtsize_next[0]
            # get the coordinates-to-center of the combined string
            this_ctr_txt_combined = get_ul_of_centered_size(q1_size, (txtwidth_tot, txtsize[1]))

            # print the surname part
            surname_pos = (this_ctr_txt_combined[0], ctr_text_pos[1])
            draw_front.text(surname_pos, this_item, font=this_font, fill=textcol)
            draw_front.text((surname_pos[0]+q2_ul[0], surname_pos[1]), this_item, font=this_font, fill=textcol)                

            # print the postnominal part
            wcomma_pos = (this_ctr_txt_combined[0] + txtsize[0], ctr_text_pos[1] + (txtsize_noc[1] - txtsize_next[1]))
            draw_front.text(wcomma_pos, next_item, font=next_font, fill=textcol)
            draw_front.text((wcomma_pos[0]+q2_ul[0], wcomma_pos[1]), next_item, font=next_font, fill=textcol)                

            this_errormsg = "NOTE: We've tried to print badge for \"%s\" nicely but this should be manually checked to make sure it looks ok" % name_on_badge
            errormsg.extend([this_errormsg])
            if verbose:
                print(this_errormsg)
        
        else:
            # ok seriously we don't know what's going on, just do the simple print
            pass





        if name_print_simple:
            # just plot the whole thing in the smaller font
            this_item = name_on_badge
            this_key = 'given_name'
            this_font, ctr_text_pos, multiline = get_text_params(this_item, fonts[this_key], this_key, draw_front, textsize_max=textsize_max)

            if multiline[0]:
                for i_line, this_line in enumerate(multiline[1]):
                    # multiline has: [False] if multiple lines not needed,
                    # and [True, text_lines, text_start_positions] if it is needed
                    # where each of the latter are lists
                    ctr_text_pos = multiline[2][i_line]
                    draw_front.text(ctr_text_pos, this_line, font=this_font, fill=textcol)
                    draw_front.text((ctr_text_pos[0]+q2_ul[0], ctr_text_pos[1]), this_line, font=this_font, fill=textcol)
                    #txtsize = this_font.getsize("Lancaster University")

            else:
                # mirror text in Q1 and Q2 of badge
                draw_front.text(ctr_text_pos, this_item, font=this_font, fill=textcol)
                draw_front.text((ctr_text_pos[0]+q2_ul[0], ctr_text_pos[1]), this_item, font=this_font, fill=textcol)

            # also print a notification
            this_errormsg = "NOTE: Badge for %s printed without separating given from surname, should be manually checked to make sure it looks ok" % name_on_badge
            errormsg.extend([this_errormsg])
            if verbose:
                print(this_errormsg)



    '''
        Affiliation
    '''
    this_item = thecols['affiliation_col']
    this_key  = 'affiliation'
    if len(reg[this_item]) > 1:
        # if this is multi-line we want to both move the whole text up a bit *and* make it a bit smaller
        this_font, ctr_text_pos, multiline = get_text_params(reg[this_item], fonts[this_key], this_key, draw_front, adjust_startheight=True, adjust_startsize=True, textsize_max=textsize_max)

        if multiline[0]:

            for i_line, this_line in enumerate(multiline[1]):
                # multiline has: [False] if multiple lines not needed,
                # and [True, text_lines, text_start_positions] if it is needed
                # where each of the latter are lists
                ctr_text_pos = multiline[2][i_line]
                draw_front.text(ctr_text_pos, this_line, font=this_font, fill=textcol)
                draw_front.text((ctr_text_pos[0]+q2_ul[0], ctr_text_pos[1]), this_line, font=this_font, fill=textcol)
                txtsize = this_font.getsize("Lancaster University")
                dy_affil = int(txtsize[1] * 0.25)
                

        else:
            # mirror text in Q1 and Q2 of badge
            draw_front.text(ctr_text_pos, reg[this_item], font=this_font, fill=textcol)
            draw_front.text((ctr_text_pos[0]+q2_ul[0], ctr_text_pos[1]), reg[this_item], font=this_font, fill=textcol)
            dy_affil = 0

    else:
        this_errormsg = "NOTE: Badge for %s has no affiliation (%s)" % (reg[thecols['nameonbadge_col']], reg[orderno_col])
        errormsg.extend([this_errormsg])
        if verbose:
            print(this_errormsg)
        # this is used below so just needs to be defined even if there is no affiliation
        dy_affil = 0


    '''
        Pronouns
    '''
    this_item = thecols['pronouns_col']
    this_key  = 'pronouns'
    this_font, ctr_text_pos, multiline = get_text_params(reg[this_item], fonts[this_key], this_key, draw_front, textsize_max=textsize_max)
    ctr_text_pos = (ctr_text_pos[0], ctr_text_pos[1] + dy_affil)
    # mirror text in Q1 and Q2 of badge
    # these are fixed strings so assuming the badge is designed properly it shouldn't ever be multi-line
    # also, assuming we've filled nulls properly then at worst this is printing an empty string so no if statement required
    draw_front.text(ctr_text_pos, reg[this_item], font=this_font, fill=textcol)
    draw_front.text((ctr_text_pos[0]+q2_ul[0], ctr_text_pos[1]), reg[this_item], font=this_font, fill=textcol)


    '''
        Lunches
    '''
    xspace_adjust = 37

    if n_lunch > 0:
        the_lunch_img  = Image.new('RGB', lunch_menu_size, (255, 255, 255))
        draw_lunch = ImageDraw.Draw(the_lunch_img)

        this_text = 'Lunches:  '
        this_key  = 'header'
        this_font = fonts[this_key]
        this_tcol = headercol
        x_pos = xspace_adjust  # this is just what's needed to align the start of this text with the fixed text
        y_pos = 1              # remember these are just within the lunch text image
        draw_lunch.text((x_pos, y_pos), this_text, font=this_font, fill=this_tcol)

        # the text is on the same line but in a different font so we need to figure out where that starts
        txtsize = this_font.getsize(this_text)
        dx = txtsize[0]
        dy = txtsize[1]
        dx_indent = 50
        this_key  = 'regular'
        this_tcol = textcol
        this_font = fonts[this_key]
        txtsize = this_font.getsize("()")
        dy_smaller = dy - txtsize[1] + 5
        x_pos += dx
        y_pos += dy_smaller
        # now we're set up to start printing lunches
        for i_lunch, lunch_key in enumerate(lunch_print.keys()):
            if reg[lunch_key] > 0:
                this_text = '%s  ' % lunch_print[lunch_key]
                draw_lunch.text((x_pos, y_pos), this_text, font=this_font, fill=this_tcol)
                txtsize = this_font.getsize(this_text)
                x_pos += txtsize[0]

        # now that the lunches are printed, print the line(s) beneath
        x_pos = xspace_adjust + dx_indent
        y_pos = 1 + dy
        this_key  = 'regular'
        this_tcol = textcol
        this_font = fonts[this_key]
        dy = font_heights[this_key]
        this_text = '(non-binding, but please collect lunch from'
        draw_lunch.text((x_pos, y_pos), this_text, font=this_font, fill=this_tcol)
        y_pos += dy
        this_text = 'corresponding locations)'
        draw_lunch.text((x_pos, y_pos), this_text, font=this_font, fill=this_tcol)
     
        rot_lunch = the_lunch_img.rotate(180.0)
        the_front.paste(rot_lunch, lunch_menu_pos)




    '''
        Dinner menu choices and guests (upside-down)
    '''
    if (reg[thecols['dinner_col']] > 0) | dinner_guest:
        # This needs to be printed upside down, and there's no way to do that with the text command
        # so we will print onto a temporary image, rotate it, and then paste the whole image.
        the_dinner  = Image.new('RGB', dinner_menu_size, (255, 255, 255))
        draw_dinner = ImageDraw.Draw(the_dinner)
        x_start = xspace_adjust   
        y_start = 1
        x_pos = x_start
        y_pos = y_start
        dx_indent = 50

        this_text = "RAS Awards Dinner"
        this_key  = 'header'
        this_font = fonts[this_key]
        dy = font_heights[this_key]
        this_tcol = headercol
        draw_dinner.text((x_pos, y_pos), this_text, font=this_font, fill=this_tcol)
        y_pos += dy 

        this_text = "Your menu choices:"
        this_key  = 'header'
        this_font = fonts[this_key]
        dy = font_heights[this_key]
        this_tcol = textcol
        draw_dinner.text((x_pos, y_pos), this_text, font=this_font, fill=this_tcol)
        y_pos += dy 

        this_text = ''
        for menu_item in ['Starter', 'Main', 'Dessert']:
            this_text += menu_print[reg[menu_item].strip()]
            if 'Dessert' not in menu_item:
                this_text += ', '

        this_key = 'regular'
        this_font = fonts[this_key]
        dy = font_heights[this_key]
        this_tcol = textcol
        draw_dinner.text((x_pos + dx_indent, y_pos), this_text, font=this_font, fill=this_tcol)
        y_pos += dy 


        if dinner_guest:
            dy_g = 15
            n_guests = int(reg[thecols['guest_col']])
            if n_guests > 3:
                dy = int(0.6*dy)
                dy_g = 2
                key_add = '_sm'
            else:
                key_add = ''

            for i_guest in range(n_guests):
                if i_guest == 0:
                    s_guest = ''
                else:
                    s_guest = '%d ' % (i_guest+1)

                # NOTE this will likely break as I've assumed a format for the column names
                # based on the guest number here, and that may not be true for you
                # 
                y_pos += dy_g
                this_text = '+ Guest: ' + reg['RAS Awards Guest %sName' % s_guest]
                this_key  = 'header' + key_add
                this_font = fonts[this_key]
                dy = font_heights[this_key]
                this_tcol = textcol
                draw_dinner.text((x_pos, y_pos), this_text, font=this_font, fill=this_tcol)
                y_pos += dy 

                this_text = ''
                for menu_item in ['Guest %sStarter' % s_guest, 'Guest %sMain' % s_guest, 'Guest %sDessert' % s_guest]:
                    this_text += menu_print[reg[menu_item].strip()]
                    if 'Dessert' not in menu_item:
                        this_text += ', '

                this_key = 'regular' + key_add
                this_font = fonts[this_key]
                dy = font_heights[this_key]
                this_tcol = textcol
                draw_dinner.text((x_pos + dx_indent, y_pos), this_text, font=this_font, fill=this_tcol)
                y_pos += dy 


        rot_dinner = the_dinner.rotate(180.0)
        the_front.paste(rot_dinner, dinner_menu_pos)


        #the_dinner.save("dinner_menu_temp.png")
    



    # if make_pdf == False then this never gets written to but return it either way
    # just in case of I-don't-know-what
    badgefile_out = badge_path_out + surname.lower().replace(' ', '_').replace('/', '_').replace('\\', '_') + '_' + first_name.lower().replace(' ', '_').replace('/', '_').replace('\\', '_') + '_' + reg[orderno_col].lower().replace('/', '_').replace('\\', '_').replace(' ', '_') + ".pdf"



    # what we return depends slightly on whether we've been asked to make front-back pairs or just return the front

    if both_sides:


        #the_front.save("front_of_badge.png")
        the_back_file = Image.open(back_path)
        the_back  = Image.new('RGB', page_pix, (255, 255, 255))
        the_back.paste(the_back_file)


        imlist = [the_front, the_back]


        if make_pdf:
            the_front.save(badgefile_out, resolution=dpi, save_all=True, append_images=[the_back])

    else:
        # if you're here it means you only want to print the front (variable) side of the badge to the PDF
        # e.g. if your printer wants the back side as 1 file and the front sides all as separate files
        imlist = [the_front]

        if make_pdf:
            the_front.save(badgefile_out, resolution=dpi)






    return imlist, badgefile_out, errormsg






#bye
