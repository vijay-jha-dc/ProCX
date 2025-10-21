"""
Festival and Seasonal Context Manager
Provides festival-aware, seasonal, and product-category-specific contextual insights
for generating more empathetic and contextually relevant customer messages.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class Festival:
    """Festival information."""
    name: str
    date: datetime
    keywords: List[str]  # Product keywords relevant to this festival
    greeting: Dict[str, str]  # Greetings in different languages
    significance: str  # Why this festival matters
    product_categories: List[str]  # Relevant product categories


class FestivalContextManager:
    """
    Manages festival and seasonal context for empathetic message generation.
    Tracks Indian festivals and their relationship to product purchases.
    """
    
    def __init__(self):
        """Initialize with Indian festival calendar."""
        self.festivals = self._load_indian_festivals_2025()
        self.seasonal_themes = self._define_seasonal_themes()
    
    def _load_indian_festivals_2025(self) -> List[Festival]:
        """
        Load major Indian festivals for 2025.
        Note: Dates are approximate, adjust based on lunar calendar.
        """
        festivals = [
            Festival(
                name="Diwali",
                date=datetime(2025, 10, 20),  # Approximate
                keywords=["diya", "lamp", "candle", "decoration", "sweets", "gift", "gold", "jewelry", "clothes", "electronics"],
                greeting={
                    "en": "Happy Diwali! May this festival of lights bring joy and prosperity.",
                    "hi": "दीपावली की शुभकामनाएं! यह प्रकाश का त्योहार आपके जीवन में खुशियां लाए।",
                    "ta": "தீபாவளி வாழ்த்துக்கள்! இந்த விளக்கு திருநாள் உங்கள் வாழ்வில் மகிழ்ச்சியை கொண்டு வரட்டும்.",
                    "te": "దీపావళి శుభాకాంక్షలు! ఈ దీపాల పండుగ మీ జీవితంలో ఆనందాన్ని తీసుకురావాలి.",
                    "bn": "দীপাবলির শুভেচ্ছা! এই আলোর উৎসব আপনার জীবনে আনন্দ নিয়ে আসুক।"
                },
                significance="Festival of lights, major shopping season",
                product_categories=["Home Decor", "Electronics", "Jewelry", "Clothing", "Gifts"]
            ),
            Festival(
                name="Holi",
                date=datetime(2025, 3, 14),  # Approximate
                keywords=["color", "gulal", "water gun", "festive", "sweets", "traditional wear"],
                greeting={
                    "en": "Happy Holi! May your life be filled with colors of joy.",
                    "hi": "होली की शुभकामनाएं! आपका जीवन खुशियों के रंगों से भर जाए।",
                    "ta": "ஹோலி வாழ்த்துக்கள்! உங்கள் வாழ்க்கை மகிழ்ச்சியின் நிறங்களால் நிரம்பட்டும்.",
                    "te": "హోలీ శుభాకాంక్షలు! మీ జీవితం ఆనందం రంగులతో నిండిపోవాలి.",
                    "bn": "হোলির শুভেচ্ছা! আপনার জীবন আনন্দের রঙে ভরে যাক।"
                },
                significance="Festival of colors, spring celebration",
                product_categories=["Colors", "Festive Wear", "Sweets", "Gifts"]
            ),
            Festival(
                name="Raksha Bandhan",
                date=datetime(2025, 8, 9),  # Approximate
                keywords=["rakhi", "brother", "sister", "gift", "sweets", "traditional"],
                greeting={
                    "en": "Happy Raksha Bandhan! Celebrating the bond of love.",
                    "hi": "रक्षा बंधन की शुभकामनाएं! भाई-बहन के प्यार का त्योहार।",
                    "ta": "ரக்ஷா பந்தன் வாழ்த்துக்கள்! அன்பின் பிணைப்பைக் கொண்டாடுகிறோம்.",
                    "te": "రక్షా బంధన్ శుభాకాంక్షలు! ప్రేమ బంధాన్ని జరుపుకుంటున్నాము.",
                    "bn": "রক্ষাবন্ধনের শুভেচ্ছা! ভালোবাসার বন্ধন উদযাপন করছি।"
                },
                significance="Brother-sister bond celebration, gift season",
                product_categories=["Gifts", "Jewelry", "Sweets", "Clothing"]
            ),
            Festival(
                name="Dussehra",
                date=datetime(2025, 10, 2),  # Approximate
                keywords=["festive", "traditional", "gold", "new beginning", "celebration"],
                greeting={
                    "en": "Happy Dussehra! May good triumph over evil in your life.",
                    "hi": "दशहरा की शुभकामनाएं! आपके जीवन में सत्य की जीत हो।",
                    "ta": "விஜயதசமி வாழ்த்துக்கள்! உங்கள் வாழ்வில் நன்மை வெல்லட்டும்.",
                    "te": "దసరా శుభాకాంక్షలు! మీ జీవితంలో మంచి గెలవాలి.",
                    "bn": "দশেরার শুভেচ্ছা! আপনার জীবনে ভালো খারাপের উপর জয়ী হোক।"
                },
                significance="Victory of good over evil, auspicious for purchases",
                product_categories=["Electronics", "Vehicles", "Gold", "Clothing"]
            ),
            Festival(
                name="Ganesh Chaturthi",
                date=datetime(2025, 8, 27),  # Approximate
                keywords=["ganesh", "idol", "decoration", "sweets", "puja", "traditional"],
                greeting={
                    "en": "Happy Ganesh Chaturthi! May Lord Ganesha bless you.",
                    "hi": "गणेश चतुर्थी की शुभकामनाएं! गणपति बप्पा मोरया!",
                    "ta": "விநாயகர் சதுர்த்தி வாழ்த்துக்கள்! விநாயகர் உங்களை ஆசீர்வதிக்கட்டும்.",
                    "te": "వినాయక చవితి శుభాకాంక్షలు! వినాయకుడు మిమ్మల్ని ఆశీర్వదించాలి.",
                    "bn": "গণেশ চতুর্থীর শুভেচ্ছা! গণেশ আপনাকে আশীর্বাদ করুন।"
                },
                significance="Celebration of Lord Ganesha, new beginnings",
                product_categories=["Idols", "Decorations", "Sweets", "Puja Items"]
            ),
            Festival(
                name="Durga Puja",
                date=datetime(2025, 10, 8),  # Approximate
                keywords=["durga", "pandal", "traditional wear", "jewelry", "festive"],
                greeting={
                    "en": "Happy Durga Puja! May Maa Durga bless you with strength.",
                    "hi": "दुर्गा पूजा की शुभकामनाएं! मां दुर्गा आपको शक्ति प्रदान करें।",
                    "ta": "துர்கா பூஜை வாழ்த்துக்கள்! துர்கா தேவி உங்களுக்கு வலிமை அளிப்பாள்.",
                    "te": "దుర్గా పూజ శుభాకాంక్షలు! దుర్గమ్మ మీకు శక్తిని ఇవ్వాలి.",
                    "bn": "দুর্গা পুজোর শুভেচ্ছা! মা দুর্গা আপনাকে শক্তি দিন।"
                },
                significance="Major festival in Eastern India, grand celebrations",
                product_categories=["Clothing", "Jewelry", "Decorations", "Gifts"]
            ),
            Festival(
                name="Eid",
                date=datetime(2025, 4, 1),  # Approximate (Eid-ul-Fitr)
                keywords=["eid", "festive", "traditional", "clothes", "gifts", "sweets"],
                greeting={
                    "en": "Eid Mubarak! May this special day bring peace and joy.",
                    "hi": "ईद मुबारक! यह खास दिन शांति और खुशियां लाए।",
                    "ta": "ஈத் முபாரக்! இந்த சிறப்பு நாள் அமைதியையும் மகிழ்ச்சியையும் தரட்டும்.",
                    "te": "ఈద్ ముబారక్! ఈ ప్రత్యేక రోజు శాంతి మరియు ఆనందాన్ని తీసుకురావాలి.",
                    "bn": "ঈদ মোবারক! এই বিশেষ দিনটি শান্তি এবং আনন্দ নিয়ে আসুক।"
                },
                significance="Islamic festival, celebration of breaking fast",
                product_categories=["Clothing", "Gifts", "Sweets", "Jewelry"]
            ),
            Festival(
                name="Christmas",
                date=datetime(2025, 12, 25),
                keywords=["christmas", "tree", "decoration", "gift", "cake", "santa", "celebration"],
                greeting={
                    "en": "Merry Christmas! Wishing you peace and joy.",
                    "hi": "क्रिसमस की शुभकामनाएं! आपको शांति और खुशी मिले।",
                    "ta": "கிறிஸ்துமஸ் வாழ்த்துக்கள்! உங்களுக்கு அமைதியும் மகிழ்ச்சியும் கிடைக்கட்டும்.",
                    "te": "క్రిస్మస్ శుభాకాంక్షలు! మీకు శాంతి మరియు ఆనందం కలగాలి.",
                    "bn": "ক্রিসমাসের শুভেচ্ছা! আপনার শান্তি এবং আনন্দ হোক।"
                },
                significance="Christian festival, gift-giving season",
                product_categories=["Decorations", "Gifts", "Electronics", "Toys"]
            ),
            Festival(
                name="New Year",
                date=datetime(2025, 1, 1),
                keywords=["new year", "celebration", "party", "resolution", "gift"],
                greeting={
                    "en": "Happy New Year! Wishing you success and happiness.",
                    "hi": "नव वर्ष की शुभकामनाएं! आपको सफलता और खुशियां मिलें।",
                    "ta": "புத்தாண்டு வாழ்த்துக்கள்! உங்களுக்கு வெற்றியும் மகிழ்ச்சியும் கிடைக்கட்டும்.",
                    "te": "నూతన సంవత్సర శుభాకాంక్షలు! మీకు విజయం మరియు ఆనందం కలగాలి.",
                    "bn": "নববর্ষের শুভেচ্ছা! আপনার সাফল্য এবং সুখ হোক।"
                },
                significance="New Year celebration, fresh starts",
                product_categories=["Party Supplies", "Gifts", "Electronics", "Clothing"]
            )
        ]
        
        return festivals
    
    def _define_seasonal_themes(self) -> Dict[str, Dict[str, Any]]:
        """Define seasonal themes and their characteristics."""
        return {
            "summer": {
                "months": [3, 4, 5, 6],
                "keywords": ["summer", "heat", "cooling", "ac", "fan", "cotton", "light"],
                "product_categories": ["Cooling Appliances", "Summer Wear", "Beverages"],
                "messaging_tone": "refreshing, cool, comfort-focused"
            },
            "monsoon": {
                "months": [7, 8, 9],
                "keywords": ["rain", "monsoon", "umbrella", "waterproof", "indoor"],
                "product_categories": ["Rain Gear", "Indoor Entertainment", "Waterproof Items"],
                "messaging_tone": "cozy, protective, indoor-comfort"
            },
            "festive_season": {
                "months": [10, 11],  # Diwali season
                "keywords": ["festive", "celebration", "gift", "shopping", "special"],
                "product_categories": ["Gifts", "Decorations", "Clothing", "Electronics"],
                "messaging_tone": "celebratory, joyful, generous"
            },
            "winter": {
                "months": [12, 1, 2],
                "keywords": ["winter", "warm", "heater", "woolen", "cozy"],
                "product_categories": ["Heaters", "Winter Wear", "Warm Beverages"],
                "messaging_tone": "warm, comforting, cozy"
            }
        }
    
    def get_current_festival_context(self, reference_date: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """
        Get festival context for current date or reference date.
        
        Args:
            reference_date: Optional reference date (defaults to now)
            
        Returns:
            Festival context if within festival period, None otherwise
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        # Check if we're within 7 days before or 3 days after any festival
        for festival in self.festivals:
            days_diff = (reference_date.date() - festival.date.date()).days
            
            if -7 <= days_diff <= 3:  # Festival window
                context = {
                    "festival_name": festival.name,
                    "festival_date": festival.date,
                    "days_until_festival": -days_diff if days_diff < 0 else 0,
                    "days_after_festival": days_diff if days_diff > 0 else 0,
                    "is_before_festival": days_diff < 0,
                    "is_festival_day": days_diff == 0,
                    "is_after_festival": days_diff > 0,
                    "keywords": festival.keywords,
                    "greetings": festival.greeting,
                    "significance": festival.significance,
                    "relevant_categories": festival.product_categories
                }
                return context
        
        return None
    
    def get_seasonal_context(self, reference_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get seasonal context for current date.
        
        Args:
            reference_date: Optional reference date (defaults to now)
            
        Returns:
            Seasonal context dictionary
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        current_month = reference_date.month
        
        for season_name, season_info in self.seasonal_themes.items():
            if current_month in season_info["months"]:
                return {
                    "season": season_name,
                    "keywords": season_info["keywords"],
                    "relevant_categories": season_info["product_categories"],
                    "messaging_tone": season_info["messaging_tone"]
                }
        
        return {
            "season": "general",
            "keywords": [],
            "relevant_categories": [],
            "messaging_tone": "professional and friendly"
        }
    
    def is_product_festival_relevant(self, product_category: str, purchased_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Check if a product purchase is festival-relevant.
        
        Args:
            product_category: Product category name
            purchased_date: Date of purchase (defaults to now)
            
        Returns:
            Dictionary with relevance information
        """
        if purchased_date is None:
            purchased_date = datetime.now()
        
        festival_context = self.get_current_festival_context(purchased_date)
        
        if not festival_context:
            return {
                "is_festival_relevant": False,
                "relevance_score": 0.0,
                "context": "No active festival period"
            }
        
        # Check if product category matches festival categories
        relevant_categories = festival_context.get("relevant_categories", [])
        product_lower = product_category.lower()
        
        # Direct category match
        for cat in relevant_categories:
            if cat.lower() in product_lower or product_lower in cat.lower():
                return {
                    "is_festival_relevant": True,
                    "relevance_score": 1.0,
                    "festival": festival_context["festival_name"],
                    "context": f"Highly relevant for {festival_context['festival_name']}",
                    "significance": festival_context["significance"],
                    "festival_timing": {
                        "is_before": festival_context["is_before_festival"],
                        "is_during": festival_context["is_festival_day"],
                        "is_after": festival_context["is_after_festival"]
                    }
                }
        
        # Keyword match
        keywords = festival_context.get("keywords", [])
        keyword_matches = [kw for kw in keywords if kw.lower() in product_lower]
        
        if keyword_matches:
            return {
                "is_festival_relevant": True,
                "relevance_score": 0.7,
                "festival": festival_context["festival_name"],
                "context": f"Moderately relevant for {festival_context['festival_name']}",
                "matched_keywords": keyword_matches,
                "significance": festival_context["significance"],
                "festival_timing": {
                    "is_before": festival_context["is_before_festival"],
                    "is_during": festival_context["is_festival_day"],
                    "is_after": festival_context["is_after_festival"]
                }
            }
        
        return {
            "is_festival_relevant": False,
            "relevance_score": 0.0,
            "context": f"Not directly relevant to {festival_context['festival_name']}"
        }
    
    def get_festival_greeting(self, language: str = "en", reference_date: Optional[datetime] = None) -> Optional[str]:
        """
        Get festival greeting in specified language.
        
        Args:
            language: Language code (en, hi, ta, te, bn)
            reference_date: Optional reference date
            
        Returns:
            Festival greeting string or None
        """
        festival_context = self.get_current_festival_context(reference_date)
        
        if not festival_context:
            return None
        
        greetings = festival_context.get("greetings", {})
        return greetings.get(language, greetings.get("en"))
    
    def generate_contextual_insight(
        self,
        product_category: str,
        customer_language: str = "en",
        purchase_date: Optional[datetime] = None
    ) -> str:
        """
        Generate contextual insight for empathy agent.
        
        Args:
            product_category: Product category
            customer_language: Customer's preferred language
            purchase_date: Date of purchase
            
        Returns:
            Contextual insight string
        """
        insights = []
        
        # Festival relevance
        festival_relevance = self.is_product_festival_relevant(product_category, purchase_date)
        if festival_relevance["is_festival_relevant"]:
            insights.append(f"🎉 FESTIVAL CONTEXT: {festival_relevance['context']}")
            insights.append(f"   Festival: {festival_relevance['festival']}")
            insights.append(f"   Significance: {festival_relevance['significance']}")
            
            # Add greeting suggestion
            greeting = self.get_festival_greeting(customer_language, purchase_date)
            if greeting:
                insights.append(f"   Suggested Greeting: {greeting}")
            
            # Add timing context
            timing = festival_relevance.get("festival_timing", {})
            if timing.get("is_before"):
                insights.append("   Timing: Pre-festival purchase (customer preparing)")
            elif timing.get("is_during"):
                insights.append("   Timing: Festival day purchase (urgent/important)")
            elif timing.get("is_after"):
                insights.append("   Timing: Post-festival purchase (possible issue needs special care)")
        
        # Seasonal context
        seasonal_context = self.get_seasonal_context(purchase_date)
        if seasonal_context["season"] != "general":
            insights.append(f"🌤️ SEASONAL CONTEXT: {seasonal_context['season'].title()} season")
            insights.append(f"   Tone: {seasonal_context['messaging_tone']}")
        
        return "\n".join(insights) if insights else "No special contextual factors detected"


# Factory function
def create_festival_context_manager() -> FestivalContextManager:
    """Create a FestivalContextManager instance."""
    return FestivalContextManager()
