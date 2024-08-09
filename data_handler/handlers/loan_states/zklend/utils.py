import pandas as pd
from db.crud import ZkLendDBConnector
from db.models import ZkLendCollateralDebt
from decimal import Decimal


class ZkLendInitializer:
    """
    A class that initializes the zkLend loan states.
    To have actual collateral_enabled values.
    """
    FIRST_INDEX_ELEMENTS = (
        "Repayment",
        "zklend::market::Market::Repayment",
        "Liquidation",
        "zklend::market::Market::Liquidation",
    )

    def __init__(self, zklend_state: "ZkLendState"):
        self.db_connector = ZkLendDBConnector()
        self.zklend_state = zklend_state

    @staticmethod
    def _select_element(row: pd.Series) -> str:
        """
        Selects the element from the given row.
        :param row: Series row.
        :return: str
        """
        if row["key_name"] in "CollateralEnabled":
            return row["data"][0]
        else:
            return row["data"][1]

    def get_user_ids_from_df(self, df: pd.DataFrame) -> list[str]:
        """
        Extracts the user ids from the given DataFrame.

        :param df: The DataFrame to extract the user ids from.
        :return: The list of user ids.
        """
        return df.apply(self._select_element, axis=1).to_list()

    def set_last_loan_states_per_users(self, users_ids: list[str]) -> None:
        """
        Sets the last loan states for the given users.

        :param users_ids: The list of user ids to set the loan states for.
        :param zklend_state: The zkLend state object.
        """
        loan_states = self.db_connector.get_by_user_ids(users_ids)
        for loan_state in loan_states:
            self._set_loan_state_per_user(loan_state)

    def _set_loan_state_per_user(self, loan_state: ZkLendCollateralDebt) -> None:
        """
        Sets the loan state for a user.

        :param loan_state: The loan state data.
        """
        user_loan_state = self.zklend_state.loan_entities[loan_state.user_id]
        user_loan_state.collateral_enabled.values = loan_state.collateral_enabled
        user_loan_state.collateral.values = self._convert_float_to_decimal(
            loan_state.collateral
        )
        user_loan_state.debt.values = self._convert_float_to_decimal(loan_state.debt)

    @staticmethod
    def _convert_float_to_decimal(data: dict | None) -> dict | None:
        """
        Convert float values to Decimal for a given dictionary.
        :param data: The dictionary to convert.
        :return: The converted dictionary or None
        """
        if data:
            return {k: Decimal(v) for k, v in data.items()}

        return None
