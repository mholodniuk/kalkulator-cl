import os
import requests
from bs4 import BeautifulSoup
from Parser import Parser
import dotenv


class EdukacjaCl:
    session: requests.session
    username: str
    password: str
    current_semester: int
    web_token: str
    web_session_token: str
    index: str

    def __init__(self, session: requests.session, username=None, password=None, from_file=False) -> None:
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

        if from_file:
            # create exmples directory and add your index.html file from edukacja.cl
            self.index = self.get_index_from_file('./examples/index.html')
        else:
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

        # to do: check if this was successful
        login = BeautifulSoup(post_login.content, 'html.parser')
        
        return login.find('input', {'name': 'clEduWebSESSIONTOKEN'}).get('value')


    def get_index(self) -> str:
        index_url = "https://edukacja.pwr.wroc.pl/EdukacjaWeb/indeks.do?clEduWebSESSIONTOKEN=" + self.web_session_token + \
            "&event=WyborSluchacza"
        try:
            return self.session.get(index_url).content
        except:
            print('Unable to get the index subpage')
            exit()

    def get_index_from_file(self, file_name: str) -> str:
        try:
            with open(file_name, 'r') as file:
                return file.read()
        except:
            print(f'Could not open {file_name}')
            exit()


    def get_current_semester(self) -> int:
        return int(Parser.find_student_data(BeautifulSoup(self.index, 'html.parser'), 'Numer semestru'))


    def print_gpa_from_semester_list(self, semesters: list) -> None:
        # not sure about edge case here
        if any(nr < 1 or nr > self.current_semester for nr in semesters):
            print('given semester(s) list is out of range')
        else:
            courses = BeautifulSoup(self.index, 'html.parser')

            semesters_list = []
            for i in semesters:
                semesters_list.extend(
                    Parser.find_semesters_data(courses, (self.current_semester - i))    
                )

            course_list = Parser.split_into_course_format(
                Parser.filter_and_format_data(
                    Parser.search_for_rows_and_filter(str(semesters_list))
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
    # edukacja = EdukacjaCl(requests.Session(), username=pwr123456, password=password)
    edukacja = EdukacjaCl(requests.Session(), from_file=False)
    
    # no space on the end
    semesters_input = str(input("Podaj semestry, z których średnie policzyć (np. 1 2 3): "))
    semester_list = [int(i) for i in list(semesters_input.split(' '))]

    edukacja.print_gpa_from_semester_list(semester_list)