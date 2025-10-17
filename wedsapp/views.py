# views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import HallBooking, Feedback
import re
import json
from django.utils.safestring import mark_safe


def _parse_int_from_string(val):
    """Try to convert a value to int. If direct int() fails, extract the first
    integer sequence from the string (e.g. '1 Day' -> 1). Returns None when
    no integer can be found.
    """
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        m = re.search(r"(\d+)", str(val))
        if m:
            return int(m.group(1))
    return None

def home(request):
    return render(request, 'home.html')

def menu(request):
    return render(request, 'menu.html')

def about(request):
    return render(request, 'about.html')

def book_hall(request):
    # Allow cart items passed via ?cart=... on GET from menu 'Proceed to Book'
    cart_text = request.GET.get('cart') if request.method == 'GET' else None
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        guests = request.POST.get('guests')
        date = request.POST.get('date')
        days = request.POST.get('days')
        food_items = request.POST.get('food_items', '').strip()

        # Parse numeric values safely (frontend may send strings like '1 Day')
        guests_value = _parse_int_from_string(guests)
        days_value = _parse_int_from_string(days)

        if guests_value is None or days_value is None:
            messages.error(request, 'Please provide valid numeric values for guests and days.')
            # Re-render the form preserving submitted values so user can correct them
            return render(request, 'book_hall.html', {
                'name': name,
                'phone': phone,
                'email': email,
                'guests': guests,
                'date': date,
                'days': days,
            })

        # Save to database
        booking = HallBooking.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=name,
            phone=phone,
            email=email,
            guests=guests_value,
            date=date,
            days=days_value,
            food_items=food_items,
        )

        # Send email notification
        try:
            subject = "New Hall Booking Request"
            # prepare a display version of food items
            food_items_display = food_items if food_items else 'None'

            message = f"""
New Booking Received:

Booking ID: {booking.id}
Name: {name}
Phone: {phone}
Email: {email}
Number of Guests: {guests}
Booking Date: {date}
Duration: {days} day(s)
Selected Food Items:
{food_items_display}
Submitted at: {booking.created_at.strftime('%Y-%m-%d %H:%M:%S')}
"""
            # prefer numeric values in internal emails
            message = message.replace(f"Number of Guests: {guests}", f"Number of Guests: {guests_value}")
            message = message.replace(f"Duration: {days} day(s)", f"Duration: {days_value} day(s)")
            # message already contains the food items display
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                ['kanagaviswesh.g2004@gmail.com'],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email sending failed: {e}")

        messages.success(request, 'Booking submitted successfully!')
        return render(request, 'book_hall.html', {'success': True})

    # On GET: if the menu passed cart items (via query param), prefill the textarea
    context = {}
    if cart_text:
        # cart_text is URL-encoded JSON (or older formats). Decode and try to parse
        try:
            import urllib.parse
            decoded = urllib.parse.unquote(cart_text)
            try:
                cart = json.loads(decoded)
            except Exception:
                # not JSON (legacy); fall back to the raw decoded value
                cart = decoded

            # If we have a list of items, build a readable summary for the textarea
            if isinstance(cart, list):
                lines = []
                for it in cart:
                    if isinstance(it, str):
                        lines.append(it)
                    elif isinstance(it, dict):
                        items = it.get('items') or []
                        lines.append(f"{it.get('name')}: {', '.join(items)}")
                    else:
                        lines.append(str(it))
                context['food_items'] = "\n".join(lines)
                # pass a safe JSON string to the template so client-side can render chips
                context['food_cart'] = mark_safe(json.dumps(cart))
            else:
                context['food_items'] = str(cart)
                context['food_cart'] = mark_safe('[]')
        except Exception:
            context['food_items'] = cart_text
            context['food_cart'] = mark_safe('[]')
    return render(request, 'book_hall.html', context)

def feedback(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        experience = request.POST.get('experience')
        rating = request.POST.get('rating')
        image = request.FILES.get('image')
        
        # Convert rating stars to number
        rating_map = {
            '⭐': 1,
            '⭐⭐': 2,
            '⭐⭐⭐': 3,
            '⭐⭐⭐⭐': 4,
            '⭐⭐⭐⭐⭐': 5
        }
        rating_value = rating_map.get(rating, 5)
        
        # Save feedback to database
        Feedback.objects.create(
            name=name,
            experience=experience,
            rating=rating_value,
            image=image
        )
        
        messages.success(request, 'Thank you for your feedback!')
        return redirect('feedback')
    
    return render(request, 'feedback.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')