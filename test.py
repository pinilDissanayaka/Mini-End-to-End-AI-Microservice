import asyncio
from sqlalchemy import update
from database import SessionLocal
from database.models import Agent
from utils import FAQMatcher


async def test_update_initial_suggestions():
    """Update initialSuggestion for an existing Agent based on webName."""
    matcher = FAQMatcher()

    # sample suggestions payload
    initial_suggestions = [
        {
        "id": "1",
        "message": "Hi, How are you?",
        "suggestions": ["Never tried diving before?", "Diving Packages", "Best place to go diving right now!"]
        },
        {
        "id": "2",
        "message": "can you customize a dive trip for me?",
        "suggestions": ["can you tailor dives to my experience?", "can you plan around my dates & budget?", "how do i request a custom quote?"]
        },
        {
        "id": "3",
        "message": "what dive/snorkel locations do you cover?",
        "suggestions": ["do you go to Unawatuna & Galle reefs?", "do you visit Colombo shipwrecks?", "can you take me to Pigeon Island (Trinco)?"]
        },
        {
        "id": "4",
        "message": "how many days do i need in sri lanka for ocean adventures?",
        "suggestions": ["is 5–7 days enough for highlights?", "what would a 10–14 day coast plan look like?", "can you suggest a day-by-day plan?"]
        },
        {
        "id": "5",
        "message": "do you provide airport or hotel transfers?",
        "suggestions": ["can you pick me up at Bandaranaike Airport?", "is the transfer private or shared?", "is it included in packages?"]
        },
        {
        "id": "6",
        "message": "what accommodation levels can i choose near the coast?",
        "suggestions": ["do you offer Economy & Mid-range stays?", "can i upgrade to Luxury or Boutique?", "which partner hotels do you use?"]
        },
        {
        "id": "7",
        "message": "what meal plans are available on tours/boats?",
        "suggestions": ["do you offer snacks & refreshments on day trips?", "is Half Board or Full Board possible on multi-day?", "can you handle dietary needs?"]
        },
        {
        "id": "8",
        "message": "what activities can you arrange?",
        "suggestions": ["can you book scuba & discover scuba?", "do you offer snorkeling, SUP or kayaking?", "can you arrange whale/dolphin watching (seasonal)?"]
        },
        {
        "id": "9",
        "message": "what are your most popular themed trips?",
        "suggestions": ["what’s in ‘Wreck Explorer’ (3D/2N)?", "what’s in ‘Reef & Turtles’ (2D/1N)?", "what’s in ‘Coast-to-Coast’ (7D/6N)?"]
        },
        {
        "id": "10",
        "message": "do you offer flexible booking options?",
        "suggestions": ["can i modify my dates later?", "what’s your reschedule policy?", "are there change fees?"]
        },
        {
        "id": "11",
        "message": "how do i contact you quickly?",
        "suggestions": ["can i call your hotline/WhatsApp?", "can i email the reservations team?", "do you respond on Facebook/Instagram?"]
        },
        {
        "id": "12",
        "message": "what’s the best time to visit each coast?",
        "suggestions": ["when is the south/west coast dive season?", "when is the east coast season (Trinco/Kalpitiya)?", "when is whale watching best?"]
        },
        {
        "id": "13",
        "message": "what should i know before diving/snorkeling?",
        "suggestions": ["what certifications or medical forms do i need?", "can i rent full gear from you?", "what’s the local currency and common languages?"]
        },
        {
        "id": "14",
        "message": "can i combine ocean adventures with inland highlights?",
        "suggestions": ["can you mix beach days with Kandy/Ella?", "can we add a Yala safari day?", "can we do rafting at Kitulgala en route?"]
        },
        {
        "id": "15",
        "message": "how do payments and invoices work?",
        "suggestions": ["what payment methods do you accept?", "when is the balance due?", "can i get a formal invoice/receipt?"]
        },
        {
        "id": "16",
        "message": "what is your cancellation policy?",
        "suggestions": ["are bookings refundable?", "how far in advance must i cancel?", "can i rebook without penalty?"]
        },
        {
        "id": "17",
        "message": "do you provide instructors, guides, and safety briefings?",
        "suggestions": ["are dives guided by certified professionals?", "what’s included in the safety briefing & insurance?", "can i request an English-speaking instructor?"]
        },
        {
        "id": "18",
        "message": "can you arrange family-friendly trips?",
        "suggestions": ["can you plan around kids’ ages & swim levels?", "are life jackets & child gear available?", "are there calm snorkel spots for beginners?"]
        },
        {
        "id": "19",
        "message": "can you help with special occasions?",
        "suggestions": ["do you have honeymoon/surprise add-ons?", "can you arrange private boat charters?", "can you set up photography or drone shots?"]
        },
        {
        "id": "20",
        "message": "how do i start a booking?",
        "suggestions": ["can i submit the contact form?", "what info do you need (dates, pax, budget, cert level)?", "how soon will you confirm availability?"]
        },
        {
        "id": "21",
        "message": "do you cover less-touristy or niche locations?",
        "suggestions": ["can i add Kalpitiya or Hikkaduwa wrecks?", "can we include Nilaveli/Pigeon Island?", "do you run night dives when conditions allow?"]
        },
        {
        "id": "22",
        "message": "what about safety, weather, and visibility?",
        "suggestions": ["how do you decide go/no-go on rough days?", "what’s typical water temp & visibility by season?", "do you provide dive insurance options?"]
        }
    ]


    web_name = "adrenaline"

    async with SessionLocal() as session:
        # Update existing Agent's initialSuggestion based on webName
        stmt = (
            update(Agent)
            .where(Agent.webName == web_name)
            .values(initialSuggestion=initial_suggestions)
            .returning(Agent.id)
        )

        result = await session.execute(stmt)
        updated_agent = result.fetchone()
        
        if updated_agent is None:
            print(f"No agent found with webName: {web_name}")
            return
        
        agent_id = updated_agent[0]
        await session.commit()
        
        print(f"Successfully updated initialSuggestion for agent ID: {agent_id} with webName: {web_name}")

        # Load into matcher
        loaded = await matcher.load_from_database(session, web_name)

        assert loaded >= 1, "Expected at least one suggestion to be loaded from DB"

        # Now test matching and suggestions
        match = await matcher.match("can i book a demo?", web_name)
        assert match is not None
        print(f"Match found: {match}")

        suggestions = await matcher.suggestions("pricing plans", web_name, k=3)
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        print(f"Suggestions: {suggestions}")
        
        
if __name__ == "__main__":
    asyncio.run(test_update_initial_suggestions())
