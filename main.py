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
class StudentData:
    index_number: int

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
    number_of_courses: int
    courses: list

def calculate_average(_courses: list) -> float:
    grade_times_ects = 0
    ects_result = 0
    for course in _courses:
        grade_times_ects += course.grade * course.ects_value
        ects_result += course.ects_value

    return (grade_times_ects/ects_result)

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

            semester_list = []
            # semestry od 1 do 4, musi być wypelniony ocenami, inaczej wyjdzie zle
            for i in range(4, 7):
                table = courses.find_all('table', {'class': 'KOLOROWA'})[i]
                for row in table:
                    semester_list.append(row)
            

            line = str(semester_list)
            course_list = list()
            soup = BeautifulSoup(line, 'html.parser')
        
            for tr in soup.find_all('tr'):
                for td in tr:
                    word = str(td.text)
                    word = word.replace("\r\n", "")
                    word = word.replace("\xa0", "")
                    word = word.replace("\n", "")
                    word = word.strip()
                    course_list.append(word)

            course_list = list(filter(None, course_list))

            chunked_list = list()
            for i in range(0, len(course_list), 5):
                chunked_list.append(course_list[i:i+5])

            tmp_courses = []
            semester_list = []
            for chunck in chunked_list:
                if(chunck[0].strip() != "Kod kursu"):
                    tmp_courses.append(
                        Course(chunck[0].strip(), chunck[1].strip(), chunck[2].strip(), int(chunck[3]), float(chunck[4])))
                else:
                    semester_list.append(tmp_courses)
                    tmp_courses = []
            
            if tmp_courses:
                semester_list.append(tmp_courses)

            semester_list.pop(0)

            for semester in semester_list:
                print(calculate_average(semester))

