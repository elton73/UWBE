class Accuracy():
    def __init__(self):
        self.true_positives = None
        self.true_negatives = None
        self.false_positives = None
        self.false_negatives = None

    def get_sensitiviy(self):
        return self.true_positives/(self.true_positives+self.false_negatives)

    def get_specificity(self):
        return self.true_negatives/(self.true_negatives+self.false_positives)

    def get_accuracy(self):
        return ((self.true_positives+self.true_negatives) /
                (self.true_positives+self.true_negatives+self.false_positives+self.false_negatives))
