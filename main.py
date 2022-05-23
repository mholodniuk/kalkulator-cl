import os
from numpy import empty
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv('.env')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

@dataclass
class Course:
    id: str # kod kursu
    course_name: str # nazwa kursu
    class_types: str # forma zajęć
    ects_value: int # punkty ECTS 
    grade: float # ocena

@dataclass
class Semester:
    id: int
    number_of_ECTS: int
    courses: list
    number_of_courses: len(courses)

def calculate_average(courses: list) -> float:
    '''
    param: courses - list of Course objects

    returns: average grade from given course list
    '''
    grade_times_ects = 0
    ects_result = 0
    for course in courses:
        grade_times_ects += course.grade * course.ects_value
        ects_result += course.ects_value

    return (grade_times_ects/ects_result)



def divide_into_sublists(chunked_list: list):
    '''
    param: chunked list - raw list of undivided courses

    Divides given lists into correct order

    returns: list (semesters) of lists (courses in this semester) 
    '''
    courses_in_semester = []
    semester_list = []
    for chunck in chunked_list:
        if(chunck[0].strip() != "Kod kursu"):
            courses_in_semester.append(
                Course(chunck[0].strip(), chunck[1].strip(), chunck[2].strip(), int(chunck[3]), float(chunck[4])))
        else:
            semester_list.append(courses_in_semester)
            courses_in_semester = []
    if courses_in_semester:
        semester_list.append(courses_in_semester)
    semester_list.pop(0)

    return semester_list



def filter_data(unfiltered_list: list) -> list:
    '''
    param: unfiltered_list - list with empty spaces and undivided into Course format

    returns: beautiful filtered list
    '''
    unfiltered_list = list(filter(None, unfiltered_list))
    chunked_list = list()
    for i in range(0, len(unfiltered_list), 5):
        chunked_list.append(unfiltered_list[i:i+5])
    
    return chunked_list



def find_course_data(semester_table_data: str) -> list:
    '''
    params: soup - BeautifulSoup object to parse for proper course data

    return: nice formatted data
    '''
    soup = BeautifulSoup(semester_table_data, 'html.parser')
    list_of_courses = []
    for tr in soup.find_all('tr'):
        for td in tr:
            word = str(td.text)
            word = word.replace("\r\n", "")
            word = word.replace("\xa0", "")
            word = word.replace("\n", "")
            word = word.strip()
            list_of_courses.append(word)

    return list_of_courses



def find_courses_table(semester: int, courses: BeautifulSoup) -> list:
    '''
    params: semester to look for grades (all grades must be given)

    returns: table with proper semester data
    '''
    semester_list = []
    table = courses.find_all('table', {'class': 'KOLOROWA'})[semester + 3]
    for row in table:
        semester_list.append(row)
    return semester_list

class EdukacjaCl:
    session: requests.session.Session
    web_token: str
    web_session_token: str

    def __init__() -> None:
        pass

with requests.Session() as session:
    # get login page to get the client authorization key
    get_login = session.get("https://edukacja.pwr.wroc.pl/EdukacjaWeb/studia.do")
    if get_login:
        # get the html code
        soup = BeautifulSoup(get_login.content, 'html.parser')
        web_token = soup.find('input', {'name': 'cl.edu.web.TOKEN'}).get('value')

        # get the token from form tag and compose login-post data
        data = {
            'cl.edu.web.TOKEN': web_token,
            'login': username,
            'password': password,
        }

        #log in 
        post_login = session.post("https://edukacja.pwr.wroc.pl/EdukacjaWeb/logInUser.do", data=data)
        #print(post_login.text)
        if post_login:

            login = BeautifulSoup(post_login.content, 'html.parser')

            # get the token from form tag and compose login-post data
            web_session_token = login.find('input', {'name': 'clEduWebSESSIONTOKEN'}).get('value')

            # get the index subpage
            index = "https://edukacja.pwr.wroc.pl/EdukacjaWeb/indeks.do?clEduWebSESSIONTOKEN=" + web_session_token + \
                "&event=WyborSluchacza"
            get_index = session.get(index)

            courses = BeautifulSoup(get_index.content, 'html.parser')

            data = []
            data.append(find_courses_table(1, courses))
            data.append(find_courses_table(2, courses))
            data.append(find_courses_table(3, courses))

        
            course_list = find_course_data(str(data))

            chunked_list = filter_data(course_list)

            semester_list = divide_into_sublists(chunked_list)

            for semester in reversed(semester_list):
                print(calculate_average(semester))