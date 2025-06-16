"""
Unit tests for calculator.py core functions
"""
import pytest

from calculator import (
    calculate_next_version,
    calculate_operation,
    get_config_data,
    get_operation_data,
)


class TestCalculateOperation:
    """Test the calculate_operation function"""

    def test_add_operation(self):
        """Test addition operation"""
        result = calculate_operation("add", [1.0, 2.0, 3.0])
        assert result == 6
        assert isinstance(result, int)

    def test_subtract_operation(self):
        """Test subtraction operation"""
        result = calculate_operation("subtract", [10.0, 3.0, 2.0])
        assert result == 5

    def test_multiply_operation(self):
        """Test multiplication operation"""
        result = calculate_operation("multiply", [2.0, 3.0, 4.0])
        assert result == 24

    def test_divide_operation(self):
        """Test division operation"""
        result = calculate_operation("divide", [100.0, 5.0, 2.0])
        assert result == 10

    def test_power_operation(self):
        """Test power operation"""
        result = calculate_operation("power", [2.0, 3.0])
        assert result == 8

    def test_modulo_operation(self):
        """Test modulo operation"""
        result = calculate_operation("modulo", [10.0, 3.0])
        assert result == 1

    def test_float_to_int_conversion(self):
        """Test that whole number floats are converted to integers"""
        result = calculate_operation("add", [1.0, 2.0])
        assert isinstance(result, int)
        assert result == 3

    def test_float_preservation(self):
        """Test that non-whole floats are preserved"""
        result = calculate_operation("divide", [10.0, 3.0])
        assert isinstance(result, float)
        assert abs(result - 3.333333333333333) < 1e-10

    def test_invalid_method(self):
        """Test invalid operation method"""
        with pytest.raises(ValueError, match="Invalid method"):
            calculate_operation("invalid", [1.0, 2.0])

    def test_insufficient_args_subtract(self):
        """Test subtraction with insufficient arguments"""
        with pytest.raises(ValueError, match="requires at least 2 arguments"):
            calculate_operation("subtract", [1.0])

    def test_insufficient_args_divide(self):
        """Test division with insufficient arguments"""
        with pytest.raises(ValueError, match="requires at least 2 arguments"):
            calculate_operation("divide", [1.0])

    def test_power_wrong_args(self):
        """Test power operation with wrong number of arguments"""
        with pytest.raises(ValueError, match="requires exactly 2 arguments"):
            calculate_operation("power", [2.0, 3.0, 4.0])

    def test_modulo_wrong_args(self):
        """Test modulo operation with wrong number of arguments"""
        with pytest.raises(ValueError, match="requires exactly 2 arguments"):
            calculate_operation("modulo", [10.0])

    def test_division_by_zero(self):
        """Test division by zero"""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            calculate_operation("divide", [10.0, 0.0])

    def test_modulo_by_zero(self):
        """Test modulo by zero"""
        with pytest.raises(ValueError, match="Cannot modulo by zero"):
            calculate_operation("modulo", [10.0, 0.0])

    def test_edge_cases(self):
        """Test edge cases"""
        # Large numbers
        result = calculate_operation("multiply", [1000000.0, 1000000.0])
        assert result == 1000000000000

        # Negative numbers
        result = calculate_operation("add", [-5.0, 3.0])
        assert result == -2

        # Zero handling
        result = calculate_operation("multiply", [5.0, 0.0])
        assert result == 0


class TestGetConfigData:
    """Test the get_config_data function"""

    def test_get_config_structure(self):
        """Test that get_config returns valid structure"""
        config = get_config_data()

        assert config["name"] == "CalculatorServer"
        assert config["version"] == "1.0.0"
        assert "supported_operations" in config
        assert len(config["supported_operations"]) == 6
        assert "operations" in config

        # Check all required operations are present
        operations = [op["name"] for op in config["operations"]]
        expected_ops = ["add", "subtract", "multiply", "divide", "power", "modulo"]
        assert all(op in operations for op in expected_ops)

    def test_operation_details(self):
        """Test operation details in config"""
        config = get_config_data()
        add_op = next(op for op in config["operations"] if op["name"] == "add")

        assert add_op["description"] == "Addition operation"
        assert add_op["min_args"] == 2
        assert add_op["max_args"] is None
        assert "example" in add_op


class TestGetOperationData:
    """Test the get_operation_data function"""

    def test_get_operation_valid(self):
        """Test getting a valid operation"""
        operation = get_operation_data("add")

        assert operation["name"] == "add"
        assert operation["description"] == "Addition operation"
        assert operation["min_args"] == 2

    def test_get_operation_invalid(self):
        """Test getting an invalid operation"""
        result = get_operation_data("invalid")

        assert "error" in result
        assert result["error"] == "Operation not found"

    def test_all_operations_accessible(self):
        """Test that all operations can be retrieved"""
        config = get_config_data()
        for op_name in config["supported_operations"]:
            operation = get_operation_data(op_name)
            assert "error" not in operation
            assert operation["name"] == op_name


class TestCalculateNextVersion:
    """Test the calculate_next_version function"""

    def test_next_version_increment(self):
        """Test version increment"""
        result = calculate_next_version("1.0.0")
        assert result == "1.1.0"

        result = calculate_next_version("2.5.0")
        assert result == "2.6.0"

    def test_next_version_edge_cases(self):
        """Test version increment edge cases"""
        result = calculate_next_version("0.0.0")
        assert result == "0.1.0"

        result = calculate_next_version("10.99.0")
        assert result == "10.100.0"


class TestIntegration:
    """Integration tests combining multiple functions"""

    def test_all_supported_operations_work(self):
        """Test that all supported operations actually work"""
        config = get_config_data()

        test_cases = {
            "add": ([2.0, 3.0], 5),
            "subtract": ([10.0, 3.0], 7),
            "multiply": ([3.0, 4.0], 12),
            "divide": ([20.0, 4.0], 5),
            "power": ([2.0, 3.0], 8),
            "modulo": ([10.0, 3.0], 1)
        }

        for op_name in config["supported_operations"]:
            if op_name in test_cases:
                args, expected = test_cases[op_name]
                result = calculate_operation(op_name, args)
                assert result == expected, f"Operation {op_name} failed"

    def test_operation_metadata_consistency(self):
        """Test that operation metadata is consistent with actual behavior"""
        config = get_config_data()

        for operation in config["operations"]:
            op_name = operation["name"]
            min_args = operation["min_args"]
            max_args = operation["max_args"]

            # Test minimum arguments
            test_args = [1.0] * min_args
            if op_name not in ["power", "modulo"]:  # These have specific requirements
                try:
                    calculate_operation(op_name, test_args)
                except ValueError:
                    pytest.fail(f"Operation {op_name} failed with minimum args")

            # Test maximum arguments (if specified)
            if max_args is not None:
                test_args = [1.0] * (max_args + 1)
                with pytest.raises(ValueError):
                    calculate_operation(op_name, test_args)
