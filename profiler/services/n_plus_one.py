from collections import Counter
import re

def normalize_sql(sql: str) -> str:
    
    sql = re.sub(r'\b\d+\b', '?', sql)
    
    sql = re.sub(r"'[^']*'", '?', sql)
    
    sql = ' '.join(sql.split())
    
    return sql.strip().lower()




def detect_n_plus_one(queries: list[dict]) -> list[dict]:
    
    normalized = [normalize_sql(q["sql"]) for q in queries]
    counts = Counter(normalized)
    
    duplicates = []
    for pattern, count in counts.items():
        if count >= 3:  
            duplicates.append({
                "query_pattern": pattern,
                "count": count,
            })
    
    return duplicates