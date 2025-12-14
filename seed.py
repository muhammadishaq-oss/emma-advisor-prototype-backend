import asyncio
from beanie import init_beanie
from database import client
from models import User, Family, College, Milestone, Tip, ChatMessage, RichMediaLink

async def seed_data():
    print("Initializing Beanie...")
    await init_beanie(database=client.emma_advisor_db, document_models=[User, Family, College, Milestone, Tip, ChatMessage])

    print("Clearing existing data...")
    await College.delete_all()
    await Milestone.delete_all()
    await Tip.delete_all()

    print("Seeding Colleges...")
    colleges = [
        College(
            name="University of California, Berkeley",
            acceptance_rate="14%",
            tuition="$45,000/year",
            emotional_tagline="Where big ideas meet bigger impact.",
            default_fit_reason="Known for its strong academic programs and vibrant campus culture, perfect for ambitious students who thrive in a dynamic environment.",
            default_fit_reason_student="Good for curious thinkers who want to change the world.",
            rich_media_links=[
                RichMediaLink(type="Campus Tour", url="#"),
                RichMediaLink(type="Day in the Life", url="#"),
                RichMediaLink(type="Student POV", url="#"),
            ]
        ),
        College(
            name="Reed College",
            acceptance_rate="35%",
            tuition="$65,000/year",
            emotional_tagline="Unleash your intellect in a community that values deep inquiry.",
            default_fit_reason="A highly intellectual and quirky environment, ideal for independent thinkers who love rigorous academics and a close-knit community.",
            default_fit_reason_student="Lots of outdoorsy, chill people who love to read and think.",
            rich_media_links=[
                RichMediaLink(type="Campus Tour", url="#"),
                RichMediaLink(type="Student Life", url="#"),
            ]
        ),
        College(
            name="Emory University",
            acceptance_rate="19%",
            tuition="$60,000/year",
            emotional_tagline="A vibrant community where intellect and compassion converge.",
            default_fit_reason="Offers a balanced environment with strong academics and a focus on community engagement, great for well-rounded students.",
            default_fit_reason_student="Creative energy + strong academics for a balanced life.",
            rich_media_links=[
                RichMediaLink(type="Virtual Tour", url="#"),
                RichMediaLink(type="Alumni Stories", url="#"),
            ]
        )
    ]
    await College.insert_many(colleges)

    print("Seeding Milestones...")
    milestones = [
        Milestone(text="Refine college list based on financial aid estimates.", month="Current"),
        Milestone(text="Prepare for SAT/ACT retakes or subject tests.", month="Current"),
        Milestone(text="Brainstorm essay topics and outline first drafts.", month="Current"),
        Milestone(text="Schedule college visits or virtual tours.", month="Current"),
    ]
    await Milestone.insert_many(milestones)

    print("Seeding Tips...")
    tips = [
        Tip(text="Insider Tip: Admissions officers spend 7–10 minutes per file."),
        Tip(text="Insider Tip: Summer experiences carry major weight."),
        Tip(text="Insider Tip: Demonstrate interest by engaging with colleges online."),
        Tip(text="Insider Tip: Start your essays early to allow for multiple revisions."),
    ]
    await Tip.insert_many(tips)

    print("Seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_data())