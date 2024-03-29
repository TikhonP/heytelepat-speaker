from abc import ABC

from dialogs.measurments_dialogs import AddValueDialog
from events.event import Event, EventDialog


class MeasurementNotificationDialog(AddValueDialog, EventDialog):
    category = None

    def first(self, text):
        measurement_description = str(
            self.data.get('custom_text') or self.data.get('patient_description') or
            'Пожалуйста, произведите измерение ' + self.data.get('title')
        )
        self.objectStorage.play_speech.play(
            measurement_description + " Вы готовы произнести ответ сейчас? Перед ответом нажмите на кнопку.")
        self.send_ws_data({
            'token': self.objectStorage.token,
            'request_type': 'is_sent',
            'measurement_id': self.data['id'],
        })
        self.current_input_function = self.yes_no
        self.call_later_delay = 15
        self.call_later_on_end = True

    def yes_no(self, text):
        if self.is_positive(text):
            self.call_later_on_end = False
            self.category = self.data['fields'].pop(0)
            self.objectStorage.play_speech.play(
                "Произнесите значение {}".format(self.category.get('text')))
            self.current_input_function = self.third
            self.need_permanent_answer = True
            return
        elif self.is_negative(text):
            self.objectStorage.play_speech.play("Хотите отложить напоминание на 15 минут?", cache=True)
            self.call_later_delay = 15
            self.call_later_yes_no_fail_text = "Введите значение позже с помощию команды 'заполнить опросники'."
            self.current_input_function = self.call_later_yes_no
            self.need_permanent_answer = True
        else:
            measurement_description = str(
                self.data.get('custom_text') or self.data.get('patient_description') or
                'Пожалуйста, произведите измерение ' + self.data.get('title')
            )
            self.objectStorage.play_speech.play(
                "Извините, я вас не очень понял. " + measurement_description + " Вы готовы произнести ответ сейчас?"
            )
            self.current_input_function = self.yes_no
            self.need_permanent_answer = True

    current_input_function = first


class MeasurementNotificationEvent(Event, ABC):
    name = "Уведомление об измерении"

    async def loop_item(self):
        await self.web_socket_connect(
            'measurements/',
            {
                "token": self.object_storage.token,
                "request_type": "init"
            },
        )

    async def return_dialog(self, dialog_engine_instance):
        self.dialog_class = MeasurementNotificationDialog
        return await self.get_dialog(self.object_storage, self.get_data(), self.ws, dialog_engine_instance)
