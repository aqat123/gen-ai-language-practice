"""
Writing Prompts Service
Provides CEFR-leveled writing prompts for the writing module.
"""

from typing import List, Dict
import random


# Writing prompts organized by CEFR level
WRITING_PROMPTS = {
    "A1": [
        {
            "title": "My Daily Routine",
            "prompt": "Describe your typical day. What time do you wake up? What do you eat for breakfast? What do you do in the evening?",
            "keywords": ["wake up", "breakfast", "work", "evening", "sleep"]
        },
        {
            "title": "My Family",
            "prompt": "Write about your family. Who are the members of your family? What do they do? What do they look like?",
            "keywords": ["mother", "father", "brother", "sister", "family"]
        },
        {
            "title": "My Favorite Food",
            "prompt": "What is your favorite food? Describe it. Why do you like it? When do you usually eat it?",
            "keywords": ["food", "eat", "like", "delicious", "favorite"]
        },
        {
            "title": "My Home",
            "prompt": "Describe where you live. How many rooms does your home have? What is your favorite room? Why?",
            "keywords": ["house", "room", "live", "bedroom", "kitchen"]
        },
        {
            "title": "My Best Friend",
            "prompt": "Write about your best friend. What is their name? What do they look like? What do you do together?",
            "keywords": ["friend", "name", "together", "play", "like"]
        },
        {
            "title": "A Typical Weekend",
            "prompt": "What do you usually do on the weekend? Do you relax at home or go out? Who do you spend time with?",
            "keywords": ["weekend", "Saturday", "Sunday", "relax", "fun"]
        },
        {
            "title": "My Hobbies",
            "prompt": "What do you like to do in your free time? Do you have any hobbies? How often do you do them?",
            "keywords": ["hobby", "like", "free time", "play", "read"]
        },
        {
            "title": "Going Shopping",
            "prompt": "Describe a typical shopping trip. What do you usually buy? Where do you go shopping? Who do you go with?",
            "keywords": ["shop", "buy", "store", "money", "clothes"]
        }
    ],
    "A2": [
        {
            "title": "A Memorable Trip",
            "prompt": "Write about a trip you took. Where did you go? What did you see? What was the most interesting thing you did?",
            "keywords": ["trip", "travel", "visit", "interesting", "remember"]
        },
        {
            "title": "My Hometown",
            "prompt": "Describe your hometown or city. What is it famous for? What do you like or dislike about it? Would you recommend it to visitors?",
            "keywords": ["hometown", "city", "famous", "like", "recommend"]
        },
        {
            "title": "Learning a Language",
            "prompt": "Why are you learning this language? What do you find easy or difficult? How do you practice?",
            "keywords": ["learn", "language", "difficult", "practice", "study"]
        },
        {
            "title": "A Special Celebration",
            "prompt": "Describe a celebration or festival in your country. When does it happen? What do people do? What is your favorite part?",
            "keywords": ["celebration", "festival", "tradition", "enjoy", "special"]
        },
        {
            "title": "My Job or Studies",
            "prompt": "Write about your work or studies. What do you do? What do you like about it? What are your goals for the future?",
            "keywords": ["work", "study", "job", "goal", "future"]
        },
        {
            "title": "Healthy Living",
            "prompt": "How do you stay healthy? Do you exercise? What kind of food do you eat? What could you improve?",
            "keywords": ["healthy", "exercise", "food", "sport", "improve"]
        },
        {
            "title": "Technology in My Life",
            "prompt": "How do you use technology every day? What apps or devices do you use most? Can you imagine life without them?",
            "keywords": ["technology", "phone", "computer", "internet", "use"]
        },
        {
            "title": "A Restaurant Experience",
            "prompt": "Describe a recent visit to a restaurant. What did you order? How was the food? Would you go back?",
            "keywords": ["restaurant", "food", "order", "delicious", "waiter"]
        }
    ],
    "B1": [
        {
            "title": "Environmental Concerns",
            "prompt": "What environmental issues concern you most? What can individuals do to help protect the environment? What changes have you made in your life?",
            "keywords": ["environment", "pollution", "recycle", "climate", "protect"]
        },
        {
            "title": "The Impact of Social Media",
            "prompt": "How has social media changed the way we communicate? What are the advantages and disadvantages? How do you use it?",
            "keywords": ["social media", "communication", "advantages", "disadvantages", "connect"]
        },
        {
            "title": "An Inspirational Person",
            "prompt": "Write about someone who has inspired you. Who are they? What have they achieved? Why do you admire them?",
            "keywords": ["inspire", "admire", "achieve", "influence", "respect"]
        },
        {
            "title": "Career Aspirations",
            "prompt": "What are your career goals? What steps are you taking to achieve them? What challenges might you face?",
            "keywords": ["career", "goals", "achieve", "challenge", "future"]
        },
        {
            "title": "Cultural Differences",
            "prompt": "Compare your culture with another culture you know. What are the main differences? What similarities surprised you?",
            "keywords": ["culture", "difference", "tradition", "compare", "custom"]
        },
        {
            "title": "A Book That Changed My Perspective",
            "prompt": "Write about a book that had a significant impact on you. What was it about? How did it change your thinking?",
            "keywords": ["book", "read", "impact", "perspective", "change"]
        },
        {
            "title": "The Benefits of Travel",
            "prompt": "Why is traveling important? What have you learned from your travel experiences? Where would you like to go next?",
            "keywords": ["travel", "experience", "learn", "culture", "adventure"]
        },
        {
            "title": "Work-Life Balance",
            "prompt": "How important is work-life balance? How do you manage your time between work and personal life? What could be improved?",
            "keywords": ["balance", "work", "life", "time", "manage"]
        }
    ],
    "B2": [
        {
            "title": "The Future of Education",
            "prompt": "How do you think education will change in the next 20 years? What role will technology play? What traditional methods should be preserved?",
            "keywords": ["education", "future", "technology", "traditional", "change"]
        },
        {
            "title": "Ethics of Artificial Intelligence",
            "prompt": "As AI becomes more prevalent, what ethical concerns should we address? How can we ensure AI benefits society? What regulations might be needed?",
            "keywords": ["artificial intelligence", "ethics", "society", "regulation", "benefit"]
        },
        {
            "title": "Urbanization and Quality of Life",
            "prompt": "Discuss the effects of urbanization on quality of life. What are the benefits of living in cities? What problems need to be solved?",
            "keywords": ["urbanization", "city", "quality", "problem", "solution"]
        },
        {
            "title": "The Power of Habit",
            "prompt": "How do habits shape our lives? Describe a habit you've successfully changed or developed. What strategies worked for you?",
            "keywords": ["habit", "change", "develop", "strategy", "routine"]
        },
        {
            "title": "Global Citizenship",
            "prompt": "What does it mean to be a global citizen? What responsibilities do we have to people in other countries? How can individuals make a difference?",
            "keywords": ["global", "citizen", "responsibility", "difference", "world"]
        },
        {
            "title": "The Influence of Advertising",
            "prompt": "Analyze how advertising influences consumer behavior. What techniques are most effective? Should there be more restrictions on advertising?",
            "keywords": ["advertising", "influence", "consumer", "marketing", "persuade"]
        },
        {
            "title": "Renewable Energy Transition",
            "prompt": "Discuss the challenges and opportunities of transitioning to renewable energy. What obstacles exist? What innovations give you hope?",
            "keywords": ["renewable", "energy", "transition", "challenge", "innovation"]
        },
        {
            "title": "Mental Health Awareness",
            "prompt": "Why has mental health become a more discussed topic? What can society do to better support mental health? How has your understanding evolved?",
            "keywords": ["mental health", "awareness", "support", "society", "wellbeing"]
        }
    ],
    "C1": [
        {
            "title": "The Paradox of Choice",
            "prompt": "In modern society, we have unprecedented choice in nearly every aspect of life. Analyze whether having more choices leads to greater satisfaction or increased anxiety. How do you navigate decision-making in your own life?",
            "keywords": ["choice", "paradox", "satisfaction", "anxiety", "decision"]
        },
        {
            "title": "Preserving Languages and Cultures",
            "prompt": "With globalization, many minority languages face extinction. Examine the tension between global communication and cultural preservation. What is lost when a language disappears? What solutions exist?",
            "keywords": ["language", "preservation", "globalization", "culture", "extinction"]
        },
        {
            "title": "The Philosophy of Success",
            "prompt": "Different cultures and individuals define success differently. Critically examine how society defines success and whether these definitions serve us well. How has your own definition evolved?",
            "keywords": ["success", "philosophy", "definition", "society", "achievement"]
        },
        {
            "title": "Privacy in the Digital Age",
            "prompt": "Analyze the tradeoffs between convenience and privacy in our digital lives. Are we too willing to surrender personal data? What are the long-term implications for society?",
            "keywords": ["privacy", "digital", "data", "surveillance", "security"]
        },
        {
            "title": "The Role of Failure in Innovation",
            "prompt": "Some argue that our educational and professional systems don't adequately value failure as a learning tool. Examine this claim. How might we better incorporate lessons from failure?",
            "keywords": ["failure", "innovation", "learning", "education", "risk"]
        },
        {
            "title": "Authenticity in Social Media",
            "prompt": "Discuss the tension between curated online personas and authentic self-expression. How does social media affect our sense of identity? Can we be truly authentic online?",
            "keywords": ["authenticity", "social media", "identity", "persona", "genuine"]
        }
    ],
    "C2": [
        {
            "title": "The Epistemology of Expertise",
            "prompt": "In an era of information abundance and widespread misinformation, how should we evaluate expertise and authority? Analyze the relationship between specialized knowledge, public trust, and democratic decision-making. What frameworks might help us navigate this complexity?",
            "keywords": ["epistemology", "expertise", "authority", "knowledge", "trust"]
        },
        {
            "title": "Consciousness and Artificial Intelligence",
            "prompt": "As AI systems become more sophisticated, questions about machine consciousness gain urgency. Examine the philosophical and practical implications of potentially conscious AI. What criteria would we use to recognize machine consciousness? What ethical obligations might we have?",
            "keywords": ["consciousness", "AI", "philosophy", "ethics", "sentience"]
        },
        {
            "title": "The Economics of Attention",
            "prompt": "Analyze how the commodification of attention has reshaped media, politics, and social interaction. What are the second and third-order effects of designing systems to maximize engagement? How might we create more sustainable attention economies?",
            "keywords": ["attention", "economics", "media", "engagement", "commodification"]
        },
        {
            "title": "Post-Scarcity Societies",
            "prompt": "Explore the philosophical and practical challenges of transitioning to post-scarcity economies. How might automation and abundance change human motivation, social structures, and meaning-making? What historical precedents inform this discussion?",
            "keywords": ["post-scarcity", "automation", "abundance", "society", "meaning"]
        }
    ]
}


def get_writing_prompt(level: str, exclude_recent: List[str] = None) -> Dict[str, str]:
    """
    Get a random writing prompt for the specified CEFR level.

    Args:
        level: CEFR level (A1, A2, B1, B2, C1, C2)
        exclude_recent: List of recently used prompt titles to avoid repetition

    Returns:
        Dictionary with title, prompt, and keywords
    """
    if level not in WRITING_PROMPTS:
        level = "A1"  # Default to A1 if invalid level

    prompts = WRITING_PROMPTS[level]

    # Filter out recently used prompts
    if exclude_recent:
        available_prompts = [p for p in prompts if p["title"] not in exclude_recent]
        if not available_prompts:
            available_prompts = prompts  # Reset if all have been used
    else:
        available_prompts = prompts

    return random.choice(available_prompts)


def get_all_prompts_for_level(level: str) -> List[Dict[str, str]]:
    """
    Get all writing prompts for a specific CEFR level.

    Args:
        level: CEFR level (A1, A2, B1, B2, C1, C2)

    Returns:
        List of prompt dictionaries
    """
    if level not in WRITING_PROMPTS:
        level = "A1"

    return WRITING_PROMPTS[level]


def get_prompt_count(level: str) -> int:
    """Get the number of prompts available for a level."""
    return len(WRITING_PROMPTS.get(level, []))
