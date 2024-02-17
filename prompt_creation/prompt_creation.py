import linking_prompt as lp


class PromptCreation:
    schema_details = None
    foreign_keys = None
    primary_keys = None

    def __init__(self, schema_details, foreign_keys, primary_keys):
        self.schema_details = schema_details
        self.foreign_keys = foreign_keys
        self.primary_keys = primary_keys

    def hard_prompt_maker(self, test_sample_text, database, schema_links, sub_questions):
        instruction = "# Use the intermediate representation and the schema links to generate the SQL queries for each of the questions.\n"
        fields = self.find_fields_mysql_like("college_2")
        fields += "Foreign_keys = " + self.find_foreign_keys_mysql_like("college_2") + '\n'
        fields += self.find_fields_mysql_like(database)
        fields += "Foreign_keys = " + self.find_foreign_keys_mysql_like(database) + '\n'
        stepping = f'''\nA: Let's think step by step. "{test_sample_text}" can be solved by knowing the answer to the following sub-question "{sub_questions}".'''
        fields += "\n"
        prompt = instruction + fields + lp.hard_prompt + 'Q: "' + test_sample_text + '"' + '\nschema_links: ' + schema_links + stepping + '\nThe SQL query for the sub-question"'
        return prompt

    def medium_prompt_maker(self, test_sample_text, database, schema_links):
        instruction = "# Use the the schema links and Intermediate_representation to generate the SQL queries for each of the questions.\n"
        fields = self.find_fields_mysql_like("college_2")
        fields += "Foreign_keys = " + self.find_foreign_keys_mysql_like("college_2") + '\n'
        fields += self.find_fields_mysql_like(database)
        fields += "Foreign_keys = " + self.find_foreign_keys_mysql_like(database) + '\n'
        fields += "\n"
        prompt = instruction + fields + lp.medium_prompt + 'Q: "' + test_sample_text + '\nSchema_links: ' + schema_links + '\nA: Let’s think step by step.'
        return prompt

    def easy_prompt_maker(self, test_sample_text, database, schema_links):
        instruction = "# Use the the schema links to generate the SQL queries for each of the questions.\n"
        fields = self.find_fields_mysql_like("college_2")
        fields += self.find_fields_mysql_like(database)
        fields += "\n"
        prompt = instruction + fields + lp.easy_prompt + 'Q: "' + test_sample_text + '\nSchema_links: ' + schema_links + '\nSQL:'
        return prompt

    def classification_prompt_maker(self, test_sample_text, database, schema_links):
        instruction = "# For the given question, classify it as EASY, NON-NESTED, or NESTED based on nested queries and JOIN.\n"
        instruction += "\nif need nested queries: predict NESTED\n"
        instruction += "elif need JOIN and don't need nested queries: predict NON-NESTED\n"
        instruction += "elif don't need JOIN and don't need nested queries: predict EASY\n\n"
        fields = self.find_fields_mysql_like("college_2")
        fields += "Foreign_keys = " + self.find_foreign_keys_mysql_like("college_2") + '\n'
        fields += self.find_fields_mysql_like(database)
        fields += "Foreign_keys = " + self.find_foreign_keys_mysql_like(database) + '\n'
        fields += "\n"
        prompt = instruction + fields + lp.classification_prompt + 'Q: "' + test_sample_text + '\nschema_links: ' + schema_links + '\nA: Let’s think step by step.'
        return prompt

    def schema_linking_prompt_maker(self, test_sample_text, database):
        instruction = "# Find the schema_links for generating SQL queries for each question based on the database schema and Foreign keys.\n"
        fields = self.find_fields_mysql_like(database)
        foreign_keys = "Foreign_keys = " + self.find_foreign_keys_mysql_like(database) + '\n'
        prompt = instruction + lp.schema_linking_prompt + fields + foreign_keys + 'Q: "' + test_sample_text + """"\nA: Let’s think step by step."""
        return prompt

    def find_foreign_keys_mysql_like(self, db_name):
        df = self.foreign_keys[self.foreign_keys['Database name'] == db_name]
        output = "["
        for index, row in df.iterrows():
            output += row['First Table Name'] + '.' + row['First Table Foreign Key'] + " = " + row[
                'Second Table Name'] + '.' + row['Second Table Foreign Key'] + ','
        output = output[:-1] + "]"
        return output

    def find_fields_mysql_like(self, db_name):
        df = self.schema_details[self.schema_details['Database name'] == db_name]
        df = df.groupby(' Table Name')
        output = ""
        for name, group in df:
            output += "Table " + name + ', columns = ['
            for index, row in group.iterrows():
                output += row[" Field Name"] + ','
            output = output[:-1]
            output += "]\n"
        return output

    def find_primary_keys_mysql_like(self, db_name):
        df = self.primary_keys[self.primary_keys['Database name'] == db_name]
        output = "["
        for index, row in df.iterrows():
            output += row['Table Name'] + '.' + row['Primary Key'] + ','
        output = output[:-1]
        output += "]\n"
        return output

    def debugger_prompt(self, test_sample_text, database, sql):
        instruction = """#### For the given question, use the provided tables, columns, foreign keys, and primary keys to fix the given SQLite SQL QUERY for any issues. If there are any problems, fix them. If there are no issues, return the SQLite SQL QUERY as is.
    #### Use the following instructions for fixing the SQL QUERY:
    1) Use the database values that are explicitly mentioned in the question.
    2) Pay attention to the columns that are used for the JOIN by using the Foreign_keys.
    3) Use DESC and DISTINCT when needed.
    4) Pay attention to the columns that are used for the GROUP BY statement.
    5) Pay attention to the columns that are used for the SELECT statement.
    6) Only change the GROUP BY clause when necessary (Avoid redundant columns in GROUP BY).
    7) Use GROUP BY on one column only.
    8) Use Nested Queries only when required. If the nested query can be replaced with simple SQL commands, then use them.
    9) Make sure there is a space before and after the conditional symbols like !=, =, <>, >, <
    
    The output should always be a SQL query without any explanation or reasoning for the correction.
    """
        fields = self.find_fields_mysql_like(database)
        fields += "Foreign_keys = " + self.find_foreign_keys_mysql_like(database) + '\n'
        fields += "Primary_keys = " + self.find_primary_keys_mysql_like(database)
        prompt = instruction + fields + '#### Question: ' + test_sample_text + '\n#### SQLite SQL QUERY\n' + sql + '\n#### SQLite FIXED SQL QUERY\n'
        return prompt
