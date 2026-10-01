from openai import OpenAI
from dotenv import load_dotenv
from typing import Any
import os
import json

load_dotenv()


class CollaborativeSummaryLLM:

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_insight_summary(self, candidate_insights: list[str],current_activity: dict) -> list[dict[str, Any]]:

        prompt = f"""
                You are a user behavior analyzer for an e-commerce recommendation system.

                You will be provided with:
                1. The current user's current session activity and recent historical activity.
                2. Preference insights generated from users who are behaviorally similar to the current user.

                Your task is to combine these two sources of information and generate a final set of
                user preference insights that can be used by a recommendation system.

                IMPORTANT RULES:

                - The current user's own behavior is the primary source of truth.
                - Give higher importance to repeated and recent behavior of the current user.
                - Current session activity should be treated as especially relevant.
                - Similar-user insights should only be used to strengthen, supplement, or discover
                preferences that are reasonably consistent with the current user's behavior.
                - Do not blindly copy preferences from similar users.
                - Do not introduce a preference solely because similar users have it if there is no
                supporting evidence from the current user's behavior.
                - If the current user's behavior conflicts with a similar-user preference, prefer the
                current user's behavior.
                - Give more importance to preferences supported by multiple similar users.
                - Only infer a preference when there is sufficient evidence.
                - Do not invent preferences that are not supported by the provided data.
                - If there is insufficient evidence for a field, return an empty list or null.
                - Return ONLY valid JSON.
                - Do not include explanations, markdown, or additional text.

                Return a JSON list containing one preference object.

                The preference object must contain these fields:

                - "brands": list of brands the user appears to prefer.
                - "categories": list of product categories the user appears to prefer.
                - "price_range": preferred price range as a string such as "100-200".
                - "colors": list of preferred colors.
                - "materials": list of preferred materials.
                - "styles": list of preferred styles.
                - "occasions": list of occasions the user appears to shop for,
                such as casual, formal, party, wedding, work, etc.
                - "matching_items": list of complementary or commonly paired items
                that appear relevant to the user's preferences.
                - "cart_abandonment_reasons": list of reasons inferred from past
                cart abandonment behavior, such as price, waiting for an occasion,
                lack of discounts, etc.
                - "return_reasons": list of reasons inferred from past returns,
                such as size, color, quality, fit, etc.
                - "purchase_factors": list of factors that appear to influence
                the user's purchases, such as price, brand, quality, size, color, etc.
                - "purchase_frequency": a string representing the user's purchase
                frequency, such as daily, weekly, monthly, occasionally, etc.

                Example output:

                [
                    {{
                        "brands": ["Nike", "Adidas"],
                        "categories": ["sneakers", "sportswear"],
                        "price_range": "100-200",
                        "colors": ["black", "white"],
                        "materials": ["cotton"],
                        "styles": ["casual", "sporty"],
                        "occasions": ["casual", "gym"],
                        "matching_items": ["socks", "sports shoes"],
                        "cart_abandonment_reasons": ["high price"],
                        "return_reasons": ["size"],
                        "purchase_factors": ["comfort", "brand", "price"],
                        "purchase_frequency": "monthly"
                    }}
                ]

                CURRENT USER BEHAVIOR:

                {current_activity}

                SIMILAR USER PREFERENCE INSIGHTS:

                {candidate_insights}
                """


        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )

            response_content = response.choices[0].message.content

            if not response_content:
                print("LLM response is empty.")
                return []

            preferences = json.loads(response_content)

            if not isinstance(preferences, list):
                print("LLM response is not a list.")
                return []

            return preferences

        except json.JSONDecodeError as e:
            print(f"Error parsing LLM JSON response: {e}")
            return []

        except Exception as e:
            print(f"Error in LLM. Unable to send request: {e}")
            return []