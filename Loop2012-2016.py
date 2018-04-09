from matcher_saber import *
directory = r"C:\Users\JuanEduardo\Google Drive\Gloria\Matcher\BasesPython"


for i in range(2012, 2015):
    db_1 = pd.read_csv(directory+"\Matcher"+str(i)+".csv")
    db_2 = pd.read_csv(directory+"\Matcher"+str(i+1)+".csv")

    db_1, db_2 = db_1.values, db_2.values
    matchings = do_match(db_1, db_2, doc = "Matcher-"+str(i)+"-vs-"+str(i+1)+".xlsx", av_meet=True)
    codes = stata_codes(matchings, doc="Do-2012vs"+str(i)+".xlsx")


do_file = open("id_replace_8_04_2018.do", "w")
for y in range(2012, 2015):
    print(y)
    doc = ""
    data = pd.read_csv(directory+"\Matcher-"+str(y)+"-vs"+str(y+1)+".csv")
    data = pd.DataFrame(data)
    year = str(y)
    txt1 = "replace id_sede = "
    txt2 = " if id_sede == "
    txt3 = " & periodo == " + year
    # Lo que necesito es que... si el ID no está vacío...

    for id in range(len(data)):
        matchid = data.ix[id, "Match ID"]
        comp = data.ix[id, "Similarity"]
        oid = data.ix[id, "Original ID"]
        if matchid != 0 and comp > 95 and matchid != 248814:
            if matchid != oid:
                line = txt1 + str(oid) + txt2 + str(matchid) + txt3
                do_file.write("\n"+line)

do_file.close()



