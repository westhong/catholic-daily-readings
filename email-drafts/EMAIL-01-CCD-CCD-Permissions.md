# Email Draft 1 — 給 CCD (Confraternity of Christian Doctrine)

**收件人：** Associate Director, Permissions, CCD
**地址：** 3211 Fourth Street, NE, Washington, DC 20017-1194
**Email：** nabperm@usccb.org
**主題：** Permission Inquiry — Free Catholic Daily Readings Project for Chinese-Speaking Catholics Worldwide

---

Dear Associate Director,

I am writing to inquire about obtaining permission for a free, open-source Catholic daily readings project.

**About the Project:**

My name is [Your Name], and I am an independent developer in Canada. I have built a free, open-source project called "Catholic Daily Readings" (https://github.com/westhong/catholic-daily-readings) that currently serves daily Mass readings in Traditional Chinese to Chinese-speaking Catholics worldwide.

The project is entirely free — no ads, no monetization, no commercial use. It is a work of personal devotion, aimed at spreading God's Word to Chinese-speaking Catholics who currently have no free daily reading resource in their language.

**What We Are Requesting Permission For:**

We are planning to expand the project to include English readings. Specifically, we would like to request permission to:

1. **Display the daily reading references** (lectionary numbers, feast names, and chapter:verse references such as "Luke 24:13-35") obtained from the USCCB daily readings page, in our open-source project

2. **Serve the New American Bible Revised Edition (NABRE) text** for these readings, dynamically fetched in real-time when users request them (not pre-stored), to users who agree to use the content for personal prayer and research only

3. **Pre-compute and publish the 3-year lectionary cycle structure** (lectionary numbers + chapter references only, no full text) on our public GitHub repository, marked as "for research use"

**Our Current Approach:**

For the MVP currently on GitHub, we:
- Scrape lectionary metadata (lectionary number, feast name, reading references) from the USCCB website
- Fetch the actual Bible text from a third-party API (bible.fhl.net) that provides the Chinese Union Version / 思高譯本 translation
- Users run the script locally to get their daily readings

We are seeking formal permission to make this project more freely accessible, particularly to English-speaking users, while remaining in full compliance with CCD's copyright policies.

**Why We Believe This Serves the Catholic Mission:**

There is currently no free, open-source Catholic daily readings system available to Chinese-speaking or English-speaking Catholics worldwide. Many existing resources require paid subscriptions. Our project seeks to remove that barrier — for the glory of God and the spread of His Word (Matthew 28:19).

**Questions:**

1. Does CCD have a specific licensing pathway for open-source, non-commercial devotional projects?
2. Is there a permission process for displaying the daily lectionary structure (lectionary numbers + references only) on a public repository?
3. For serving NABRE text via API fetch (not pre-storage), what conditions must be met?

We are happy to:
- Provide full attribution to CCD on every reading displayed
- Limit use to personal/private devotional purposes
- Include the standard CCD copyright acknowledgment
- Discuss any licensing fees if applicable

Please let us know the appropriate path forward, or if there is someone else we should speak with.

Thank you for your time and for your service to the Church.

In Christ,

[Your Name]
Email: westhong@gmail.com
GitHub: https://github.com/westhong/catholic-daily-readings

---

## Notes for West:

- CCD has a specific policy: "No permission or fee is needed to display the daily readings on an RSS feed only on a website which does not condition access by users on the users giving anything of value to the website operator." This might cover our use case partially.
- NABRE policy: <5,000 words, <40% of single book = no permission needed
- The key question is whether our "dynamic API fetch" model constitutes a "digital application" requiring a license
- Email address found on: https://www.usccb.org/offices/new-american-bible/permissions
