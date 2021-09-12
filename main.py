from io import StringIO

from flask import render_template, Flask, request
import pandas as pd
import numpy as np

app = Flask(__name__, instance_path="/Users/svgro/Documents/coding_projects/learning_center_attendance_V2/instance")


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/uploader', methods=['POST'])  # look at later
def uploader():
    try:
        if request.method == 'POST':
            aeries_query = pd.read_excel(request.files['aeriesQuery'])
            program_roster = pd.read_excel(request.files['programRoster'], sheet_name=None, skiprows=4)
            query_program(aeries_query, program_roster)
            return 'file uploaded successfully'
    except Exception as e:
        print(e)


def query_program(aeries_query: pd.DataFrame, program_rosters: dict[str, pd.DataFrame]) -> pd.DataFrame:
    # https://stackoverflow.com/questions/10715965/create-a-pandas-dataframe-by-appending-one-row-at-a-time/17496530#17496530
    dict_list = []
    # output_df = pd.DataFrame(columns=['Student ID',	'Last Name', 'First Name', 'Middle Name', 'Birthdate', 'Sex', 'Grade', 'LangFlu', 'EthCd', 'Race1', 'Class0', 'Class1', 'Class2', 'Class3', 'Class4', 'Class5', 'Class6', 'Class7', 'Class8', 'Class9', 'Class10', 'AVID', 'ELD', 'PTS', 'ETS', 'MIG', 'Ethnic Code'])
    aeries_query.groupby('Student ID').apply(
        lambda df: dict_list.append(convert_to_one_row(df))
    )
    output_df: pd.DataFrame = pd.DataFrame(dict_list)
    final_df = add_programs(output_df, program_rosters)
    final_df['Class8'] = ''
    final_df['Class10'] = 'College Bound'
    final_df = final_df[['Student ID', 'Last Name', 'First Name', 'Middle Name', 'Birthdate', 'Sex', 'Grade', 'LangFlu', 'EthCd', 'Race1', 'Class0', 'Class1', 'Class2', 'Class3', 'Class4', 'Class5', 'Class6', 'Class7', 'Class8', 'Class9', 'Class10', 'AVID', 'ELD', 'PTS', 'ETS', 'ME', 'Ethnic Code']]
    return final_df


def convert_to_one_row(input_df: pd.DataFrame) -> dict:
    single_row_dict = input_df.iloc[0].to_dict()
    [add_dict_values(single_row_dict, subject, period, semester) for subject, period, semester in
     zip(input_df['Course title'], input_df['Period'], input_df['Semester'])]
    remove_cols = ['Course title', 'Period', 'Semester']
    [single_row_dict.pop(key) for key in remove_cols]
    return single_row_dict
    ###convert one row to dict, then add the classes one by one


def add_dict_values(row_dict, subject, period, semester):
    if 'AVID' in subject:
        row_dict['AVID'] = 'x'
    row_dict['Class' + str(period)] = subject


def readLocalFiles():
    aeries_query = pd.read_excel('Aeries Student Roster Query - August 18, 2021.xlsx')
    program_roster = pd.read_excel('Program Roster (8.19.21).xlsx', sheet_name=None, skiprows=5)
    output_df = query_program(aeries_query, program_roster)
    output_df.to_excel('output.xlsx', index=False)


def add_programs(student_df: pd.DataFrame, program_rosters: dict[str, pd.DataFrame]) -> pd.DataFrame:
    for program_name_year, program_roster in program_rosters.items():
        if program_name_year != 'Tracklist':
            split_name = program_name_year.split(' ')
            program_name = split_name[0]
            # crate new column for program with nans
            student_df[program_name] = np.nan
            # merges program with aeries query on student id
            student_df = student_df.merge(program_roster, how='left', left_on='Student ID', right_on='Student ID', suffixes=('', '_remove'))
            # mark students who are in program in the new program column
            student_df.loc[student_df['Last'].notna(), program_name] = 'x'
            # removed unneeded extra columns from the join
            student_df = student_df.drop(['Grade_remove', 'EL', 'Last', 'First'], 1)

    return student_df


readLocalFiles()
# app.run()
