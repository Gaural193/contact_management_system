from django.shortcuts import render
from django.shortcuts import redirect , render
from django.db.models import Q
import vobject
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.http import HttpResponse
from django.db.models import Count
from django.contrib.auth import authenticate, login, logout




# List all contacts
@login_required
def contact_list(request):
    contacts = Contact.objects.all()
    query = request.GET.get('q')
    if query:
        contacts = contacts.filter(
            Q(first_name__icontains=query) | 
            Q(email__icontains=query) | 
            Q(phone_number__icontains=query)
        ) # Simple search
    return render(request, 'contact_list.html', {'contacts': contacts})

# Create a new contact
@login_required
def contact_create(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact_list')
    else:
        form = ContactForm()
    return render(request, 'contact_create.html', {'form': form})

# Edit an existing contact
@login_required
def contact_edit(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect('contact_list')
    else:
        form = ContactForm(instance=contact)
    return render(request, 'contact_edit.html', {'form': form, 'contact': contact})

# Delete a contact
@login_required
def contact_delete(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    contact.delete()
    return redirect('contact_list')

@login_required
def import_contacts(request):
    if request.method == 'POST':
        vcf_file = request.FILES['vcf_file']

        # Read the VCF file and decode from bytes to string
        try:
            vcf_content = vcf_file.read().decode('utf-8')  # Decoding from bytes to string
            contacts = vobject.readComponents(vcf_content)  # Parse the VCF content
            
            for contact in contacts:
                contact_name = contact.fn.value if 'fn' in contact.contents else ''
                contact_email = contact.email.value if 'email' in contact.contents else ''
                contact_phone = contact.tel.value if 'tel' in contact.contents else ''

                # Create a new contact in the database
                Contact.objects.create(
                    first_name=contact_name,
                    email=contact_email,
                    phone_number=contact_phone
                )

            return render(request, 'import_success.html')  # Show a success page

        except Exception as e:
            return render(request, 'import_error.html', {'error': str(e)})  # Show an error page

    return render(request, 'import_contacts.html')  # Render the import form

@login_required
def contacts_list(request):
    contacts = Contact.objects.all()  # Fetch all contacts
    return render(request, 'contacts_list.html', {'contacts': contacts})

@login_required
def export_contacts(request):
    contacts = Contact.objects.all()
    output = []
    for contact in contacts:
        vcard = vobject.vCard()
        vcard.add('fn').value = f"{contact.first_name} {contact.last_name}"
        vcard.add('tel').value = contact.phone_number
        if contact.email:
            vcard.add('email').value = contact.email
        output.append(vcard.serialize())
    response = HttpResponse(output, content_type='text/vcard')
    response['Content-Disposition'] = 'attachment; filename="contacts.vcf"'
    return response



@login_required
def merge_duplicates(request):
    # Find duplicates based on the 'email' field (you can change this to 'phone_number' or 'first_name')
    duplicates = Contact.objects.values('email').annotate(email_count=Count('email')).filter(email_count__gt=1)
    
    # Get the actual duplicate contacts
    duplicate_contacts = Contact.objects.filter(email__in=[item['email'] for item in duplicates])
    
    if request.method == 'POST':
        contact1_id = request.POST.get('contact1_id')  # Primary contact
        contact2_id = request.POST.get('contact2_id')  # Duplicate contact to merge into primary
        
        # Ensure valid IDs are passed
        if not contact1_id or not contact2_id:
            return render(request, 'merge_duplicates.html', {
                'duplicates': duplicate_contacts,
                'error': 'Please select both contacts.'
            })
        
        # Get contacts by their IDs
        contact1 = get_object_or_404(Contact, id=contact1_id)
        contact2 = get_object_or_404(Contact, id=contact2_id)

        # Merge data from contact2 into contact1
        contact1.first_name = contact1.first_name or contact2.first_name
        contact1.last_name = contact1.last_name or contact2.last_name
        contact1.phone_number = contact1.phone_number or contact2.phone_number
        contact1.email = contact1.email or contact2.email
        

        # Save merged contact1
        contact1.save()
        
        # Delete contact2 (only if it is completely redundant)
        contact2.delete()
        
        # Redirect to the contact list
        return redirect('contact_list')

    return render(request, 'merge_duplicates.html', {
        'duplicates': duplicate_contacts
    })

# Create your views here.


# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('contact_list')
    return render(request, 'login.html')

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')
