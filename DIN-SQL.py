import pandas as pd
import time
import sys
from prompt_creation.prompt_creation import PromptCreation
from datetime import datetime
from models.gemini_model import GeminiModel
from models.gpt_model import GPTModel

if sys.argv[1] == "--dataset" and sys.argv[3] == "--output":
    dataset_schema = sys.argv[2] + "tables.json"
    dataset = sys.argv[2] + "dev_test.json"
    output_file = sys.argv[4]
    chosen_model = "gemini"  # default model
    if len(sys.argv) > 5 and sys.argv[5] == "--model":
        if len(sys.argv) == 7:
            if sys.argv[6] in ['gemini', 'gpt', 'gpt4', 'llama']:
                chosen_model = sys.argv[6]

else:
    raise Exception("Please use this format python CoT.py --dataset data/ --output predicted_sql.txt")


def load_data(input_dataset):
    return pd.read_json(input_dataset)


def creating_schema(dataset_json):
    schema_df = pd.read_json(dataset_json)
    schema_df = schema_df.drop(['column_names', 'table_names'], axis=1)
    schema = []
    f_keys = []
    p_keys = []
    for index, row in schema_df.iterrows():
        tables = row['table_names_original']
        col_names = row['column_names_original']
        col_types = row['column_types']
        foreign_keys = row['foreign_keys']
        primary_keys = row['primary_keys']
        for col, col_type in zip(col_names, col_types):
            index, col_name = col
            if index == -1:
                for table in tables:
                    schema.append([row['db_id'], table, '*', 'text'])
            else:
                schema.append([row['db_id'], tables[index], col_name, col_type])
        for primary_key in primary_keys:
            index, column = col_names[primary_key]
            p_keys.append([row['db_id'], tables[index], column])
        for foreign_key in foreign_keys:
            first, second = foreign_key
            first_index, first_column = col_names[first]
            second_index, second_column = col_names[second]
            f_keys.append([row['db_id'], tables[first_index], tables[second_index], first_column, second_column])

    schema_details = pd.DataFrame(schema, columns=['Database name', ' Table Name', ' Field Name', ' Type'])
    primary_key_details = pd.DataFrame(p_keys, columns=['Database name', 'Table Name', 'Primary Key'])
    foreign_key_details = pd.DataFrame(f_keys,
                                       columns=['Database name', 'First Table Name', 'Second Table Name',
                                                'First Table Foreign Key',
                                                'Second Table Foreign Key'])
    return schema_details, primary_key_details, foreign_key_details


def write_output_file(selected_model, result):
    if selected_model == "gemini":
        with open(output_file, 'w') as f:
            for line in result:
                f.write(f"{line}\n")

    elif selected_model == "gpt":
        with open("./data/gpt_predicted_sql.txt", 'w') as f:
            for line in result:
                f.write(f"{line}\n")

    elif selected_model == "gpt4":
        with open("./data/gpt4_predicted_sql.txt", 'w') as f:
            for line in result:
                f.write(f"{line}\n")


if __name__ == '__main__':
    spider_schema, spider_primary, spider_foreign = creating_schema(dataset_schema)

    data_df = load_data(dataset)
    print(f"Number of data samples {data_df.shape[0]}")
    generated_output = []

    print(f"Start Time ---> {datetime.utcnow()}")
    prompt_obj = PromptCreation(spider_schema, spider_foreign, spider_primary)

    if chosen_model == "gemini":
        model = GeminiModel()

    elif chosen_model == "gpt" or chosen_model == "gpt4":
        model = GPTModel(chosen_model)

    else:
        model = GeminiModel()

    for index, row in data_df.iterrows():
        print(f"index is {index}")
        schema_links = None
        while schema_links is None:
            try:
                if chosen_model == "gemini":
                    schema_links = model.gemini_response_generation(
                        prompt_obj.schema_linking_prompt_maker(row['question'],
                                                               row['db_id']))

                elif chosen_model == "gpt" or chosen_model == "gpt4":
                    schema_links = model.gpt_response_generation(
                        prompt_obj.schema_linking_prompt_maker(row['question'],
                                                               row['db_id']))

            except Exception as ex:
                time.sleep(3)
                pass
        try:
            schema_links = schema_links.split("Schema_links: ")[1]

        except Exception as ex:
            print("Slicing error for the schema_linking module")
            schema_links = "[]"

        classification = None
        while classification is None:
            try:
                if chosen_model == "gemini":
                    classification = model.gemini_response_generation(
                        prompt_obj.classification_prompt_maker(row['question'],
                                                               row['db_id'],
                                                               schema_links[1:]))

                elif chosen_model == "gpt" or chosen_model == "gpt4":
                    classification = model.gpt_response_generation(
                        prompt_obj.classification_prompt_maker(row['question'],
                                                               row['db_id'],
                                                               schema_links[1:]))
            except Exception as ex:
                time.sleep(3)
                pass
        try:
            predicted_class = classification.split("Label: ")[1]

        except Exception as ex:
            print("Slicing error for the classification module")
            predicted_class = '"NON-NESTED"'

        if '"EASY"' in predicted_class:
            SQL = None
            while SQL is None:
                try:
                    if chosen_model == "gemini":
                        SQL = model.gemini_response_generation(
                            prompt_obj.easy_prompt_maker(row['question'], row['db_id'],
                                                         schema_links))

                    elif chosen_model == "gpt" or chosen_model == "gpt4":
                        SQL = model.gpt_response_generation(
                            prompt_obj.easy_prompt_maker(row['question'], row['db_id'],
                                                         schema_links))
                except Exception as ex:
                    time.sleep(3)
                    pass

        elif '"NON-NESTED"' in predicted_class:
            SQL = None
            while SQL is None:
                try:
                    if chosen_model == "gemini":
                        SQL = model.gemini_response_generation(
                            prompt_obj.medium_prompt_maker(row['question'], row['db_id'],
                                                           schema_links))

                    elif chosen_model == "gpt" or chosen_model == "gpt4":
                        SQL = model.gpt_response_generation(
                            prompt_obj.medium_prompt_maker(row['question'], row['db_id'],
                                                           schema_links))

                except Exception as ex:
                    time.sleep(3)
                    pass

            try:
                if SQL.index("SQL: ") > -1:
                    SQL = SQL.split("SQL: ")[1]

            except Exception as ex:
                print("SQL slicing error")
                SQL = "SELECT"
        else:
            if len(classification.split('question = ["')) > 1 or len(classification.split('questions = ["')) > 1:
                if 'question = ["' in classification:
                    sub_questions = classification.split('question = ["')[1].split('"]')[0]

                elif 'questions = ["' in classification:
                    sub_questions = classification.split('questions = ["')[1].split('"]')[0]

                SQL = None
                while SQL is None:
                    try:
                        if chosen_model == "gemini":
                            SQL = model.gemini_response_generation(
                                prompt_obj.hard_prompt_maker(row['question'], row['db_id'],
                                                             schema_links,
                                                             sub_questions))

                        elif chosen_model == "gpt" or chosen_model == "gpt4":
                            SQL = model.gpt_response_generation(
                                prompt_obj.hard_prompt_maker(row['question'], row['db_id'],
                                                             schema_links,
                                                             sub_questions))
                    except Exception as ex:
                        time.sleep(3)
                        pass
            try:
                if SQL.index("SQL: ") > -1:
                    SQL = SQL.split("SQL: ")[1]

            except Exception as ex:
                print("SQL slicing error")
                SQL = "SELECT"

        debugged_SQL = None
        while debugged_SQL is None:
            try:
                if chosen_model == "gemini":
                    debugged_SQL = model.gemini_debugger_response_generation(
                        prompt_obj.debugger_prompt(row['question'], row['db_id'],
                                                   SQL)).replace("\n", " ")

                elif chosen_model == "gpt" or chosen_model == "gpt4":
                    time.sleep(60)
                    debugged_SQL = model.gpt_debug_response_generation(
                        prompt_obj.debugger_prompt(row['question'], row['db_id'],
                                                   SQL)).replace("\n", " ")

            except Exception as ex:
                time.sleep(3)
                pass

        SQL = "SELECT " + debugged_SQL
        generated_output.append([row['question'], SQL, row['query'], row['db_id']])
        print(f"Iteration {index} done")
    print(f"End Time ---> {datetime.utcnow()}")

    df = pd.DataFrame(generated_output, columns=['NLQ', 'PREDICTED SQL', 'GOLD SQL', 'DATABASE'])
    results = df['PREDICTED SQL'].tolist()

    write_output_file(chosen_model, results)
