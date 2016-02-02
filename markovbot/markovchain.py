import utils

class MarkovChain(object):
    def __init__(self, word_grouping=2, min_sentence_length=5):
        self.chain = {}
        self.parsed_words = 0
        self.parsed_messages = 0
        self.word_grouping = word_grouping
        self.min_sentence_length = min_sentence_length

        self.start_index = "START"
        self.end_index = "END"

    def get_pairs(self, words):
        words = [self.start_index] + words + [self.end_index]

        for i in range(len(words) - 1):
            yield (words[i], words[i + 1])

    def get_groups(self, words):
        words = [self.start_index] + words + [self.end_index]

        if len(words) < self.word_grouping:
            return

        for i in range(len(words) - (self.word_grouping - 1)):
            yield (words[i:i+self.word_grouping])

    def add_message(self, message):
        words = message.split()
        if len(words) < self.min_sentence_length:
            return
        self.parsed_messages += 1
        self.parsed_words += len(words)

        groups = self.get_groups(words)
        first = True
        for group in groups:
            if first:
                self.add_to_chain(self.start_index, tuple(group[1:]))
                first = False
            key = tuple(group[:len(group) - 1])
            value = group[-1]
            self.add_to_chain(key, value)

    def add_to_chain(self, key, value):
        if key in self.chain:
            self.chain[key].append(value)
        else:
            self.chain[key] = [value]

    def generate_text(self, max_length=25):
        generated_text = []

        test_group = utils.randomelement(self.chain[self.start_index])
        if test_group[-1] == self.end_index:
            generated_text += list(test_group[:len(test_group) - 1])
            return ' '.join(generated_text)
        else:
            generated_text += list(test_group)

        last_end = 0
        for i in range(max_length):
            possible_words = self.chain[test_group]
            if self.end_index in possible_words:
                last_end = i

            word = utils.randomelement(self.chain[test_group])
            if word == self.end_index:
                break
            generated_text.append(word)
            test_group = test_group[1:] + (word,)

        generated_text = generated_text[:last_end + self.word_grouping - 1]
        return ' '.join(generated_text)
