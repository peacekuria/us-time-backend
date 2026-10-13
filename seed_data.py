# seed_data.py
"""Static content used to populate a fresh database.

Kept separate from ``seed.py`` so the data can be reviewed and edited without
touching the loading logic.
"""

# Assessment questions shown by the Self Assessment tab.
QUESTIONS = [
    {
        "text": "Have you experienced persistent feelings of sadness or hopelessness?",
        "category": "mood",
        "order_index": 1,
    },
    {
        "text": "Have you lost interest or pleasure in activities you used to enjoy?",
        "category": "interest",
        "order_index": 2,
    },
    {
        "text": "Have you noticed changes in your appetite or weight?",
        "category": "appetite",
        "order_index": 3,
    },
    {
        "text": "Do you have trouble sleeping or sleep too much?",
        "category": "sleep",
        "order_index": 4,
    },
    {
        "text": "Do you often feel tired or lack energy?",
        "category": "energy",
        "order_index": 5,
    },
]

# Disorders shown by the Browse Disorders tab, each with treatment options.
DISORDERS = [
    {
        "name": "Depression",
        "description": (
            "A common but serious mood disorder that causes persistent "
            "sadness and a loss of interest in activities once enjoyed."
        ),
        "symptoms": (
            "Persistent sadness, loss of interest, sleep changes, appetite "
            "changes, fatigue, difficulty concentrating"
        ),
        "remedies": [
            ("Talking therapy", "Structured counselling such as CBT or interpersonal therapy.", "therapy"),
            ("Antidepressant medication", "Prescribed medication managed by a clinician.", "medication"),
            ("Regular physical activity", "Movement most days of the week lifts mood and energy.", "lifestyle"),
            ("Consistent sleep routine", "Regular sleep and wake times support recovery.", "lifestyle"),
            ("Social support", "Staying connected with trusted people reduces isolation.", "lifestyle"),
        ],
    },
    {
        "name": "Anxiety Disorder",
        "description": (
            "A group of conditions marked by excessive worry or fear that "
            "interferes with day-to-day activities."
        ),
        "symptoms": (
            "Excessive worry, restlessness, rapid heartbeat, sweating, "
            "difficulty concentrating, irritability, trouble sleeping"
        ),
        "remedies": [
            ("Cognitive behavioural therapy", "Reframes the thought patterns that feed anxiety.", "therapy"),
            ("Breathing and relaxation", "Slow breathing and grounding exercises calm the body's alarm response.", "lifestyle"),
            ("Gradual exposure", "Approaching feared situations in small, planned steps.", "therapy"),
            ("Anti-anxiety medication", "Short or long term medication prescribed by a clinician.", "medication"),
            ("Caffeine reduction", "Less caffeine often reduces the physical symptoms of anxiety.", "lifestyle"),
        ],
    },
    {
        "name": "Bipolar Disorder",
        "description": (
            "A condition involving episodes of unusually elevated mood that "
            "alternate with periods of depression."
        ),
        "symptoms": (
            "Mood swings, high energy with little sleep, racing thoughts, "
            "impulsive decisions, followed by low mood and fatigue"
        ),
        "remedies": [
            ("Mood stabilising medication", "The cornerstone of bipolar treatment, managed by a psychiatrist.", "medication"),
            ("Psychoeducation", "Learning to recognise early warning signs of a mood shift.", "therapy"),
            ("Stable daily rhythm", "Regular sleep, meals and activity help prevent episodes.", "lifestyle"),
            ("Family involvement", "Involving close contacts in a written care plan.", "lifestyle"),
        ],
    },
    {
        "name": "Stress",
        "description": (
            "The body's response to pressure. Short bursts are normal, but "
            "prolonged stress affects both mental and physical health."
        ),
        "symptoms": (
            "Tension, headaches, irritability, poor concentration, "
            "difficulty sleeping, feeling overwhelmed"
        ),
        "remedies": [
            ("Time management", "Breaking work into smaller, ordered tasks lowers the sense of overload.", "lifestyle"),
            ("Mindfulness practice", "Short daily meditation or breathing exercises reduce tension.", "lifestyle"),
            ("Physical activity", "Exercise discharges the stress response.", "lifestyle"),
            ("Setting boundaries", "Saying no to extra demands protects recovery time.", "lifestyle"),
            ("Counselling", "Brief therapy helps build coping strategies.", "therapy"),
        ],
    },
    {
        "name": "Insomnia",
        "description": (
            "A sleep disorder where it is hard to fall asleep, stay asleep, "
            "or get restful sleep, affecting daytime functioning."
        ),
        "symptoms": (
            "Difficulty falling asleep, waking during the night, waking too "
            "early, daytime tiredness and irritability"
        ),
        "remedies": [
            ("Sleep hygiene", "A fixed schedule, dark cool room and no screens before bed.", "lifestyle"),
            ("Stimulus control", "Using the bed only for sleep and getting up if awake too long.", "therapy"),
            ("Relaxation training", "Progressive muscle relaxation and guided breathing at bedtime.", "lifestyle"),
            ("Sleep diary review", "Tracking sleep patterns to find and fix triggers.", "therapy"),
            ("Sleep medication", "Short term support only, under medical supervision.", "medication"),
        ],
    },
]
