"""Travel conversation templates."""
from __future__ import annotations
import random

TOPICS = [
    "trip_planning", "destinations", "packing", "flights", "accommodation",
    "local_food", "transportation", "sightseeing", "travel_tips", "culture_shock",
    "solo_travel", "budget_travel", "travel_photos", "visa", "jet_lag",
]

_USER: dict[str, list[str]] = {
    "trip_planning": [
        "I'm trying to plan a trip but the options are overwhelming.",
        "I've been on a planning spreadsheet for this trip for three weeks.",
        "How far in advance do you book international trips?",
        "I spontaneously booked a trip for next month and now I need to plan everything.",
        "Group travel planning is a democracy and democracies are complicated.",
    ],
    "destinations": [
        "I can't decide between two places I've always wanted to visit.",
        "Somewhere I've always wanted to go finally seems within reach.",
        "I just got back from somewhere completely new and it exceeded all expectations.",
        "What's the most underrated place you've been to?",
        "Everyone recommends the same tourist destinations. I want to go somewhere different.",
    ],
    "packing": [
        "I always pack too much and then spend the whole trip carrying things I never use.",
        "I've finally mastered packing light. It changes everything.",
        "The one thing I forgot to pack was the most important thing.",
        "How do you pack for two weeks in a single carry-on?",
        "I'm trying the capsule wardrobe approach to travel packing. Ambitious.",
    ],
    "flights": [
        "My flight was delayed six hours and I made unexpected friends in the terminal.",
        "I scored an incredible flight deal and I'm choosing not to question it.",
        "Long-haul flights are a test of endurance and I barely passed.",
        "Window seat or aisle seat — this is a revealing personality question.",
        "I can never sleep on planes. Everyone else seems to manage it fine.",
    ],
    "accommodation": [
        "I stayed in a tiny hotel room last trip and honestly didn't mind.",
        "Hostels are great for meeting people if you're in the right headspace for it.",
        "I found an Airbnb that was exactly as pictured. Still shocked.",
        "The hotel breakfast is worth the price. I will die on this hill.",
        "Checking in at 2am after a long journey and the room is ready — relief.",
    ],
    "local_food": [
        "The best meal of my life was from a street food stall.",
        "I always try to eat where the locals eat, not where the guidebooks point.",
        "Food is the fastest way into a place's culture.",
        "I tried something unfamiliar last trip and it immediately became a favourite.",
        "Coming home and missing specific food from a trip is a real phenomenon.",
    ],
    "transportation": [
        "Public transport in some cities is a masterclass in efficiency.",
        "I got completely lost on public transport in a foreign city. Best accident of the trip.",
        "Renting a car gave me freedom I didn't expect to love so much.",
        "Train travel through beautiful scenery is its own kind of experience.",
        "I took a local bus I probably shouldn't have and had an adventure.",
    ],
    "sightseeing": [
        "Some famous sights are exactly as impressive in person as you expect.",
        "I wandered away from the tourist area and found the actual city.",
        "Museum fatigue is real. Three is my limit in one day.",
        "The best thing I saw on a trip was something completely unplanned.",
        "I have hundreds of photos of a place I want to actually remember differently.",
    ],
    "travel_tips": [
        "What's the one travel tip you wish you'd known earlier?",
        "Offline maps have saved me more times than I can count.",
        "Always carry cash in local currency even if cards work most places.",
        "Learning five phrases in the local language makes a real difference.",
        "Travel insurance feels unnecessary until it suddenly is very necessary.",
    ],
    "culture_shock": [
        "Little things in a new country catch you completely off guard.",
        "I expected more differences and was surprised by how much was familiar.",
        "The adjustment to a new culture is disorienting and then exciting.",
        "I made a cultural mistake that was embarrassing but educational.",
        "Coming home after a long trip abroad is its own kind of reverse culture shock.",
    ],
    "solo_travel": [
        "I travelled alone for the first time last year and it was transformative.",
        "Solo travel sounds lonely to some people but I find it the opposite.",
        "Being responsible for every decision when travelling alone is liberating and terrifying.",
        "I met more people travelling solo than I ever did in a group.",
        "Would you travel alone to somewhere completely unfamiliar?",
    ],
    "budget_travel": [
        "I did a two-week trip on a very tight budget and it was one of the best I've taken.",
        "Free walking tours are genuinely good and worth the tip at the end.",
        "Cooking your own meals occasionally saves a surprising amount on a long trip.",
        "Shoulder season travel is the best kept secret — fewer crowds, lower prices.",
        "The expensive option isn't always the better experience.",
    ],
    "travel_photos": [
        "I took five hundred photos and use about twelve of them.",
        "I'm trying to take fewer photos and actually experience the place.",
        "The best photo I took on a trip was completely unposed.",
        "Editing travel photos is almost as enjoyable as taking them.",
        "I printed photos from my last trip and it made the memories more tangible.",
    ],
    "visa": [
        "Visa applications are stressful in a way I never fully anticipate.",
        "I applied for a visa and got it in two days. Unexpected.",
        "Some countries have remarkably easy visa processes. Others are absurd.",
        "I missed a trip because of a visa issue and I'm still a bit bitter.",
        "Checking visa requirements well in advance is advice I keep having to learn again.",
    ],
    "jet_lag": [
        "I crossed seven time zones and I'm genuinely not sure what day it is.",
        "The first day after a long flight I always feel slightly outside of reality.",
        "Getting sunlight immediately when you arrive really does help with jet lag.",
        "I have a theory that jet lag going east is worse than going west.",
        "I just accepted the jet lag and leaned into the early morning quiet time.",
    ],
}

_ASSISTANT: dict[str, list[str]] = {
    "trip_planning": [
        "Planning is part of the experience. The anticipation is real.",
        "Spontaneous trips need fast decisions. Start with accommodation first.",
        "For international trips, three months ahead is comfortable. Six is better.",
        "Group planning works best with one person nominated as the tiebreaker.",
        "Spreadsheets are the correct tool for complex trip planning. Embrace it.",
    ],
    "destinations": [
        "Go to the one you keep thinking about. That's the answer.",
        "Underrated places are usually underrated for logistical reasons, not quality.",
        "First-time visits that exceed expectations are the best kind.",
        "Off-the-beaten-path travel requires more planning but pays off.",
        "The difference between tourists and travellers is mostly how long you stay.",
    ],
    "packing": [
        "The rule: if you're unsure, leave it out. You can buy almost anything abroad.",
        "Packing light is a learnable skill. Takes a few trips to nail.",
        "The most important thing always gets forgotten. It's law.",
        "A carry-on only trip is a different level of travel freedom.",
        "Capsule wardrobes work beautifully for travel. Neutral colours, mix-and-match.",
    ],
    "flights": [
        "Long delays are terrible and occasionally lead to something unexpectedly good.",
        "Flight deals require flexibility. If you have it, use it.",
        "Long-haul endurance improves with practice. Eventually.",
        "Window for scenery, aisle for freedom. It genuinely says something about you.",
        "The inability to sleep on planes is cruel and I share your suffering.",
    ],
    "accommodation": [
        "Room size matters much less than location and comfort of the bed.",
        "Hostels are excellent for solo travel specifically.",
        "Accurate Airbnb listings deserve a five-star review on principle.",
        "Hotel breakfast is a ritual worth protecting.",
        "A room being ready at 2am is a small mercy worth appreciating.",
    ],
    "local_food": [
        "Street food is almost always where the real food is.",
        "Eating where locals eat versus where guidebooks recommend is a reliable divide.",
        "Food is anthropology. It tells you what a place values.",
        "Trying something new abroad and loving it is one of travel's great pleasures.",
        "Missing specific foods from a trip is a sign you were somewhere genuinely good.",
    ],
    "transportation": [
        "Efficient public transport is a marker of a well-run city.",
        "Getting lost using public transport and then finding your way is adventure.",
        "A rental car changes the scope of what you can see.",
        "Train travel through beautiful landscapes is slow travel at its best.",
        "Local buses are where you see how a place actually moves.",
    ],
    "sightseeing": [
        "Some famous places are famous because they're genuinely extraordinary.",
        "Wandering away from tourist areas is where the real city starts.",
        "Museum spacing matters. Three in a day and everything blurs.",
        "The unplanned thing is often what you remember most.",
        "Photos are nice but presence is better. Some things are worth just watching.",
    ],
    "travel_tips": [
        "Offline maps. Non-negotiable. Download before you land.",
        "Cash in local currency is a universal backup when technology fails.",
        "Local phrases open doors that English doesn't.",
        "Travel insurance is cheap relative to what it costs when you need it.",
        "The best tip is: leave more time than you think you need.",
    ],
    "culture_shock": [
        "The small unexpected things catch you more than the big obvious ones.",
        "Familiar things in unfamiliar places are often more surprising than the differences.",
        "Culture adjustment is uncomfortable briefly and then wonderful.",
        "Cultural mistakes made respectfully are usually forgiven generously.",
        "Reverse culture shock on returning home is real and underappreciated.",
    ],
    "solo_travel": [
        "Solo travel is one of the best ways to learn how you actually are.",
        "Meeting people is easier alone than in a group.",
        "Total decision ownership on a trip is terrifying and very clarifying.",
        "Solo travel isn't lonely. Different kind of social.",
        "The answer to 'would you travel alone somewhere unfamiliar' is almost always worth finding out.",
    ],
    "budget_travel": [
        "Budget constraints force creativity. Often leads to better experiences.",
        "Free walking tours are consistently excellent across most cities.",
        "Cooking occasionally on longer trips adds up to real savings.",
        "Shoulder season is the travel secret hiding in plain sight.",
        "Expensive and good don't always correlate. Especially in food.",
    ],
    "travel_photos": [
        "Five hundred photos and twelve used sounds about right actually.",
        "Intentional photography means better photos and more presence.",
        "The unposed shot is usually the honest one.",
        "Photo editing is a creative extension of the experience.",
        "Printed photos are tangible in a way screens aren't. Worth doing.",
    ],
    "visa": [
        "Visa stress is universal and slightly disproportionate to the actual process.",
        "Fast visa approvals are a pleasant surprise every time.",
        "The ease of visa processes varies enormously by passport and destination.",
        "Missing a trip due to visa issues is genuinely painful.",
        "Checking requirements early is the one lesson that keeps needing relearning.",
    ],
    "jet_lag": [
        "Seven time zones is serious business. Give yourself a grace day.",
        "The first day post-long-haul is a write-off. Accept it.",
        "Sunlight really does help the circadian clock reset.",
        "Eastward travel jet lag is worse for most people. Your theory has support.",
        "Leaning into the jet lag early mornings is surprisingly productive.",
    ],
}


def get_topics() -> list[str]:
    return TOPICS


def get_user_message(topic: str, rng: random.Random) -> str:
    return rng.choice(_USER.get(topic, [f"What do you know about {topic.replace('_', ' ')}?"]))


def get_assistant_message(topic: str, rng: random.Random) -> str:
    return rng.choice(_ASSISTANT.get(topic, ["That's interesting. Tell me more about it."]))
