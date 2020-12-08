from random import randint
import re

## Fix Housing File
def clean_housing(Housing, Zip, auto_zip):

    # Fills in missing values with placeholder "Corrupted" value so program can generate appropriate value
    Housing.fillna("ZZZZ", inplace=True)

    # Fix guid
    list_h = []
    for i in range(len(Housing)):
        if re.search("^[A-Z]{4}$", Housing.iloc[i, 0]):
            list_h.append(i)
    Housing.drop(Housing.index[list_h], inplace=True)

    # Fix zip code data with nearby zip code from Zip dataset
    for i in range(len(Housing)):
        if re.search("^[A-Z]{4}$", Housing.iloc[i, 1]):
            search = str(Housing.iloc[i, 0])

            rslt = Zip.loc[Zip["guid"] == search]
            zip_r = rslt.iloc[0, 1]
            city_r = rslt.iloc[0, 2]
            corr = Zip.query('zip_code!=@zip_r & city==@city_r')
            Housing.iloc[i, 1] = corr.iloc[0, 1][0] + str("0000")
            auto_zip[search] = str(Housing.iloc[i,1])

    # Clean rest of Housing data
    Housing['housing_median_age'].replace("^[A-Z]{4}$", value=randint(10, 50), inplace=True, regex=True)
    Housing['total_rooms'].replace("^[A-Z]{4}$", value=randint(1000, 2000), inplace=True, regex=True)
    Housing['total_bedrooms'].replace("^[A-Z]{4}$", value=randint(1000, 2000), inplace=True, regex=True)
    Housing['population'].replace("^[A-Z]{4}$", value=randint(5000, 10000), inplace=True, regex=True)
    Housing['households'].replace("^[A-Z]{4}$", value=randint(500, 2500), inplace=True, regex=True)
    Housing['median_house_value'].replace("^[A-Z]{4}$", value=randint(100000, 250000), inplace=True, regex=True)
    return Housing, auto_zip

## Clean Income File
def clean_income(Income, auto_zip):

    # Fills in missing values with placeholder "Corrupted" value so program can generate appropriate value
    Income.fillna("ZZZZ", inplace=True)

    # Dropping rows with corrupted guid
    list_i = []
    for i in range(len(Income)):
        if re.search("^[A-Z]{4}$", Income.iloc[i, 0]):
            list_i.append(i)
    Income.drop(Income.index[list_i], inplace=True)

    # Correcting Zip codes with ones previously generated for Housing Data
    for i in range(len(Income)):
        if re.search("^[A-Z]{4}$", Income.iloc[i, 1]):
            Income.iloc[i, 1] = auto_zip[Income.iloc[i, 0]]

    # Correcting Income File's median income
    Income['median_income'].replace("^[A-Z]{4}$", value=randint(100000, 750000), inplace=True, regex=True)
    return Income

## Clean Zip File
def clean_zip(Zip, auto_zip):

    # Fills in missing values with placeholder "Corrupted" value so program can generate appropriate value
    Zip.fillna("ZZZZ", inplace=True)

    # Dropping rows with corrupted guid
    list_z = []
    for i in range(len(Zip)):
        if re.search("^[A-Z]{4}$", Zip.iloc[i, 0]):
            list_z.append(i)
    Zip.drop(Zip.index[list_z], inplace=True)

    # Correcting Zip codes with ones previously generated for Housing Data
    for i in range(len(Zip)):
        if re.search("^[A-Z]{4}$", Zip.iloc[i, 1]):
            Zip.iloc[i, 1] = auto_zip[Zip.iloc[i, 0]]

    return Zip
