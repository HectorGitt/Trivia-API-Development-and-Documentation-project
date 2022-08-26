import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from settings import DB_NAME, DB_USER, DB_PASSWORD

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = DB_NAME
        self.database_path = "postgresql://{}:{}@{}/{}".format(DB_USER,DB_PASSWORD,'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        #new quesion
        self.new_question = {'question':'What is your name?', 'answer':'Olaitan', 'category': 1, 'difficulty': 2}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paginated_questions(self):
        """Test GET request for paginated questions"""
        res = self.client().get('/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['current_category'])
        
    
    def test_get_categories(self):
        """Test GET request for categories"""
        res = self.client().get('/categories')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_categories'])
        self.assertTrue(len(data['categories']))
        self.assertEqual(data['success'], True)
        
    def test_get_question_search(self):
        """Test POST request for searching questions"""
        res = self.client().post("/questions/search", json={"searchTerm": "who"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertGreater(data["total_questions"], 2)
    
    def test_create_new_question(self):
        """Test POST request for creating new question"""
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
      
    def test_get_category_questions(self):
        """Test GET request for category questions"""
        res = self.client().get("/categories/2/questions")
        data = json.loads(res.data)
        
        category = Category.query.filter_by(id=2).first()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], category.type)
              
    def test_delete_question(self):
        '''Test DELETE request for deleting question'''
        res = self.client().delete("/questions/38")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 38)
    
     
    def test_quiz_questions(self):
        """Test POST request for quiz questions"""
        res = self.client().post("/question/quiz", json={"previous_questions": [10], 'quiz_category': {'id':1}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(data['question']['id'], 10)
    
    def test_404_category_questions(self):
        """Test 404 error request for category questions"""
        res = self.client().get("/categories/399/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data["message"], "unprocessable")
    
    def test_422_post_quiz_questions(self):
        """Test 422 error request for playing quiz"""
        res = self.client().post("/question/quiz") 
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
        
    def test_400_question_search(self):
        """Test 400 error request for searching questions"""
        res = self.client().post("/questions/search") 
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')
        
        
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()