from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignupForm, LoginForm, ImageUploadForm
from .models import UserProfile, UploadImage
import os

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            return redirect('login')
    else:
        form = SignupForm()

    return render(request, 'users/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # ✅ Set session variable
            request.session['user_id'] = user.id
            return redirect('dashboard')
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})
def logout_view(request):
    request.session.flush()
    return redirect('login')


@login_required
def rewards_view(request):
    # Current user points
    user_profile = request.user.userprofile
    user_points = user_profile.points

    # Top 5 scorers
    top_scorers = UserProfile.objects.order_by('-points')[:5]

    return render(request, 'users/rewards.html', {
        'user_points': user_points,
        'top_scorers': top_scorers
    })

def dashboard(request):
    # ✅ Check if user is logged in via session
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')  # redirect to your login page

    images = UploadImage.objects.all()

    valid_images = []
    for img in images:
        if img.image and os.path.exists(img.image.path):
            valid_images.append(img)
        else:
            # delete broken DB entry
            img.delete()

    return render(request, 'users/dashboard.html', {'images': valid_images})
       
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .image_compare import is_duplicate  # assuming you have this function

@login_required
def upload(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_image = request.FILES['image']
            lat = form.cleaned_data['latitude']
            lng = form.cleaned_data['longitude']

            # 🔴 Check location duplicates
            pending_entry = UploadImage.objects.filter(
            user=request.user,
            latitude=lat, 
            longitude=lng, 
            is_completed=False
            ).exists()

            if pending_entry:
                return JsonResponse({
                    "status": "warning",
                    "message": "You already have a pending upload for this location. Please wait for it to complete.",
                    "redirect": "/users/dashboard/"
                })


                
 # 🔴 Check image duplicates
            for img in UploadImage.objects.all():
                if is_duplicate(new_image, img.image):
                    return JsonResponse({
                           "status": "error",
                            "message": "Duplicate image detected",
                            "redirect": "/users/dashboard/"
                        })

            # Save new image
            upload = form.save(commit=False)
            upload.user = request.user
            upload.save()

                    
            return JsonResponse({
                "status": "success",
                "message": "Image uploaded successfully",
                "redirect": "/users/dashboard/"
               })

            
         
            
        else:
            return JsonResponse({
                "status": "error",
                "message": "Form is not valid",
                "redirect": "/users/dashboard/"
            })


    else:
        form = ImageUploadForm()

    return render(request, 'users/upload.html', {'form': form})

from .opencv_utils import verify_cleaned

@login_required
def upload_cleaned(request, image_id):
    upload = UploadImage.objects.get(id=image_id)

    if request.method == 'POST':
        cleaned_img = request.FILES.get('cleaned_image')

        if upload.is_completed:
            return JsonResponse({
                "status": "error",
                "message": "area is already cleaned",
                "redirect": "/users/dashboard/"
            })


        # 🔴 VERIFY USING OPENCV
        is_clean = verify_cleaned(upload.image.path, cleaned_img)

        if not is_clean:
            return JsonResponse({
                "status": "error", 
                "message": "Area is not cleaned properly",
                "redirect": "/users/dashboard/"
                })

        # ✅ CLEANED
        upload.cleaned_image = cleaned_img
        upload.is_completed = True

        if not upload.points_awarded:
            profile = UserProfile.objects.get(user=request.user)
            profile.points += 10
            profile.save()
            upload.points_awarded = True

        upload.save()

        return JsonResponse({"status": "success", "message": "Cleanup verified! +10 points","redirect": "/users/dashboard/"})

    return render(request, 'users/upload_cleaned.html', {'upload': upload})

import google.generativeai as genai
from django.http import JsonResponse
import json


# Securely configure the API
genai.configure(api_key="ADD YOUR G-MAPS API KEY HERE")

def green_expert_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_msg = data.get("message", "")

            # System Prompt based on your project components
            # This ensures the AI knows about your OpenCV and Firebase setup
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = (
                f"You are the 'Green Expert' for Mission Clean Earth. "
                f"Your goal is to promote environmental awareness and guide volunteers. "
                f"Help with waste identification, recycling, and explaining our "
                f"AI-based cleanup verification process. "
                f"User asks: {user_msg}"
            )

            response = model.generate_content(prompt)
            return JsonResponse({"reply": response.text})
            
        except Exception as e:
            # This will help you debug in your terminal if it fails again
            print(f"Connection Error: {e}")
            return JsonResponse({"reply": "I'm having trouble connecting to the eco-database. Please check your internet or API limits."}, status=500)
            
    return render(request, 'users/chatbot_page.html')
