import os
import requests
from flask import Flask, render_template, request, session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'babatunde_secret_key'  # Needed for Search History
API_KEY = os.getenv('USDA_API_KEY')

BENEFIT_MAP = {
    # BRAIN, EYES, CIRCULATION, GUT (New additions)
    'Choline, total': '🧠 BRAIN: Supports neurotransmitter synthesis and memory.',
    'Vitamin B-12': '🧠 BRAIN: Protects nerve cells and supports mental clarity.',
    'Vitamin A, RAE': '👁️ EYES: Essential for night vision and corneal health.',
    'Lutein + zeaxanthin': '👁️ EYES: Filters blue light to protect the retina.',
    'Vitamin K (phylloquinone)': '🔄 CIRCULATION: Regulates blood clotting and artery health.',
    'Fiber, total dietary': '🦠 GUT: Prebiotic support for digestion and microbiome.',
    'Niacin': '🦠 STOMACH: Supports digestive enzymes and nerve function.',

    # EXISTING SYSTEMS
    'Potassium, K': '🫀 HEART: Regulates blood pressure and heart rhythm.',
    'Iron, Fe': '🩸 BLOOD: Essential for oxygen transport and fighting fatigue.',
    'Zinc, Zn': '🧪 DETOX: Supports liver enzymes for toxin removal.',
    'Magnesium, Mg': '⚖️ METABOLIC: Helps prevent kidney stones and regulates energy.',
    'Calcium, Ca': '🦷 TEETH: Strengthens enamel and jawbone density.',
    'Vitamin C, total ascorbic acid': '🫁 LUNGS: Reduces airway inflammation and boosts immunity.'
}


@app.route('/')
def index():
    if 'history' not in session:
        session['history'] = []
    return render_template('index.html', history=session['history'])


@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('food_item')

    # Save to history (Keep last 5)
    history = session.get('history', [])
    if query not in history:
        history.insert(0, query)
    session['history'] = history[:5]
    session.modified = True

    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={API_KEY}&query={query}"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get('foods'):
            food = data['foods'][0]
            nutrients = food.get('foodNutrients', [])
            found_benefits = []
            for n in nutrients:
                name = n['nutrientName']
                if name in BENEFIT_MAP:
                    found_benefits.append(
                        {'chemical': name, 'amount': f"{n['value']} {n['unitName']}", 'benefit': BENEFIT_MAP[name]})
            return render_template('result.html', food_name=food['description'], benefits=found_benefits)
        return render_template('result.html', food_name=query, benefits=None)
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    app.run(debug=True)
