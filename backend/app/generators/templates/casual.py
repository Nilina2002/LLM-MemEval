"""Casual conversation templates — everyday chitchat across many topics."""
from __future__ import annotations
import random

TOPICS = [
    "weekend_plans", "weather", "favorite_foods", "movies", "music",
    "sports", "travel_memories", "hobbies", "pets", "family",
    "work_stress", "books", "tv_shows", "cooking", "exercise",
    "technology", "sleep", "social_media", "childhood_memories", "future_goals",
]

_USER: dict[str, list[str]] = {
    "weekend_plans": [
        "So what are you planning to do this weekend?",
        "I have absolutely no plans this weekend and honestly that feels great.",
        "Any good ideas for what to do on a weekend when the weather's nice?",
        "I was thinking of finally cleaning my apartment this weekend. Riveting, I know.",
        "Do you ever just want to spend the whole weekend doing absolutely nothing?",
    ],
    "weather": [
        "The weather's been so unpredictable lately, hasn't it?",
        "I cannot stand this heat. How do people live in hot climates?",
        "I actually love rainy days. Is that weird?",
        "It finally feels like autumn. Best season change of the year.",
        "The fog this morning was so thick I could barely see the street.",
    ],
    "favorite_foods": [
        "I've been really into cooking lately. Trying new recipes every week.",
        "What's your go-to comfort food when you've had a terrible day?",
        "I tried this amazing restaurant last night. Best pasta I've ever had.",
        "I'm convinced pizza is the perfect food. There's no downside.",
        "I've been trying to eat healthier but I keep getting pulled back to junk food.",
    ],
    "movies": [
        "Have you seen anything good lately? I need a movie recommendation.",
        "I rewatched an old favorite last night and it hit even harder the second time.",
        "I don't understand how some movies get sequels and others don't.",
        "Horror movies stress me out but I can't stop watching them.",
        "The cinema experience is just different from watching at home, right?",
    ],
    "music": [
        "I've had the same song stuck in my head for three days straight.",
        "What kind of music do you listen to when you need to focus?",
        "I went to a live concert recently and it was incredible.",
        "I can't work with lyrics in the background — instrumentals only for me.",
        "Discovering a new artist you love is one of the best feelings.",
    ],
    "sports": [
        "Did you catch the game last night? What a finish.",
        "I started running recently and I have absolutely no idea how people enjoy it.",
        "My team has been on a terrible losing streak. I'm losing faith.",
        "I think watching live sports is completely different from watching on TV.",
        "I played tennis for the first time in years yesterday and it was rough.",
    ],
    "travel_memories": [
        "I was thinking about a trip I took a few years ago. It was amazing.",
        "What's the most memorable place you've ever visited?",
        "I really want to travel more but it's hard to find time.",
        "Travelling alone sounds scary but I think it'd be incredibly freeing.",
        "I always come back from trips completely exhausted but totally happy.",
    ],
    "hobbies": [
        "I picked up a new hobby last month and I'm completely obsessed with it.",
        "Do you have any hobbies that people find surprising?",
        "I've been trying to get into photography but the gear is so expensive.",
        "I used to paint a lot but I kind of lost touch with it over the years.",
        "Gaming is honestly one of my favorite ways to unwind.",
    ],
    "pets": [
        "My cat did the funniest thing this morning. Animals are wild.",
        "I really want a dog but my apartment doesn't allow pets.",
        "Do you think pets can sense when you're sad?",
        "I grew up with animals so a house without them feels strange to me.",
        "My dog has learned to open the fridge. I don't know whether to be proud or alarmed.",
    ],
    "family": [
        "Family gatherings are equal parts wonderful and exhausting.",
        "I called my parents last night and realized how much I miss them.",
        "Having siblings is a special kind of chaos.",
        "How often do you visit family? I feel like I never do it enough.",
        "My aunt gave me unsolicited life advice again. Classic.",
    ],
    "work_stress": [
        "Work has been completely overwhelming this week.",
        "I think I need to get better at saying no to extra projects.",
        "How do you switch off from work mode when you get home?",
        "I had the most infuriating meeting today. Two hours I'll never get back.",
        "Remote work is great but sometimes I really miss having colleagues nearby.",
    ],
    "books": [
        "I just finished a book I couldn't put down. Any recommendations?",
        "I'm one of those people who reads multiple books at the same time.",
        "Physical books vs e-readers — where do you stand?",
        "I haven't read a novel in months and I feel slightly guilty about it.",
        "Non-fiction or fiction — do you have a preference?",
    ],
    "tv_shows": [
        "I started a new series and I'm already three episodes in tonight.",
        "Are you a watch-one-episode-a-week person or a binge watcher?",
        "I got way too emotionally invested in a show and then it was cancelled.",
        "Reality TV is terrible but I watch it anyway. I'm not proud.",
        "I need a good series recommendation. Something I can get properly into.",
    ],
    "cooking": [
        "I made something new last night and it actually turned out well.",
        "Cooking for one is harder than it sounds — everything makes too many servings.",
        "I've been meal prepping on Sundays and it's genuinely changed my week.",
        "I burned my dinner tonight. Again. I think the stove hates me.",
        "Do you follow recipes exactly or improvise as you go?",
    ],
    "exercise": [
        "I've been trying to build a consistent workout routine but keep breaking it.",
        "The hardest part about exercising is actually starting.",
        "I went to a yoga class for the first time and I was absolutely terrible.",
        "Walking is underrated as exercise. I do it every morning now.",
        "I signed up for a 5K and I'm already questioning my life choices.",
    ],
    "technology": [
        "My phone died in the middle of the day and I felt genuinely lost.",
        "Do you think we're too dependent on technology?",
        "I got a new laptop and the setup process took an entire evening.",
        "Smart home devices are convenient until they stop working.",
        "I tried to explain social media to my grandmother. It did not go well.",
    ],
    "sleep": [
        "I slept terribly last night and I can feel it in everything today.",
        "I've become obsessed with getting eight hours of sleep.",
        "Do you have any tricks for falling asleep faster?",
        "I had the strangest dream last night. I can't stop thinking about it.",
        "Naps are either restorative or they ruin your whole evening. No middle ground.",
    ],
    "social_media": [
        "I took a break from social media last week and honestly felt much better.",
        "The algorithm decided I need to see dog videos now. I'm not complaining.",
        "I posted something online and the response made me overthink everything.",
        "Does anyone else doomscroll way too much at night?",
        "I unfollowed a lot of accounts recently and my feed is so much better.",
    ],
    "childhood_memories": [
        "Something today reminded me of something from when I was a kid.",
        "Do you ever get hit with a sudden nostalgia for something random?",
        "I found old photos from when I was young and I barely recognize myself.",
        "Childhood summers felt infinite. Now summers are over before I notice them.",
        "I tried to explain a game we used to play as kids and it sounded ridiculous.",
    ],
    "future_goals": [
        "I've been thinking a lot about where I want to be in five years.",
        "I really want to learn a new skill this year but haven't started yet.",
        "Setting goals feels productive. Following through is the hard part.",
        "I want to travel more, read more, and stress less. Simple enough, right?",
        "Do you ever feel like your plans keep shifting and that's somehow okay?",
    ],
}

_ASSISTANT: dict[str, list[str]] = {
    "weekend_plans": [
        "Honestly, doing nothing sounds perfect to me. Rest is underrated.",
        "Maybe a hike if the weather cooperates? Otherwise a good book and coffee.",
        "I've been meaning to visit that new market downtown. Could be fun.",
        "Cooking something ambitious is always on my weekend list. Sometimes I even do it.",
        "A balance of productivity and laziness — that's the ideal weekend formula.",
    ],
    "weather": [
        "Hot weather is just not for me. Give me a mild, cloudy day any time.",
        "Rainy days are great for staying in and being cozy. Nothing weird about it.",
        "The weather has been all over the place. Dressing for it is a guessing game.",
        "Autumn is genuinely the best season. Crisp air, good light, cozy vibes.",
        "I like fog actually. Makes everything feel a bit mysterious.",
    ],
    "favorite_foods": [
        "Homemade pasta is my comfort food. Nothing else comes close.",
        "A good bowl of ramen on a cold night is unbeatable.",
        "Cooking is surprisingly meditative once you get into it.",
        "Pizza is perfect food. You are correct. No notes.",
        "The healthy eating struggle is real. One good day, three bad ones.",
    ],
    "movies": [
        "I rewatched an old favourite recently too — it held up really well.",
        "Horror is such a weird genre to enjoy. And yet here we are.",
        "Cinema trips are worth it for the big spectacle films especially.",
        "Sequels are such a gamble. Some are great, most shouldn't exist.",
        "I go through phases where I only watch documentaries.",
    ],
    "music": [
        "For focus I stick to lo-fi or classical. Anything with lyrics kills my concentration.",
        "Live music is just electric. The energy in the room is unlike anything else.",
        "I've been going down a rabbit hole of 70s music lately. Highly recommend.",
        "Getting a song stuck in your head is either wonderful or torture depending on the song.",
        "Finding a new artist you love is like discovering a whole new world.",
    ],
    "sports": [
        "Live sport is a different experience entirely. The crowd changes everything.",
        "Running is one of those things that gets easier after the first month or so.",
        "Watching your team lose repeatedly is its own special kind of suffering.",
        "Tennis is hard but so satisfying when you hit a good shot.",
        "I watch sport more for the strategy than anything. It's like a puzzle.",
    ],
    "travel_memories": [
        "The best trips are usually the ones that didn't go perfectly to plan.",
        "Solo travel changes how you see yourself, I think.",
        "There's always somewhere I want to go that I haven't been to yet.",
        "Coming back from travel always gives me this weird mix of relief and longing.",
        "The memories from trips stay so vivid. Normal days blur together but travel sticks.",
    ],
    "hobbies": [
        "Hobbies that absorb you completely are so valuable for mental health.",
        "Photography is one of those hobbies that trains you to see differently.",
        "I used to paint too. Should probably pick it up again.",
        "Gaming gets a bad reputation it doesn't fully deserve.",
        "Finding a hobby you're genuinely terrible at and not caring is weirdly freeing.",
    ],
    "pets": [
        "Animals definitely sense emotion. My cat always shows up when I'm stressed.",
        "Pets make a space feel like a home. I think that's just true.",
        "The no-pets policy in apartments is one of life's injustices.",
        "A dog that can open the fridge is either a genius or a menace. Maybe both.",
        "Growing up with animals does something to you. Makes you more patient, maybe.",
    ],
    "family": [
        "Family gatherings are exactly that — wonderful and exhausting in equal measure.",
        "Distance from family makes you appreciate them more, I think.",
        "Siblings are the people who know exactly how to drive you crazy.",
        "Unsolicited advice from relatives is basically a love language in some families.",
        "Calling home more often is always on my list. I never do it enough either.",
    ],
    "work_stress": [
        "Switching off after work is a skill I'm still developing.",
        "The two-hour meeting problem is universal. Every workplace has it.",
        "Saying no is incredibly hard but gets easier with practice.",
        "Overwhelming weeks make you appreciate the quiet ones.",
        "Remote work is a trade-off. More focus, less spontaneous connection.",
    ],
    "books": [
        "Multiple books at once is the only way. Different moods need different books.",
        "Physical books have a quality that screens just don't replicate.",
        "Non-fiction in the morning, fiction at night — that's my system.",
        "A book that grabs you from the first page is a rare and wonderful thing.",
        "I go through reading droughts and then devour five books in a week. No pattern.",
    ],
    "tv_shows": [
        "Binge watching entirely. I have no discipline with good TV.",
        "Getting emotionally attached to a cancelled show is a rite of passage.",
        "Reality TV is a guilty pleasure I've fully stopped feeling guilty about.",
        "A really great show is almost a shame to finish because then it's over.",
        "The pilot episode is everything. You know in the first ten minutes.",
    ],
    "cooking": [
        "Cooking for one is genuinely hard. The portions never work out.",
        "Meal prepping changed my week completely. Sunday you is doing future you a favour.",
        "Improvising in the kitchen is how the best meals happen.",
        "Burning dinner is a rite of passage. Every cook does it regularly.",
        "Following recipes exactly is fine for baking. Cooking needs more freedom.",
    ],
    "exercise": [
        "Starting is definitely the hardest part. After ten minutes it gets easier.",
        "Walking is underrated. Good for the body and clears the head.",
        "Yoga looks calm from the outside. It is not always calm on the inside.",
        "Signing up for something scary is good motivation. Terrifying, but effective.",
        "Consistency matters more than intensity. Fifteen minutes every day beats one epic session.",
    ],
    "technology": [
        "Losing your phone for a day reveals how dependent on it you really are.",
        "Smart home stuff is great right until it needs a firmware update.",
        "Setting up a new device is always more work than it should be.",
        "Technology dependency is complicated — it genuinely helps but the cost is attention.",
        "Explaining modern technology to older generations is an exercise in patience.",
    ],
    "sleep": [
        "Eight hours is transformative. Everything is worse when you're sleep-deprived.",
        "A dark room and no screens for thirty minutes before bed. That's the system.",
        "Vivid dreams are either fascinating or unsettling. Rarely in between.",
        "Naps are high-risk, high-reward. Timing is everything.",
        "Bad sleep compounds. One rough night is fine. Three in a row is a problem.",
    ],
    "social_media": [
        "A social media break always feels better than expected going in.",
        "The algorithm learns you uncomfortably quickly.",
        "Curating your feed intentionally makes a huge difference.",
        "Doomscrolling at night is a habit I'm actively trying to break.",
        "Posting something and then immediately regretting it is a universal experience.",
    ],
    "childhood_memories": [
        "Nostalgia hits hardest for completely random things. A smell, a colour.",
        "Old photos are strange — you remember the moment and also don't.",
        "Childhood summers did feel endless. Time genuinely moves differently when you're young.",
        "Explaining childhood games to people who didn't grow up in the same era is always a bit awkward.",
        "Some memories only unlock when you visit the place where they happened.",
    ],
    "future_goals": [
        "Five-year plans are valuable even when they don't survive first contact with reality.",
        "Learning a new skill is always worth starting even imperfectly.",
        "Plans shifting isn't failure. It's just updating based on new information.",
        "Travel more, worry less — that's a pretty solid life philosophy.",
        "Goals are good but so is being okay with where you are right now.",
    ],
}


def get_topics() -> list[str]:
    return TOPICS


def get_user_message(topic: str, rng: random.Random) -> str:
    messages = _USER.get(topic, [f"What do you think about {topic.replace('_', ' ')}?"])
    return rng.choice(messages)


def get_assistant_message(topic: str, rng: random.Random) -> str:
    messages = _ASSISTANT.get(topic, ["That's an interesting point. Tell me more."])
    return rng.choice(messages)
