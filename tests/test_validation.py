import json
import pytest

from src.manager import Manager
from src.models import Parameters


def _manager_with_transfers(tmp_path, amounts, min_transfer_pln=100.0, max_transfer_pln=5000.0) -> Manager:
    transfers = [
        {"amount_pln": amount, "date": "2025-01-10", "settlement_year": 2025, "settlement_month": 1, "tenant": "tenant-1"}
        for amount in amounts
    ]
    transfers_file = tmp_path / "transfers.json"
    transfers_file.write_text(json.dumps(transfers))
    return Manager(
        Parameters(transfers_json_path=str(transfers_file)),
        min_transfer_pln=min_transfer_pln,
        max_transfer_pln=max_transfer_pln
    )


def test_transfers_and_refunds_within_limits_are_accepted(tmp_path):
    manager = _manager_with_transfers(tmp_path, [100.0, 2500.0, 5000.0, -3000.0])
    assert manager.get_invalid_transfers() == []

    manager = _manager_with_transfers(tmp_path, [2500.0, -2500.0], min_transfer_pln=2500.0, max_transfer_pln=2500.0)
    assert manager.get_invalid_transfers() == []


def test_transfers_and_refunds_outside_limits_are_reported(tmp_path):
    manager = _manager_with_transfers(tmp_path, [50.0, 2500.0, 6000.0, -3000.0, -6000.0])
    invalid_amounts = sorted(transfer.amount_pln for transfer in manager.get_invalid_transfers())
    
    assert invalid_amounts == [-6000.0, 50.0, 6000.0]
    assert len(manager.transfers) == 5  


def test_minimum_greater_than_maximum_is_rejected():
    with pytest.raises(ValueError):
        Manager(Parameters(), min_transfer_pln=5000.0, max_transfer_pln=100.0)
