from siftpy import SiftBuilder, ContextProvider
import json, os

class JsonLoader(object):

    def load(self, path):
        with open(path, 'r', encoding='utf-8') as jsonfile:
            return json.loads(jsonfile.read())

class Student(object):

    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.popularity = data["popularity"]
        self.grades = data["grades"]

    def __repr__(self):
        return "[Student Object ID: {}]".format(str(self.id))

class Seat(object):
  
    def __init__(self, data):
        self.id = data["id"]
        self.column = data["column"]
        self.row = data["row"]
        self.student = None

    def __repr__(self):
        return "[Seat Object ID: {}]".format(str(self.id))


class FinalsWeekContextProvider(ContextProvider):

    def __init__(self, dictionary, *args, **kwargs):
        super(FinalsWeekContextProvider, self).__init__(*args, **kwargs)
        self.students = []
        self.seats = []
        self.requestor_student = None
        self.requestor_seat = None

        for student_data in dictionary["students"]:
            student = Student(student_data)
            if student.id == dictionary["requestor_student_id"]:
                self.requestor_student = student
            self.students.append(student)

        for seat_data in dictionary["seats"]:
            self.seats.append(Seat(seat_data))

        for seat_mapping in dictionary["seat_map"]:
            student = self.__get(self.students, id=seat_mapping["student_id"])
            seat = self.__get(self.seats, row=seat_mapping["row"], column=seat_mapping["column"])
            seat.student = student

        self.requestor_seat = self.__get(self.seats, student=self.requestor_student)

        self.__init_context()

    def __init_context(self):
        self.context.students = self.students
        self.context.seats = self.seats
        self.context.requestor.student = self.requestor_student
        self.context.requestor.seat = self.requestor_seat


    def __get(self, arr, **values):
        for item in arr:
            failed = False
            for key, value in values.items():
                if not getattr(item, key) == value:
                    failed = True
            if not failed:
                return item 

    def requestor_by_type(self, cls):
        if cls is Student:
            return self.requestor_student
        if cls is Seat:
            return self.requestor_seat
    
    def all_of_type(self, cls):
        if cls is Student:
            return self.students
        if cls is Seat:
            return self.seats
        

def print_component(component):
    string = ''
    if component.__class__ is Seat:
        string += "      Seat -- ID: {}, Row: {}, Col: {}".format(str(component.id),str(component.row),str(component.column))
    if component.__class__ is Student:
        string += "      Student -- ID: {}, Grades: {}, Popularity: {}".format(str(component.id),str(component.grades),str(component.popularity))
    print(string)

def print_results(results, context_provider):
    print ("--- results ---")
    requestor_seat = context_provider.requestor_by_type(Seat)
    requestor_student = context_provider.requestor_by_type(Student)
    print("Requestor Seat -- ID: {}, Row: {}, Col: {}".format(str(requestor_seat.id),str(requestor_seat.row),str(requestor_seat.column)))
    print("Requestor Student ID: {}, Grades: {}, Pop: {}".format(str(requestor_student.id),str(requestor_student.grades),str(requestor_student.popularity)))

    for component in results:
        if component.__class__ is list:
            print("Component set OR:")
            for item in component:
                print_component(item)
        else:
            print_component(component)
    
strategy_json_path = os.path.dirname(__file__) + 'fixtures/choices.json'        
seed_json_path = os.path.dirname(__file__) + 'fixtures/student_seed_2.json'        
strategy_data = JsonLoader().load(strategy_json_path)      
seed_data = JsonLoader().load(seed_json_path)      

context_provider = FinalsWeekContextProvider(seed_data)
sift = SiftBuilder().build(strategy_data, context_provider)
sift.print()

#results = sift.evaluate().data
#print_results(results, context_provider)
from pprint import pprint
for choice in sift.current_choice:
    pprint(choice.question)
    choice.choose(input())
print(sift.results())