from django.shortcuts import render
import json
import math
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import TestQuestion, FieldOfStudy, UserProfile


def home(request):
    """
    Renders the home page.
    """
    value = request.GET.get('value')
    if value == 'Agree':
        print(True, value)
    return render(request, 'Main.html', {})


# Response mapping for user answers
RESPONSE_MAPPING = {
    "Strongly Agree": 2,
    "Agree": 1,
    "Neutral": 0,
    "Disagree": -1,
    "Strongly Disagree": -2
}

# Interest categories and their weights
INTEREST_CATEGORIES = [
    'practical', 'analytical', 'artistic', 'social',
    'enterprising', 'conventional', 'scientific', 'technical'
]
INTEREST_WEIGHTS = {
    'practical': 1, 'analytical': 1, 'artistic': 1,
    'social': 1, 'enterprising': 1, 'conventional': 1,
    'scientific': 2, 'technical': 1
}


def calculate_interest_score(user_profile, answers):
    """
    Calculate and update interest scores for a user based on their answers.
    """
    # Reset interest scores
    for category in INTEREST_CATEGORIES:
        setattr(user_profile, f"{category}_interest", 0)

    # Process each answer
    for answer in answers:
        question_id = answer.get('question_id')
        response = answer.get('selected_option')

        if question_id and response in RESPONSE_MAPPING:
            try:
                question = TestQuestion.objects.get(id=question_id)
                score = RESPONSE_MAPPING[response] * question.weight
                interest_field = f"{question.interest_type}_interest"

                # Update the corresponding interest field
                if hasattr(user_profile, interest_field):
                    current_value = getattr(user_profile, interest_field)
                    setattr(user_profile, interest_field, current_value + score)
            except TestQuestion.DoesNotExist:
                continue  # Skip invalid questions

    user_profile.save()


def calculate_similarity(user_profile, field):
    """
    Calculate similarity between user interests and field requirements.
    """
    user_vector = [
        max(0, getattr(user_profile, f"{category}_interest", 0))
        for category in INTEREST_CATEGORIES
    ]
    field_vector = [
        max(0, getattr(field, f"min_{category}_interest", 0))
        for category in INTEREST_CATEGORIES
    ]
    dot_product = sum(u * f * INTEREST_WEIGHTS[category]
                      for u, f, category in zip(user_vector, field_vector, INTEREST_CATEGORIES))
    magnitude_user = math.sqrt(sum(u ** 2 for u in user_vector))
    magnitude_field = math.sqrt(sum(f ** 2 for f in field_vector))
    if magnitude_user == 0 or magnitude_field == 0:
        return 0
    return dot_product / (magnitude_user * magnitude_field)


def generate_recommendations(user_profile, difficulty, top_n=3):
    """
    Generate top field recommendations based on similarity scores.
    """
    fields_with_score = []
    for field in FieldOfStudy.objects.filter(difficulty_level=difficulty):
        similarity = calculate_similarity(user_profile, field)
        fields_with_score.append({'field': field, 'score': similarity, 'career_paths': field.career_paths})

    # Sort fields by similarity (descending)
    fields_with_score.sort(key=lambda x: x['score'], reverse=True)

    # If no fields match, return an empty list
    if not fields_with_score or fields_with_score[0]['score'] == 0:
        return []

    return fields_with_score[:top_n]  # Return top-N recommendations


@csrf_exempt
def analyze(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Extract and validate data
            name = data.get('name', '').strip()
            gender = data.get('gender', '').strip()
            dob = data.get('dob', '').strip()
            answers = data.get('answers', [])
            difficulty = data.get('difficulty', '').strip()
            top_n = data.get('top_n', 3)  # Number of recommendations to return

            if not name or not gender or not dob:
                return JsonResponse({'error': 'Please provide your name, gender, and date of birth.'}, status=400)
            if difficulty not in ["Moderate", "Challenging"]:
                return JsonResponse({'error': 'Invalid difficulty level.'}, status=400)

            try:
                date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

            if not answers or not isinstance(answers, list):
                return JsonResponse({'error': 'Answers are missing or invalid.'}, status=400)

            # Get or create the user profile
            user_profile, _ = UserProfile.objects.get_or_create(
                name=name, gender=gender, date_of_birth=date_of_birth
            )

            # Calculate interest scores
            calculate_interest_score(user_profile, answers)

            # Generate recommendations
            recommendations = generate_recommendations(user_profile, difficulty, top_n=top_n)

            # Handle no recommendations
            if not recommendations:
                return JsonResponse({
                    'user_info': {
                        'name': user_profile.name,
                        'gender': user_profile.gender,
                        'date_of_birth': user_profile.date_of_birth.strftime('%Y-%m-%d'),
                    },
                    'difficulty': difficulty,
                    'interests': {category: getattr(user_profile, f"{category}_interest") for category in
                                  INTEREST_CATEGORIES},
                    'message': 'We currently lack sufficient data to recommend a major. Please try again in the future.'
                }, status=200)
            # Prepare response
            response_data = {
                'user_info': {
                    'name': user_profile.name,
                    'gender': user_profile.gender,
                    'date_of_birth': user_profile.date_of_birth.strftime('%Y-%m-%d'),
                },
                'difficulty': difficulty,
                'interests': {category: getattr(user_profile, f"{category}_interest") for category in
                              INTEREST_CATEGORIES},
                'recommendations': [
                    {'name': item['field'].name, 'description': item['field'].description, 'score': item['score'],
                     'career_paths': item['career_paths']}
                    for item in recommendations
                ],
            }
            print(response_data)
            return JsonResponse(response_data, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Something went wrong: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)
