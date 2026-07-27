from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionAskCourse(Action):

    def name(self):
        return "action_ask_course"

    def run(self, dispatcher, tracker, domain):
        text = tracker.latest_message.get("text")

        if "برمجة" in text:
            dispatcher.utter_message(
                text="💻 مواد البرمجة:\n- برمجة 1\n- برمجة 2\n- هياكل بيانات"
            )

        elif "رياضيات" in text:
            dispatcher.utter_message(
                text="📐 مواد الرياضيات:\n- تفاضل\n- جبر خطي\n- إحصاء"
            )

        elif "شبكات" in text:
            dispatcher.utter_message(
                text="🌐 مواد الشبكات:\n- شبكات 1\n- شبكات 2\n- أمن معلومات"
            )

        elif "ذكاء" in text:
            dispatcher.utter_message(
                text="🤖 مواد الذكاء الاصطناعي:\n- AI\n- تعلم آلة\n- رؤية حاسوبية"
            )

        else:
            dispatcher.utter_message(
                text="🎓 عندنا مواد: برمجة، رياضيات، شبكات، ذكاء اصطناعي"
            )

        return []