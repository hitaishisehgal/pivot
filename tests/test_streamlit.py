from streamlit.testing.v1 import AppTest

def test_streamlit_overview_runs():
    app=AppTest.from_file("app/streamlit_app.py").run(timeout=60)
    assert not app.exception
