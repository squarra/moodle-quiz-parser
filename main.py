from flask import Flask, render_template
from bs4 import BeautifulSoup


class Question:
    def __init__(self, data):
        self.qtext = data.find("div", {"class": "content"}).contents[0].contents[2].text
        self.answers = []

    def __repr__(self):
        return f"{self.__class__.__name__}{vars(self)}"


class MultichoiceQuestion(Question):
    def __init__(self, data):
        super().__init__(data)
        options = data.find("div", {"class": "answer"}).find_all("div", recursive=False)
        self.single_choice = options[0].input["type"] == "radio"
        self.answers = [
            {"text": option.div.div.text, "correct": False} for option in options
        ]
        corr = [
            c.text
            for c in data.find("div", {"class": "rightanswer"}).find_all(
                "p", recursive=False
            )
        ]
        for answer in self.answers:
            if answer["text"] in corr:
                answer["correct"] = True


class TrueFalseQuestion(Question):
    def __init__(self, data):
        super().__init__(data)
        self.answers = ["True", "False"]
        self.correct = data.find("div", {"class": "rightanswer"}).contents


class DescriptionQuestion(Question):
    def __init__(self, data):
        super().__init__(data)


def parse_questions(ques):
    questions = []
    for que in ques:
        classes = que["class"]
        if "multichoice" in classes:
            questions.append(MultichoiceQuestion(que))
        elif "truefalse" in classes:
            questions.append(TrueFalseQuestion(que))
        elif "description" in classes:
            questions.append(DescriptionQuestion(que))
        else:
            questions.append(Question(que))
    return questions


app = Flask(__name__)
app.jinja_env.globals.update(
    isinstance=isinstance,
    MultichoiceQuestion=MultichoiceQuestion,
    TrueFalseQuestion=TrueFalseQuestion,
    DescriptionQuestion=DescriptionQuestion,
)


@app.route("/")
def home():
    with open("quiz.html") as f:
        data = f.read()
        soup = BeautifulSoup(data, "html.parser")
        title = soup.body.find("div", {"class": "page-header-headings"}).text
        ques = soup.body.find_all("div", {"class": "que"})
        questions = parse_questions(ques)
    return render_template("index.html", title=title, questions=questions)


if __name__ == "__main__":
    app.run(debug=True)
