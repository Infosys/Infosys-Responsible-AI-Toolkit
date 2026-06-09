This is the read me file for doing unit test coverage for this hallucination module.

1. Navigate to test_files folder in terminal cd Rag\test_files

2. use "pytest rag_integration_tests.py -q -v" to test individual models (replace module name)

3. use "pytest --cov=RAG --cov-report=term-missing rag_integration_tests.py test_service_defaultqa.py test_service_cot.py test_service_thot.py test_service_lot.py test_service_show_score.py test_admin_db.py test_router_exceptions.py" to run full test and coverage

4. use "coverage report -m" to check coverage

5. use "coverage html" to convert coverage to html format

6. use "start htmlcov\index.html" to view coverage report in your browser