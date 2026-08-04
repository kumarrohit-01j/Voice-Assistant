import webbrowser

RECIPES = [
    # Punjabi
    "butter chicken", "sarson da saag", "makki di roti",
    "chole bhature", "amritsari kulcha", "dal makhani",
    "paneer tikka", "aloo paratha", "lassi", "rajma chawal",

    # Bihar
    "litti chokha", "sattu paratha", "thekua",
    "malpua", "baingan bharta", "dal pitha",

    # Fast Food
    "burger", "pizza", "hot dog", "sandwich", "fries",
    "noodles", "momos", "pasta", "fried rice",

    # Veg
    "veg pulao", "shahi paneer", "mix veg", "kadhi chawal",
    "veg biryani", "palak paneer",

    # Non Veg
    "chicken biryani", "mutton curry", "egg curry",
    "fish fry", "chicken tikka",

    # Healthy
    "oats", "salad", "smoothie", "boiled eggs", "fruit bowl"
]


def handle_recipe(query, voice):

    query = query.lower()

    # remove extra words
    query = query.replace("recipe", "").replace("make", "").strip()

    for food in RECIPES:
        if food in query:
            voice.speak(f"Searching {food} recipe")
            webbrowser.open(
                f"https://www.youtube.com/results?search_query={food}+recipe"
            )
            return True

    return False