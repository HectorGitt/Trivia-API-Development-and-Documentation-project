import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    #get page value from request
    page = request.args.get("page", 1, type=int)
    #start value for pagination
    start = (page - 1) * QUESTIONS_PER_PAGE
    #end value for pagination
    end = start + QUESTIONS_PER_PAGE
    
    #return questions based on pagination
    questions = [question.format() for question in selection]
    
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,POST,DELETE"
        )
        response.headers.add(
            "Access-Control-Allow-Credentials", "true"
        )
        return response


    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route('/categories', methods=['GET'])
    def get_categories():
        #get all categories from database
        categories = Category.query.all()
        #create a dictionary of categories
        category_dict = {}
        for category in categories:
            category_dict[category.id] = category.type
        return jsonify(
            {
                'success': True,
                'categories': category_dict,
                'total_categories': len(category_dict),
            }
        )

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions', methods=['GET'])
    def retrieve_questions():
        #get all questions from database
        all_questions = Question.query.order_by(Question.id).all()
        #paginatate questions
        selection = paginate_questions(request, all_questions)
        #get all categories from database
        categories = Category.query.all()
        #create a dictionary of questions
        category_dict = {}
        for category in categories:
            category_dict[category.id] = category.type
        return jsonify(
            {
                'success': True,
                'questions': selection,
                'total_questions': len(all_questions),
                'categories': category_dict,
                'current_category':"Science",
            }
        )
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            #get question from database
            question = Question.query.filter(Question.id == question_id).one_or_none()
            
            #check if question is none
            if question is None:
                abort(404)
            question.delete()
            #get all questions from database
            all_questiions = Question.query.order_by(Question.id).all()
            #paginatate questions
            paginated_questions = paginate_questions(request, all_questiions)
            
            return jsonify(
                {
                    'success': True,
                    'deleted': question_id,
                }
            )
        except:
            abort(422)
        
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def post_question():
        try:
            #get data from request
            body = request.get_json()
            new_question = body.get('question', None)
            new_answer = body.get('answer',None)
            new_category=body.get('category', None)
            new_difficulty = body.get('difficulty', None)
            #pass data to Question class
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty
            )
            #add question to database
            question.insert()
            return jsonify(
                {
                    "success": True,
                    "created": question.id,
                }
            )
        except:
            abort(422)
        
        
    @app.route('/questions/search', methods=['POST'])
    def search_question():
        try:
            #get data from request
            body = request.get_json()
            search = body.get('searchTerm', None)
            #check if search term exists
            if search:
                #get questions from database filtering by search term
                questions = Question.query.filter(Question.question.ilike(f'%{search}%')).all()
                #format questions
                question_list = [question.format() for question in questions]
                return jsonify(
                    {
                        'success': True,
                        'questions': question_list,
                        'total_questions':len(question_list),
                        'current_category':'Science'
                    }
                )
        except:
            abort(400)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    def category_questions(category_id):
        try:
            #get category from database
            category = Category.query.filter_by(id=category_id).one_or_none()
            
            #check if category is none
            if category is None:
                abort(404)
            
            #get questions from database filtering by category
            questions = Question.query.filter_by(category=category.id).all()
            #format questions
            questions_list = [question.format() for question in questions]
            return jsonify(
                {
                    'success':True,
                    'questions': questions_list,
                    'total_questions':len(questions_list),
                    'current_category': category.type,
                }
            )
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    
    @app.route('/question/quiz', methods=["POST"])
    def quiz_questions():
        try:
            #get data from request
            body = request.get_json()
            previous = body.get('previous_questions', None)
            category = body.get('quiz_category', None)
            #get question from category excluding previous questions
            if category['id'] == 0:
                question = Question.query.filter(~Question.id.in_(previous)).first()
            else:
                question = Question.query.filter(Question.category==category['id'], ~Question.id.in_(previous)).first()
            #check if question exists
            if question:
                question = question.format()
            else:
                question=None
            return jsonify(
                {
                    'success': True,
                    'question':question,
                }
            )
        except:
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"success": False, "error": 500, "message": "Server Error"}), 500
    
    
    return app

