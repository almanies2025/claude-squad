#!/usr/bin/env python3
"""
EF MBA Reflection Generator
Usage: python3 ef_mba_reflection_generator.py [output_file]
"""

LESSON_FOCUS = "Early Stage Financing (Sessions 2–4)"
MODULE = "FNCE696 – Entrepreneurial Finance, Sessions 2-4"
PROFESSOR = "Dr. Ser-Keng Ang, Ph.D."
EMAIL_TO = "Dang Anh"
EMAIL_CC = "Prof. Ang Ser Keng"

REFLECTION = """
Sessions 2–4 gave me a much more practical understanding of how early-stage financing actually works — not just the textbook definitions, but how it plays out in the real world, especially in Southeast Asia.

One of the biggest takeaways for me was the "funding gap" — what the professor called the "missing middle." Angels typically invest US$50,000 to US$200,000, while institutional VCs usually deploy US$2 million and above. But in between those two ranges sits roughly US$500,000 to US$5 million where a lot of promising startups struggle to raise capital. This gap is even more visible in Southeast Asia because angel networks here are still developing and ticket sizes jump too quickly from small to large. That is why we are seeing more micro-VCs, venture debt, and corporate VC stepping in to fill the void.

The comparison between angels and VCs was also really helpful. Angels are essentially individual investors — usually successful entrepreneurs putting in their own money. They move fast, sometimes decide based on gut feel, and care about more than just the financial return. VCs, on the other hand, are institutional. They manage other people's money (LPs), follow formal governance structures, and have strict exit timelines built into their fund life. This shapes everything from how they evaluate deals to how involved they get after investing.

I also found the VC investment process very illuminating. The six stages — from pitching through to signing and closing — can stretch from a few weeks to over a year. Term sheet negotiation and legal documentation are the most time-consuming parts, which I did not fully appreciate before. Understanding that GPs and MDs are the decision-makers, while associates and analysts do the groundwork, also gives me a clearer picture of who to focus on when networking or pitching.

Singapore's position as the regional VC hub was another eye-opener. It captured 56% of Southeast Asia's total deal volume and 64% of deal value in 2022. That is remarkable concentration and says a lot about Singapore's regulatory environment and deal infrastructure compared to its neighbors.

What really stuck with me was the honest framing of VC success rates. Out of 1,000 proposals a VC receives, they might fund just 2. Of those two, 30% go bust, 30% break even, and 10% deliver the outsized returns that make the whole fund work. This means founders need to treat fundraising as a credibility-building process, not just a transaction.

Overall, these sessions made it clear that early-stage financing is a structured ecosystem. It is not just about who has the most money — it is about staged funding, aligned incentives, and knowing which investor fits which stage of your startup journey.
"""


def main():
    output = []
    output.append(f"Subject: EF MBA Reflection – {LESSON_FOCUS}\n")
    output.append(f"To: {EMAIL_TO}")
    output.append(f"Cc: {EMAIL_CC}\n")
    output.append(f"Module: {MODULE}\n")
    output.append(REFLECTION.strip())

    text = "\n".join(output)
    print(text)

    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1], "w") as f:
            f.write(text)
        print(f"\n[Saved to {sys.argv[1]}]")


if __name__ == "__main__":
    main()
