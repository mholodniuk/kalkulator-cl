from bs4 import BeautifulSoup
from Course import Course

class Parser:

    def divide_into_sublists(chunked_list: list) -> list:
        '''
        param: chunked list - raw list of undivided courses

        Divides given list into list of lists (list of semesters, which are list of courses)
        and filters rows with title-data

        returns: list (semesters) of lists (courses in this semester) 
        '''
        courses_in_semester = []
        semester_list = []
        for chunk in chunked_list:
            if(chunk[0].strip() != "Kod kursu"):
                courses_in_semester.append(
                    Course(chunk[0].strip(), chunk[1].strip(), chunk[2].strip(), int(chunk[3]), float(chunk[4])))
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

        Divides the result of find_course_data method into Course type chunks
        (still including unnecessary title-data).

        returns: filtered list
        '''
        filtered_list = list(filter(None, unfiltered_list))
        chunked_list = list()
        for i in range(0, len(filtered_list), 5):
            chunked_list.append(filtered_list[i:i+5])
        
        return chunked_list


    def find_course_data(semester_table_data: str) -> list:
        '''
        params: str -  HTML text to parse and find proper course data

        Removes all the unnecessary parts of HTML from course_table_data,
        and transforms it into a list.

        return: nice formatted data (unfiltered)
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

        Finds all rows from the index table from given semester.

        returns: table with proper semester data (raw HTML)
        '''
        semester_list = []
        table = courses.find_all('table', {'class': 'KOLOROWA'})[semester + 3]
        for row in table:
            semester_list.append(row)
        return semester_list