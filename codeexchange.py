import pandas as pd

directory = r"C:\Users\JuanEduardo\Google Drive\Gloria\Matcher\Resultados"

do_file = open("id_replace.do", "w")
do_file.write("\n /* Si un colegio hizo match con los de 2012, se le pondrá el código de 2012.  ")
do_file.write("\n Si el código ID de un año es igual al de 2012, entonces se deja igual. ")
do_file.write("\n si no lo es, entonces se asegura de que haya una compatibilidad superior al 95%. */")
for y in range(2013, 2017):
    print(y)
    doc = ""
    data = pd.read_csv(directory+"\Matcher-2012-vs"+str(y)+".csv")
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

