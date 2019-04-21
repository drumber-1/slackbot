import random
import pickle


class ReactionData:
    def __init__(self, message_floor=10):
        self.message_floor = message_floor
        self.total_messages = 0
        self.total_reactions = 0
        self.reaction_counts = {}

    def on_reaction(self, reaction):
        self.total_reactions += 1
        if reaction in self.reaction_counts:
            self.reaction_counts[reaction] += 1
        else:
            self.reaction_counts[reaction] = 1

    def on_message(self):
        self.total_messages += 1
        reaction_chance = self.total_reactions / max(self.total_messages, self.message_floor)
        reaction_roll = random.random()
        should_react = reaction_roll < reaction_chance
        if should_react:
            reaction_roll = random.randint(0, self.total_reactions + 1)
            cumulative = 0
            for r in self.reaction_counts:
                cumulative += self.reaction_counts[r]
                if reaction_roll < cumulative:
                    return r
            print("Ran out of reactions (This shouldn't happen!)")
        return None

    def save(self, filename):
        f = open(filename, 'wb')
        data = {"total_message": self.total_messages,
                "total_reactions": self.total_reactions,
                "reaction_counts": self.reaction_counts}
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        f.close()

    def load(self, filename):
        f = open(filename, 'rb')
        data = pickle.load(f)
        self.total_messages = data["total_message"]
        self.total_reactions = data["total_reactions"]
        self.reaction_counts = data["reaction_counts"]
        f.close()
