from matcher_saber import *

# directory = r"C:\Users\JuanEduardo\PycharmProjects\Matcher"  # The directory where they are located
# saber11 = pd.read_csv(directory+"\Matcher11.csv")                 # The Saber 11° Database
# saber11 = saber11.values
#
# saber3 = pd.read_csv(directory+"\Matcher359.csv")                 # Saber 3°, 5°, 9° Database
# saber3 = saber3.values
#
# # If you want to see how it works (rapidly) you can just  uncomment the following lines (that slice the data), and
# # perform the functions over them.
#
#
# # saber11 = saber11[:30, :]
# # saber3 = saber3[:30, :]

directory = r"C:\Users\JuanEduardo\Google Drive\Gloria\Matcher\BasesPython"

saber11 = pd.read_csv(directory+"\Matcher11.csv")                 # The Saber 11° Database
saber11 = saber11.values

saber3 = pd.read_csv(directory+"\Base359_matcher.csv")                 # Saber 3°, 5°, 9° Database
saber3 = saber3.values
saber3 = saber3[:1000, :]
matching = do_match(saber11, saber3, doc="Matcher_3_4_2018.xlsx", freq=10)  # This implements the matcher between Saber11 and Saber359
codes = stata_codes(matching, doc="Stata_Matcher_3_4_2018.xlsx")

##

# Matching 2012 with 2013
# directory = r"C:\Users\JuanEduardo\PycharmProjects\Matcher\MatchSaberYears"
# saber2012 = pd.read_csv(directory+"\Matcher2012.csv")                 # The Saber 11° Database
# saber2012 = saber2012.values
#
# saber2013 = pd.read_csv(directory+"\Matcher2013.csv")                 # Saber 3°, 5°, 9° Database
# saber2013 = saber2013.values
#
# saber2012 = saber2012[:30, :]
# saber2013 = saber2013[:10000, :]


# matching = do_match(saber2012, saber2013, av_meet=True, doc="Prueba2012.xlsx", deb = 27)
#
# codes = stata_codes(matching)
