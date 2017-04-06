from __future__ import absolute_import, division, print_function, unicode_literals
from siftpy._util.helpers import (merge, flatten,) 
from siftpy._util.printers import SiftPrinter
from siftpy._util.exceptions import ValidationException
from siftpy._choice import Choice
from siftpy._reducer import Reducer
from siftpy._context_extractor import ContextExtractor

class Sift(object):    

    def __init__(self, config):
        self.config = config
        self.__printer = self.config.SiftPrinter(self.config)
        self.__context_extractor = ContextExtractor()
        self.__reducer = Reducer()
        self.__choice_results = None      
        self.__answered = False  

    def print(self):
        self.__printer.print(self)
        print(Translator(self.config).translate(self))

    @property
    def is_choice(self):
        return self.aggregation_type in (
            self.config.SiftAggregationType.ChooseSource,
            self.config.SiftAggregationType.ChooseElement,)


    def get_choice(self):
        for sift in self.sifts:
            choice = sift.get_choice()
            if choice:
                return choice
        if self.is_choice and not self.__answered:
            if self.aggregation_type == self.config.SiftAggregationType.ChooseElement:
                options = self.results()
                if options:
                    return Choice(options, self.__answer, None)  
            elif self.aggregation_type == self.config.SiftAggregationType.ChooseSource:
                options = self.sifts
                if options:
                    return Choice(options, self.__answer, "description")  

    def __answer(self, results):
        if not self.is_choice:
            raise Exception("You cannot 'answer' a result sift")
        self.__answered = True
        if self.aggregation_type == self.config.SiftAggregationType.ChooseElement:
            self.__choice_results = results
        else:
            self.sifts = [sift for sift in self.sifts if sift in results]

    def results(self):
        if self.__choice_results is not None:
            return self.__choice_results

        return self.__reducer.reduce(self.__branch_results, self.filters, self.returning_object_property)

    @property
    def __branch_results(self):
        if self.__is_leaf:
            return self.__leaf_results
        return flatten(self.__child_sift_results)

    @property
    def __is_leaf(self): return len(self.sifts) == 0  

    @property
    def __leaf_results(self):
        return self.__context_extractor.list(self.context_provider, self.context_source)

    @property
    def __child_sift_results(self):
        return [sift.results() for sift in self.sifts]


class Translator(object):

    def __init__(self, config):
        self.config = config

    def translate(self, sift):
        base_text = "Either" if sift.is_choice else "All items from"

        filter_descriptions = [self.__context_filter_description(filter) for filter in sift.original_source[self.config.SiftPropertyKey.Filters]]
        filter_text = "where " + ",".join(filter_descriptions) if filter_descriptions else ""

        if not sift.sifts:
            source = sift.context_source
        else:
            child_str = []
            for child in sift.sifts:
                child_str.append("(" + self.translate(child)+")")
            source = " {}".format(" OR ".join(child_str) )
            source = base_text + source
            
        return "{source} {filter_text}".format(base_text=base_text, source=source, filter_text=filter_text)

    def __context_filter_description(self, filter):
        return "{property} {operator} {comparison_value}".format(
                property=filter["property"],
                operator=filter["operator"],
                comparison_value=filter["comparison_value"])