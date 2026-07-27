from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionAskDoctor(Action):

    def name(self):
        return "action_ask_doctor"

    def run(self, dispatcher, tracker, domain):

        text = tracker.latest_message.get('text')

        if "قلب" in text:
            dispatcher.utter_message(
                text="👨‍⚕️ أطباء القلب:\n- د. أحمد\n- د. محمد\n- د. سامر"
            )
        else:
            dispatcher.utter_message(
                text="👨‍⚕️ لدينا جميع التخصصات، الرجاء تحديد القسم (قلب، عيون، أسنان)"
            )

        return []