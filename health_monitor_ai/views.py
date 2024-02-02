import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from openai import OpenAI

client = OpenAI(api_key='')

# Set your OpenAI API key


def parse_input(input_str):
    diet_plan_start_index = input_str.find('diet_plan:')
    exercise_plan_start_index = input_str.find('exercise_plan:')

    # Extract diet plan string
    diet_plan_str = input_str[diet_plan_start_index +
                              len('diet_plan:'):exercise_plan_start_index].strip()
    diet_plan_dict = {}
    current_key = None
    for line in diet_plan_str.split('\n'):
        line = line.strip()
        if line:
            if line.endswith(":"):
                current_key = line[:-1]
                diet_plan_dict[current_key] = ""
            else:
                if current_key:
                    diet_plan_dict[current_key] += line

    # Extract exercise plan string
    exercise_plan_str = input_str[exercise_plan_start_index +
                                  len('exercise_plan:'):].strip()
    exercise_plan_list = [item.strip()
                          for item in exercise_plan_str.split('\n') if item.strip()]

    # Create JSON object
    result = {
        "diet_plan": diet_plan_dict,
        "exercise_plan": exercise_plan_list
    }

    return json.dumps(result, indent=4)


@api_view(['POST'])
# def save_user_data(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             user = User(
#                 email=data['email'],
#                 age=data['age'],
#                 sex=data['sex'],
#                 height=data['height'],
#                 weight=data['weight'],
#                 targetWeight=data['targetWeight'],
#                 purpose=data['purpose'],
#                 heartRates=data.get('heartRates', []),
#                 sleep=data.get('sleep', []),
#                 steps=data.get('steps', [])
#             )
#             user.save()
#             return Response({"message": "User saved successfully"}, status=201)
#         except Exception as e:
#             return Response({"error": str(e)}, status=400)
#     else:
#         return Response({"error": "Method not allowed"}, status=405)
def save_user_data(request):
    if request.method == 'POST':
        try:
            print("request.data ", request.data)
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                print("hello....")
                serializer.save()
                return Response({'message': 'User data saved successfully'}, status=status.HTTP_201_CREATED)
            else:
                print("Validation errors:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Exception type:", type(e))
            print("Exception:", e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
def recommendation(request):
    if request.method == 'POST':
        # Retrieve the latest user record
        try:
            data = json.loads(request.body)
            email = data.get("email")
            user = User.objects.filter(email=email).latest('_id')
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # Extract relevant information from the latest user record
        age = user.age
        sex = user.sex
        height = user.height
        weight = user.weight

        # Extract heart rate data for the user
        # Extract heart rate data for the user
        heart_rate_data = [(hr['date'], hr['value']) for hr in user.heartRates]

        # Extract sleep data for the user
        sleep_data = [(sleep['from_date'], sleep['to_date'],
                       sleep['sleep_value']) for sleep in user.sleep]

        # Extract steps data for the user
        steps_data = [(steps['date'], steps['steps']) for steps in user.steps]

        # Include prompt for generating diet plan
        context = "Generate a custom diet and exercise plan based on the provided information\n"

        # Format data for chat-GPT4 model
        context += f"Age: {age},Sex: {sex},Height: {height},Weight: {weight},Blood sugar: 150,Total Cholesterol: 200, sgpt: 80, bilirubin: 2,haemoglobin: 9, "

        # Add heart rate data to the context
        # for hr_date, hr_value in heart_rate_data:
        hr_date, hr_value = heart_rate_data[0]
        context += f"Avg Heart Rate: {hr_value} bpm, "

        # Add sleep data to the context
        # for sleep_from_date, sleep_to_date, sleep_value in sleep_data:
        #     context += f"Sleep - {sleep_value}\n"

        # Add steps data to the context
        # for steps_date, steps_value in steps_data:
        steps_date, steps_value = steps_data[0]
        context += f"Steps {steps_value}\n"
        context += 'The response format should be diet_plan:$dietplan exercise_plan: $exercise_plan only and it should be a json.\n'
        context += 'For diet plan please return Breakfast,Mid_Morning_Snack,Lunch,Evening_Snack,Dinner,Late_Night_Snack,special_instructions,supplements.\n'
        context += 'For exercise plan please return daywise plan Monday,tuesday,wednesday,thursday,friday,saturday,special_instructions and Physical_activity_goal'
        # Generate diet plan using chat-GPT4 model
        response = client.chat.completions.create(
            model="gpt-4", messages=[{
                "role": 'user',
                "content": context
            }])

        # Return generated diet plan as JSON response
        return Response(response.choices[0].message.content)

    else:
        return Response({"error": "Method not allowed"}, status=405)
