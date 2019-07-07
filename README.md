# conference-badges
**Dynamic printing of conference badges**

The scripts and images in this repository allow you, given a spreadsheet of registration information, to create conference badges. The badges have the following properties:

 - They print on regular A4 paper
 - They are designed to be folded twice to make an **A6 (portrait) badge** and fit in standard A6 badge sleeves
 - They are reversible (name/affiliation information on both sides of the badge)
 - The names are in a large font to avoid attendees' awkward close-up squinting at each other's chests
 - The font sizes are dynamic and auto-reduce if the text is too long for the default size
 - Social event information, dinner tickets, bus passes etc. can be printed on the badge for each attendee (based on the spreadsheet)
 - Different attendee categories (e.g. student, organiser, press) can be printed on the badge based on the spreadsheet
 - The inside of the badges has room for additional information, e.g. the outline schedule, a map of the venue, wifi password


### Getting the code running

The scripts are in Python 3; you can duplicate the environment used in e.g. conda via `environment.yml` in the top-level directory. You will need `pandas`, `numpy` and `pillow`.

Images used to construct badges are in the `images/` sub-directory.

To check everything is working in principle, try 
`python make_all_badges.py` 
at the command line. It should read from the example spreadsheet and generate 5 example badges into the `individual_badges/` sub-folder, as well as a file called `all_badges_front_out.pdf` which has the front-side of all 5 badges. 


### Context - The Example Conference

The code and images were created for a specific conference: the [UK National Astronomy Meeting](http://nam2019.org) held at [Lancaster University](http://www.lancaster.ac.uk) from 30 June - 4 July 2019. Therefore the example images all use this imagery, schedule, map etc. Depending on which license you are using (see the `LICENSE` file for more details) you can adapt/swap out images to suit your specific needs.

For context that may help in reading the code, this conference:

 - offered single-day registration or full-meeting registration
 - offered free bus passes **or** free parking for attendees. Bus passes for those who chose them are printed directly on the badge using an icon agreed upon with the local bus company. Parking permits were distributed separately.
 - had multiple social and networking events attendees could pay extra for: conference dinner, "pie & quiz night", and a tour of Lancaster Castle. Each was printed/not printed on the badge using icon images depending on the attendee's selection. If the conference dinner was selected, the chosen menu options were printed inside the badge, as were those of extra dinner guests (reminding attendees of their choices avoids problems with catering on the night). Extra dinner tickets for guests were distributed separately.
 - had multiple themed lunches throughout the meeting. These were free and choices were non-binding, but they were used to help catering distribute food in correct proportions to the different lunch venues, and thus people's lunch signups were printed inside the badges with a message asking them to pick up their lunch from the corresponding venue. To everyone's surprise, this actually worked.
 - had a Code of Conduct drawn up specifically for the meeting; a link to the CoC and information on reporting violations was printed on the inside of the badge.


### Badge output format

The badges are output as raster PDFs (2 sides A4) with layout applied using Pillow, an image library for Python. The use of raster images rather than vectorised graphics is intentional, so that aside from whatever resizing may be necessary for your printer's margins the badges are WYSIWYG (i.e. no surprises due to variations in font libraries if you send these off to get printed). The font is Helvetica Neue.

The example conference had about 550 attendees so the badges were professionally printed on thick glossy paper and creased for precise folding, but choosing A4 for a conference located in Europe meant re-printing individual badges could be done on a regular office printer with standard paper.

The badge size is specified once in `make_badge.py` in inches, so changing the paper size (e.g. to 8.5 x 11 for North America) should be straightforward. The raster badges are designed to print at 300 dpi, so changing the paper size requires changing the layout as well, e.g. creating new base images for the fixed information on the front and back of the badges. Badge prototypes were originally designed and laid out in presentation software (Keynote) with a slide size in pixels corresponding to A4 x 300 dpi, and this worked well for translating layout positions in pixels into the Python scripts. 

Adding 8.5 x 11 as a built-in option to the script is flagged for future work, but for now if you want to do this you'll have to modify the code yourself (you could leave the layout the same and just have wider margins, but you'd need to shorten the page).

The inside of the badges is printed upside-down so that it will be right-side-up when people flip over the badge.


### Using the scripts

There are 4 Python scripts:

#### Scripts to run from the command line

 - `make_all_badges.py`: input the registration spreadsheet (CSV) and generate all the badges as individual files and/or one single file. Also flags potential issues (e.g. name mismatches; see spreadsheet info below) that might need following up. *Use this script to generate all your badges.*
 - `make_one_badge.py`: generate a single badge, either to modify a badge that's already in the spreadsheet or to generate a new badge on the fly. Run at the command line without additional inputs to print detailed info on the changes you can make. Theoretically you could use it to generate all your badges, but as this matches to the spreadsheet for each badge, that would be much slower than using `make_all_badges` above. This is designed to be used at the registration desk during the conference for one-off reprints. New badges or changes to badges do *not* get recorded in the spreadsheet.

#### Support scripts

 - `get_badge_spreadsheet.py`: designed to be imported by the other scripts, e.g. `from get_badge_spreadsheet import get_badge_spreadsheet`. Reads in the spreadsheet and returns it to whichever program is being used to make/modify a badge.
 - `make_badge.py`: designed to be imported by the other scripts, e.g. `from make_badge import make_badge`; this has functions to generate a single badge and return it to the other scripts.


### The input spreadsheet

If you are adapting this code for your conference, use the included spreadsheet as a template for your spreadsheet format. There are a few key properties it should ideally have:

 1. Separate entries for given name, surname, and the name as printed on the badge: e.g. `'Given Name': 'Brooke', 'Surname': 'Simmons', 'Name on Badge': 'Dr Brooke D Simmons'`

 These are separated/duplicated so that attendees have the freedom to have slight variations in their printed names, but surnames will be printed in a larger font on a separate line (which is especially useful for an academic conference where attendees recognise each other by publication record, e.g. "Simmons et al".). If the `Name on Badge` ends in `Surname` the code detects this and prints accordingly. If the badge ends with a postnominal, e.g. 'Smith MBE' the code detects this and prints the surname in the default larger font and the postnominal a smaller font on the same line.

 2. `Affiliation`: to be printed underneath the name, e.g. `Lancaster University`

 If the affiliation is very long it will be printed on two lines instead of one, and moved up slightly so that there is still room for the pronouns.

 3. `Preferred Pronouns`: optional, but important for fostering an inclusive conference. e.g. `she/her/hers`

 If not present, this will be left blank, but it's strongly encouraged to include them in registration information. The code assumes these are added to the spreadsheet via a drop-down list or otherwise limited set of inputs, so no attempt is made to dynamically resize fonts or check for typos.

4. An index/unique ID column of some kind, which will be part of the output PDF filename so that 2 people will the same name don't overwrite each other's badges.

There are also other options that you can include in the spreadsheet:

 5. Various flags to indicate whether the attendee is in a special category and should get a banner on the badge (`1`/`0` in the spreadsheet)

 6. Various flags to indicate whether full registration or day registration (for multi-day conferences) and, if the latter, which days (will be flagged on the badge front)

 7. Various flags for paid options such as social events, conference dinner etc (will be denoted by icons on the badge front)

 Paid social options are only printed on one side of the reversible badge, to prevent anyone turning one ticket into two via a physical cut and paste.

 8. Additional conference dinner information such as menu choices for attendee and any guests (will be printed inside the badge)

 The code assumes these are added to the spreadsheet via a drop-down list or otherwise limited set of inputs, so no attempt is made to dynamically resize fonts or check for typos.

 9. Themed lunch choices (will be printed inside the badge).

The spreadsheet column names expected by the program are in `make_badge.py`, and should be relatively straightforward to modify. The order in the spreadsheet does not matter and leading/trailing spaces in the column names will be trimmed, but the column names are case-sensitive. 


### Licensing

The code and images can be used under one of 3 difference licenses, and you can choose which to use depending on your needs. See the `LICENSE` file for more information.


--Brooke Simmons (@vrooje), 5 July 2019

(c) 2019 Brooke Simmons
