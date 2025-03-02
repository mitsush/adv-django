from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse

from .models import Food, Consume, HealthGoal
from .forms import FoodForm, HealthGoalForm

def index(request):
    if request.method == "POST":
        food_consumed = request.POST['food_consumed']
        consumed_item = Food.objects.get(name=food_consumed)
        user = request.user
        consume = Consume(user=user, food_consumed=consumed_item)
        consume.save()
        return redirect('/')
    else:
        foods = Food.objects.all()

    consumed_food = []
    today_calories = 0
    today_protein = 0
    today_carbs = 0
    today_fat = 0
    calorie_percent = 0
    protein_percent = 0
    carbs_percent = 0
    fat_percent = 0
    goal = None
    
    if request.user.is_authenticated:
        consumed_food = Consume.objects.filter(user=request.user)
        
        # Calculate today's nutrition totals
        today_calories = sum(item.food_consumed.calories for item in consumed_food)
        today_protein = sum(item.food_consumed.proteins for item in consumed_food)
        today_carbs = sum(item.food_consumed.carbs for item in consumed_food)
        today_fat = sum(item.food_consumed.fats for item in consumed_food)
        
        # Get user's goals if they exist
        try:
            goal = HealthGoal.objects.get(user=request.user)
            # Calculate percentages for progress bars
            calorie_percent = min(round((today_calories / goal.daily_calorie_goal) * 100), 100) if goal.daily_calorie_goal > 0 else 0
            protein_percent = min(round((today_protein / goal.protein_goal) * 100), 100) if goal.protein_goal > 0 else 0
            carbs_percent = min(round((today_carbs / goal.carb_goal) * 100), 100) if goal.carb_goal > 0 else 0
            fat_percent = min(round((today_fat / goal.fat_goal) * 100), 100) if goal.fat_goal > 0 else 0
        except HealthGoal.DoesNotExist:
            goal = None

    return render(request, 'app/index.html', {
        'foods': foods,
        'consumed_food': consumed_food,
        'today_calories': today_calories,
        'today_protein': today_protein,
        'today_carbs': today_carbs,
        'today_fat': today_fat,
        'goal': goal,
        'calorie_percent': calorie_percent,
        'protein_percent': protein_percent,
        'carbs_percent': carbs_percent,
        'fat_percent': fat_percent,
    })


def delete_consume(request, id):
    consumed_food = Consume.objects.get(id=id)
    if request.method == 'POST':
        consumed_food.delete()
        return redirect('/')
    return render(request, 'app/delete.html', {'consume': consumed_food})


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "app/register.html", {"form": form})


@login_required
def add_food(request):
    if request.method == "POST":
        form = FoodForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = FoodForm()
    return render(request, "app/add_food.html", {"form": form})


@login_required
def update_goals(request):
    goal, created = HealthGoal.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = HealthGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = HealthGoalForm(instance=goal)

    return render(request, "app/update_goals.html", {"form": form, "goal": goal})


@login_required
def chart_data(request):
    consumed = Consume.objects.filter(user=request.user)
    goal, _ = HealthGoal.objects.get_or_create(user=request.user)

    data = {
        "labels": [c.food_consumed.name for c in consumed],
        "carbs": [c.food_consumed.carbs for c in consumed],
        "proteins": [c.food_consumed.proteins for c in consumed],
        "fats": [c.food_consumed.fats for c in consumed],
        "calories": [c.food_consumed.calories for c in consumed],

        "goal_carbs": goal.carb_goal,
        "goal_proteins": goal.protein_goal,
        "goal_fats": goal.fat_goal,
        "goal_calories": goal.daily_calorie_goal,
    }
    return JsonResponse(data)