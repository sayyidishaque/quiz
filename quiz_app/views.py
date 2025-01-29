from django.contrib import auth, messages
from django.shortcuts import redirect, render
from .models import Question, Answer, UserAnswer
from django.contrib.auth.models import User
from .forms import QuestionForm, AnswerForm


def load_questions(request):
    """
    Handle the loading and submission of quiz questions.

    If the user is not authenticated, they are redirected to the login page.
    If the request method is POST, the user's answers are processed, scored, and saved.
    The user is then redirected to the results page with their total score.
    If the request method is GET, the quiz page is rendered with the list of questions.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object, either a redirect or a rendered template.
    """
    if not request.user.is_authenticated:
        return redirect('index')  # Redirect to login if the user is not authenticated

    questions = Question.objects.prefetch_related('answer_set').all()

    if request.method == 'POST':
        total_score = 0
        for question in questions:
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id:
                selected_answer = Answer.objects.filter(id=selected_answer_id).first()

                # Save the user's answer
                user_answer = UserAnswer.objects.create(
                    user=request.user,
                    question=question,
                    selected_answer=selected_answer
                )

                # Update the score if the selected answer is correct
                user_answer.calculate_score()
                total_score += user_answer.score

        # Redirect to the results page with the score
        return redirect('quiz_results', score=total_score)

    return render(request, 'quiz_page.html', {'questions': questions})


def index(request):
    """
    Handle user login.

    If the request method is POST, authenticate the user and log them in.
    If the request method is GET, render the login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object, either a redirect or a rendered template.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            return render(request, 'index.html', {'error': 'Invalid username or password'})

    return render(request, 'index.html')


def logout_view(request):
    """
    Handle user logout.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object, a redirect to the home page.
    """
    auth.logout(request)
    return redirect('/')


def register(request):
    """
    Handle user registration.

    If the request method is POST, create a new user and log them in.
    If the request method is GET, render the registration page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object, either a redirect or a rendered template.
    """
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})

        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email already exists'})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        auth.login(request, user)
        return redirect('/')

    return render(request, 'register.html')


def quiz_results(request, score):
    """
    Display the quiz results.

    Args:
        request (HttpRequest): The HTTP request object.
        score (int): The user's total score.

    Returns:
        HttpResponse: The HTTP response object, a rendered template with the quiz results.
    """
    total_questions = Question.objects.count()
    percentage_score = (score / total_questions) * 100 if total_questions > 0 else 0
    return render(request, 'quiz_results.html', {
        'score': score,
        'total_questions': total_questions,
        'percentage_score': percentage_score,
    })


def add_question(request):
    """
    Handle adding a new quiz question.

    If the user is not authenticated, they are redirected to the login page.
    If the request method is POST, the new question and its answers are saved.
    If the request method is GET, the add question page is rendered.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object, either a redirect or a rendered template.
    """
    if not request.user.is_authenticated:
        return redirect('index')  # Redirect to login if the user is not authenticated

    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save()

            # Handle answers for the question
            for key, value in request.POST.items():
                if key.startswith('answer_text_'):
                    answer_text = value
                    is_correct = request.POST.get(f'is_correct_{key.split("_")[-1]}', False) == 'on'
                    Answer.objects.create(
                        question=question,
                        text=answer_text,
                        correct=is_correct
                    )

            return redirect('add_question')  # Redirect to the add question page after saving the question

    else:
        question_form = QuestionForm()

    return render(request, 'add_question.html', {'question_form': question_form})