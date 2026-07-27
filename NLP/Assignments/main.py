import re

patterns = {
    "PlantCare": re.compile(
    r"(plant|fern|cactus|lily).*(water|watering|hydrate)"
    r"|"
    r"(water|watering|hydrate).*(plant|fern|cactus|lily)",
    re.I),

    "LightRequirement": re.compile(
    r"(light|sun|bright|shade).*(need|require|get)"
    r"|"
    r"(need|require|get).*(light|sun|bright|shade)",
    re.I),

   "RepottingAdvice": re.compile(
    r"(repot|repotting|replant|transplant).*(plant|flower|pot|soil)?"
    r"|"
    r"(plant|flower|pot|soil)?.*(repot|repotting|replant|transplant)",
    re.I),

    "FertilizerAdvice": re.compile(
    r"(fertilize|fertilizing|fertilizer|manure|compost)",
    re.I) ,

    "DiseasesAdvice": re.compile(
    r"(disease|sick|infected|affect).*(houseplant|plant|indoor plant)"
    r"|"
    r"(houseplant|plant|indoor plant).*(disease|sick|infected|affect)",
    re.I)

}


responses = {
    "PlantCare": "Most indoor plants thrive if you water them once a week. However, ferns need more humidity—mist them every 3 days.",
    "LightRequirement": "Cacti generally need at least 6 hours of direct sunlight daily. If indoors, place them near a bright south-facing window.",
    "RepottingAdvice": "You should repot most houseplants once a year, preferably in spring when growth resumes.",
    "FertilizerAdvice": "Fertilize your plants according to their type and season. For most indoor plants, a balanced fertilizer once a month is sufficient." ,
    "DiseasesAdvice": "Common houseplant diseases include fungal infections, root rot, and pests. Make sure to check your plants regularly and maintain proper care.",
    "Unknown": "Sorry, I didn’t catch that. Could you rephrase your plant question?"
}


def detect_intent(user_input):
    for intent, pattern in patterns.items():
        if pattern.search(user_input):
            return intent
    return "Unknown"


def get_bot_reply(user_input):
    intent = detect_intent(user_input)
    return responses[intent]


def botanical_help_bot():
    print("Welcome to Botanical-Help Bot! Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Bot: Goodbye! ")
            break
        reply = get_bot_reply(user_input)
        print("Bot:", reply)


if __name__ == "__main__":
    botanical_help_bot()
