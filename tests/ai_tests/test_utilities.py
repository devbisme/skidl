import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import tempfile
import shutil
import collections
import hashlib
import json
import re
from contextlib import contextmanager

# Add the src directory to the path so we can import skidl
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from skidl.utilities import (
    export_to_all, detect_os, Rgx, sgn, debug_trace, consistent_hash,
    num_to_chars, rmv_quotes, add_quotes, cnvt_to_var_name, to_list,
    list_or_scalar, flatten, set_attr, rmv_attr, add_unique_attr,
    from_iadd, set_iadd, rmv_iadd, merge_dicts, reset_get_unique_name,
    get_unique_name, fullmatch, filter_list, expand_indices, expand_buses,
    find_num_copies, norecurse, TriggerDict, is_binary_file, is_url,
    find_and_open_file, find_and_read_file, get_abs_filename, opened
)


class TestExportToAll:
    """Test cases for export_to_all decorator."""
    
    def test_export_to_all_adds_to_existing_all(self):
        """Test that export_to_all adds function to existing __all__ list."""
        # Create a mock module with existing __all__
        mock_module = Mock()
        mock_module.__all__ = ['existing_func']
        
        with patch('sys.modules', {'test_module': mock_module}):
            @export_to_all
            def test_func():
                pass
            test_func.__module__ = 'test_module'
            
            # Apply decorator
            decorated_func = export_to_all(test_func)
            
        assert 'test_func' in mock_module.__all__
        assert decorated_func == test_func

    def test_export_to_all_creates_new_all(self):
        """Test that export_to_all creates __all__ if it doesn't exist."""
        mock_module = Mock(spec=[])  # Module without __all__
        del mock_module.__all__  # Ensure __all__ doesn't exist
        
        with patch('sys.modules', {'test_module': mock_module}):
            @export_to_all
            def test_func():
                pass
            test_func.__module__ = 'test_module'
            
            decorated_func = export_to_all(test_func)
            
        assert hasattr(mock_module, '__all__')
        assert mock_module.__all__ == ['test_func']


class TestDetectOS:
    """Test cases for detect_os function."""
    
    @patch('platform.system', return_value='Windows')
    def test_detect_windows(self, mock_system):
        """Test detection of Windows OS."""
        assert detect_os() == 'Windows'
        
    @patch('platform.system', return_value='Linux')
    def test_detect_linux(self, mock_system):
        """Test detection of Linux OS."""
        assert detect_os() == 'Linux'
        
    @patch('platform.system', return_value='Darwin')
    def test_detect_macos(self, mock_system):
        """Test detection of MacOS."""
        assert detect_os() == 'MacOS'
        
    @patch('platform.system', return_value='Unknown')
    def test_detect_unknown_os(self, mock_system):
        """Test exception for unknown OS."""
        with pytest.raises(Exception, match="Unknown type of operating system!"):
            detect_os()


class TestRgx:
    """Test cases for Rgx class."""
    
    def test_rgx_creation(self):
        """Test creating Rgx instance."""
        pattern = r'\d+'
        rgx = Rgx(pattern)
        assert str(rgx) == pattern
        assert isinstance(rgx, str)
        assert isinstance(rgx, Rgx)


class TestSgn:
    """Test cases for sgn function."""
    
    @pytest.mark.parametrize("input_val,expected", [
        (5, 1),
        (-3, -1),
        (0, 0),
        (0.5, 1),
        (-0.1, -1),
        (0.0, 0)
    ])
    def test_sgn_values(self, input_val, expected):
        """Test sgn function with various values."""
        assert sgn(input_val) == expected


class TestDebugTrace:
    """Test cases for debug_trace decorator."""
    
    def test_debug_trace_with_flag(self, capsys):
        """Test debug_trace prints when debug_trace=True."""
        @debug_trace
        def test_function():
            return "result"
            
        result = test_function(debug_trace=True)
        captured = capsys.readouterr()
        
        assert result == "result"
        assert "Doing test_function ..." in captured.out
        
    def test_debug_trace_without_flag(self, capsys):
        """Test debug_trace doesn't print when debug_trace=False."""
        @debug_trace
        def test_function():
            return "result"
            
        result = test_function(debug_trace=False)
        captured = capsys.readouterr()
        
        assert result == "result"
        assert captured.out == ""


class TestConsistentHash:
    """Test cases for consistent_hash function."""
    
    def test_consistent_hash_same_input(self):
        """Test that same input produces same hash."""
        text = "test string"
        hash1 = consistent_hash(text)
        hash2 = consistent_hash(text)
        assert hash1 == hash2
        
    def test_consistent_hash_different_input(self):
        """Test that different inputs produce different hashes."""
        hash1 = consistent_hash("string1")
        hash2 = consistent_hash("string2")
        assert hash1 != hash2
        
    def test_consistent_hash_length(self):
        """Test that hash is 16 characters long."""
        result = consistent_hash("test")
        assert len(result) == 16
        
    def test_consistent_hash_hex_format(self):
        """Test that hash contains only hex characters."""
        result = consistent_hash("test")
        assert all(c in '0123456789abcdef' for c in result)


class TestNumToChars:
    """Test cases for num_to_chars function."""
    
    @pytest.mark.parametrize("num,expected", [
        (1, "A"),
        (2, "B"),
        (26, "Z"),
        (27, "AA"),
        (28, "AB"),
        (52, "AZ"),
        (53, "BA")
    ])
    def test_num_to_chars_conversion(self, num, expected):
        """Test conversion of numbers to spreadsheet column format."""
        assert num_to_chars(num) == expected


class TestRmvQuotes:
    """Test cases for rmv_quotes function."""
    
    def test_rmv_quotes_with_quotes(self):
        """Test removing quotes from quoted string."""
        assert rmv_quotes('"hello world"') == "hello world"
        assert rmv_quotes('  "test"  ') == "test"
        
    def test_rmv_quotes_without_quotes(self):
        """Test string without quotes remains unchanged."""
        assert rmv_quotes("hello") == "hello"
        
    def test_rmv_quotes_non_string(self):
        """Test non-string input returns unchanged."""
        assert rmv_quotes(123) == 123
        assert rmv_quotes(None) is None


class TestAddQuotes:
    """Test cases for add_quotes function."""
    
    def test_add_quotes_string(self):
        """Test adding quotes to string."""
        result = add_quotes("hello")
        assert result == '"hello"'
        
    def test_add_quotes_special_chars(self):
        """Test adding quotes to string with special characters."""
        result = add_quotes('hello "world"')
        assert '"' in result  # Should be properly escaped
        
    def test_add_quotes_non_string(self):
        """Test non-string input returns unchanged."""
        assert add_quotes(123) == 123
        assert add_quotes(None) is None


class TestCnvtToVarName:
    """Test cases for cnvt_to_var_name function."""
    
    @pytest.mark.parametrize("input_str,expected", [
        ("hello-world", "hello_world"),
        ("123abc", "_23abc"),
        ("valid_name", "valid_name"),
        ("with spaces", "with_spaces"),
        ("special!@#chars", "special___chars")
    ])
    def test_cnvt_to_var_name_conversion(self, input_str, expected):
        """Test conversion of strings to valid Python variable names."""
        assert cnvt_to_var_name(input_str) == expected


class TestToList:
    """Test cases for to_list function."""
    
    def test_to_list_scalar(self):
        """Test converting scalar to list."""
        assert to_list(5) == [5]
        assert to_list("hello") == ["hello"]
        
    def test_to_list_already_list(self):
        """Test that lists are returned unchanged."""
        original = [1, 2, 3]
        assert to_list(original) is original
        
    def test_to_list_tuple(self):
        """Test that tuples are returned unchanged."""
        original = (1, 2, 3)
        assert to_list(original) is original
        
    def test_to_list_set(self):
        """Test that sets are returned unchanged."""
        original = {1, 2, 3}
        assert to_list(original) is original


class TestListOrScalar:
    """Test cases for list_or_scalar function."""
    
    def test_list_or_scalar_multi_element(self):
        """Test multi-element list returns unchanged."""
        lst = [1, 2, 3]
        assert list_or_scalar(lst) == lst
        
    def test_list_or_scalar_single_element(self):
        """Test single-element list returns element."""
        assert list_or_scalar([5]) == 5
        
    def test_list_or_scalar_empty_list(self):
        """Test empty list returns None."""
        assert list_or_scalar([]) is None
        
    def test_list_or_scalar_scalar(self):
        """Test scalar returns unchanged."""
        assert list_or_scalar(42) == 42
        
    def test_list_or_scalar_tuple(self):
        """Test tuple behavior."""
        assert list_or_scalar((1, 2)) == (1, 2)
        assert list_or_scalar((1,)) == 1
        assert list_or_scalar(()) is None


class TestFlatten:
    """Test cases for flatten function."""
    
    def test_flatten_nested_list(self):
        """Test flattening nested lists."""
        nested = [1, [2, 3], [4, [5, 6]]]
        expected = [1, 2, 3, 4, 5, 6]
        assert flatten(nested) == expected
        
    def test_flatten_flat_list(self):
        """Test flattening already flat list."""
        flat = [1, 2, 3, 4]
        assert flatten(flat) == flat
        
    def test_flatten_with_tuples_and_sets(self):
        """Test flattening with mixed container types."""
        mixed = [1, (2, 3), {4, 5}]
        result = flatten(mixed)
        assert 1 in result
        assert 2 in result
        assert 3 in result
        assert 4 in result or 5 in result  # Sets are unordered


class TestSetAttr:
    """Test cases for set_attr function."""
    
    def test_set_attr_single_object(self):
        """Test setting attribute on single object."""
        obj = Mock()
        set_attr(obj, 'test_attr', 'value')
        assert obj.test_attr == 'value'
        
    def test_set_attr_multiple_objects(self):
        """Test setting attribute on multiple objects."""
        obj1, obj2 = Mock(), Mock()
        set_attr([obj1, obj2], 'test_attr', 'value')
        assert obj1.test_attr == 'value'
        assert obj2.test_attr == 'value'


class TestRmvAttr:
    """Test cases for rmv_attr function."""
    
    def test_rmv_attr_existing(self):
        """Test removing existing attribute."""
        obj = Mock()
        obj.test_attr = 'value'
        rmv_attr(obj, 'test_attr')
        assert not hasattr(obj, 'test_attr')
        
    def test_rmv_attr_non_existing(self):
        """Test removing non-existing attribute doesn't raise error."""
        obj = Mock()
        rmv_attr(obj, 'non_existing')  # Should not raise


class TestFromIadd:
    """Test cases for from_iadd function."""
    
    def test_from_iadd_true(self):
        """Test object with iadd_flag True."""
        obj = Mock()
        obj.iadd_flag = True
        assert from_iadd(obj) is True
        
    def test_from_iadd_false(self):
        """Test object with iadd_flag False."""
        obj = Mock()
        obj.iadd_flag = False
        assert from_iadd(obj) is False
        
    def test_from_iadd_no_flag(self):
        """Test object without iadd_flag."""
        obj = Mock()
        del obj.iadd_flag
        assert from_iadd(obj) is False
        
    def test_from_iadd_list(self):
        """Test list of objects."""
        obj1 = Mock()
        obj1.iadd_flag = False
        obj2 = Mock()
        obj2.iadd_flag = True
        assert from_iadd([obj1, obj2]) is True


class TestMergeDicts:
    """Test cases for merge_dicts function."""
    
    def test_merge_dicts_simple(self):
        """Test simple dictionary merge."""
        dict1 = {'a': 1, 'b': 2}
        dict2 = {'c': 3, 'd': 4}
        merge_dicts(dict1, dict2)
        expected = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        assert dict1 == expected
        
    def test_merge_dicts_nested(self):
        """Test nested dictionary merge."""
        dict1 = {'a': {'x': 1, 'y': 2}}
        dict2 = {'a': {'y': 3, 'z': 4}}
        merge_dicts(dict1, dict2)
        expected = {'a': {'x': 1, 'y': 3, 'z': 4}}
        assert dict1 == expected


class TestGetUniqueName:
    """Test cases for get_unique_name function."""
    
    def test_get_unique_name_first_call(self):
        """Test first call with empty list."""
        reset_get_unique_name()
        result = get_unique_name([], 'name', 'R')
        assert result == 'R1'
        
    def test_get_unique_name_with_conflicts(self):
        """Test name generation with conflicts."""
        reset_get_unique_name()
        obj1 = Mock()
        obj1.name = 'R1'
        obj2 = Mock()
        obj2.name = 'R2'
        
        result = get_unique_name([obj1, obj2], 'name', 'R')
        assert result == 'R3'
        
    def test_get_unique_name_with_initial(self):
        """Test with initial name provided."""
        reset_get_unique_name()
        result = get_unique_name([], 'name', 'R', initial='R5')
        assert result == 'R5'


class TestFullmatch:
    """Test cases for fullmatch function."""
    
    def test_fullmatch_success(self):
        """Test successful full match."""
        result = fullmatch(r'\d+', '123')
        assert result is not None
        
    def test_fullmatch_partial_fail(self):
        """Test partial match fails."""
        result = fullmatch(r'\d+', '123abc')
        assert result is None
        
    def test_fullmatch_no_match(self):
        """Test no match."""
        result = fullmatch(r'\d+', 'abc')
        assert result is None


class TestFilterList:
    """Test cases for filter_list function."""
    
    def test_filter_list_basic(self):
        """Test basic filtering."""
        obj1 = Mock()
        obj1.name = 'test1'
        obj1.type = 'A'
        
        obj2 = Mock()
        obj2.name = 'test2'
        obj2.type = 'B'
        
        result = filter_list([obj1, obj2], type='A')
        assert result == [obj1]
        
    def test_filter_list_regex(self):
        """Test filtering with regex."""
        obj1 = Mock()
        obj1.name = 'IO1'
        
        obj2 = Mock()
        obj2.name = 'PWR'
        
        result = filter_list([obj1, obj2], name=Rgx(r'IO\d+'))
        assert result == [obj1]


class TestExpandIndices:
    """Test cases for expand_indices function."""
    
    def test_expand_indices_integers(self):
        """Test expanding integer indices."""
        result = expand_indices(0, 10, False, 1, 2, 3)
        assert result == [1, 2, 3]
        
    def test_expand_indices_slice(self):
        """Test expanding slice indices."""
        result = expand_indices(0, 10, False, slice(1, 4))
        assert result == [1, 2, 3]
        
    def test_expand_indices_string(self):
        """Test expanding string indices."""
        result = expand_indices(0, 10, False, "A,B,C")
        assert result == ["A", "B", "C"]


class TestFindNumCopies:
    """Test cases for find_num_copies function."""
    
    def test_find_num_copies_scalars(self):
        """Test with all scalar values."""
        result = find_num_copies(a=1, b=2, c=3)
        assert result == 1
        
    def test_find_num_copies_lists(self):
        """Test with list values."""
        result = find_num_copies(a=[1, 2, 3], b=4)
        assert result == 3
        
    def test_find_num_copies_mismatched_error(self):
        """Test error with mismatched list lengths."""
        with pytest.raises(ValueError, match="Mismatched lengths"):
            find_num_copies(a=[1, 2], b=[1, 2, 3])


class TestNorecurse:
    """Test cases for norecurse decorator."""
    
    def test_norecurse_prevents_recursion(self):
        """Test that norecurse prevents recursive calls."""
        call_count = 0
        
        @norecurse
        def recursive_func(n):
            nonlocal call_count
            call_count += 1
            if n > 0:
                return recursive_func(n - 1)
            return n
            
        result = recursive_func(5)
        assert call_count == 1  # Should only call once
        assert result is None


class TestTriggerDict:
    """Test cases for TriggerDict class."""
    
    def test_trigger_dict_basic(self):
        """Test basic TriggerDict functionality."""
        trigger_called = False
        
        def trigger_func(d, key, value):
            nonlocal trigger_called
            trigger_called = True
            
        d = TriggerDict()
        d.trigger_funcs['test'] = trigger_func
        d['test'] = 'value'
        
        assert trigger_called is True
        
    def test_trigger_dict_no_change(self):
        """Test trigger not called when value doesn't change."""
        trigger_called = False
        
        def trigger_func(d, key, value):
            nonlocal trigger_called
            trigger_called = True
            
        d = TriggerDict({'test': 'value'})
        d.trigger_funcs['test'] = trigger_func
        d['test'] = 'value'  # Same value
        
        assert trigger_called is False


class TestIsBinaryFile:
    """Test cases for is_binary_file function."""
    
    def test_is_binary_file_text(self):
        """Test with text file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('Hello, world!')
            f.flush()
            result = is_binary_file(f.name)
            
        os.unlink(f.name)
        assert result is False
        
    def test_is_binary_file_nonexistent(self):
        """Test with non-existent file."""
        result = is_binary_file('nonexistent_file.txt')
        assert result is False


class TestIsUrl:
    """Test cases for is_url function."""
    
    @pytest.mark.parametrize("url,expected", [
        ("http://example.com", True),
        ("https://example.com", True),
        ("ftp://example.com", False),
        ("file.txt", False),
        ("/path/to/file", False)
    ])
    def test_is_url_detection(self, url, expected):
        """Test URL detection."""
        assert is_url(url) == expected


class TestFindAndOpenFile:
    """Test cases for find_and_open_file function."""
    
    def test_find_and_open_file_existing(self):
        """Test finding and opening existing file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('test content')
            f.flush()
            
            fp, filename = find_and_open_file(f.name)
            content = fp.read()
            fp.close()
            
        os.unlink(f.name)
        assert content == 'test content'
        assert filename == f.name
        
    def test_find_and_open_file_not_found(self):
        """Test file not found raises exception."""
        with pytest.raises(FileNotFoundError):
            find_and_open_file('nonexistent_file.txt')
            
    def test_find_and_open_file_allow_failure(self):
        """Test file not found with allow_failure=True."""
        fp, filename = find_and_open_file('nonexistent_file.txt', allow_failure=True)
        assert fp is None
        assert filename is None


class TestOpened:
    """Test cases for opened context manager."""
    
    def test_opened_with_filename(self):
        """Test opened context manager with filename."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('test content')
            f.flush()
            
            with opened(f.name, 'r') as file_obj:
                content = file_obj.read()
                
        os.unlink(f.name)
        assert content == 'test content'
        
    def test_opened_with_file_object(self):
        """Test opened context manager with file object."""
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt') as f:
            f.write('test content')
            f.seek(0)
            
            with opened(f, 'r') as file_obj:
                content = file_obj.read()
                
        assert content == 'test content'
        
    def test_opened_invalid_type(self):
        """Test opened with invalid type raises error."""
        with pytest.raises(TypeError):
            with opened(123, 'r') as f:
                pass


if __name__ == '__main__':
    pytest.main([__file__])
