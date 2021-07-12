from dialogs.dialog import Dialog
import requests
import logging


categories = [
    [['пульс'], {
        "id": 1,
        "name": "pulse",
        "description": "Пульс в покое",
        "unit": "удары в минуту",
        "type": "integer",
        "default_representation": "scatter",
        "is_legacy": False,
        "subcategory": "Измерения"
    }],
]
dry_categories = [
    {
        "id": 30,
        "name": "symptom",
        "description": "Симптом заболевания",
        "unit": "",
        "type": "string",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Общее",
    },
    {
        "id": 31,
        "name": "action",
        "description": "Действие",
        "unit": "",
        "type": "string",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Общее",
    },
    {
        "id": 19,
        "name": "waist_circumference",
        "description": "Окружность талии",
        "unit": "см",
        "type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 3,
        "name": "diastolic_pressure",
        "description": "Диастолическое (нижнее) артериальное давление",
        "unit": "мм рт. ст.",
        "type": "integer",
        "default_representation": "scatter",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 1,
        "name": "pulse",
        "description": "Пульс в покое",
        "unit": "удары в минуту",
        "type": "integer",
        "default_representation": "scatter",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 4,
        "name": "weight",
        "description": "Вес",
        "unit": "кг",
        "type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 5,
        "name": "height",
        "description": "Рост",
        "unit": "см",
        "type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 2,
        "name": "systolic_pressure",
        "description": "Систолическое (верхнее) артериальное давление в покое",
        "unit": "мм рт. ст.",
        "type": "integer",
        "default_representation": "scatter",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 25,
        "name": "temperature",
        "description": "Температура",
        "unit": "град Цельсия",
        "type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 24,
        "name": "glukose",
        "description": "Глюкоза",
        "unit": "моль/литр",
        "type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 23,
        "name": "pain_assessment",
        "description": "Оценка боли",
        "unit": "балл(а)(ов)",
        "type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Ощущения",
    },
    {
        "id": 21,
        "name": "leg_circumference_right",
        "description": "Обхват правой голени",
        "unit": "см",
        "type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 29,
        "name": "medicine",
        "description": "Принятое лекарство",
        "unit": "",
        "type": "string",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Общее",
    },
    {
        "id": 20,
        "name": "leg_circumference_left",
        "description": "Обхват левой голени",
        "unit": "см",
        "type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 22,
        "name": "spo2",
        "description": "Насыщение крови кислородом",
        "unit": "%",
        "type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 32,
        "name": "side_effect",
        "description": "Побочный эффект",
        "unit": "",
        "type": "string",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Общее",
    },
    {
        "id": 33,
        "name": "health",
        "description": "Субъективное самочувствие",
        "unit": "",
        "type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Ощущения",
    },
    {
        "id": 34,
        "name": "activity",
        "description": "Физическая активность",
        "unit": "минуты",
        "type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Общее",
    },
    {
        "id": 35,
        "name": "information",
        "description": "Общая информация",
        "unit": "",
        "type": "string",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Общее",
    },
    {
        "id": 36,
        "name": "steps",
        "description": "Количество пройденных шагов",
        "unit": "шаги",
        "type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Данные с мобильных устройств",
    },
    {
        "id": 37,
        "name": "glukose_fasting",
        "description": "Глюкоза натощак",
        "unit": "ммоль/л",
        "type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Эндокринология",
    },
    {
        "id": 38,
        "name": "peak_flow",
        "description": "Предельная скорость выдоха",
        "unit": "л/мин",
        "type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Пульмонология",
    },
]


class AddValueDialog(Dialog):
    def first(self, _input):
        self.objectStorage.speakSpeech.play(
            "Какое значение вы хотите отправить?", cashed=True)
        self.cur = self.second
        self.need_permanent_answer = True

    def second(self, _input):
        self.category = None
        text = _input.lower()

        for i in categories:
            for phrase in i[0]:
                if phrase in text:
                    self.category = i[1]
                    break
            if self.category is not None:
                break

        if self.category is None:
            for i in dry_categories:
                keys = i['description'].strip().lower().split()
                for k in keys:
                    if k in text:
                        self.category = i
                        break
                if self.category is not None:
                    break

        if self.category is None:
            self.objectStorage.speak.play(
                "Категория нераспознана, "
                "пожалуйста, назовите категорию еще раз", cashed=True)
            self.cur = self.second
            return

        self.objectStorage.speakSpeech.play(
            "Произнесите значение", cashed=True)
        self.cur = self.third
        self.need_permanent_answer = True

    def third(self, _input):
        if self.category["type"] == "integer":
            if not _input.isdigit():
                self.objectStorage.speakSpeech.play(
                    "Значение не распознано, пожалуйста,"
                    " произнесите его еще раз", cashed=True)
                return
        elif self.category["type"] == "float":
            if _input.isdigit():
                value = int(_input)
            elif 'и' in _input.lower():
                d = [i.strip() for i in _input.lower().split('и')]
                if sum([i.isdigit() for i in d]) and len(d) == 2:
                    value = float(".".join(d))
                else:
                    self.objectStorage.speakSpeech.play(
                        "Значение не распознано, пожалуйста,"
                        " произнесите его еще раз", cashed=True)
        else:
            logging.error("Unknown type %s" % self.category["type"])
            return

        answer = requests.post(
            self.objectStorage.host+'/speakerapi/pushvalue/',
            json={
                'token': self.objectStorage.token,
                'data': [{
                    'category_name': self.category['name'],
                    'value': value
                }]
            })

        if answer.status_code == 200:
            text = "Значение успешно отправлено."
        else:
            text = "Произошла ошибка при отправлении значения"
            logging.error("Value send err {} {}".format(
                answer, answer.text[:100]))

        self.objectStorage.speakSpeech.play(text, cashed=True)

    cur = first
    name = 'Отправить значение измерения'
    keywords = ['измерени', 'значени']