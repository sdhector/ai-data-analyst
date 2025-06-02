import unittest
import pandas as pd
import numpy as np
import json
import sys

# Adjust sys.path to allow importing from the 'core' directory
sys.path.insert(0, '.') 
sys.path.insert(0, '../..') 

from core.function_registry import visualization_functions
# Import data_analysis_functions to patch its _current_dataset
from core.function_registry import data_analysis_functions 

class TestVisualizationFunctions(unittest.TestCase):

    def test_bar_chart_json_serialization(self):
        """
        Tests that the chart_config from create_bar_chart can be JSON serialized,
        which implies that numpy arrays have been converted to lists.
        """
        original_dataset = None
        # Check if _current_dataset attribute exists in data_analysis_functions
        if hasattr(data_analysis_functions, '_current_dataset'):
            original_dataset = data_analysis_functions._current_dataset

        # Create a sample DataFrame with numpy arrays
        sample_data = {
            'category': np.array(['A', 'B', 'A', 'C', 'B']),
            'value': np.array([10, 20, 15, 5, 25], dtype=np.int64),
            'extra_numeric': np.array([1.1, 2.2, 3.3, 4.4, 5.5], dtype=np.float64) 
        }
        sample_df = pd.DataFrame(sample_data)
        
        # Patch _current_dataset in data_analysis_functions
        data_analysis_functions._current_dataset = sample_df

        try:
            chart_output = visualization_functions.create_bar_chart(
                container_id='test_bar_container',
                x_col='category',
                y_col='value',
                title='Test Bar Chart Serialization'
            )

            self.assertEqual(chart_output['status'], 'success', 
                             f"Chart creation failed: {chart_output.get('error')}")

            chart_config = chart_output['result']['chart_config']

            # Attempt to serialize the chart_config to JSON
            json_string = json.dumps(chart_config)
            
            self.assertTrue(True, "JSON serialization succeeded.")

        finally:
            # Clean up: Restore the original _current_dataset in data_analysis_functions
            data_analysis_functions._current_dataset = original_dataset

if __name__ == '__main__':
    unittest.main()
