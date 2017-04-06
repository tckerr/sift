from siftpy import SiftBuilder
from tests.providers import ExampleContextProvider
import os
from tests.data.loaders import JsonLoader
from pprint import pprint

def generate_context():    
    candidates_json_path = os.path.dirname(__file__) + '/data/fixtures/seeds/candidates.json'   
    employers_json_path = os.path.dirname(__file__) + '/data/fixtures/seeds/employers.json'   
    recruiter_json_path = os.path.dirname(__file__) + '/data/fixtures/seeds/recruiter.json'   

    loader = JsonLoader()
    candidates_data = loader.load(candidates_json_path)      
    employers_data = loader.load(employers_json_path)      
    recruiter_data = loader.load(recruiter_json_path)      

    return ExampleContextProvider(candidates_data, employers_data, recruiter_data)

def get_recruiter_requirements():
    requirements_json_path = os.path.dirname(__file__) + '/data/fixtures/sifts/recruiter_requirements.json'   
    return JsonLoader().load(requirements_json_path)

def get_employer_requirements():
    requirements_json_path = os.path.dirname(__file__) + '/data/fixtures/sifts/employer_requirements.json'   
    return JsonLoader().load(requirements_json_path)

def candidate_sift():
    context_provider = generate_context()
    builder = SiftBuilder()
    
def print_dollars(value):
    return '${:,.2f}'.format(value)

def run_test():
    context_provider = generate_context()
    builder = SiftBuilder()
    ''' 
    Let's find all candidates who are:
        - looking
        - years_experience >= 2
        - min salary of 60k
        - satisfy ONE of the following: 
            - Salary requirement is > than 90k
            - agreeableness AND conscientiousness are each >= 4
    '''
    recruiter_requirements = get_recruiter_requirements()
    candidate_sift = builder.build(recruiter_requirements, context_provider)
    choice = candidate_sift.get_choice()
    print(choice.question)
    choice.choose(input())
    eligible_candidates = candidate_sift.results()
    context_provider.context.eligible_candidates = eligible_candidates

    '''
    Now let's find some employers who will hire our candidates.
    Only ones worth our time are:
        - hiring at least one person
        - meets the recruiter's min commission
    '''
    employer_requirements = get_employer_requirements()
    employer_sift = builder.build(employer_requirements, context_provider)
    eligible_employers = employer_sift.results()
    eligible_employers = sorted(eligible_employers, key=lambda e: e.commission_pct, reverse=True)

    '''
    Now let's match candidates to employers.
    '''
    earnings = 0
    placed = []
    for employer in eligible_employers:
        employer_filter = {
            "is_choice": False,
            "context_source": "eligible_candidates",
            "filters": employer.requirements
        }
        sift = builder.build(employer_filter, context_provider)
        candidates = sorted(sift.results(),  key=lambda e: e.salary_requirement)
        for slot in range(0, min(employer.quantity, len(candidates))):
            candidate = candidates.pop()
            local_earnings = candidate.salary_requirement * employer.commission_pct
            placed.append(candidate)
            print("Placing {} {} at {}. Recruiter earnings {} * {} = {}.".format(
                candidate.first_name,
                candidate.last_name,
                employer.name,
                print_dollars(candidate.salary_requirement),
                str(employer.commission_pct),
                print_dollars(local_earnings)))
            earnings += local_earnings

        context_provider.context.eligible_candidates = [c for c in context_provider.context.eligible_candidates if c not in placed]

    print("Done! Placed {} candidates for total earnings of: {}".format(str(len(placed)), print_dollars(earnings)))