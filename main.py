import os
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
    id: int # kod kursu
    course_name: str # nazwa kursu
    class_types: str # forma zajęć
    ECTS_value: int # punkty ECTS 
    grade: float # ocena

@dataclass
class Semester:
    id: int
    number_of_ECTS: int
    number_of_courses: int
    courses: list

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
            # decompose do usuniecia elementow !!

            semester_list = []
            second = []
            #iterate through all valid semesters -> must be given by user
            # semestry od 1 do 4
            for i in range(3, 7):
                table = courses.find_all('table', {'class': 'KOLOROWA'})[i]
                for row in table:
                    semester_list.append(row)
                    #print(row)

            

            line = str(semester_list)
            #print(line)
            course_list = list()
            soup = BeautifulSoup(line, 'html.parser')
        
            for tr in soup.find_all('tr'):
                for td in tr:
                    word = str(td.text)
                    word = word.replace("\r\n", "")
                    word = word.replace("\xa0", "")
                    word = word.replace("\n", "")
                    word = word.replace("  ", " ")
                    course_list.append(word)

            course_list = list(filter(None, course_list))

            chunked_list = list()
            for i in range(0, len(course_list), 5):
                chunked_list.append(course_list[i:i+5])

            print(chunked_list)