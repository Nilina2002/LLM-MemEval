"""Shopping conversation templates."""
from __future__ import annotations
import random

TOPICS = [
    "online_shopping", "finding_deals", "product_reviews", "returns",
    "impulse_buys", "wishlist", "delivery", "electronics", "clothing",
    "groceries", "gift_ideas", "comparing_prices", "subscriptions", "second_hand", "loyalty_programs",
]

_USER: dict[str, list[str]] = {
    "online_shopping": [
        "I just spent an hour browsing and added everything to my cart and bought nothing.",
        "Online shopping is too convenient. My bank account is not happy about it.",
        "I bought something online and it looks nothing like the photos.",
        "The number of tabs I have open from online shopping is frankly embarrassing.",
        "I've started a rule where I leave things in my cart for 24 hours before buying.",
    ],
    "finding_deals": [
        "I found a deal so good I bought two of them and I'm not sure why.",
        "Do you have any tricks for finding good deals online?",
        "Sale season is either a great opportunity or a trap. Depends on discipline.",
        "I spent more time researching a discounted item than it was worth.",
        "I missed a flash sale by three minutes and I'm still thinking about it.",
    ],
    "product_reviews": [
        "How much do you trust online reviews at this point?",
        "I spent an hour reading reviews to buy a fifteen dollar item.",
        "The bad reviews are always more useful than the five-star ones.",
        "I bought something with amazing reviews and it was terrible.",
        "Fake reviews have made product research genuinely difficult.",
    ],
    "returns": [
        "I need to return something and I've been putting it off for two weeks.",
        "Free returns are the thing that makes online shopping genuinely work.",
        "I bought three sizes to find one that fits and now I need to return two.",
        "I lost the receipt for an in-store return. Classic.",
        "The return policy was the deciding factor in where I bought from.",
    ],
    "impulse_buys": [
        "I bought something impulsively yesterday that I absolutely do not need.",
        "Impulse buys from late night browsing have a 50/50 hit rate.",
        "I went in for one thing and left with seven. It always happens.",
        "The impulse buy that turned out to be the best thing I own.",
        "I've gotten much better at resisting impulse buys. Took years.",
    ],
    "wishlist": [
        "My wish list is so long it's basically a second shopping cart.",
        "I add things to my wish list and then forget about them for months.",
        "Do you keep a wish list for gift ideas for yourself?",
        "I cleared my wish list and immediately felt lighter.",
        "Some things stay on the wish list so long they become obsolete.",
    ],
    "delivery": [
        "The package was supposedly delivered and I have absolutely no idea where it is.",
        "I love tracking a package in real time even when it changes nothing.",
        "Same-day delivery has ruined my patience for anything that takes longer.",
        "A delivery showed up a week early and it was the best surprise.",
        "I ordered something from overseas and it's been in customs for two weeks.",
    ],
    "electronics": [
        "I'm trying to decide on a new laptop and the options are genuinely overwhelming.",
        "My headphones finally gave up after five years and I need to find new ones.",
        "The feature I paid extra for on my last phone I never once used.",
        "I went to buy one accessory and ended up in a technology spiral.",
        "Waiting for the new model versus buying the current one is always a dilemma.",
    ],
    "clothing": [
        "Shopping for clothes online is a gamble I keep taking.",
        "I need something specific and can't find it anywhere.",
        "I tried something on in store and then found it cheaper online.",
        "My style has shifted and I'm slowly replacing most of my wardrobe.",
        "The size on the label and the actual fit are sometimes unrelated.",
    ],
    "groceries": [
        "Online grocery shopping changed my life and also my relationship with produce.",
        "I went to the supermarket without a list and spent twice what I planned.",
        "The item I specifically went to buy was out of stock.",
        "I'm trying to plan meals better so I waste less food.",
        "Buying in bulk saves money until it doesn't and you throw most of it away.",
    ],
    "gift_ideas": [
        "I have no idea what to get someone who has everything they want.",
        "Experience gifts versus physical gifts — do you have a preference?",
        "I found the perfect gift and I'm genuinely excited to give it.",
        "I always panic about gifts and then find something at the last minute.",
        "The best gifts are the ones that show you were actually paying attention.",
    ],
    "comparing_prices": [
        "I found the same product for different prices on three different sites.",
        "Price comparison sites save money until they send you down a rabbit hole.",
        "I checked if I could find it cheaper and saved more than I expected.",
        "Is it worth spending an hour comparing prices to save five dollars?",
        "Cheapest isn't always best but sometimes cheapest is genuinely fine.",
    ],
    "subscriptions": [
        "I added up all my subscriptions last month and immediately cancelled two.",
        "Free trials that automatically convert to paid are a specific kind of trap.",
        "I've been meaning to cancel a subscription I don't use for three months.",
        "Annual billing is cheaper but commits you in a way monthly doesn't.",
        "I found a subscription I forgot I had. That's embarrassing and expensive.",
    ],
    "second_hand": [
        "I've been buying second-hand more and the quality is often better than new.",
        "Finding something great in a second-hand shop feels like a win.",
        "Selling old things I don't use has funded some of my new purchases.",
        "Second-hand electronics make me slightly nervous but they're usually fine.",
        "Charity shops are underrated for specific things. Books, especially.",
    ],
    "loyalty_programs": [
        "I have too many loyalty cards and never remember to use them.",
        "I redeemed loyalty points for something useful for once.",
        "Are loyalty programs worth the data you give them?",
        "I just found out I had enough loyalty points to cover an entire purchase.",
        "I signed up for a loyalty program and regretted the inbox consequences.",
    ],
}

_ASSISTANT: dict[str, list[str]] = {
    "online_shopping": [
        "The cart abandon is a valid strategy. Sometimes you want it less after a day.",
        "Convenient purchasing removes the friction that protects your wallet.",
        "Product photos versus reality is a very well-known gap.",
        "The browsing tab collection is universal. Mine gets out of control regularly.",
        "24-hour cart rule is genuinely effective. Kills a lot of impulses.",
    ],
    "finding_deals": [
        "Price tracking tools send alerts when things you've saved hit target prices.",
        "Sale discipline — only buying things you would have bought anyway — is the key.",
        "Flash sale regret is its own specific feeling.",
        "Buying two of something good you found on sale is reasonable actually.",
        "Research time exceeding item value is a trap worth noticing.",
    ],
    "product_reviews": [
        "Reviews are useful with appropriate scepticism. Look for patterns across many.",
        "One-star reviews reveal the worst-case scenarios. Useful data.",
        "Reviews at the three-star level are often the most honest.",
        "Fakes have become sophisticated. Verified purchase filters help somewhat.",
        "The gap between review and reality is narrower for boring, functional products.",
    ],
    "returns": [
        "Procrastinated returns are a universal problem. Set a calendar reminder.",
        "Free returns changed e-commerce in a fundamental way.",
        "Buying multiple sizes to find the right fit is rational.",
        "Lost receipts are the universe enforcing a boundary on your return.",
        "Return policy as a decision factor is very sensible.",
    ],
    "impulse_buys": [
        "Some impulse buys are genuinely good. The problem is you can't know in advance.",
        "Late night browsing purchases have a quality distribution problem.",
        "Going in for one thing and leaving with seven is gravity, basically.",
        "The impulse buy that turns out to be great is the one that keeps the habit alive.",
        "Resisting impulse buys is a skill that develops with practice and mild regret.",
    ],
    "wishlist": [
        "Long wish lists are aspirational, not transactional. That's fine.",
        "The items that stay on the list longest are either perfect or unnecessary.",
        "Wish lists double as gift guides. Share them widely.",
        "Clearing a wish list is a kind of digital decluttering.",
        "Items that become obsolete on the list tell you something about what you actually need.",
    ],
    "delivery": [
        "Missing deliveries are one of the great friction points of e-commerce.",
        "Package tracking is anxiety management with extra steps.",
        "Same-day delivery has recalibrated expectations in a way that's hard to undo.",
        "An early delivery is the best kind of surprise.",
        "Customs delays are a lesson in international supply chain patience.",
    ],
    "electronics": [
        "Laptop choice paralysis is real. Narrow by use case first, then by budget.",
        "Headphone research is its own rabbit hole. Set a budget and stop at five options.",
        "The features you pay for matter less than the features you actually use.",
        "One accessory purchase spiralling into a technology review session is classic.",
        "Waiting for the new model is sometimes rational and sometimes just delay.",
    ],
    "clothing": [
        "Online clothing fit is genuinely hard to predict. Size charts help sometimes.",
        "Finding something specific and not finding it anywhere is a specific frustration.",
        "Trying in store and buying cheaper online is an efficient hybrid approach.",
        "Wardrobe refreshes are more satisfying when done gradually.",
        "Size inconsistency across brands is a known and unsolved problem.",
    ],
    "groceries": [
        "Online groceries are great except for produce, which needs physical selection.",
        "Lists are everything. Without one, the supermarket is a trap.",
        "Out-of-stock on the specific thing you came for is a law of nature.",
        "Meal planning and grocery waste reduction go hand in hand.",
        "Bulk buying works best for things that don't expire.",
    ],
    "gift_ideas": [
        "Consumables are a reliable gift for people who have everything.",
        "Experience gifts are memorable in a way objects aren't.",
        "Excitement about giving a gift is a good sign you found the right one.",
        "Last-minute gifts often work out. The thoughtfulness is what lands.",
        "The best gifts show observation. That's what people remember.",
    ],
    "comparing_prices": [
        "Price comparison is worth it above a certain threshold. Know yours.",
        "Same product, different prices: check seller reputation alongside price.",
        "Browser extensions that surface comparison prices are very useful.",
        "Time has value. An hour for five dollars saved is often not worth it.",
        "Cheapest is fine for commodities. For quality goods, value matters more.",
    ],
    "subscriptions": [
        "Subscription audit is a useful annual exercise. Almost everyone cancels something.",
        "Free trials that auto-convert rely on forgetting. Calendar reminder at sign-up.",
        "The subscription you don't cancel but also don't use is pure cost.",
        "Annual billing discipline means you have to actually value the service.",
        "Forgotten subscriptions are effectively donations to the company.",
    ],
    "second_hand": [
        "Second-hand shopping rewards patience and willingness to search.",
        "Charity shop book sections are consistently excellent.",
        "Selling what you don't use is cleaner than hoarding and mildly profitable.",
        "Second-hand electronics: check return policy and test immediately.",
        "The quality of older, better-made goods often exceeds modern equivalents.",
    ],
    "loyalty_programs": [
        "Loyalty programs work best when you'd shop there anyway.",
        "Unredeemed points are money left on the table.",
        "The data trade-off is real. Worth knowing what you're exchanging.",
        "Finding accumulated points worth a full purchase is a small delight.",
        "Loyalty inbox consequences are a known side effect. Use a separate email.",
    ],
}


def get_topics() -> list[str]:
    return TOPICS


def get_user_message(topic: str, rng: random.Random) -> str:
    return rng.choice(_USER.get(topic, [f"What do you think about {topic.replace('_', ' ')}?"]))


def get_assistant_message(topic: str, rng: random.Random) -> str:
    return rng.choice(_ASSISTANT.get(topic, ["That makes sense. Anything else on your mind?"]))
