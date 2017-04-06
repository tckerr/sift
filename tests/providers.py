from tests.objects import Recruiter, Candidate, Employer
from siftpy import ContextProvider

class ExampleContextProvider(ContextProvider):

    def __init__(self, candidates, employers, recruiter, *args, **kwargs):
        super(ExampleContextProvider, self).__init__(*args, **kwargs)
        recruiter = Recruiter(recruiter)
        candidates = [Candidate(data) for data in candidates]    
        employers = [Employer(data) for data in employers]
        self.__init_context(recruiter, candidates, employers)

    def __init_context(self, recruiter, candidates, employers):
        self.context.recruiter = recruiter
        self.context.candidates = candidates
        self.context.employers = employers

    def __get(self, arr, **values):
        for item in arr:
            failed = False
            for key, value in values.items():
                if not getattr(item, key) == value:
                    failed = True
            if not failed:
                return item 