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

# The Following lines import the databases that contains the schools names. We use pandas for convenience.

dir = r"C:\Users\JuanEduardo\PycharmProjects\CodingThings" # The directory where they are located
saber11 = pd.read_csv(dir+"\Matcher11.csv")                # The Saber 11° Database
saber11 = saber11.values

saber3 = pd.read_csv(dir+"\Matcher359.csv")                # Saber 3°, 5°, 9° Database
saber3 = saber3.values

# We defined an object called School as follows:
class school:
    """ The school class is created for each school. Using the information contained in this class,
        and provided a set for comparisons, the user is able to find the closest match (if it's reasonable)
        by using the available geographical and institutional information combined with one string distance measure:
        the Levenshtein distance of transformations, as provided fue the FuzzyWuzzy Library.

        Attributes:
        ---------------------
            information: A NumPy array that contains all the school's information in the following order:
                         [Name, Municipality, School's DANE code, School's ID].

            name_original: School's Name
            mun_original: School's Municipality
            dane_schoriginal: School's "DANE" code
            id_original: School's ID (given by a certain Database).

    """
    def __init__(self, original):
        self.information = original.reshape(1, 4)
        self.name_original, self.mun_original, self.dane_schoriginal, self.id_original = original

    def matcher(self, comparisons):
        """ Finds the best match.

            Finds the best school that matches(if available) the Original School Name and information using the
            set of Comparisons (aka, the other schools' names).

            This is the main function of the algorithm, and it uses all the functions described below it

            Parameters
            ---------------------
            comparisons: A NumPy 2D-array that contains the information of all the schools that are available for comparison.
                         Each row of the array is thought as a school. And has the same column-order as the original:
                         [Name, Municipality, School's DANE code, School's ID].

            Returns
            ---------------------
                Another NumPy array that contains both the original school's information and the colest school's information,
                and in the last position an indicator of the similarity of the schools' name based on Levenshtein's distance,
                and the Set Ratio as a scorer.

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

        elif (av_choice.shape[0] == 0) & (na_choice.shape != 0):
            av_ans = process.extractOne(self.name_original, av_choice[:, 0], scorer=fuzz.token_set_ratio)
            na_ans = (0, 0)
        else:
            av_ans = (0, 0)
            na_ans = (0, 0)

        fit_av = np.array(av_ans[1]).reshape(1, 1)
        fit_na = np.array(na_ans[1]).reshape(1, 1)

        if fit_av >= fit_na:
            self.solution = comparisons[comparisons[:, 0] == av_ans[0]]
            self.unique = self.multiple(self.solutionPicker(self.solution)).reshape(1, 4)
            return np.hstack([self.information, self.unique, fit_av, self.first])
        else:
            self.solution = comparisons[comparisons[:, 0] == na_ans[0]]
            self.unique = self.multiple(self.solutionPicker(self.solution)).reshape(1, 4)
            return np.hstack([self.information, self.unique, fit_na, self.first])

    def solutionPicker(self, solution):
        """ Filters out non-credible solutions.

            The extractOne function of the Fuzzy Wuzzy Library extracts the most similar school name to the original.
            In the method matcher, the algorithm searches for all the comparisons that have the same name as the closest match.
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
                            return np.zeros((1, 4))

            elif self.status == "DaneNaN":
                prov = solution[solution[:, 1] == self.mun_original]
                if prov.shape[0] > 0:
                    return prov
                else:
                    return np.zeros((1, 4))
            elif self.status == "MunNaN":
                prov = solution[solution[:, 2] == self.dane_schoriginal]
                if prov.shape[0] > 0:
                    return prov
                else:
                    return np.zeros((1, 4))
            else:
                return np.zeros((1, 4))

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

        self.first = 0
        if solmulti.shape[0] > 1:
            self.first = 1
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
            self.with_codes: a NumPy 2D-array that contains the schools that have the same information (either DANE or
                             municipality) as the original school.

            self.with_na: a NumPy 2D-array that contains the schools that do not have the same information as the
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
            self.with_codes = comparisons[comparisons[:, 2] == self.dane_schoriginal]
            self.with_na = comparisons[comparisons[:, 2] != self.dane_schoriginal]

            if len(self.with_codes) == 0 and len(self.with_na) != 0:
                self.with_codes = self.with_na
                return self.with_codes, self.with_na
            elif len(self.with_na) == 0 and len(self.with_codes) != 0:
                self.with_na = self.with_codes
                return self.with_codes, self.with_na
            elif len(self.with_codes) == 0 and len(self.with_na) == 0:
                return comparisons, comparisons
            else:
                return self.with_codes, self.with_na


        elif pd.isna(self.mun_original) and pd.isna(self.dane_schoriginal):
            self.status = "FulNaN"
            return comparisons, comparisons

        elif pd.isna(self.dane_schoriginal) and not pd.isna(self.mun_original):
            self.status = "DaneNaN"
            self.with_codes = comparisons[comparisons[:, 1] == self.mun_original]
            self.with_na = comparisons[comparisons[:, 1] != self.mun_original]
            return self.with_codes, self.with_na

        else:
            self.status = "Complete"
            self.with_codes = comparisons[(comparisons[:, 1] == self.mun_original) | (comparisons[:, 2] == self.dane_schoriginal)]
            self.with_na = comparisons[(comparisons[:, 1] != self.mun_original) | (comparisons[:, 2] != self.dane_schoriginal)]
            return self.with_codes, self.with_na


def do_match(original_db, comparison_db, deb=0, deb2=0, doc="matcher.xlsx", partial=True, freq=10000):
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
    results = np.zeros((1, 9))

    for i in range(deb, last):
        print(i)
        if pd.isna(original_db[i][0]):
            pass
        else:
            results = np.vstack([results, school(original_db[i]).matcher(comparison_db)])
            if i == (last-1):
                results = pd.DataFrame(results)
                results.columns = ["Original School Name", "Original Municipality", "Original DANE", "Original ID",
                                   "Match School Name",    "Match Municipality",    "Match DANE",    "Match ID",
                                   "Similarity"]

                results.to_excel(doc)

        if partial and i % freq == 0:
            name = str(i)+doc
            to_excel = pd.DataFrame(results)
            to_excel.columns = ["Original School Name", "Original Municipality", "Original DANE", "Original ID",
                                "Match School Name",    "Match Municipality",    "Match DANE",    "Match ID",
                                "Similarity"]
            to_excel.to_excel(name)
    return results


def stata_codes(info, doc="stata_codes.xlsx"):
    """ This function creates the code needed in Stata to impute to each school in the Original Database the ID codes
    in the comparison database.

    Arguments
    -------------
    info: It's a Pandas Data Frame with the output of the do_match. It could be either the Python Variable, or
    an imported Spreadsheet.

    doc: The name of Excel Spreadsheet.

    Returns
    -------------
        This function returns Pandas Data Frame with all the Stata codes necessary to create a variable that can relate
        each school in the Original Database with the comparison Database.
        In addition, it creates an Excel Spreadsheet with it.

    """
    length = info.shape[0]
    database = info.iloc
    txt = "replace newID = "
    txt2 = " if ID == "
    codes = np.array(["gen newID = ."])
    for i in range(length):
        if database[i, 4] == "0" or pd.isna(database[i, 4]):
            pass
        else:
            line = txt + str(database[i, 7]) + txt2 + str(database[i, 3])
            codes = np.vstack([codes, line])

    codes = pd.DataFrame(codes)
    codes.to_excel(doc)
    return codes

