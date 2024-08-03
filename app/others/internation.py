
class Internation:
    HAN_EN = {
    }
    def get(self, en):
        return en
        return self.HAN_EN.get(en, en)

    def gets(self, en):
        return [self.HAN_EN.get(en, en), en]

HAN_EN = Internation()