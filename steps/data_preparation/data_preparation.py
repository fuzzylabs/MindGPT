from zenml.steps import step
import pandas as pd



def case_normalize_data(data: pd.DataFrame) -> pd.DataFrame:
    ...


def lemmatise_data(data: pd.DataFrame) -> pd.DataFrame:
    ...


def remove_punctuation_and_special_characters(data: pd.DataFrame) -> pd.DataFrame:
    ...


def remove_duplicates(data: pd.DataFrame) -> pd.DataFrame:
    ...


@step
def load_data(data_path) -> pd.DataFrame:
    ...

@step
def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    ...


@step
def validate_data(data: pd.DataFrame) -> pd.DataFrame:
    ...


@step
def version_data(data: pd.DataFrame) -> pd.DataFrame:
    ...

