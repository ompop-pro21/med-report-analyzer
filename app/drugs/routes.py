from flask import Blueprint, render_template, request
import requests
from .utils import get_drug_info_from_ai

drugs_bp = Blueprint('drugs', __name__)

@drugs_bp.route('/search', methods=['GET', 'POST'])
def search():
    results = None
    error = None
    
    if request.method == 'POST':
        query = request.form.get('drug_name')
        if query:
            # Step 1: Use AI to normalize the drug name (e.g., Paracetamol -> Acetaminophen)
            ai_info = get_drug_info_from_ai(query)
            
            search_term = query
            if ai_info:
                # Prefer the generic name for FDA search as it's more reliable
                search_term = ai_info.get('generic_name', query)
            
            # Step 2: OpenFDA API Call
            url = "https://api.fda.gov/drug/label.json"
            # Try searching by generic name first, then brand name
            params = {
                'search': f'openfda.generic_name:"{search_term}"',
                'limit': 1
            }
            
            try:
                resp = requests.get(url, params=params)
                data = resp.json()
                
                # If generic search fails, try brand name from AI or original query
                if 'error' in data:
                     brand_search = ai_info.get('brand_name', query) if ai_info else query
                     params['search'] = f'openfda.brand_name:"{brand_search}"'
                     resp = requests.get(url, params=params)
                     data = resp.json()

                if 'results' in data:
                    res = data['results'][0]
                    results = {
                        'brand': res.get('openfda', {}).get('brand_name', [ai_info.get('brand_name', query) if ai_info else query])[0],
                        'generic': res.get('openfda', {}).get('generic_name', [ai_info.get('generic_name', '') if ai_info else ''])[0],
                        'purpose': res.get('purpose', [ai_info.get('description', 'N/A') if ai_info else 'N/A'])[0],
                        'warnings': res.get('warnings', ['No warnings found'])[0][:500] + "..." # Truncate long text
                    }
                else:
                    # Fallback to AI info if FDA fails entirely
                    if ai_info:
                         results = {
                            'brand': ai_info.get('brand_name'),
                            'generic': ai_info.get('generic_name'),
                            'purpose': ai_info.get('description'),
                            'warnings': "Detailed FDA warnings not found. Please consult a doctor."
                        }
                    else:
                        error = "Drug not found in FDA database."
            except Exception as e:
                error = "Connection to FDA service failed."
                
    return render_template('drugs/search.html', results=results, error=error)