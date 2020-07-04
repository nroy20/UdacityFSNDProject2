import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={'/':{'origins':"*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, DELETE, POST')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def retrieve_categories():
    categories = Category.query.all()
    formatted_categories = {category.id: category.type for category in categories}
    
    if len(categories) == 0:
      abort(404)
    
    return jsonify({
      'success': True,
      'categories': formatted_categories
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def retrieve_questions():
    selection = Question.query.order_by(Question.id).all()
  
    if len(selection) == 0:
      abort(404)

    current_questions = paginate_questions(request, selection)

    categories = Category.query.all()
    formatted_categories = {category.id: category.type for category in categories}
    
    if len(categories) == 0:
      abort(404)

    return jsonify({
  		'success':True,
  		'questions': current_questions,
  		'total_questions': len(selection),
  		'categories': formatted_categories,
  		'current_category': None,
  		})

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_questions(question_id):
    
    if question_id == 0:
      abort(400)

    to_delete = Question.query.get(question_id)
    if not to_delete:
      abort(404)

    to_delete.delete()

    return jsonify({
      'success': True,
      'deleted_id': question_id
      }), 200

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
    body = request.get_json()

    question = body.get('question')
    answer = body.get('answer')
    category = body.get('category')
    difficulty = body.get('difficulty')

    try:
      question = Question(
        question=question,
        answer=answer,
        category=category,
        difficulty=difficulty
      )
      question.insert()

      selection = Question.query.all()
      if len(selection) == 0:
        abort(404)

      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'question_id': question.id,
        'current_category': None,
        'total_questions': len(Question.query.all())
      })
    except:
      abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    search_term = body.get('searchTerm')

    if not search_term:
      abort(400)

    selection = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()

    if len(selection) == 0:
      abort(404)

    current_questions = paginate_questions(request, selection)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'current_category': None
    })
    

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    current_category = Category.query.get(category_id)
    selection = Question.query.filter(Question.category == category_id).all()
    current_questions = paginate_questions(request, selection)

    return jsonify({
  		'success':True,
  		'questions': current_questions,
  		'total_questions': len(selection),
  		})


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    
  
  @app.route('/quizzes', methods=['POST'])
  def get_next_question():
    #take category, use as filter and create selection of questions
    #other filter should be no previous questions
    body = request.get_json()
    quiz_category = body['quiz_category']['id']
    previous_questions = body.get("previous_questions")
    if quiz_category == 0:
      selection = Question.query.filter(Question.id.notin_(previous_questions)).all()
    else:
      selection = Question.query.filter(Question.category == quiz_category, 
    Question.id.notin_(previous_questions)).all()

    if len(selection) == 0:
      return jsonify({
        'success': True
      })

    #get random question from selection and display
    next_question = random.choice(selection).format()

    return jsonify({
      'success': True,
      'question': next_question
    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
    }), 404

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
    }), 400

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
    }), 422
  
  return app

    