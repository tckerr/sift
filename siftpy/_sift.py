from __future__ import absolute_import, division, print_function, unicode_literals

from siftpy._util.helpers import (merge, flatten, filter_list) 
from siftpy._util.printers import SiftPrinter
from siftpy._util.exceptions import InvalidChoiceException, ValidationException


class Choice(object):
    def __init__(self, options, sift):
        self.__sift = sift
        self.pending = True
        self.question = self.__build_question(options)
        
    def __build_question(self, choices):
        return {str(i): choice for i, choice in enumerate(choices)}

    def choose(self, i):
        index = str(i)
        if index not in self.question:
            raise InvalidChoiceException("Answer '{}'' is not present in the list of options".format(index))
        answer = [self.question[index]]
        self.pending = False
        self.__sift.provide_answer(answer)

class ContextObjectListProvider(object):
    def next(self, context_provider, context_source):
        val = getattr(context_provider.context, context_source)
        if val is None:
            raise StopIteration()
        try:
            iterator = iter(val)            
        except:
            iterator = [item]
        for item in iterator:
            yield item

    def list(self, context_provider, context_source):
        return list(self.next(context_provider, context_source))


class Sift(object):    

    def __init__(self, config):
        self.config = config
        self.__printer = self.config.SiftPrinter(self.config)
        self.__choice_results = None
        self.__context_object_list_provider = ContextObjectListProvider()

    @property
    def current_choice(self):
        while(True):
            choice = self.get_choice()
            if not choice:
                break
            yield choice
        raise StopIteration()

    def get_choice(self):       

        for self in self.sifts:
            choice = self.get_choice()
            if choice:
                return choice

        if self.is_choice:
            options = self.results()
            if options:
                return Choice(options, self)

    def provide_answer(self, results):
        if not self.is_choice:
            raise Exception("You cannot 'answer' a result sift")
        self.__choice_results = results
        self.is_choice = False

    def print(self):
        self.__printer.print(self)

    def results(self):
        if self.__choice_results is not None:
            return self.__choice_results

        return self.__filter_and_convert(self.__branch_results)

    @property
    def __branch_results(self):
        if self.__is_leaf:
            return self.__leaf_results
        return flatten(self.__child_sift_results)

    @property
    def __is_leaf(self):
        return len(self.sifts) == 0    

    @property
    def __leaf_results(self):
        return self.__context_object_list_provider.list(self.context_provider, self.context_source)

    @property
    def __child_sift_results(self):
        return [sift.results() for sift in self.sifts]

    def __filter_and_convert(self, result_set):
        filtered = self.__filter(result_set)
        if self.returning_object_property is not None:
            return self.__convert(filtered)
        return filtered

    def __filter(self, object_list):
        for filter_fn in self.filters:
            object_list = filter_list(filter_fn, object_list)
        return object_list

    def __convert(self, result_set): 
        new_result_set = []
        for result in result_set:
            prop = getattr(result, self.returning_object_property)
            if prop:
                new_result_set.append(prop)
        return new_result_set