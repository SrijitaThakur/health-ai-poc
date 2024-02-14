import os
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from openai import OpenAI
from dotenv import load_dotenv
from django.http import JsonResponse

# Load environment variables from .env file
load_dotenv()
api_key = os.environ.get('OPENAI_API_KEY')

# Check if the API key is available
if not api_key:
    raise Exception("OpenAI API key not found in environment variables.")

client = OpenAI(api_key=api_key)


@api_view(['POST'])
def save_user_data(request):
    if request.method == 'POST':
        try:
            print("request.data ", request.data)
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
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
        bloodSugar = user.bloodSugar
        dietaryFatTotal = user.dietaryFatTotal
        dietarySugar = user.dietarySugar
        dietaryWater = user.dietaryWater
        dietaryProtein = user.dietaryProtein
        dietaryFiber = user.dietaryFiber
        bloodPressureSystolic = user.bloodPressureSystolic
        bloodPressureDiastolic = user.bloodPressureDiastolic
        steps = user.steps

        # Include prompt for generating diet plan
        context = "Generate a custom diet and exercise plan based on the provided information\n"

        # Format data for chat-GPT4 model
        context += f"Age: {age}, Sex: {sex}, Height: {height}, Weight: {weight}, Blood sugar: {bloodSugar}, "
        context += f"Dietary Fat Total: {dietaryFatTotal}, Dietary Sugar: {dietarySugar}, "
        context += f"Dietary Water: {dietaryWater}, Dietary Protein: {dietaryProtein}, "
        context += f"Dietary Fiber: {dietaryFiber}, Blood Pressure Systolic: {bloodPressureSystolic}, "
        context += f"Blood Pressure Diastolic: {bloodPressureDiastolic}, "

        if user.heartRates is not None:
            # Initialize variables to calculate average heart rate
            total_hr_value = 0
            total_hr_entries = len(user.heartRates)
            # Iterate over all heart rate entries
            for hr in user.heartRates:
                total_hr_value += hr.get('value', 0)
            # Calculate average heart rate
            avg_hr_value = total_hr_value / total_hr_entries
            # Update the context with average heart rate
            context += f"Avg Heart Rate: {avg_hr_value:.2f} bpm, "

        # Add sleep data to the context
        if user.sleep is not None:
            # Get the first sleep entry
            first_sleep = user.sleep[0]
            # Extract values from the first sleep entry
            sleep_from_date = first_sleep.get('startDate')
            sleep_to_date = first_sleep.get('endDate')
            sleep_value = first_sleep.get('value')
            # Update the context
            context += f"Sleep: {sleep_value}, "

        context += f"Steps: {steps}, "
        context += 'The response should be in json and the format should be like diet_plan: $dietplan, exercise_plan: $exercise_plan only and it should not have any special characters like newline or tab.\n'
        context += 'For diet plan please return Breakfast,Mid_Morning_Snack,Lunch,Evening_Snack,Dinner,Late_Night_Snack,special_instructions,supplements.\n'
        context += 'For exercise plan please return daywise plan Monday,tuesday,wednesday,thursday,friday,saturday,special_instructions and Physical_activity_goal'
        print("context ", context)
        # Generate diet plan using chat-GPT4 model
        response = client.chat.completions.create(
            model="gpt-4", messages=[{
                "role": 'user',
                "content": context
            }])
        json_content = json.loads(response.choices[0].message.content)

        # Return JSON response
        return JsonResponse(json_content)

    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
