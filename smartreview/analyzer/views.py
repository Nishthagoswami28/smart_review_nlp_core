from django.shortcuts import render, redirect
from .models import Review, User
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .nlp_core import analyze_reviews, parse_uploaded_file
import tempfile 
import re
from .clean import clean_raw_reviews  # ✅ import the clean function


# Create your views here.
def home(request):
    user_id = request.session.get('user_id')
    user = User.objects.filter(id=user_id).first() if user_id else None
    return render(request, "home.html", {"user": user})

def register(request):
    if request.method == 'POST':
        name1 = request.POST.get("name")
        email1 = request.POST.get("email")
        password1 = request.POST.get("password")
        phone1 = request.POST.get("phone")
        address1 = request.POST.get("address")
        city1 = request.POST.get("city")
        state1 = request.POST.get("state")
        country1 = request.POST.get("country")

        User(
            name=name1,
            email=email1,
            password=password1,
            phone=phone1,
            address=address1,
            city=city1,
            state=state1,
            country=country1,
        ).save()
        return render(request, "login.html", {"message": "Registration successful. Please log in"})

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = User.objects.filter(email=email, password=password).first()

        if user:
            request.session['user_id'] = user.id
            request.session['user_name'] = user.name  # ✅ Add this
            return redirect('home')
        else:
            return render(request, "login.html", {"message": "Login not successful"})

    return render(request, "login.html")

def about(request):
    return render(request, "about.html")

def upload_reviews(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.filter(id=user_id).first()
    context = {}

    if request.method == 'POST':
        platform = request.POST.get('platform') or 'Unknown Platform'
        product_name = request.POST.get('product_name') or 'Unnamed Product'
        product_image_file = request.FILES.get('product_image')
        review_input_type = request.POST.get('review_input_type')
        product_url = request.POST.get('product_url')

        reviews = []

        try:
            # Load raw review input
            if review_input_type == 'paste':
                pasted_text = request.POST.get('pasted_reviews', '')
                reviews = clean_raw_reviews(pasted_text)
            elif review_input_type == 'file':
                uploaded_file = request.FILES.get('uploaded_file')
                if uploaded_file:
                    raw_data = uploaded_file.read().decode('utf-8')
                    reviews = clean_raw_reviews(raw_data)
            else:
                context['error'] = 'Please select a valid review input method.'
                return render(request, 'upload.html', context)

            if not reviews:
                context['error'] = 'No valid reviews found after cleaning.'
                return render(request, 'upload.html', context)

            # NLP analysis
            summary, detailed_results = analyze_reviews(reviews)
            sample_reviews = [r['review'] for r in detailed_results[:3]]
            all_keywords = [kw for r in detailed_results for kw in r['keywords']]
            unique_keywords = sorted(set(all_keywords))[:10]

            final_result = {
                'review': '\n'.join(sample_reviews),
                'sentiment': (
                    'positive' if summary['positive_pct'] > 50 else
                    'negative' if summary['negative_pct'] > 50 else
                    'neutral'
                ),
                'keywords': unique_keywords,
                'summary': summary
            }

            # Save product image
            product_image_path = None
            if product_image_file:
                fs = FileSystemStorage()
                filename = fs.save(product_image_file.name, product_image_file)
                product_image_path = fs.url(filename)

            # Add data to context
            context.update({
                'result': final_result,
                'image_url': product_image_path or '/static/images/sample.jpg',
                'platform': platform,
                'product_name': product_name,
            })

            # Save Review to database
            Review.objects.create(
                user=user,
                text=final_result['review'],
                sentiment=final_result['sentiment'],
                keywords=', '.join(final_result['keywords']),
                platform=platform,
                product_name=product_name,
                product_image=product_image_path or '/static/images/sample.jpg',
                product_url=product_url
            )

        except Exception as e:
            context['error'] = f"Error processing reviews: {str(e)}"

    return render(request, 'upload.html', context)


def view_reviews(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return render(request, 'view_reviews.html', {
            'reviews': [],
            'error': 'You must be logged in to view your reviews.',
        })

    reviews = Review.objects.filter(user_id=user_id).order_by('-date_created')

    # Optional: prepare a friendly structure (you can also handle this directly in template)
    review_data = []
    for review in reviews:
        review_data.append({
            'platform': review.platform,
            'product_name': review.product_name,
            'product_image': review.product_image or '/static/images/default.jpg',
            'sentiment': review.sentiment,
            'review_snippet': review.text[:200] + '...' if len(review.text) > 200 else review.text,
            'keywords': review.keywords.split(', '),
            'timestamp': review.date_created.strftime('%d %b %Y, %I:%M %p'),
            'product_url': review.product_url
        })

    return render(request, 'view_reviews.html', {
        'reviews': review_data
    })

def logout_view(request):
    request.session.flush()
    return redirect('login')

def profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)
    return render(request, 'profile.html', {'user': user})

def change_password(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        current = request.POST.get('current_password')
        new = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')

        if user.password != current:
            return render(request, 'change_password.html', {'message': 'Current password is incorrect.'})
        
        if new != confirm:
            return render(request, 'change_password.html', {'message': 'New passwords do not match.'})

        user.password = new
        user.save()
        return redirect('profile')

    return render(request, 'change_password.html')


def edit_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        user.city = request.POST.get('city')
        user.state = request.POST.get('state')
        user.country = request.POST.get('country')
        user.save()
        return redirect('profile')

    return render(request, 'edit_profile.html', {'user': user})


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirm']

        if password != confirm:
            return render(request, 'forgot_password.html', {'message': 'Passwords do not match.'})

        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            return render(request, 'login.html', {'message': 'Password reset successful. Please login.'})
        except User.DoesNotExist:
            return render(request, 'forgot_password.html', {'message': 'No account found with that email.'})
    return render(request, 'forgot_password.html')


def clean_raw_reviews(raw_text):
    # Step 1: Remove numeric IDs and standalone star ratings
    cleaned = re.sub(r'^\d{6,}$', '', raw_text, flags=re.MULTILINE)
    cleaned = re.sub(r'^\s*[1-5]\s*$', '', cleaned, flags=re.MULTILINE)

    # Step 2: Remove names, dates, certified buyer lines
    cleaned = re.sub(r'^Certified Buyer.*$', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'^[A-Z][a-z]+\s+[A-Z][a-z]+$', '', cleaned, flags=re.MULTILINE)  # likely full names
    cleaned = re.sub(
        r'^(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|'
        r'Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*,?\s*\d{4}$',
        '', cleaned, flags=re.MULTILINE)

    # Step 3: Remove cut-off markers like READ MORE
    cleaned = re.sub(r'READ\s*MORE', '', cleaned, flags=re.IGNORECASE)

    # Step 4: Group meaningful review lines
    lines = cleaned.strip().splitlines()
    grouped = []
    buffer = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if buffer.endswith(('.', '!', '?')):
            grouped.append(buffer.strip())
            buffer = line
        else:
            buffer += " " + line
    if buffer:
        grouped.append(buffer.strip())

    # Step 5: Remove duplicates
    unique_reviews = list(dict.fromkeys(grouped))

    return unique_reviews
