import json
import firebase_admin
from firebase_admin import credentials, firestore

# Note: You need to download the service account key from Firebase Console
# and save it as 'serviceAccountKey.json' in this folder.
# For now, I'll assume the environment is already authenticated via the MCP tools
# but for a standalone migration script, we need the SDK.

def migrate():
    with open('book_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Initialize Firestore (assuming local auth or ADC)
    try:
        firebase_admin.initialize_app()
    except ValueError:
        pass # Already initialized
        
    db = firestore.client()
    
    print(f"🚀 Migrating {len(data)} posts to Firestore...")
    for post in data:
        doc_id = str(post['day'])
        db.collection('posts').document(doc_id).set(post)
        print(f"✅ Migrated Day {doc_id}")
    
    print("✨ Migration Complete.")

if __name__ == "__main__":
    migrate()
