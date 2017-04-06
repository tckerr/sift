class Personality(object):
  
    def __init__(self, data):
        self.openness = data["openness"]
        self.conscientiousness = data["conscientiousness"]
        self.extraversion = data["extraversion"]
        self.agreeableness = data["agreeableness"]
        self.neuroticism = data["neuroticism"]

    def __repr__(self):
        return "[O({}), C({}), E({}), A({}), N({})]".format(
            str(self.openness),
            str(self.conscientiousness),
            str(self.extraversion),
            str(self.agreeableness),
            str(self.neuroticism))

class Recruiter(object):
    def __init__(self, data):
        self.min_commission = data["min_commission"]        

class Candidate(object):

    def __init__(self, data):
        self.id = data["id"]
        self.first_name = data["first_name"]
        self.last_name = data["last_name"]
        self.gender = data["gender"]
        self.age = data["age"]
        self.years_experience = data["years_experience"]
        self.salary_requirement = data["salary_requirement"]
        self.is_looking = data["is_looking"]
        self.personality = Personality(data["personality"])

    def __repr__(self):
        return "{} {}".format(self.first_name, self.last_name)


class Employer(object):
    def __init__(self, data):
        self.name = data["name"]
        self.requirements = data["requirements"]
        self.commission_pct = data["commission_pct"]
        self.quantity = data["quantity"]

    def __repr__(self):
        return "{}".format(self.name)
