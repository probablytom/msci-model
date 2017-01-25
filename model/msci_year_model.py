'''

    Tom Wallis, for my MSci 5th year project.
    A model of a student with several responsibilities through their MSci
        final year.

'''

# right now, responsibilities only come from lecturer to student.
# Later, the student will get responsibilities from lecturers as well as
#  ...classes, and they'll need to prioritise using responsibility formalism.

from msci_model_classes import Lecturer, Student

student = Student()
lecturer = Lecturer()  # An authority for responsibilities to come from


def model_main():
    print("There should really be a model here!")

if __name__ == "__main__":
    model_main()
