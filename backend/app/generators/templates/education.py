"""Education / student life conversation templates."""
from __future__ import annotations
import random

TOPICS = [
    "coursework", "exams", "study_habits", "professors", "campus_life",
    "group_projects", "internships", "research", "lectures", "assignments",
    "graduation", "career_advice", "learning_methods", "time_management", "library",
]

_USER: dict[str, list[str]] = {
    "coursework": [
        "I have three assignments due this week and I haven't started any of them.",
        "My coursework this semester is actually interesting for once.",
        "I'm struggling to see how this module is relevant to my degree.",
        "The reading list for this course is genuinely intimidating.",
        "I think I picked the right major. This material actually excites me.",
    ],
    "exams": [
        "Exams in two weeks and I feel completely underprepared.",
        "I just finished my last exam. The relief is indescribable.",
        "Open book exams are still hard. How is that possible?",
        "I studied for hours and then blanked completely in the exam.",
        "Multiple choice exams are either easy or cruel depending on how they're written.",
    ],
    "study_habits": [
        "I can't study with any noise but also can't study in total silence. Narrow window.",
        "Spaced repetition has genuinely changed how I learn things.",
        "I always plan to study and then end up reorganising my desk instead.",
        "The Pomodoro technique sounds simple but it actually works for me.",
        "How do you stay focused when you're studying something you find boring?",
    ],
    "professors": [
        "I have a professor who somehow makes everything interesting. Rare gift.",
        "I emailed a professor and they responded immediately. Didn't expect that.",
        "Office hours are so useful and almost nobody goes to them.",
        "I have one professor whose lectures I genuinely look forward to.",
        "The difference a good lecturer makes to a difficult subject is enormous.",
    ],
    "campus_life": [
        "University is the first time I've lived away from home and it's an adjustment.",
        "The campus food has gotten surprisingly good lately.",
        "I found a quiet corner of the library no one seems to know about.",
        "Campus events are hit or miss but I keep going to them.",
        "I'm on the student committee and it's more work than I expected.",
    ],
    "group_projects": [
        "Group projects are a lesson in managing people as much as managing the project.",
        "We had one person in our group who did absolutely nothing.",
        "Actually collaborating on a group project and having it go well is genuinely rare.",
        "How do you handle a group project when no one agrees on direction?",
        "I hate group projects but I understand why they assign them.",
    ],
    "internships": [
        "I got offered an internship and I'm excited but also nervous.",
        "My internship taught me more about real work than most of my courses.",
        "I'm trying to decide between two internship offers and it's a hard choice.",
        "The gap between university work and real work was bigger than I expected.",
        "I had an internship that turned into a job offer. Still deciding.",
    ],
    "research": [
        "I started working in a research lab last term and it's completely different from coursework.",
        "Reading academic papers is a skill that takes time to develop.",
        "My thesis topic is exciting but the scope is terrifying.",
        "Research is 90% reading and 10% actually doing something.",
        "Getting something published must feel incredible. I can't imagine it yet.",
    ],
    "lectures": [
        "I went to every lecture this semester. First time I've done that.",
        "Recording lectures is useful but I always feel guilty watching at 1.5x speed.",
        "Long lectures without a break are genuinely hard to stay focused through.",
        "I took notes by hand today instead of typing and retained everything better.",
        "Online lectures are convenient but I miss the energy of a live room.",
    ],
    "assignments": [
        "I submitted an assignment at 11:59pm and I need to stop living like this.",
        "I got really good feedback on an assignment and it genuinely made my week.",
        "Word counts are both a constraint and a comfort. At least you know when to stop.",
        "I reread an old assignment and couldn't believe I wrote something that bad.",
        "I have an assignment on a topic I know nothing about. Exciting and terrifying.",
    ],
    "graduation": [
        "Graduation is closer than I expected and I don't know how to feel.",
        "The post-graduation question of what to do next is constant background noise.",
        "I'm excited to graduate but I'll genuinely miss parts of this.",
        "Some people know exactly what they want to do after graduation. I'm not those people.",
        "The thought of leaving university and entering the real world is surreal.",
    ],
    "career_advice": [
        "I have no idea what I want to do with my degree and that's a strange feeling.",
        "Is networking as important as people say? It feels uncomfortable.",
        "I went to a career fair today. Mixed feelings.",
        "A mentor told me something today that actually shifted how I think about my career.",
        "I think the degree matters less than the skills you build alongside it.",
    ],
    "learning_methods": [
        "Teaching something to someone else is the best way to find out if you actually understand it.",
        "I've started making mind maps and they help me connect concepts.",
        "Active recall is genuinely better than passive rereading. Evidence based.",
        "I learn by doing almost exclusively. Reading about it isn't enough for me.",
        "Some people absorb information through listening. I need to write everything down.",
    ],
    "time_management": [
        "I thought I was managing my time well until this week proved otherwise.",
        "Saying no to things is one of the most important time management skills.",
        "I overcommitted to everything this semester and I'm feeling it now.",
        "Calendar blocking actually works if you stick to it.",
        "The secret to time management is mostly just starting earlier.",
    ],
    "library": [
        "I spent six hours in the library today and it was surprisingly productive.",
        "The library printer never works when I need it.",
        "Finding a good spot in the library is half the battle.",
        "Physical books from the library are still my preference for focused reading.",
        "The library closes at the worst possible times before exams.",
    ],
}

_ASSISTANT: dict[str, list[str]] = {
    "coursework": [
        "Three assignments in a week is genuinely brutal. Prioritise by deadline.",
        "Finding coursework that interests you makes such a difference in output quality.",
        "The 'how is this relevant' question is sometimes answered much later.",
        "Intimidating reading lists are a challenge worth meeting head-on.",
        "Enjoying your subject is a privilege not everyone gets. Hold onto it.",
    ],
    "exams": [
        "Two weeks is enough to cover the ground if you start now.",
        "Post-exam relief is its own category of happiness.",
        "Open book exams test understanding, not memory. Harder in some ways.",
        "Blanking in an exam and then remembering after is one of the great tortures.",
        "Multiple choice can be deceptively hard when they're well-written.",
    ],
    "study_habits": [
        "Spaced repetition is backed by evidence. One of the few study tricks that actually works.",
        "Reorganising your desk is productive procrastination. Classic.",
        "Pomodoro works because it makes the task feel finite.",
        "The right study environment varies by person. Find yours and protect it.",
        "Boring material gets easier when you connect it to things you care about.",
    ],
    "professors": [
        "A professor who makes material engaging is teaching a skill as much as content.",
        "Fast email responses from academics are a wonderful surprise.",
        "Office hours being underutilised is one of university's best kept secrets.",
        "Looking forward to a lecture is a great sign you're in the right subject area.",
        "Good teaching is rarer than it should be. Appreciate it when you find it.",
    ],
    "campus_life": [
        "Living away from home for the first time is its own education.",
        "Hidden library corners are a competitive resource. Guard yours.",
        "Campus events are worth attending even when you're not sure about them.",
        "Student committee work teaches more practical skills than most modules.",
        "Good campus food is more important to wellbeing than people admit.",
    ],
    "group_projects": [
        "Group projects teach collaboration, which is most of what actual work is.",
        "One person not pulling their weight is infuriating and unfortunately common.",
        "Assigning clear ownership of tasks early prevents most conflict.",
        "A group project that actually works is something you appreciate more later.",
        "The frustration of group projects is the lesson. Real teams are messy too.",
    ],
    "internships": [
        "Internship nerves are normal. You're not expected to know everything on day one.",
        "Real work experience is irreplaceable. Courses prepare you, experience teaches you.",
        "Choosing between two good offers is a good problem to have.",
        "The gap between education and work is real but closable quickly.",
        "A return offer after an internship is a strong vote of confidence.",
    ],
    "research": [
        "Research lab work shifts how you see knowledge — it's not fixed, it's built.",
        "Reading papers is a skill. Abstract, intro, conclusion first. Then depth if needed.",
        "Thesis scope is always scary at the start. It narrows as you work.",
        "Research is mostly failing productively until something works.",
        "A publication is one of those milestones that feels surreal when it happens.",
    ],
    "lectures": [
        "Perfect attendance is a commitment that pays off at exam time.",
        "1.5x speed playback is a fine way to review. Don't feel guilty.",
        "Long lectures need a break. That's just human attention span physics.",
        "Handwritten notes improve retention. The slowness forces you to prioritise.",
        "Online lectures are convenient but you lose the social context of a room.",
    ],
    "assignments": [
        "11:59pm submissions are bad for your wellbeing. Worth fixing that habit.",
        "Good feedback on an assignment means the marker engaged seriously with your work.",
        "Word counts are constraints that teach you to be concise.",
        "Rereading old work is a great way to see how much you've improved.",
        "Unfamiliar assignment topics are the best opportunities. You learn more.",
    ],
    "graduation": [
        "Graduation approaching is a strange mix of excitement and grief.",
        "Not knowing what comes next is uncomfortable and also completely normal.",
        "Missing parts of university after leaving is universal.",
        "Some people who know exactly what they want to do after graduation change their mind anyway.",
        "The transition out of education is its own adjustment period.",
    ],
    "career_advice": [
        "Not knowing what you want to do is fine. Most people figure it out gradually.",
        "Networking is just relationship-building with intention. Less transactional than it sounds.",
        "Career fairs are useful for information, less so for immediate opportunities.",
        "A good mentor can change your trajectory. Worth seeking out.",
        "Skills and portfolio matter more and more relative to the degree alone.",
    ],
    "learning_methods": [
        "Teaching is the deepest test of understanding. If you can't explain it, you don't know it.",
        "Mind maps are excellent for showing how concepts connect to each other.",
        "Active recall over passive review is well-supported by learning research.",
        "Learning by doing is valid. Reading about swimming doesn't teach you to swim.",
        "Finding your learning modality and using it consistently is high-leverage.",
    ],
    "time_management": [
        "Overcommitting is how you learn your actual capacity. Sometimes the hard way.",
        "Saying no is a skill. It protects everything else you said yes to.",
        "Calendar blocking works when you respect the blocks you create.",
        "Starting earlier solves most time management problems.",
        "The week that proves you're stretched is useful information about sustainable pace.",
    ],
    "library": [
        "Six productive library hours is a genuinely good day.",
        "Library printers failing before deadlines is a universal experience.",
        "A good library spot is worth protecting. Don't tell too many people.",
        "Physical reading for deep understanding is still hard to beat.",
        "Library hours before major deadlines are always too short.",
    ],
}


def get_topics() -> list[str]:
    return TOPICS


def get_user_message(topic: str, rng: random.Random) -> str:
    return rng.choice(_USER.get(topic, [f"Tell me about {topic.replace('_', ' ')}."]))


def get_assistant_message(topic: str, rng: random.Random) -> str:
    return rng.choice(_ASSISTANT.get(topic, ["Interesting. What else is on your mind?"]))
