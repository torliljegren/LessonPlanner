import platform
import tkinter as tk

# Enable comparison between days
# usage:  DAY_COMP["tis"] < DAY_COMP["tors"] ==> True
DAY_COMP = {
    "måndag": 0,
    "månd": 0,
    "mån": 0,
    "må": 0,
    "m": 0,

    "tisdag": 1,
    "tisd": 1,
    "tis": 1,
    "ti": 1,

    "onsdag": 2,
    "onsd": 2,
    "ons": 2,
    "on": 2,
    "o": 2,

    "torsdag": 3,
    "torsd": 3,
    "tors": 3,
    "tor": 3,
    "to": 3,

    "fredag": 4,
    "fred": 4,
    "fre": 4,
    "fr": 4,
    "f": 4,

    "lördag": 5,
    "lörd": 5,
    "lör": 5,
    "lö": 5,
    "l": 5,

    "söndag": 6,
    "sönd": 6,
    "sön": 6,
    "sö": 6,
    "s": 6
}

# Constants for font styles

INFO_FONT = (None, 12, "italic") if platform.system() == "Darwin" else ("Calibri", 9, "italic")
TITLE_FONT = (None, 18, "bold") if platform.system() == "Darwin" else ("Calibri", 13, "bold")
HEADING_FONT = (None, 14, "bold") if platform.system() == "Darwin" else ("Calibri", 11, "bold")
BASE_FONT = (None, 14, "normal") if platform.system() == "Darwin" else ("Calibri", 11, "normal")
WEEK_FONT = (None, 14, "bold") if platform.system() == "Darwin" else ("Calibri", 11, "bold")
ID_FONT = (None, 12, "italic") if platform.system() == "Darwin" else ("Calibri", 10, "normal")
DAY_FONT = (None, 14, "italic") if platform.system() == "Darwin" else ("Calibri", 11, "italic")


# Constants for widget styles

ENTRY_RELIEF = tk.FLAT if platform.system() != "MacOS" else None
BUTTON_RELIEF = None
if platform.system() == "Windows":
    BUTTON_RELIEF = tk.GROOVE
elif platform.system() == "Linux":
    BUTTON_RELIEF = tk.FLAT


# Constants for colors

SEL_COLOR = "SteelBlue1"
TEST_COLOR = "khaki"
CANCELLED_COLOR = "snow3"
POSLOCK_COLOR = "pale green"
ODD_COLOR = "dark goldenrod"
BG_COLOR = "SystemWindow" if platform.system() == "Windows" else "white"
BUTTON_COLOR = "azure2" if platform.system() == "Linux" else None
BUTTON_HLCOLOR = "azure4" if platform.system() != "Darwin" else None
ENTRY_COLOR = "#bdbbb7" #"#DCDAD5"


# Constant for max undo states

MAX_UNDO = 10


# Help message

HELPMSG = "Hjälp och instruktioner om hur programmet fungerar finns i filen \"Manual.docx\" i samma mapp som " + \
          "Lektionsplaneraren."


# Constants for breaks

BREAKS = (44, 52, 1, 9, 14)


# Platform dependant scrolling constant
SCR_SPEED = 1 if platform.system() == "Darwin" else 120

# Time (s) since last save needed to trigger "Do you want to save before exit"-dialog box
DONOTASK_SAVE_TIME = 10
