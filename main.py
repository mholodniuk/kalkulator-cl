import os
import requests
from bs4 import BeautifulSoup
from Parser import Parser
import dotenv
from rsa import verify

class EdukacjaCl:
    session: requests.session
    username: str
    password: str
    current_semester: int
    web_token: str
    web_session_token: str
    index: str

    def __init__(self, session: requests.session, username=None, password=None) -> None:
        self.session = session
        if username is None or password is None:
            if os.path.exists('.env'):
                dotenv.load_dotenv('.env')
                self.username = os.getenv('USERNAME')
                self.password = os.getenv('PASSWORD')
            else:
                print('Could not find .env file, make sure to create it')
                exit()
        else:
            self.username = username
            self.password = password

        self.web_token = self.get_web_token()        
        self.web_session_token = self.get_web_session_token()
        self.index = self.get_index()
        self.current_semester = self.get_current_semester()


    def get_web_token(self) -> str:
        try:
            get_login = self.session.get("https://edukacja.pwr.wroc.pl/EdukacjaWeb/studia.do")
            home = BeautifulSoup(get_login.content, 'html.parser')
            return home.find('input', {'name': 'cl.edu.web.TOKEN'}).get('value')
        except requests.ConnectionError:
            print('Unable to connect to edukacja.cl')
            exit()


    def get_web_session_token(self) -> str:
        data = {
            'cl.edu.web.TOKEN': self.web_token,
            'login': self.username,
            'password': self.password 
        }
        post_login = self.session.post("https://edukacja.pwr.wroc.pl/EdukacjaWeb/logInUser.do", data=data)

        if requests.get(post_login.url, auth = (self.username, self.password)).status_code == 200:
            login = BeautifulSoup(post_login.content, 'html.parser')
            return login.find('input', {'name': 'clEduWebSESSIONTOKEN'}).get('value')
        else:
            print('Unable to log in using your data')
            exit()


    def get_index(self) -> str:
        index_url = "https://edukacja.pwr.wroc.pl/EdukacjaWeb/indeks.do?clEduWebSESSIONTOKEN=" + self.web_session_token + \
            "&event=WyborSluchacza"
        try:
            return self.session.get(index_url).content
        except:
            print('Unable to get the index subpage')
            exit()


    def get_current_semester(self) -> int:
        courses = BeautifulSoup(self.index, 'html.parser')
        personal_data = Parser.find_course_data(str(Parser.find_courses_table(-3, courses)))
        return int(personal_data[38])


    def print_gpa_from_semester_list(self, semesters: list) -> None:
        if any(nr < 1 or nr >= self.current_semester for nr in semesters):
            print('given semester list is out of range')
        else:
            courses = BeautifulSoup(self.index, 'html.parser')

            semesters_list = []
            for i in semesters:
                semesters_list.extend(
                    Parser.find_courses_table((self.current_semester - i), courses)    
                )

            course_list = Parser.divide_into_sublists(
                Parser.filter_data(
                    Parser.find_course_data(str(semesters_list))
                )
            )
            print(self.calculate_average_multiple_semesters(course_list))


    def calculate_average_multiple_semesters(self, semesters: list) -> float:
        grade_times_ects = 0
        ects_result = 0
        for semester in semesters:
            for course in semester:
                grade_times_ects += course.grade * course.ects_value
                ects_result += course.ects_value

        return (grade_times_ects / ects_result)


if __name__ == "__main__":
    edukacja = EdukacjaCl(requests.Session())
    
    number_of_semesters = str(input("Podaj semestry, z których średnie policzyć [np. 1 2 3]: "))
    semester_list = list(number_of_semesters.split(' '))
    semester_list = [int(i) for i in semester_list]

    edukacja.print_gpa_from_semester_list(semester_list)
    
