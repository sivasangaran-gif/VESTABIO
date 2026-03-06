from app import app, perform_omnibase_analysis

with app.app_context():
    res = perform_omnibase_analysis("This is my dinner", "guest@omnihealth.ai", "test_meal.jpg")
    print("Result:", res)
