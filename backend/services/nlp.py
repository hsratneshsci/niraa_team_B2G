import re
from google import genai
import os

# Configure Gemini if key is provided (simulating secure env var usage or passing directly for simplicity)
API_KEY = "AIzaSyDL4ezhQ1WHB9FvpMC0CetECVdCUKoVyig" # Provided in prompt.
client = genai.Client(api_key=API_KEY)
MODEL_ID = 'gemini-1.5-flash'

def extract_amount(text):
    """
    Extracts income amount from text, prioritizing currency contexts.
    """
    if not text: return 0.0
    text = text.lower()
    
    # Pattern 1: "500 rupees", "rs 500", "₹500"
    match = re.search(r'(?:rs\.?|rupees|₹)\s*(\d+(?:,\d+)*(?:\.\d+)?)', text)
    if match: return float(match.group(1).replace(',', ''))
    
    match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:rs\.?|rupees|₹)', text)
    if match: return float(match.group(1).replace(',', ''))
    
    # Pattern 2: "earned 500", "made 500"
    match = re.search(r'(?:earned|made|got|income)\s*(\d+(?:,\d+)*(?:\.\d+)?)', text)
    if match: return float(match.group(1).replace(',', ''))

    # Fallback: Find the largest number in the text (heuristic)
    numbers = re.findall(r'(\d+(?:,\d+)*(?:\.\d+)?)', text)
    if numbers:
        valid_nums = [float(n.replace(',', '')) for n in numbers]
        return max(valid_nums) # Assume the income is likely the main/largest number
        
    return 0.0

def process_chat_gemini(text):
    """
    Uses Gemini if available, otherwise seamlessly switches to 'Fake AI' mode.
    """
    try:
        # Try real AI first
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=f"""
            Role: Helpful assistant for Indian gig workers.
            User: "{text}"
            Format:
            Skills: [List]
            Reply: [Short friendly reply]
            """
        )
        content = response.text.strip()
        skills = []
        reply = "I didn't catch that."
        
        lines = content.split('\n')
        for line in lines:
            if line.startswith("Skills:"):
                s_str = line.replace("Skills:", "").strip()
                if s_str and s_str.lower() != "none":
                    skills = [s.strip() for s in s_str.split(',')]
            elif line.startswith("Reply:"):
                reply = line.replace("Reply:", "").strip()
        return skills, reply

    except Exception:
        # Silent Failover to "Fake AI"
        return process_fake_ai(text)

def process_fake_ai(text):
    """
    Simulates AI processing with advanced pattern matching.
    """
    text_lower = text.lower()
    skills = extract_skills_local(text)
    
    # 1. Direct Keyword Responses (Priority)
    responses = {
        ('hi', 'hello', 'hey', 'start', 'greetings', 'namaste', 'vanakkam'): "Hello! Tell me about your work. For example: 'I drive a taxi' or 'I work in a shop'.",
        ('student', 'college', 'study', 'university', 'exam'): "Balancing work and studies is impressive! Flexible gigs like delivery or data entry are great options.",
        ('drive', 'driver', 'car', 'auto', 'taxi', 'cab', 'bus', 'truck', 'lorry', 'ambulance'): "Driving is a vital service! Stay safe on the roads. I've added driving to your skills.",
        ('cook', 'chef', 'food', 'kitchen', 'baker', 'bakery', 'mess', 'canteen'): "Cooking is a true skill! Hotels and cloud kitchens are always hiring talented staff.",
        ('delivery', 'courier', 'zomato', 'swiggy', 'amazon', 'logistics', 'parcel', 'porter', 'dunzo'): "Delivery partners are the backbone of the city. Your time management skills are valuable!",
        ('clean', 'maid', 'house keeping', 'sweeper', 'garbage', 'mop', 'broom', 'wash'): "Housekeeping is essential work. Your dedication to keeping things clean is highly valued.",
        ('security', 'guard', 'watchman', 'bouncer', 'atm', 'gate'): "Security work requires great responsibility. Your vigilance is a key asset.",
        ('sales', 'sell', 'shop', 'market', 'retail', 'promo', 'counter', 'store', 'showroom'): "Sales roles are rewarding! Your ability to communicate and convince people is a superpower.",
        ('data', 'entry', 'computer', 'type', 'excel', 'office', 'admin', 'clerk'): "Computer skills like data entry are in high demand for office roles.",
        ('teach', 'tution', 'class', 'teacher', 'coach', 'trainer'): "Teaching is noble work! Sharing knowledge is one of the best ways to contribute.",
        ('lift', 'load', 'labor', 'helper', 'construction', 'site', 'brick', 'cement', 'coolie'): "Manual labor requires strength and stamina. Your hard work builds our cities!",
        ('repair', 'mechanic', 'fix', 'technician', 'ac', 'fridge', 'tv', 'mobile', 'laptop'): "Technical repair skills are always in demand. You are a problem solver!",
        ('beauty', 'salon', 'hair', 'makeup', 'parlour', 'barber', 'spa', 'massage'): "The beauty industry is booming. Your skills help people feel confident!",
        ('tailor', 'stitch', 'sew', 'fashion', 'boutique', 'embroidery', 'weaver', 'textile'): "Tailoring requires precision and creativity. People always need good custom clothing.",
        ('paint', 'painter', 'wall', 'decor', 'whitewash', 'polish'): "Painting makes spaces beautiful. Your attention to detail is your strength.",
        ('garden', 'mali', 'plant', 'nursery', 'farm', 'agriculture', 'field'): "Working with nature is rewarding. Your efforts keep our environment green and productive.",
        ('child', 'baby', 'sitter', 'nanny', 'care', 'elder', 'patient', 'nurse', 'ward boy'): "Caregiving requires patience and love. It is a very responsible and trusted job.",
        ('warehouse', 'stock', 'store', 'inventory', 'godown', 'packer', 'picker'): "Warehousing keeps the supply chain moving. Organization is your key skill.",
        ('waiter', 'server', 'hotel', 'hospitality', 'restaurant', 'steward', 'catering'): "Hospitality is all about service. Your friendly attitude makes guests happy.",
        ('electric', 'wire', 'plumber', 'pipe', 'fitter', 'welder', 'carpenter', 'wood'): "Skilled trades are the foundation of infrastructure. Reliable technicians are always needed.",
        ('money', 'cash', 'earn', 'salary', 'pay', 'income', 'wage'): "Everyone works for a better future. I can help you find gigs to increase your earnings.",
        ('help', 'job', 'work', 'need', 'search', 'find', 'vancy'): "I'm here to help! Tell me what you are good at, and I'll find matching jobs.",
        ('photo', 'video', 'camera', 'edit', 'shoot', 'wedding'): "Creative skills like photography are in high demand for events and marketing.",
        ('event', 'dj', 'decorate', 'party', 'marriage', 'function'): "Event management is exciting! Your ability to organize and execute is key.",
        ('gym', 'yoga', 'fitness', 'train', 'sport'): "Helping others stay fit is a great service. Health is wealth!",
        ('dog', 'pet', 'animal', 'walk', 'groom'): "Working with animals requires a kind heart. Pet care is a growing field.",
        ('laundry', 'iron', 'press', 'wash', 'dry clean', 'dhobi'): "Laundry services are essential for busy professionals. Your work ensures people look their best.",
        ('waste', 'scrap', 'recycle', 'raddi', 'junk'): "Recycling and waste management are critical for a sustainable future.",
        ('property', 'broker', 'real estate', 'agent', 'rent', 'sell'): "Real estate requires strong networking and negotiation skills.",
        ('print', 'xerox', 'dtp', 'design', 'scan', 'copy'): "Printing and DTP services support businesses every day. Precision is key.",
        ('office boy', 'peon', 'tea', 'file', 'messenger'): "Office support staff keep workplaces running smoothly. Your role is important!"
    }

    reply = ""
    for keywords, response in responses.items():
        if any(k in text_lower for k in keywords):
            reply = response
            break
            
    # 2. Dynamic Skill-Based Reply (Secondary)
    if not reply and skills:
        top_skills = ", ".join(skills[:3])
        reply = f"That's great! having skills in {top_skills} opens up many opportunities for you."
        
    # 3. Generic Fallback
    if not reply:
        reply = "I understand. Could you give me more details about your daily tasks?"

    return list(set(skills)), reply

def extract_skills_local(text):
    """
    Enhanced keyword mapping for skills.
    """
    skills = []
    text_lower = text.lower()
    
    keywords = {
        'Driving': ['drive', 'car', 'taxi', 'auto', 'bike', 'uber', 'ola'],
        'Navigation': ['route', 'map', 'gps', 'area', 'location'],
        'Cooking': ['cook', 'chef', 'food', 'kitchen', 'hotel', 'restaurant', 'dish'],
        'Food Safety': ['hygiene', 'clean setup', 'wash'],
        'Logistics': ['deliver', 'package', 'courier', 'zomato', 'swiggy', 'amazon', 'flipkart'],
        'Sales': ['sell', 'sales', 'customer', 'market', 'pitch'],
        'Communication': ['speak', 'english', 'hindi', 'talk', 'call'],
        'Manual Labor': ['lift', 'load', 'heavy', 'construction', 'labour', 'helper'],
        'Cleaning': ['clean', 'sweep', 'mop', 'house', 'maid'],
        'Data Entry': ['type', 'computer', 'excel', 'data', 'office'],
        'Security': ['guard', 'watchman', 'security', 'gate', 'bouncer'],
        'Teaching': ['teach', 'tution', 'class', 'student', 'teacher'],
        'Construction': ['lift', 'load', 'heavy', 'construction', 'labour', 'helper', 'site', 'brick'],
        'Repair': ['mechanic', 'fix', 'technician', 'ac', 'fridge', 'electric', 'wire', 'plumber', 'pipe'],
        'Beauty': ['beauty', 'salon', 'hair', 'makeup', 'parlour', 'style'],
        'Tailoring': ['tailor', 'stitch', 'sew', 'fashion', 'boutique', 'cloth'],
        'Painting': ['paint', 'wall', 'decor', 'color'],
        'Gardening': ['garden', 'mali', 'plant', 'nursery', 'grass'],
        'Caregiving': ['child', 'baby', 'sitter', 'nanny', 'care', 'nurse'],
        'Warehousing': ['warehouse', 'stock', 'store', 'inventory', 'pack', 'godown', 'picker'],
        'Hospitality': ['waiter', 'server', 'hotel', 'reception', 'guest', 'steward', 'catering'],
        'Creative': ['photo', 'video', 'camera', 'edit', 'shoot', 'wedding', 'dj', 'decorate', 'party', 'marriage'],
        'Healthcare': ['nurse', 'ward boy', 'patient', 'pharmacy', 'medicine', 'doctor', 'hospital'],
        'Fitness': ['gym', 'yoga', 'fitness', 'train', 'sport', 'exercise'],
        'Pet Care': ['dog', 'pet', 'animal', 'walk', 'groom', 'vet'],
        'Laundry': ['laundry', 'iron', 'press', 'wash', 'dry clean', 'dhobi'],
        'Real Estate': ['property', 'broker', 'real estate', 'agent', 'rent', 'flat', 'land'],
        'Office Support': ['office boy', 'peon', 'tea', 'file', 'messenger', 'xerox', 'print', 'scan', 'copy']
    }
    
    for skill, keys in keywords.items():
        if any(k in text_lower for k in keys):
            skills.append(skill)
            
    return list(set(skills))

def recommend_jobs(skills):
    """
    Simple mapping based on skills to jobs.
    """
    recommendations = []
    # Flatten skills to lowercase string for easier matching
    skill_text = " ".join([s.lower() for s in skills])
    
    added_roles = set()

    def add_job(role, salary):
        if role not in added_roles:
            recommendations.append({"role": role, "salary": salary})
            added_roles.add(role)

    # Driving / Logistics
    if any(k in skill_text for k in ['driv', 'navig', 'delivery', 'cycle', 'bike', 'logistics', 'traffic']):
        add_job("Delivery Partner (Zomato/Swiggy)", "₹18,000 – ₹25,000")
        add_job("Porter / Courier", "₹15,000 – ₹22,000")
        if 'car' in skill_text or 'taxi' in skill_text or 'cab' in skill_text or 'driving' in skill_text:
            add_job("Cab Driver (Uber/Ola)", "₹25,000 – ₹35,000")

    # Food / Hospitality
    if any(k in skill_text for k in ['cook', 'chef', 'food', 'kitchen', 'hotel', 'restaurant']):
        add_job("Cloud Kitchen Chef", "₹18,000 – ₹28,000")
        add_job("Restaurant Assistant", "₹12,000 – ₹18,000")

    # Sales / Retail
    if any(k in skill_text for k in ['sales', 'customer', 'shop', 'retail', 'speak', 'comm']):
        add_job("Retail Sales Executive", "₹15,000 – ₹22,000")
        add_job("Customer Support (Voice)", "₹18,000 – ₹24,000")

    # Manual / Construction
    if any(k in skill_text for k in ['labor', 'lift', 'construct', 'paint', 'repair', 'electric']):
        add_job("Construction Site Supervisor", "₹20,000 – ₹30,000")
        add_job("Skilled Technician (Urban Company)", "₹25,000 – ₹40,000")
        
    # Office / Data
    if any(k in skill_text for k in ['data', 'computer', 'type', 'excel', 'office']):
        add_job("Data Entry Operator", "₹12,000 - ₹18,000")
        add_job("Back Office Executive", "₹15,000 - ₹20,000")

    # Creative / Events
    if any(k in skill_text for k in ['photo', 'video', 'creative', 'design', 'edit', 'event', 'dj', 'decor']):
        add_job("Event Photographer/Videographer", "₹20,000 – ₹50,000 per event")
        add_job("Freelance Video Editor", "₹15,000 – ₹40,000")
        add_job("Event Decorator Assistant", "₹15,000 - ₹25,000")

    # Healthcare / Caregiving
    if any(k in skill_text for k in ['nurse', 'patient', 'care', 'medicine', 'pharmacy', 'ward', 'baby', 'child']):
        add_job("Home Care Nurse", "₹18,000 – ₹30,000")
        add_job("Pharmacy Assistant", "₹12,000 – ₹18,000")
        add_job("Nanny / Babysitter", "₹15,000 – ₹25,000")

    # Trades (Electrician, Plumber, Painter, AC)
    if any(k in skill_text for k in ['electric', 'wire', 'plumber', 'pipe', 'ac', 'repair', 'mechanic', 'fix', 'paint']):
        add_job("Urban Company Partner (Technician)", "₹25,000 – ₹45,000")
        add_job("AC/Fridge Repair Technician", "₹20,000 – ₹35,000")
        add_job("Painter / Polisher", "₹18,000 – ₹30,000")

    # Beauty / Salon
    if any(k in skill_text for k in ['beauty', 'hair', 'makeup', 'salon', 'parlour']):
        add_job("Salon Stylist / Beautician", "₹18,000 – ₹35,000")
        add_job("Bridal Makeup Artist", "₹20,000 – ₹60,000")

    # Security
    if any(k in skill_text for k in ['guard', 'security', 'watchman', 'bouncer']):
        add_job("Security Guard (Apartment/Office)", "₹15,000 – ₹22,000")
        add_job("Personal Security / Bouncer", "₹25,000 – ₹40,000")

    # Teaching / Education
    if any(k in skill_text for k in ['teach', 'tutor', 'class', 'student']):
        add_job("Home Tutor (Part-time)", "₹10,000 – ₹25,000")
        add_job("Coaching Center Assistant", "₹12,000 – ₹18,000")

    # Fitness
    if any(k in skill_text for k in ['gym', 'yoga', 'fit', 'train']):
        add_job("Gym Trainer", "₹15,000 – ₹30,000")
        add_job("Yoga Instructor", "₹20,000 – ₹40,000")

    # Hospitality
    if any(k in skill_text for k in ['waiter', 'hotel', 'serve', 'guest', 'steward']):
        add_job("Hotel Steward / Waiter", "₹15,000 – ₹20,000 + Tips")
        add_job("Guest Relations Executive", "₹18,000 – ₹25,000")
        
    # Tailoring
    if any(k in skill_text for k in ['tailor', 'sew', 'stitch', 'fashion']):
        add_job("Boutique Tailor", "₹15,000 – ₹30,000")
        add_job("Alteration Specialist", "Per Piece Basis")

    # Gardening
    if any(k in skill_text for k in ['garden', 'plant', 'mali']):
        add_job("Landscape Gardener", "₹15,000 – ₹25,000")

    # Logistics / Warehouse
    if any(k in skill_text for k in ['warehous', 'stock', 'inventory', 'pack']):
        add_job("Warehouse Assistant", "₹12,000 - ₹18,000")
        add_job("Inventory Clerk", "₹14,000 - ₹20,000")
        
    # Real Estate
    if any(k in skill_text for k in ['property', 'broker', 'estate']):
        add_job("Real Estate Field Agent", "Commission Based")

    if not recommendations:
        add_job("Warehouse Assistant", "₹12,000 – ₹18,000")
        add_job("General Office Helper", "₹10,000 – ₹15,000")
        
    return recommendations
