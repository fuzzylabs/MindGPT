from zenml.steps import step
import pandas as pd


def reformat(df: pd.DataFrame):
    sentences = []
    df['text_scraped'].map(lambda s: sentences.extend(s.split('.')))
    return pd.DataFrame({"sentences": sentences})


def remove_punctuation(data_string: str) -> str:
    punc_nospace = {"!", "?", ".", ",", "-", "–", "+", "=", "(", ")", ":", "'", ";", '"', "%", "&", "*", "_"}
    for p in punc_nospace:
        data_string = data_string.replace(p, "")

    punc_space = {"/"}
    for p in punc_space:
        data_string = data_string.replace(p, " ")

    return data_string


# @step
def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    data = data.dropna().copy()
    data = data.drop_duplicates()
    remove_new_line = lambda s: s.replace("\n", " ")
    lower_case = lambda s: s.lower()
    strip_string = lambda s: s.strip()
    remove_nbsp = lambda s: s.replace("\xa0", " ")
    data['text_scraped'] = data['text_scraped'].map(remove_new_line)
    data['text_scraped'] = data['text_scraped'].map(lower_case)
    data['text_scraped'] = data['text_scraped'].map(strip_string)
    data['text_scraped'] = data['text_scraped'].map(remove_nbsp)

    data = reformat(data)

    # now text is split into sentences, remove punc
    data['sentences'] = data['sentences'].map(remove_punctuation)

    remove_double_spaces = lambda s: s.replace("  ", " ")
    data['sentences'] = data['sentences'].map(remove_double_spaces)

    data['sentences'] = data['sentences'].map(strip_string)

    # drop empty strings
    data = data.drop(data[data.sentences == ""].index)
    data = data.drop_duplicates()
    return data
