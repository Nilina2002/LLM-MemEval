"""Programming / software development conversation templates."""
from __future__ import annotations
import random

TOPICS = [
    "debugging", "code_review", "architecture", "algorithms", "frameworks",
    "databases", "apis", "testing", "deployment", "performance",
    "git_workflow", "documentation", "open_source", "career", "side_projects",
]

_USER: dict[str, list[str]] = {
    "debugging": [
        "I've been staring at this bug for two hours and I'm losing my mind.",
        "Why does adding a print statement always seem to fix the bug immediately?",
        "I finally found the bug and it was a single missing semicolon. I need a break.",
        "Have you ever had a bug that turned out to be someone else's library doing something unexpected?",
        "I love the moment when you figure out a bug. Pure euphoria.",
    ],
    "code_review": [
        "I got some pretty harsh code review feedback today. Hard to not take it personally.",
        "How do you handle leaving critical feedback without it sounding mean?",
        "I reviewed a PR today and the code was so clean I had nothing to say.",
        "What's your philosophy on code review — thoroughness vs speed?",
        "Should code reviews focus more on correctness or readability?",
    ],
    "architecture": [
        "I'm trying to decide between microservices and a monolith for a new project.",
        "How much do you think about architecture before you start coding?",
        "I over-engineered something yesterday. Three layers of abstraction for a simple task.",
        "Clean architecture sounds great on paper. In practice it requires discipline.",
        "When is it okay to just write quick and dirty code?",
    ],
    "algorithms": [
        "I had a technical interview today with an algorithm question I'd never seen before.",
        "Do you think algorithm knowledge matters in day-to-day development?",
        "I finally understood how a binary search tree works and it clicked beautifully.",
        "Big O notation is one of those things that's obvious in theory and tricky in practice.",
        "I implemented something from scratch today that I usually just import. Learned a lot.",
    ],
    "frameworks": [
        "The JavaScript framework landscape is honestly exhausting to keep up with.",
        "I'm debating whether to learn FastAPI or stick with Flask for a new project.",
        "What framework are you most comfortable in right now?",
        "Framework fatigue is real. Sometimes I want to write vanilla everything.",
        "The best framework is the one your team already knows, I think.",
    ],
    "databases": [
        "SQL vs NoSQL: still one of the great debates of our time.",
        "I spent today migrating a database schema and it was not fun.",
        "How do you handle database migrations in production without downtime?",
        "I discovered an N+1 query problem in production today. Not great.",
        "Indexing is one of those things that seems simple until you need to do it right.",
    ],
    "apis": [
        "I've been designing a REST API and I keep second-guessing my endpoint naming.",
        "GraphQL is powerful but I always wonder if it's overkill for smaller projects.",
        "Rate limiting is one of those API features you don't think about until you need it.",
        "I integrated a third-party API today and the documentation was absolutely terrible.",
        "Versioning APIs is harder than it looks. v1, v2, chaos.",
    ],
    "testing": [
        "I wrote unit tests for some code today and immediately found two bugs. Tests work.",
        "How do you decide what to test and what to leave untested?",
        "Integration tests are so much more valuable than unit tests in my experience.",
        "TDD is great in theory. I can never quite commit to it in practice.",
        "My test suite takes 15 minutes to run. I'm starting to hate it.",
    ],
    "deployment": [
        "I broke production today. The shame is real but also the learning.",
        "CI/CD pipelines are magical when they work and infuriating when they don't.",
        "I set up Docker for the first time for a project. Game changer.",
        "Zero-downtime deployments — how do you actually do them properly?",
        "Environment variables keep biting me. Always a different .env issue.",
    ],
    "performance": [
        "I optimised a slow query today and it went from 10 seconds to 100ms. Best feeling.",
        "Premature optimisation is a problem but so is ignoring performance entirely.",
        "Profiling is one of those skills that makes a huge difference once you learn it.",
        "My API response times crept up and I didn't notice for two weeks.",
        "Caching solves everything until it causes a different problem.",
    ],
    "git_workflow": [
        "I accidentally committed to main. Fast forward to 20 minutes of fixing it.",
        "How do you handle merge conflicts? I still find them stressful.",
        "Rebasing vs merging — where do you stand?",
        "My commit messages are usually terrible. I should be better about it.",
        "I've started writing conventional commits and it's been surprisingly helpful.",
    ],
    "documentation": [
        "Writing docs for my own code is harder than writing the code.",
        "I inherited a codebase with no documentation. Truly a horror show.",
        "Is inline documentation enough or do you need external docs too?",
        "Good variable names can replace a lot of comments.",
        "I wrote a README today and spent more time on it than on the actual feature.",
    ],
    "open_source": [
        "I made my first open source contribution last week. Small but it felt good.",
        "Maintaining an open source project looks exhausting. Respect to those who do it.",
        "The open source community is mostly amazing and occasionally very hostile.",
        "I depend on so many open source libraries and contribute to basically none of them. Guilt.",
        "How do you choose what to open source and what to keep private?",
    ],
    "career": [
        "I'm trying to figure out if I want to go more technical or into engineering management.",
        "Job searching in tech right now is strange. The market has really shifted.",
        "Senior developer titles don't mean the same thing at every company.",
        "How important is the company you work for versus the work you do there?",
        "Imposter syndrome never fully goes away, does it?",
    ],
    "side_projects": [
        "I started a side project three months ago and I'm still on the 'planning' phase.",
        "Side projects are where I learn more than at work most of the time.",
        "Has any of your side projects ever become something real?",
        "I have a graveyard of unfinished side projects. Very relatable I think.",
        "The hardest part of a side project is the boring parts — auth, deployment, logging.",
    ],
}

_ASSISTANT: dict[str, list[str]] = {
    "debugging": [
        "The observer effect in debugging is real — adding logging changes the behaviour.",
        "Two hours on one bug is when you step away and come back fresh.",
        "Finding a bug in someone else's library is a unique kind of frustration.",
        "The euphoria of fixing a long-standing bug is one of programming's great rewards.",
        "The most dangerous bugs are the ones that only appear in production.",
    ],
    "code_review": [
        "Good code review feedback focuses on the code, not the coder.",
        "Fast reviews that catch the critical things are better than slow exhaustive ones.",
        "Leaving a comment praising good code is underrated. People like hearing what's working.",
        "Reviewers should explain the why, not just say 'change this'.",
        "The best reviews make you a better developer. That's the whole point.",
    ],
    "architecture": [
        "Start with the monolith. Split later if you actually need to.",
        "Over-engineering is a real project killer. Simple things should stay simple.",
        "Architecture decisions compound. A bad one early is expensive later.",
        "Good architecture makes adding features easy and deleting things even easier.",
        "The best architecture is the one your team can maintain without heroics.",
    ],
    "algorithms": [
        "Algorithm interviews are a separate skill from day-to-day engineering.",
        "Understanding the fundamentals pays dividends even if you never implement them directly.",
        "Something clicking after you struggle with it is one of the best learning feelings.",
        "Big O matters most when your data size gets large. It's a scaling concern.",
        "Implementing things from scratch teaches you how they actually work.",
    ],
    "frameworks": [
        "Framework churn is exhausting but also means the ecosystem is active.",
        "FastAPI is excellent. Good choice if you're starting fresh.",
        "The best framework is the one that gets out of your way.",
        "Knowing vanilla well means you can work with any framework.",
        "Teams shipping on 'boring' technology consistently beat teams chasing trends.",
    ],
    "databases": [
        "SQL is underrated. It does most things extremely well.",
        "Schema migrations in production are stressful. Blue-green deployments help.",
        "N+1 queries are a right of passage. You learn to spot them quickly after the first time.",
        "The right database depends on your access patterns, not trends.",
        "Indexes are magic. Missing ones explain most slow queries.",
    ],
    "apis": [
        "REST is simple and works. Don't overthink the naming.",
        "GraphQL is great for complex data graphs. Overkill for simple CRUD.",
        "Rate limiting, versioning, and auth are the boring parts that matter most.",
        "Third-party API docs are either great or a nightmare. No middle ground.",
        "Versioning via URL prefix is boring but reliable. Just do it.",
    ],
    "testing": [
        "Tests finding bugs immediately is the whole point. It's working correctly.",
        "Test what matters: the behaviour, not the implementation.",
        "Integration tests have more real-world confidence than unit tests alone.",
        "TDD is a discipline. Hard to learn but rewarding if you can commit to it.",
        "Slow test suites kill development velocity. Worth investing in speed.",
    ],
    "deployment": [
        "Breaking prod is a rite of passage. The important thing is the post-mortem.",
        "Good CI/CD is invisible. You only notice it when it breaks.",
        "Docker removes the 'works on my machine' problem. Worth the learning curve.",
        "Zero-downtime deployment is mostly about health checks and graceful shutdowns.",
        "Environment variable management is an underappreciated part of ops.",
    ],
    "performance": [
        "100ms is almost always fast enough. Profile before you optimise.",
        "Premature optimisation is bad. Ignoring performance entirely is also bad.",
        "Profiling shows you where time actually goes, which is usually surprising.",
        "Slow creep in API response times is insidious. Good monitoring catches it early.",
        "Caching is fast and creates problems at the same time. Trade wisely.",
    ],
    "git_workflow": [
        "Accidentally committing to main is a humbling experience everyone has.",
        "Rebasing makes history cleaner. Merging is safer for shared branches.",
        "Merge conflicts are a communication problem as much as a technical one.",
        "Good commit messages are documentation for your future self.",
        "Conventional commits plus a changelog generator is a clean workflow.",
    ],
    "documentation": [
        "Writing docs is hard because it forces you to understand your own code.",
        "Undocumented code is a trap for the next person, which is usually future you.",
        "Good names remove the need for most inline comments.",
        "A README is the front door to your project. First impressions matter.",
        "External docs and inline docs serve different audiences. You need both.",
    ],
    "open_source": [
        "Small contributions count. Docs, tests, typos — they all matter.",
        "Maintaining open source without burning out is a real challenge.",
        "The community around a project matters as much as the code.",
        "Using a tool without contributing is fine. Most users don't and that's okay.",
        "What to open source depends on whether it'd be useful to others in the same situation.",
    ],
    "career": [
        "Management and technical tracks are both valid. Know which one energises you.",
        "The tech job market has genuinely shifted. More selectivity on both sides.",
        "The work you do day-to-day matters more than the company name on the CV.",
        "Imposter syndrome doesn't fully go away. You just learn to work with it.",
        "Seniority is about impact and judgment, not years of experience.",
    ],
    "side_projects": [
        "Planning indefinitely is procrastination with a good excuse. Just start building.",
        "Side projects as learning environments are genuinely where a lot of growth happens.",
        "The project graveyard is where good ideas go to become learning experiences.",
        "Finishing a side project is rarer than starting one. Ship something small first.",
        "The boring infrastructure parts of a side project are actually great to learn.",
    ],
}


def get_topics() -> list[str]:
    return TOPICS


def get_user_message(topic: str, rng: random.Random) -> str:
    messages = _USER.get(topic, [f"Thoughts on {topic.replace('_', ' ')}?"])
    return rng.choice(messages)


def get_assistant_message(topic: str, rng: random.Random) -> str:
    messages = _ASSISTANT.get(topic, ["Interesting perspective. What's your take?"])
    return rng.choice(messages)
