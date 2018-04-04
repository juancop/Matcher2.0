# School Name Matcher
# By: Juan Eduardo Coba Puerto
# e-mail: <jcoba@gmail.com>
#         <j.coba@javeriana.edu.co>
#

# Matcher 2.0

# In order for the matcher to work, you need to have installed the following libraries:
# Numpy, Pandas, FuzzyWuzzy, python-Levenshtein and xlsxwriter.


import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# We defined an object called School as follows:


class school:
    """ The school class is created for each school. Using the information contained in this class,
        and provided a set for comparisons, the user is able to find the closest match (if it's reasonable)
        by using the available geographical and institutional information combined with one string distance measure:
        the Levenshtein distance of transformations, as provided fue the FuzzyWuzzy Library.

        Parameters:
        ---------------------
        original: Contains all the information of the school.
        av_meet: if True, it means that meeting_time is provided (default = False).

        Attributes:
        ---------------------
            information: A NumPy array that contains all the school's information in the following order:
                         [Name, Municipality, School's DANE code, School's ID].

            name_original: School's Name
            mun_original: School's Municipality
            dane_schoriginal: School's "DANE" code
            id_original: School's ID (given by a certain Database).
            jornada: meeting time.

    """
    def __init__(self, original, av_meet=False):
        self.av_meet = av_meet
        self.first = np.array(0).reshape(1, 1)
        if not self.av_meet:
            self.information = original.reshape(1, 4)
            self.name_original, self.mun_original, self.dane_schoriginal, self.id_original = original
        else:
            self.information = original.reshape(1, 5)
            self.name_original, self.mun_original, self.dane_schoriginal, self.id_original, self.jornada = original

    def matcher(self, comparisons):
        """ Finds the best match.

            Finds the best school that matches(if available) the Original School Name and information using the
            set of Comparisons (aka, the other schools' names).

            This is the main function of the algorithm, and it uses all the functions described below it

            Parameters
            ---------------------
            comparisons: A NumPy 2D-array that contains the information of all the schools that are available for
                         comparison.
                         Each row of the array is thought as a school. And has the same column-order as the original:
                         [Name, Municipality, School's DANE code, School's ID].

            Returns
            ---------------------
                Another NumPy array that contains both the original school's information and the closest school's
                information, and in the last position an indicator of the similarity of the schools' name based on
                Levenshtein's distance, and the Set Ratio as a scorer.

                For more information about the Set Ration, consult the following url:
                http://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/

        """
        av_choice, na_choice = self.filter(comparisons)

        if (av_choice.shape[0] != 0) & (na_choice.shape[0] != 0):
            av_ans = process.extractOne(self.name_original, av_choice[:, 0], scorer=fuzz.token_set_ratio)
            na_ans = process.extractOne(self.name_original, na_choice[:, 0], scorer=fuzz.token_set_ratio)

        elif (av_choice.shape[0] == 0) & (na_choice.shape != 0):
            av_ans = (0, 0)
            na_ans = process.extractOne(self.name_original, na_choice[:, 0], scorer=fuzz.token_set_ratio)

        elif (av_choice.shape[0] != 0) & (na_choice.shape == 0):
            av_ans = process.extractOne(self.name_original, av_choice[:, 0], scorer=fuzz.token_set_ratio)
            na_ans = (0, 0)
        else:
            av_ans = (0, 0)
            na_ans = (0, 0)

        fit_av = np.array(av_ans[1]).reshape(1, 1)
        fit_na = np.array(na_ans[1]).reshape(1, 1)

        self.size = (1, 4)
        if self.av_meet:
            self.size = (1, 5)

        # Añado que si una solución es única, tome ese elemento. 
        solution_av = av_choice[av_choice[:, 0] == av_ans[0]]
        solution_na = na_choice[na_choice[:, 0] == na_ans[0]]
        
        n_av = len(solution_av)
        n_na = len(solution_na)
        
        if n_av == 1 and n_na != 1:
            return np.hstack([self.information, solution_av, fit_av, self.first])
        
        elif n_na == 1 and n_av != 1:
            return np.hstack([self.information, solution_na, fit_na, self.first])
        
        else:
           
            if fit_av >= fit_na:
    
                unique = self.multiple(self.solution_picker(solution_av)).reshape(self.size)
                fit_av = np.array(fuzz.token_set_ratio(self.name_original, unique)).reshape(1, 1)
                return np.hstack([self.information, unique, fit_av, self.first])
            else:
                unique = self.multiple(self.solution_picker(solution_na)).reshape(self.size)
                fit_na = np.array(fuzz.token_set_ratio(self.name_original, unique)).reshape(1, 1)
                return np.hstack([self.information, unique, fit_na, self.first])

    def solution_picker(self, solution):
        """ Filters out non-credible solutions.

            The extractOne function of the Fuzzy Wuzzy Library extracts the most similar school name to the original.
            In the method matcher, the algorithm searches for all the comparisons that have the same name as the closest
            match.
            There might be some solutions that are not ideal provided the information available, and it discards them.


            Parameters
            --------------
            solution: It's the vector of posible solutions based on the closest match. All of them have the same name,
            but may not have the same DANE cod or municipality.


            Returns
            --------------
                Depending on size and the information available, it will return either the same input, a vector of all
                the solutions that either the same DANE and municipality, or all the solutions that have either the DANE
                code or the municipality code.

                Cases:
                    1) There's exactly one solution. As there are no more options, it returns it.
                    2) There are more than one solutions:
                        a. If the school has all its information available, then searches for all the solutions
                           that have the SAME municipality AND DANE code. If there are none, it looks for all
                           the solutions that have the same municipality. If there are none, then it looks
                           to all the solutions that have the same DANE code, and if there are none, it returns
                           zeroes.

                        b. If the school only has its municipality available, it only returns the ones
                           with the same municipality. (This discards the solutions given by the na_choice)

                        c. If the school only has its DANE code, it only returns the soltuions with the
                           same code. (This also discards the na_choice solutions)

                        d. If the school doesn't have any information available, it discards ALL the solutions.

                        Therefore, one only trust in the na_choice when there's an exact match with another school.


        """
        if solution.shape[0] == 1:
            return solution
        else:
            if self.status == "Complete":
                prov = solution[(solution[:, 1] == self.mun_original) & (solution[:, 2] == self.dane_schoriginal)]
                if prov.shape[0] > 0:
                    return prov
                else:
                    prov = solution[solution[:, 1] == self.mun_original]
                    if prov.shape[0] > 0:
                        return prov
                    else:
                        prov = solution[solution[:, 2] == self.dane_schoriginal]
                        if prov.shape[0] > 0:
                            return prov
                        else:
                            return np.zeros(self.size)

            elif self.status == "DaneNaN":
                prov = solution[solution[:, 1] == self.mun_original]
                if prov.shape[0] > 0:
                    return prov
                else:
                    return np.zeros(self.size)
            elif self.status == "MunNaN":
                prov = solution[solution[:, 2] == self.dane_schoriginal]
                if prov.shape[0] > 0:
                    return prov
                else:
                    return np.zeros(self.size)
            else:
                return np.zeros(self.size)

    def multiple(self, solmulti):
        """ Selects one solution.

            Right after one filters out non-credible solutions, there might be some redundant solutions that may contain
            the same information... up to this point, if there are more than one plausible option, there's not much to
            do.

            The present function retrieves the first school in the array.

            Parameters
            -----------------
            solmulti: It's the output of solutionPicker. It's a vector that contains all the credible solutions.

            Returns
            -----------------
                If solutionPicker returns just one school, then this function doesn't do anything special. But, if
                array of credible solutions contains more than one school, then this function returns the first school,
                and changes the self.first attribute to 1, indicating that this procedure took place.
        """

        if solmulti.shape[0] > 1:
            self.first = np.array(1).reshape(1, 1)
            return solmulti[0]
        else:
            return solmulti

    def filter(self, comparisons):

        """ Defines an information status and divides the observations.

            According to the information available in the original school, it is classified as having Complete
            information (Complete), Nothing (FullNaN), or partial (MunNaN or DaneNaN). Using this categories the
            observations are divided in two groups that are later used to compare.

            Parameters
            -------------
            comparisons: A NumPy 2D-array that contains the information of all the schools that are available for
                         comparison.
                         Each row of the array is thought as a school. And has the same column-order as the original:
                         [Name, Municipality, School's DANE code, School's ID].


            Returns
            -------------
            with_codes: a NumPy 2D-array that contains the schools that have the same information (either DANE or
                             municipality) as the original school.

            with_na: a NumPy 2D-array that contains the schools that do not have the same information as the
                          original school.

        """

        # There will be four cases for comparison, depending on the completeness on the original word.
        #
        #   1. MunNaN : MUN is NaN
        #   2. FullNaN : DANE and MUN are NaN.
        #   3. DaneNaN : DANE is NaN
        #   4. Complete: DANE and MUN are not NaN

        if pd.isna(self.mun_original) and not pd.isna(self.dane_schoriginal):

            self.status = "MunNan"

            if self.av_meet and not pd.isna(self.jornada):
                condition = (comparisons[:, 2] == self.dane_schoriginal) & (comparisons[:, 4] == self.jornada)
            else:
                condition = comparisons[:, 2] == self.dane_schoriginal

            with_codes = comparisons[condition]
            with_na = comparisons[~condition]

            if len(with_codes) == 0 and len(with_na) != 0:
                with_codes = with_na
                return with_codes, with_na
            elif len(with_na) == 0 and len(with_codes) != 0:
                with_na = with_codes
                return with_codes, with_na
            elif len(with_codes) == 0 and len(with_na) == 0:
                return comparisons, comparisons
            else:
                return with_codes, with_na

        elif pd.isna(self.mun_original) and pd.isna(self.dane_schoriginal):
            self.status = "FulNaN"
            return comparisons, comparisons

        elif pd.isna(self.dane_schoriginal) and not pd.isna(self.mun_original):
            self.status = "DaneNaN"

            if self.av_meet and not pd.isna(self.jornada):
                condition = (comparisons[:, 1] == self.mun_original) & (comparisons[:, 4] == self.jornada)
            else:
                condition = comparisons[:, 2] == self.mun_original

            with_codes = comparisons[condition]
            with_na = comparisons[~condition]

            if len(with_codes) == 0 and len(with_na) != 0:
                with_codes = with_na
                return with_codes, with_na
            elif len(with_na) == 0 and len(with_codes) != 0:
                with_na = with_codes
                return with_codes, with_na
            elif len(with_codes) == 0 and len(with_na) == 0:
                return comparisons, comparisons
            else:
                return with_codes, with_na

        else:
            self.status = "Complete"

            condition = (comparisons[:, 1] == self.mun_original) | (comparisons[:, 2] == self.dane_schoriginal)
            if self.av_meet and not pd.isna(self.jornada):
                condition = condition & (comparisons[:, 4] == self.jornada)

            with_codes = comparisons[condition]
            with_na = comparisons[~condition]

            if len(with_codes) == 0 and len(with_na) != 0:
                with_codes = with_na
                return with_codes, with_na
            elif len(with_na) == 0 and len(with_codes) != 0:
                with_na = with_codes
                return with_codes, with_na
            elif len(with_codes) == 0 and len(with_na) == 0:
                return comparisons, comparisons
            else:
                return with_codes, with_na


def do_match(original_db, comparison_db, deb=0, deb2=0, doc="matcher.xlsx", partial=True, freq=10000, av_meet=False):
    """Realizes the matcher for each school name.

    This function creates a school object for each individual school available in the original database. It is mainly
    used to find the closest match for each school in Saber11 to the schools in Saber359.

    Arguments
    -------------

    original_db: It's the database that contains all the schools. This is used to create the school object.
    comparison_db: It's the database that is going to be used for comparison. It contains the names that are going to
                   be matched.

    deb: It's a debugging parameter. It defines when to start the matcher.
    deb2: It's a debugging parameter. It defines when to stop the matcher.
    doc: It's the name for the final output.
    partial: Allows for the output of partial results. (Default True)
    freq: Defines how often the partial results are created. (Only works if partial = True)
    av_meet: If ture, it means that the data provided includes the meeting time.

    Returns
    ------------
        This function returns Pandas Dataframe with all the information contained in the school object for each
        school in original_db.

        In addition, it creates an Excel Spreadsheet with it, and if partial = True, then it will also produce one
        spreadsheet every freq iterations.

    """

    last = len(original_db)
    if deb2 != 0:
        last = deb2
    if av_meet:
        results = np.zeros((1, 12))
    else:
        results = np.zeros((1, 10))

    for i in range(deb, last):
        print(i)
        if pd.isna(original_db[i][0]):
            pass
        else:
            results = np.vstack([results, school(original_db[i], av_meet).matcher(comparison_db)])
            if i == (last-1):
                results = pd.DataFrame(results)

                if av_meet:
                    results.columns = ["Original School Name", "Original Municipality", "Original DANE", "Original ID",
                                       "Original Jornada", "Match School Name", "Match Municipality", "Match DANE",
                                       "Match ID", "Match Jornada", "Similarity", "First"]

                else:
                    results.columns = ["Original School Name", "Original Municipality", "Original DANE", "Original ID",
                                       "Match School Name",    "Match Municipality",    "Match DANE",    "Match ID",
                                       "Similarity", "First"]

                results.to_excel(doc)
                results.to_csv(doc)

        if partial and i % freq == 0 and i > 0:
            name = str(i)+doc
            to_excel = pd.DataFrame(results)
            if av_meet:
                to_excel.columns = ["Original School Name", "Original Municipality", "Original DANE", "Original ID",
                                    "Original Jornada", "Match School Name", "Match Municipality", "Match DANE",
                                    "Match ID", "Match Jornada", "Similarity", "First"]

            else:
                to_excel.columns = ["Original School Name", "Original Municipality", "Original DANE", "Original ID",
                                    "Match School Name", "Match Municipality", "Match DANE", "Match ID",
                                    "Similarity", "First"]
            to_excel.to_excel(name)

    return results


def stata_codes(info, doc="stata_codes.xlsx"):
    """ This function creates the code needed in Stata to impute to each school in the Original Database the ID codes
    in the comparison database.

    Arguments
    -------------
    info: It's a Pandas Data Frame with the output of the do_match. It could be either the Python Variable, or
    an imported Spreadsheet.

    doc: The name of Do-file and the Excel Spreadsheet.

    Returns
    -------------
        This function returns Pandas Data Frame with all the Stata codes necessary to create a variable that can relate
        each school in the Original Database with the comparison Database.
        In addition, it creates a Do-File and an Excel Spreadsheet with it.

    """
    length = info.shape[0]
    database = info.ix
    txt = "replace newID = "
    txt2 = " if ID == "
    codes = np.array(["gen newID = ."])

    do_file = open(doc[:-4]+"do", "w")
    do_file.write(codes[0])

    for i in range(1, length):
        if database[i, "Match ID"] == 0 or pd.isna(database[i, "Match ID"]):
            pass
        else:
            line = txt + str(database[i, "Match ID"]) + txt2 + str(database[i, "Original ID"])
            do_file.write("\n"+line)
            codes = np.vstack([codes, line])

    do_file.close()
    codes = pd.DataFrame(codes)
    codes.to_excel(doc)
    return codes
