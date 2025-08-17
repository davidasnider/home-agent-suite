"""
Sample conversation data for testing.

Provides realistic conversation examples for testing
chat functionality, export features, and UI rendering.
"""

from datetime import datetime, timedelta

# Base timestamp for consistent test data
BASE_TIME = datetime(2025, 8, 17, 10, 0, 0)


def create_timestamp(minutes_offset=0):
    """Create ISO timestamp with offset from base time."""
    return (BASE_TIME + timedelta(minutes=minutes_offset)).isoformat() + "Z"


WEATHER_CONVERSATION = [
    {
        "role": "assistant",
        "content": (
            "👋 Hello! I'm your intelligent Home Agent Suite assistant. "
            "I can help you with weather forecasts, activity planning, "
            "research, and general questions!"
        ),
        "timestamp": create_timestamp(0),
        "agent": "supervisor",
    },
    {
        "role": "user",
        "content": "What's the weather like today in New York?",
        "timestamp": create_timestamp(1),
        "agent": "user",
    },
    {
        "role": "assistant",
        "content": (
            "🌤️ **Today's Weather in New York, NY:**\n\n"
            "**Morning (6 AM - 12 PM):**\n"
            "- Temperature: 72-78°F\n"
            "- Conditions: Partly cloudy\n"
            "- Excellent time for outdoor activities!\n\n"
            "**Afternoon (12 PM - 6 PM):**\n"
            "- Temperature: 78-82°F\n"
            "- Conditions: Sunny\n"
            "- Perfect for picnics or outdoor sports\n\n"
            "**Evening (6 PM - 12 AM):**\n"
            "- Temperature: 74-76°F\n"
            "- Conditions: Clear skies\n"
            "- Great for evening walks or outdoor dining"
        ),
        "timestamp": create_timestamp(2),
        "agent": "day_planner",
    },
    {
        "role": "user",
        "content": "What outdoor activities do you recommend for this afternoon?",
        "timestamp": create_timestamp(3),
        "agent": "user",
    },
    {
        "role": "assistant",
        "content": (
            "🌞 **Perfect Afternoon Activities for NYC (78-82°F, Sunny):**\n\n"
            "**Highly Recommended:**\n"
            "• 🏃‍♀️ Central Park jogging or cycling\n"
            "• 🧺 Picnic in Bryant Park or Washington Square\n"
            "• ⚽ Outdoor sports (tennis, basketball, frisbee)\n"
            "• 🚶‍♀️ Walking tours (High Line, Brooklyn Bridge)\n\n"
            "**Also Great:**\n"
            "• 🛥️ Ferry ride to Staten Island\n"
            "• 🎨 Outdoor art markets\n"
            "• ☕ Sidewalk café dining\n\n"
            "The sunny conditions and comfortable temperature make "
            "this ideal weather for any outdoor activity!"
        ),
        "timestamp": create_timestamp(4),
        "agent": "day_planner",
    },
]

SEARCH_CONVERSATION = [
    {
        "role": "assistant",
        "content": "Hello! How can I help you today?",
        "timestamp": create_timestamp(0),
        "agent": "supervisor",
    },
    {
        "role": "user",
        "content": "Can you tell me about the latest developments in AI?",
        "timestamp": create_timestamp(1),
        "agent": "user",
    },
    {
        "role": "assistant",
        "content": (
            "🔍 **Latest AI Developments (2025):**\n\n"
            "**Recent Breakthroughs:**\n"
            "• Advanced multimodal AI systems combining text, images, and audio\n"
            "• Improved reasoning capabilities in large language models\n"
            "• Enhanced AI safety and alignment research\n\n"
            "**Industry Trends:**\n"
            "• Increased focus on AI efficiency and smaller models\n"
            "• Growing adoption in healthcare and scientific research\n"
            "• Expanded AI regulation and governance frameworks\n\n"
            "**Key Areas of Progress:**\n"
            "• Natural language understanding\n"
            "• Computer vision and robotics integration\n"
            "• AI-assisted software development\n\n"
            "Would you like me to elaborate on any specific area?"
        ),
        "timestamp": create_timestamp(2),
        "agent": "google_search",
    },
]

ERROR_CONVERSATION = [
    {
        "role": "assistant",
        "content": "Hello! I'm here to help.",
        "timestamp": create_timestamp(0),
        "agent": "supervisor",
    },
    {
        "role": "user",
        "content": "What's the weather like?",
        "timestamp": create_timestamp(1),
        "agent": "user",
    },
    {
        "role": "assistant",
        "content": (
            "❌ Sorry, I encountered an error while processing your request: "
            "Weather service temporarily unavailable. Please try again in a moment."
        ),
        "timestamp": create_timestamp(2),
        "agent": "supervisor",
    },
    {
        "role": "user",
        "content": "Can you try again?",
        "timestamp": create_timestamp(5),
        "agent": "user",
    },
    {
        "role": "assistant",
        "content": (
            "🌤️ **Current Weather Update:**\n\n"
            "The weather service is now responding! Today looks partly cloudy "
            "with temperatures in the mid-70s. Perfect for outdoor activities!"
        ),
        "timestamp": create_timestamp(6),
        "agent": "day_planner",
    },
]

DEMO_MODE_CONVERSATION = [
    {
        "role": "assistant",
        "content": "🎭 Demo Mode: Welcome to the chatbot demo!",
        "timestamp": create_timestamp(0),
        "agent": "demo",
    },
    {
        "role": "user",
        "content": "Hello, how are you?",
        "timestamp": create_timestamp(1),
        "agent": "user",
    },
    {
        "role": "assistant",
        "content": (
            "🤖 Demo Agent Response: I received your message 'Hello, how are you?'. "
            "This is a demonstration of the chat interface. Real agent integration "
            "requires proper API keys and configuration."
        ),
        "timestamp": create_timestamp(2),
        "agent": "demo",
    },
]

# Test data for various scenarios
CONVERSATIONS = {
    "weather": WEATHER_CONVERSATION,
    "search": SEARCH_CONVERSATION,
    "error": ERROR_CONVERSATION,
    "demo": DEMO_MODE_CONVERSATION,
}

# Export data structures for testing
EXPORT_TEST_DATA = {
    "conversation_id": "chat_1629123456",
    "export_timestamp": create_timestamp(10),
    "message_count": len(WEATHER_CONVERSATION),
    "messages": WEATHER_CONVERSATION,
}

# Long conversation for pagination/performance testing
LONG_CONVERSATION = []
for i in range(50):
    LONG_CONVERSATION.extend(
        [
            {
                "role": "user",
                "content": f"User message {i+1}",
                "timestamp": create_timestamp(i * 2),
                "agent": "user",
            },
            {
                "role": "assistant",
                "content": f"Assistant response {i+1}",
                "timestamp": create_timestamp(i * 2 + 1),
                "agent": "supervisor",
            },
        ]
    )
