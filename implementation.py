from matcher_saber import *

directory = r"C:\Users\JuanEduardo\PycharmProjects\CodingThings"  # The directory where they are located
saber11 = pd.read_csv(directory+"\Matcher11.csv")                 # The Saber 11° Database
saber11 = saber11.values

saber3 = pd.read_csv(directory+"\Matcher359.csv")                 # Saber 3°, 5°, 9° Database
saber3 = saber3.values

# If you want to see how it works (rapidly) you can just  uncomment the following lines (that slice the data), and
# perform the functions over them.


# saber11 = saber11[:30, :]
# saber3 = saber3[:30, :]


matching = do_match(saber11, saber3)  # This implements the matcher between Saber11 and Saber359
codes = stata_codes(matching)

