from .db_initialize import db

collection_name = "mappings"
document_name = "categories-accounts"

def get_accounts_by_category(category_key):
    """
    Fetch all accounts associated with a given category key from the 'categories-accounts' document.
    """
    try:
        doc_ref = db.collection(collection_name).document(document_name)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            category_map = data.get("category-map", {})  # Fetch category-map field
            return category_map.get(category_key, [])
        else:
            print(f"No document found for {document_name}")
            return []
    
    except Exception as e:
        print(f"Error fetching category data: {e}")
        return []

def add_account_to_category(category_key, account_id):
    """
    Add an account to a given category key in the 'categories-accounts' document.
    """
    try:
        doc_ref = db.collection(collection_name).document(document_name)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            category_map = data.get("category-map", {})
            
            if category_key in category_map:
                if account_id not in category_map[category_key]:
                    category_map[category_key].append(account_id)
                else:
                    print(f"Account {account_id} already exists in category {category_key}")
            else:
                category_map[category_key] = [account_id]

            doc_ref.set({"category-map": category_map}, merge=True)
        
        else:
            doc_ref.set({"category-map": {category_key: [account_id]}})
        
        print(f"Added {account_id} to category {category_key}")
    
    except Exception as e:
        print(f"Error adding account to category: {e}")


def get_categories_by_account_key(account_key):
    doc_ref = db.collection(collection_name).document(document_name)
    doc = doc_ref.get()
    
    if doc.exists:
        data = doc.to_dict()
        category_map = data.get("category-map", {})
        
        matching_categories = []

        # Iterate through each category and check if the account_key exists
        for category, values in category_map.items():
            if isinstance(values, list):  # Ensure it's a list before searching
                if account_key in values:
                    matching_categories.append(category)  # Collect all matching categories

        return matching_categories if matching_categories else None
    else:
        return None
