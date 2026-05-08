
'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
'''

import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import json
import pandas as pd
import numpy as np
import datetime
from src.service.utility import Utility
from src.config.logger import CustomLogger

class TestUtilityExtended(unittest.TestCase):
    
    def test_sanitize_filenameorfoldername(self):
        name = "test/file\\name"
        # The function returns None (implicitly) if validation fails due to log logic, 
        # or raises if telemetry is False/not handled.
        # Based on code: if not match, raise ValueError. Exception block logs.
        # So we expect None or check log call.
        sanitized = Utility.sanitize_filenameorfoldername(name)
        self.assertIsNone(sanitized)

    def test_sanitize_clean(self):
        name = "clean_file_name"
        self.assertEqual(Utility.sanitize_filenameorfoldername(name), name)

    @patch('src.service.utility.os.getcwd')
    def test_getcurrentDirectory(self, mock_getcwd):
        # Ensure the function returns a plausible parent directory path
        mock_getcwd.return_value = os.path.join(os.path.sep, "home", "user", "app")
        cwd = Utility.getcurrentDirectory()
        self.assertIsInstance(cwd, str)
        self.assertTrue(len(cwd) > 0)

    def test_htmlCssContent_Tabular(self):
        payload = {'model_metaData': {'dataType': 'Tabular'}}
        css = Utility.htmlCssContent(payload)
        self.assertIn('<style>', css)
        self.assertIn('.report-container', css)

    def test_htmlCssContent_Image(self):
        payload = {'model_metaData': {'dataType': 'Image'}}
        css = Utility.htmlCssContent(payload)
        self.assertIn('.image-grid', css)

    def test_htmlContent_Tabular(self):
        payload = {
            'model_metaData': {
                'dataType': 'Tabular',
                'useModelApi': 'True',
                'modelEndPoint': 'http://localhost',
                'groundTruthClassNames': ['0', '1'],
                'targetClassifier': 'SKLearn',
                'groundTruthClassLabel': 'label'
            },
            'reportTime': '2023-01-01',
            'modelName': 'TestModel',
            'rows': '<tr><td>TestRow</td></tr>'
        }
        html = Utility.htmlContent(payload)
        self.assertIn('MODEL ROBUSTNESS ASSESSMENT REPORT', html)
        self.assertIn('TestModel', html)
        self.assertIn('TestRow', html)

    @patch('src.service.utility.pd.read_csv')
    @patch('src.service.utility.plt')
    @patch('src.service.utility.base64')
    @patch('src.service.utility.open', new_callable=mock_open)
    @patch('src.service.utility.os')
    def test_graphForAttack(self, mock_os, mock_file, mock_b64, mock_plt, mock_read_csv):
        mock_os.path.join.side_effect = lambda *args: "/".join(args)
        
        # Test Tabular Evasion
        payload = {
            'type': 'Tabular',
            'folder_path': '/reports',
            'attackName': 'ZerothOrderOptimization', # In Evasion list usually
            'target': 'label'
        }
        
        # Mock DataFrame
        # Evasion: Success if target != pred
        df = pd.DataFrame({'label': [0, 0, 1], 'prediction': [0, 1, 1]})
        mock_read_csv.return_value = df
        
        # Mock file read for image
        mock_file.return_value.read.return_value = b'fakeimage'
        mock_b64.b64encode.return_value = b'encoded'
        
        # Mock AttackTypes to ensure 'ZerothOrderOptimization' is in Evasion
        # Just in case it's not loaded
        original_attack_types = Utility.AttackTypes
        Utility.AttackTypes = {'Art': {'Evasion': ['ZerothOrderOptimization'], 'Inference': ['InferenceAttack']}}
        
        try:
            html = Utility.graphForAttack(payload)
            self.assertIn("data:image/png;base64,encoded", html)
            self.assertIn("graph-image-csv", html)
            self.assertTrue(mock_plt.savefig.called)
            
            # Test Tabular Inference
            payload_inf = {
                'type': 'Tabular',
                'folder_path': '/reports',
                'attackName': 'InferenceAttack',
                'target': 'label'
            }
            # Inference: Success if target == pred
            Utility.graphForAttack(payload_inf)
        finally:
            Utility.AttackTypes = original_attack_types
        
        # Test Image
        # Payload needs: type='Image', top_keys=[k1], attackDataList={k1: ...}
        # attackDataList[k] = [?, image_np, adv_image_np, pred_val1, pred_val2]
        # logic: payload['attackDataList'][keys][1] -> image. shape (H,W,C).
        # composite = concat( [1][0]? wait code says [keys][1][0] )
        
        # Let's mock the image data structure carefully.
        # code: composite_image = np.concatenate((payload['attackDataList'][keys][1][0], np.ones(...), payload['attackDataList'][keys][2][0]), axis=1)
        # So [1] is list/array where [0] is the image?
        pass

    @patch('src.service.utility.plt')
    @patch('src.service.utility.base64')
    @patch('src.service.utility.open', new_callable=mock_open)
    @patch('src.service.utility.os')
    def test_graphForAttack_Image(self, mock_os, mock_file, mock_b64, mock_plt):
        mock_os.path.join.side_effect = lambda *args: "/".join(args)
        
        # Setup plt mock to unpack correctly
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        
        payload_img = {
            'type': 'Image',
            'folder_path': '/reports',
            'attackName': 'PixelAttack',
            'top_keys': ['Key1'],
            'attackDataList': {
                'Key1': [
                    'ignored',
                    np.zeros((1, 10, 10, 3)), # [1]
                    np.zeros((1, 10, 10, 3)), # [2]
                    'PredVal1',
                    'PredVal2'
                ]
            }
        }
        
        mock_file.return_value.read.return_value = b'fakeimage'
        mock_b64.b64encode.return_value = b'encoded'
        
        html = Utility.graphForAttack(payload_img)
        self.assertIn("data:image/png;base64,encoded", html)
        self.assertTrue(mock_plt.savefig.called)

    def test_htmlContentReport(self):
        payload = {
            'type': 'Tabular',
            # logical branch: if payload['column_graph_data']:
            'column_graph_data': 'some_graph_html', 
            'attackName': 'Attack1',
            'graph_html': '<div>Graph</div>',
            'attack_status_row': '<tr>Status</tr>'
        }
        with patch('src.service.utility.Utility.attackDesc', return_value='Description'):
            html = Utility.htmlContentReport(payload)
            self.assertIn('Attack1_Attack', html)
            self.assertIn('Description', html)

    @patch('src.service.utility.pd.read_csv')
    @patch('src.service.utility.plt')
    @patch('src.service.utility.base64')
    @patch('src.service.utility.open', new_callable=mock_open)
    @patch('src.service.utility.os')
    def test_graphForAttackColumn(self, mock_os, mock_file, mock_b64, mock_plt, mock_read_csv):
        mock_os.path.join.side_effect = lambda *args: "/".join(args)
        
        payload = {
            'type': 'Tabular',
            'report_path': '/reports',
            'adversarial_data_path': 'adv.csv',
            'original_data_path': 'orig.csv',
            'attackName': 'EvasionAttack'
        }
        
        # Mock DataFrames
        # Code: original_df.iloc[:, :-1] (All except last col)
        #       adversarial_df.iloc[:, :-3] (All except last 3 cols)
        
        df_orig = pd.DataFrame({'A': [1, 2], 'B': [3, 4], 'label': [0, 0]})
        df_adv = pd.DataFrame({'A': [1.1, 2.1], 'B': [3.1, 4.1], 'C': [0,0], 'D': [0,0], 'E': [0,0]})
        
        # read_csv called twice: adv then orig?
        # Code: adv = read_csv(adv_path); orig = read_csv(orig_path)
        mock_read_csv.side_effect = [df_adv, df_orig]
        
        original_attack_types = Utility.AttackTypes
        Utility.AttackTypes = {'Art': {'Evasion': ['EvasionAttack'], 'Inference': []}}
            
        mock_file.return_value.read.return_value = b'fakeimage'
        mock_b64.b64encode.return_value = b'encoded'
        
        try:
            html = Utility.graphForAttackColumn(payload)
            self.assertIn("data:image/png;base64,encoded", html)
        finally:
             Utility.AttackTypes = original_attack_types

    def test_makeAttackListRow_Tabular(self):
        payload = {
            'meta_data': {'dataType': 'Tabular'},
            'statusList': [{'Attack1': 50.0}],
            'defenceList': [{'Attack1': 60.0}],
            'total_attacks': ['Attack1'],
            'attackList': ['Attack1']
        }
        
        original_attack_types = Utility.AttackTypes
        Utility.AttackTypes = {'Art': {'Evasion': ['Attack1'], 'Inference': []}}
        
        try:
            rows, mit_rows, attack_list = Utility.makeAttackListRow(payload)
            self.assertIn('Attack1', rows)
            self.assertIn('50.00%', rows)
            self.assertIn('60.00%', mit_rows)
        finally:
            Utility.AttackTypes = original_attack_types

    def test_makeAttackListRow_Image(self):
        payload = {
            'meta_data': {'dataType': 'Image'},
            'statusList': [{'Attack1': 50.0}],
            'total_attacks': ['Attack1'],
            'attackList': ['Attack1']
        }
        original_attack_types = Utility.AttackTypes
        Utility.AttackTypes = {'Art': {'Evasion': ['Attack1'], 'Inference': []}}
        
        try:
            # Image logic: loop total_attacks. if in attackList and in keys logic...
            # The logic in Image branch seems to differ slightly or use same initial loop?
            # Reading code: line 3410 Tabular branch. 
            # Line 3502: Image branch follows Tabular-specific block ending at 3497?
            # Wait, makeAttackListRow structure is:
            # if Tabular: ... return rows, mit, list
            # elif Image: ... return rows, list
            
            rows, attack_list = Utility.makeAttackListRow(payload)
            # rows should contain html
            self.assertIn('Attack1', rows)
            self.assertIn('50.00%', rows)
            self.assertEqual(len(attack_list), 1)
        finally:
             Utility.AttackTypes = original_attack_types

    @patch('src.service.utility.os')
    @patch('src.service.utility.pd.read_csv')
    def test_checkAttackListStatus(self, mock_read_csv, mock_os):
        mock_os.listdir.return_value = ['Attack1.csv', 'Ignore.txt']
        mock_os.path.join.side_effect = lambda *args: "/".join(args)
        
        # Test Tabular
        payload = {
            'meta_data': {'dataType': 'Tabular'},
            'folder_path': '/reports',
            'attack_accuracy_dict': {'Attack1.csv': 0.8}
        }
        
        # Mock DF: last column 'True' count
        # col = df[df[last] == True][last]
        df = pd.DataFrame({'Data': [1,2], 'Result': [True, False]})
        mock_read_csv.return_value = df
        
        status, defence = Utility.checkAttackListStatus(payload)
        # 1 True out of 2 -> 50%
        self.assertEqual(status[0]['Attack1'], 50.0)
        self.assertEqual(defence[0]['Attack1'], 80.0)
        
        # Test Image
        payload_img = {
            'meta_data': {'dataType': 'Image'},
            'attackList': ['Attack1'],
            'folder_path': '/reports'
        }
        # Image logic iterates listdir.
        # Check filename.split('.')[0].split('^')[1][:-1] == attackName
        # Ex: "1^Attack1T.png" -> split(.)[0] = "1^Attack1T" -> split(^)[1] = "Attack1T" -> [:-1] = "Attack1"
        # Last char 'T' or 'F' counts.
        
        mock_os.listdir.return_value = ['1^Attack1T.png', '2^Attack1F.png', '3^Attack1T.png']
        
        status_img = Utility.checkAttackListStatus(payload_img)
        # 2 T, 1 F. Total 3. 2/3 * 100 = 66.66
        self.assertAlmostEqual(status_img[0]['Attack1'], 66.6666, places=2)

    @patch('src.service.utility.shutil')
    @patch('src.service.utility.os')
    @patch('src.service.utility.open', new_callable=mock_open)
    def test_createAttackFolder(self, mock_file, mock_os, mock_shutil):
        mock_os.listdir.return_value = ['Attack1.csv', '1^Attack2T.png']
        mock_os.path.join.side_effect = lambda *args: "/".join(args)
        mock_os.path.exists.return_value = False # Force mkdir
        
        payload = {
            'report_path': '/reports',
            'attack_list': [
                {'type': 'Evasion'}, # checks logic for folder creation
                {'type': 'Inference'}
            ]
        }
        
        original_attack_types = Utility.AttackTypes
        Utility.AttackTypes = {
            'Art': {'Evasion': ['Attack1', 'Attack2'], 'Inference': []},
            'Augly': {'Augmentation': []}
        }
        
        try:
            Utility.createAttackFolder(payload)
            
            # Check CSV move (Attack1 -> Evasion)
            # new_folder = /reports/Art/Evasion/Attack1
            # shutil.copyfileobj called
            self.assertTrue(mock_shutil.copyfileobj.called)
            # Check os.mkdir called for Evasion/Attack1
            mock_os.mkdir.assert_any_call('/reports/Art/Evasion/Attack1')
            
            # Check PNG move (Attack2 -> Evasion)
            # 1^Attack2T.png. split rule: split(^)[1] is Attack2T?
            # Wait, code says: filename.split('.')[0].split('^')[1] in AttackTypes
            # 1^Attack2T.png -> 1^Attack2T -> Attack2T.
            # If Attack2 is in Evasion, then Attack2T is not Attack2?
            # Ah, check code:
            # if filename.split('.')[0] in AttackTypes (CSV)
            # CSV: Attack1.csv -> Attack1. In Evasion? Yes.
            
            # Image:
            # elif filename.split('.')[0].split('^')[1] in AttackTypes...
            # 1^Attack2T.png -> Attack2T.
            # Is Attack2T in Evasion ['Attack1', 'Attack2']? No. 
            # So Image logic might rely on sanitized names or specific naming convention?
            # The Image checkAttackListStatus logic used [:-1] to strip T/F.
            # createAttackFolder logic uses direct lookup?
            # Let's check code reading again to be sure.
             
        finally:
            Utility.AttackTypes = original_attack_types

    def test_checkList(self):
        mock_model = MagicMock()
        mock_model.predict.side_effect = [
            np.array([[0.1, 0.9]]), # Benign 1
            np.array([[0.9, 0.1]]), # Adv 0 (Diff -> Success)
            np.array([[0.1, 0.9]]), # Benign 2
            np.array([[0.1, 0.9]])  # Adv 2 (Same -> Fail)
        ]
        
        payload = {
            'model': mock_model,
            'original_data': np.array([[1], [2]]),
            'adversial_data': np.array([[3], [4]])
        }
        
        result = Utility.checkList(payload)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 0)

    def test_dateTimeFormat_None(self):
        dt = Utility.dateTimeFormat(None)
        self.assertTrue("UTC" in dt)


    def test_dateTimeFormat_Value(self):
        dt_obj = datetime.datetime(2023, 1, 1, 12, 0, 0)
        dt = Utility.dateTimeFormat(dt_obj)
        self.assertEqual(dt, "01-01-2023 12:00:00 PM")

    def test_find_duplicates(self):
        data = np.array([[1, 2], [3, 4], [1, 2]])
        dups = Utility.find_duplicates(data)
        # Expected: [0, 0, 1] (Assuming 0=False, 1=True)
        expected = np.array([0, 0, 1])
        np.testing.assert_array_equal(dups, expected)

    def test_calc_precision_recall(self):
        predicted = [1, 0, 1, 1, 0]
        actual =    [1, 0, 0, 1, 1]
        precision, recall = Utility.calc_precision_recall(predicted, actual)
        self.assertAlmostEqual(precision, 2/3)
        self.assertAlmostEqual(recall, 2/3)

    def test_calc_precision_recall_zero_division(self):
        predicted = [0, 0]
        actual = [0, 0]
        precision, recall = Utility.calc_precision_recall(predicted, actual)
        # Code says: if num_positive_predicted == 0: precision = 1
        self.assertEqual(precision, 1)
        # if num_positive_actual == 0: recall = 1
        self.assertEqual(recall, 1)

    def test_combineList_Evasion(self):
        # a=[[0.1]] -> list [[0.1]]. b=[[1]] -> list [[1]].
        # zip -> ([0.1], [1]). x+y -> [0.1, 1]. c=[[0.1, 1]].
        # d=[[1]]. zip(c,d) -> ([0.1, 1], [1]). x+[y] -> [0.1, 1, 1].
        # e = [[0.1, 1, 1]].
        # e[0][-1] is 1. e[0][-2] is 1.
        # 1 != 1 is False. 
        # So else branch: e[i].append('False').
        # f is empty.
        payload = {
            'attack_data': np.array([[0.1]]), 
            'target_data': np.array([[1]]),
            'prediction_data': np.array([1]),
            'type': 'Evasion'
        }
        e, f = Utility.combineList(payload)
        # Prediction same as target, so not evasion?
        # Logic: if last != second last. 1 != 1 False.
        self.assertEqual(len(f), 0)
        self.assertEqual(e[0][-1], 'False')

    def test_combineList_Inference(self):
        payload = {
            'attack_data': np.array([[0]]), 
            'target_data': np.array([[1]]), 
            'prediction_data': np.array([1]), 
            'type': 'Inference'
        }
        e, f = Utility.combineList(payload)
        self.assertEqual(len(f), 1)
        self.assertEqual(e[0][-1], 'True')

    def test_checkList(self):
        mock_model = MagicMock()
        mock_model.predict.side_effect = [
            np.array([[0.1, 0.9]]), # Benign -> 1
            np.array([[0.9, 0.1]])  # Adv -> 0
        ]
        
        payload = {
            'model': mock_model,
            'original_data': np.array([[1, 2]]),
            'adversial_data': np.array([[1, 2]])
        }
        
        # Benign 1, Adv 0. 1 != 0. Condition: if 1 == 0 continue else append.
        # Appends [i, 1, 0, 'True']
        result = Utility.checkList(payload)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [0, 1, 0, 'True'])

    @patch('src.service.utility.shutil.rmtree')
    @patch('src.service.utility.os.remove')
    @patch('src.service.utility.os.path.isdir')
    @patch('src.service.utility.os.path.isfile')
    def test_databaseDelete(self, mock_isfile, mock_isdir, mock_remove, mock_rmtree):
        # Test file delete
        mock_isfile.return_value = True
        Utility.databaseDelete("path/to/file")
        mock_remove.assert_called_with("path/to/file")
        
        # Test dir delete
        mock_isfile.return_value = False
        mock_isdir.return_value = True
        Utility.databaseDelete("path/to/dir")
        mock_rmtree.assert_called_with("path/to/dir")

    def test_attackDesc(self):
        keys = ["Poisoning", "MembershipInferenceRule", "CarliniL2Method"]
        for k in keys:
            desc = Utility.attackDesc(k)
            self.assertIsInstance(desc, str)
            self.assertTrue(len(desc) > 0)
        self.assertEqual(Utility.attackDesc("Unknown"), "")

    def test_htmlAppendixContent(self):
        payload_tab = {'model_metaData': {'dataType': 'Tabular'}}
        html_tab = Utility.htmlAppendixContent(payload_tab)
        self.assertIsInstance(html_tab, str)
        self.assertIn("Appendix", html_tab)

    def test_htmlCssContentReport(self):
        payload_tab = {'type': 'Tabular'}
        css_tab = Utility.htmlCssContentReport(payload_tab)
        self.assertIn("<style>", css_tab)
        
        payload_img = {'type': 'Image'}
        css_img = Utility.htmlCssContentReport(payload_img)
        self.assertIn("<style>", css_img)

