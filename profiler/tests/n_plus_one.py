from django.test import TestCase 
from ..services import detect_n_plus_one, normalize_sql



class NormalizeSQLTests(TestCase):

    def test_strips_numbers(self):
        sql_query = "SELECT * FROM users WHERE id = 433"
        self.assertEqual(
            normalize_sql(sql_query),
            "select * from users where id = ?"
        )
    
    def test_strips_string(self):
        sql_query = "SELECT * FROM users WHERE name = 'Ahmed'"

        self.assertEqual(
            normalize_sql(sql_query),
            "select * from users where name = ?"
        )
    
    def test_collapses_whitespace(self):

        sql_query = "SELECT    * from    users"

        self.assertEqual(
            normalize_sql(sql_query),
            "select * from users"
        )


class DetectNPlusOneTests(TestCase):

    def test_detects_repeated_queries(self):
        queries = [
            {"sql": "SELECT * FROM users WHERE id = 1", "time_ms": 1},
            {"sql": "SELECT * FROM users WHERE id = 2", "time_ms": 1},
            {"sql": "SELECT * FROM users WHERE id = 3", "time_ms": 1},
        ]
        results = detect_n_plus_one(queries)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["count"], 3)

    def test_no_false_positive_on_unique_queries(self):
        queries = [
            {"sql": "SELECT * FROM users", "time_ms": 1},
            {"sql": "SELECT * FROM posts", "time_ms": 1},
        ]
        results = detect_n_plus_one(queries)
        self.assertEqual(results, [])