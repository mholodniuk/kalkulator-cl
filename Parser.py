from bs4 import BeautifulSoup
from Course import Course

class Parser:

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


    def divide_into_sublists(chunked_list: list) -> list:
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
        filtered_list = list(filter(None, unfiltered_list))
        chunked_list = list()
        for i in range(0, len(filtered_list), 5):
            chunked_list.append(filtered_list[i:i+5])
        
        return chunked_list


    def find_course_data(semester_table_data: str) -> list:
        '''
        params: str -  semester_table_data to parse and find proper course data

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