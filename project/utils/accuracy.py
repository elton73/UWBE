"""
Class for finding accuracy of UWB data
"""

class Accuracy():
    def __init__(self):
        self.true_positives = 0
        self.true_negatives = 0
        self.false_positives = 0
        self.false_negatives = 0

    def get_sensitivity(self):
        return self.true_positives/(self.true_positives+self.false_negatives)

    def get_specificity(self):
        return self.true_negatives/(self.true_negatives+self.false_positives)

    def get_accuracy(self):
        return ((self.true_positives+self.true_negatives) /
                (self.true_positives+self.true_negatives+self.false_positives+self.false_negatives))

    def reset_accuracy(self):
        self.true_positives = 0
        self.true_negatives = 0
        self.false_positives = 0
        self.false_negatives = 0
