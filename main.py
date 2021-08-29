from io import StringIO

from flask import render_template, Flask, request
import pandas as pd

app = Flask(__name__, instance_path="/Users/svgro/Documents/coding_projects/learning_center_attendance_V2/instance")


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/uploader', methods=['POST'])  # look at later
def uploader():
    try:
        if request.method == 'POST':
            aeries_query = pd.read_excel(request.files['aeriesQuery'])
            program_roster = pd.read_excel(request.files['programRoster'], sheet_name=None)
            query_program(aeries_query, program_roster)
            return 'file uploaded successfully'
    except Exception as e:
        print(e)


def query_program(aeries_query: pd.DataFrame, program_roster: dict[str, pd.DataFrame]):
    #https://stackoverflow.com/questions/10715965/create-a-pandas-dataframe-by-appending-one-row-at-a-time/17496530#17496530
    dict_list = []
    # output_df = pd.DataFrame(columns=['Student ID',	'Last Name', 'First Name', 'Middle Name', 'Birthdate', 'Sex', 'Grade', 'LangFlu', 'EthCd', 'Race1', 'Class0', 'Class1', 'Class2', 'Class3', 'Class4', 'Class5', 'Class6', 'Class7', 'Class8', 'Class9', 'Class10', 'AVID', 'ELD', 'PTS', 'ETS', 'MIG', 'Ethnic Code'])
    aeries_query.groupby('Student ID').apply(
        lambda df: dict_list.append(convert_to_one_row(df))
    )
    output_df = pd.DataFrame(dict_list)
    add_programs() ##see if I can do some sort of join here or something
    print('hi')


def convert_to_one_row(input_df: pd.DataFrame) -> dict:
    single_row_dict = input_df.iloc[0].to_dict()
    [add_dict_values(single_row_dict, subject, period, semester) for subject, period, semester in zip(input_df['Course title'], input_df['Period'], input_df['Semester'])]
    remove_cols = ['Course title', 'Period', 'Semester']
    [single_row_dict.pop(key) for key in remove_cols]
    return single_row_dict
    ###convert one row to dict, then add the classes one by one

def add_dict_values(row_dict, subject, period, semester):
    if 'AVID' in subject:
        row_dict['AVID'] = 'x'
    row_dict['class' + str(period)] = subject


def readLocalFiles():
    aeries_query = pd.read_excel('Aeries Student Roster Query - August 18, 2021.xlsx')
    program_roster = pd.read_excel('Program Roster (8.19.21).xlsx', sheet_name=None)
    query_program(aeries_query, program_roster)

readLocalFiles()
# app.run()
